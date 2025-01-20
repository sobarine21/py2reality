import streamlit as st
import os
import subprocess
import time
from pathlib import Path

# Title and Description
st.title("Python Script to EXE Converter")
st.markdown("""
Upload a Python script (.py), and this app will convert it into a standalone `.exe` file for desktop use.
- The `.exe` file will be provided as a download after processing.
""")

# Upload Python script
uploaded_file = st.file_uploader("Upload Python Script", type=["py"])
output_dir = "converted_exe"

# Function to convert Python script to .exe
def convert_to_exe(script_path):
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Run PyInstaller
        result = subprocess.run(
            ["pyinstaller", "--onefile", "--distpath", output_dir, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            return None, result.stderr
        
        # Find the generated .exe file
        script_name = Path(script_path).stem
        exe_path = os.path.join(output_dir, f"{script_name}.exe")
        if os.path.exists(exe_path):
            return exe_path, None
        else:
            return None, "Failed to locate the generated .exe file."
    except Exception as e:
        return None, str(e)

# Process the uploaded script
if uploaded_file:
    # Save the uploaded script temporarily
    temp_script_path = os.path.join("temp_scripts", uploaded_file.name)
    Path("temp_scripts").mkdir(parents=True, exist_ok=True)
    
    with open(temp_script_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"Uploaded: {uploaded_file.name}")
    
    # Convert the script
    if st.button("Convert to .exe"):
        with st.spinner("Converting to .exe... This may take a moment."):
            exe_file, error = convert_to_exe(temp_script_path)
        
        # Handle conversion result
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

# Clean up
if st.button("Clear All"):
    if os.path.exists("temp_scripts"):
        for file in os.listdir("temp_scripts"):
            os.remove(os.path.join("temp_scripts", file))
        os.rmdir("temp_scripts")
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))
        os.rmdir(output_dir)
    st.success("Temporary files cleared!")
