import streamlit as st
import os
import cx_Freeze
import sys
from pathlib import Path

# Title and Description
st.title("Python Script to EXE Converter (cx_Freeze)")
st.markdown("""
Upload a Python script (.py), and this app will convert it into a standalone `.exe` file using cx_Freeze. 
The converted .exe file will automatically download upon successful conversion.
""")

# Directories for temporary files
TEMP_DIR = "temp_scripts"
OUTPUT_DIR = "converted_exe"

# Ensure directories exist
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Upload Python script
uploaded_file = st.file_uploader("Upload Python Script", type=["py"])

# Function to convert Python script to .exe using cx_Freeze
def convert_to_exe(script_path):
    try:
        # Create cx_Freeze build options
        build_options = {
            'build_exe': OUTPUT_DIR,
            'include_files': [],  # Add any necessary files here
            'packages': [],  # Add any necessary packages here
            'excludes': [],  # Add any packages to exclude here
        }

        # Create cx_Freeze executable options
        exe = cx_Freeze.Executable(
            script_path,
            base=None,  # Use 'Win32GUI' for GUI applications on Windows
            target_name=os.path.splitext(os.path.basename(script_path))[0] + ".exe"
        )

        # Create cx_Freeze setup
        cx_Freeze.setup(
            name=os.path.splitext(os.path.basename(script_path))[0],
            options={'build_exe': build_options},
            executables=[exe]
        )

        # Get the path to the generated .exe file
        exe_file = os.path.join(OUTPUT_DIR, exe.target_name)

        return exe_file

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

# Handle uploaded script
if uploaded_file:
  # Save the uploaded script temporarily
  script_path = os.path.join(TEMP_DIR, uploaded_file.name)
  with open(script_path, "wb") as f:
    f.write(uploaded_file.getbuffer())

  st.success(f"Uploaded: {uploaded_file.name}")

  # Convert to .exe
  with st.spinner("Converting to .exe... This may take a moment."):
    exe_file = convert_to_exe(script_path)

  # Download .exe automatically on successful conversion
  if exe_file:
    st.success("Conversion successful! Your .exe file is downloading now...")
    with open(exe_file, "rb") as f:
      st.download_button(
          label="Download .exe file",
          data=f,
          file_name=os.path.basename(exe_file),
          mime="application/octet-stream"
      )
  else:
    st.error("Conversion failed. Please review the logs or try again.")

# Clear temporary files automatically after use
if st.button("Clear Temporary Files"):
  # Remove temporary and output directories
  for folder in [TEMP_DIR, OUTPUT_DIR]:
    if os.path.exists(folder):
      for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))
      os.rmdir(folder)
  st.success("Temporary files cleared successfully.")
