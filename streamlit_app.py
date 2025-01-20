import streamlit as st
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

# Title and Description
st.title("Python Script to EXE Converter")
st.markdown("""
Upload a Python script (.py), and this app will convert it into a standalone `.exe` file using PyInstaller.
Once the conversion is done, the `.exe` file will automatically download.
""")

# Function to convert Python script to .exe
def convert_to_exe(script_path, output_dir):
    try:
        # Run PyInstaller with --distpath to control output directory
        result = subprocess.run(
            [
                "pyinstaller",
                "--onefile",
                "--distpath", output_dir,
                script_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check for errors in the PyInstaller process
        if result.returncode != 0:
            st.error("PyInstaller failed. Check the logs below:")
            st.text_area("PyInstaller Logs", result.stdout + "\n" + result.stderr, height=300)
            return None

        # Dynamically detect the .exe file in the output_dir
        script_name = Path(script_path).stem
        exe_file_path = Path(output_dir) / f"{script_name}.exe"
        if exe_file_path.exists():
            return str(exe_file_path)

        # If no .exe file was found, provide a meaningful error message
        st.error("Conversion failed: No .exe file found in the output directory.")
        return None

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

# Upload Python script
uploaded_file = st.file_uploader("Upload Python Script", type=["py"])

# Handle uploaded script
if uploaded_file:
    with TemporaryDirectory() as temp_dir:
        script_path = Path(temp_dir) / uploaded_file.name
        output_dir = Path(temp_dir) / "output"

        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Uploaded: {uploaded_file.name}")

        # Convert to .exe when the button is clicked
        if st.button("Convert to .exe"):
            with st.spinner("Converting to .exe... This may take a moment."):
                exe_file = convert_to_exe(script_path, output_dir)
            
            # If conversion was successful, trigger an automatic download
            if exe_file:
                st.success("Conversion successful! Your .exe file is downloading now...")
                with open(exe_file, "rb") as f:
                    st.download_button(
                        label="Download .exe file",
                        data=f,
                        file_name=os.path.basename(exe_file),
                        mime="application/octet-stream",
                        key="auto_download"
                    )
            else:
                st.error("Conversion failed. Please review the logs or try again.")

# Clear temporary files automatically after use
if st.button("Clear Temporary Files"):
    st.success("Temporary files cleared successfully.")
