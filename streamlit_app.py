import streamlit as st
import os
import subprocess
from pathlib import Path

# Title and Description
st.title("Python Script to EXE Converter")
st.markdown("""
Upload a Python script (.py), and this app will convert it into a standalone `.exe` file using PyInstaller.
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

    # Check for errors in the PyInstaller process
    if result.returncode != 0:
      st.error("PyInstaller failed. Check the logs below:")
      st.text_area("PyInstaller Logs", result.stdout + "\n" + result.stderr, height=300)
      return None

    # Dynamically detect the .exe file in the OUTPUT_DIR
    script_name = Path(script_path).stem
    for file in os.listdir(OUTPUT_DIR):
      if file.startswith(script_name) and file.endswith(".exe"):
        return os.path.join(OUTPUT_DIR, file)

    # If no .exe file was found, provide a meaningful error message
    st.error("Conversion failed: No .exe file found in the output directory.")
    return None

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
