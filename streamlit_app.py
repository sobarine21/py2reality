import streamlit as st
import os
import subprocess
from pathlib import Path

# Title and Description
st.title("Python Script to EXE Converter")
st.markdown("""
Upload a Python script (.py), and this app will convert it into a standalone `.exe` file using PyInstaller.
""")

# Directories for temporary files
TEMP_DIR = "temp_scripts"
OUTPUT_DIR = "converted_exe"

# Ensure directories exist
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Upload Python script
uploaded_file = st.file_uploader("Upload Python Script", type=["py"])

# Function to convert Python script to .exe
def convert_to_exe(script_path):
    try:
        # Run PyInstaller with --distpath to control output directory
        result = subprocess.run(
            [
                "pyinstaller",
                "--onefile",
                "--distpath", OUTPUT_DIR,
                script_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Display logs
        st.text_area("PyInstaller Logs", result.stdout + "\n" + result.stderr, height=300)

        # Check for errors in the PyInstaller process
        if result.returncode != 0:
            return None, f"PyInstaller failed with return code {result.returncode}. Check logs above."

        # Dynamically detect the .exe file in the OUTPUT_DIR
        script_name = Path(script_path).stem
        for file in os.listdir(OUTPUT_DIR):
            if file.startswith(script_name) and file.endswith(".exe"):
                return os.path.join(OUTPUT_DIR, file), None

        # If no .exe file was found, provide a meaningful error message
        return None, f"No .exe file found in {OUTPUT_DIR}. Please check PyInstaller logs for details."

    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# Handle uploaded script
if uploaded_file:
    # Save the uploaded script temporarily
    script_path = os.path.join(TEMP_DIR, uploaded_file.name)
    with open(script_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"Uploaded: {uploaded_file.name}")

    # Convert to .exe when the button is clicked
    if st.button("Convert to .exe"):
        with st.spinner("Converting to .exe... This may take a moment."):
            exe_file, error = convert_to_exe(script_path)
        
        # Handle the result of the conversion
        if exe_file:
            st.success("Conversion successful!")
            with open(exe_file, "rb") as f:
                st.download_button(
                    label="Download .exe file",
                    data=f,
                    file_name=os.path.basename(exe_file),
                    mime="application/octet-stream"
                )
        else:
            st.error(f"Conversion failed: {error}")

# Clear all temporary files
if st.button("Clear Temporary Files"):
    # Remove temporary and output directories
    for folder in [TEMP_DIR, OUTPUT_DIR]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
            os.rmdir(folder)
    st.success("All temporary files have been cleared!")
