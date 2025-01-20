import subprocess
import os
from pathlib import Path
import streamlit as st
import zipfile
import shutil
import time
import platform
import json
import hashlib

# Constants
OUTPUT_DIR = "/tmp/output"  # Ensure output is saved in Streamlit's /tmp directory
TEMP_DIR = "/tmp/temp"  # Temporary directory for intermediary files used by PyInstaller
CONFIG_FILE = "config.json"  # Optional configuration file

# Ensure necessary directories exist
def setup_directories():
    """Ensure output directory exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def cleanup_directories():
    """Clean up temporary directories after conversion."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

def log_to_file(log_data, filename="conversion.log"):
    """Log the output of PyInstaller to a file."""
    with open(filename, "a") as log_file:
        log_file.write(f"{time.ctime()} - {log_data}\n")

def show_logs(result):
    """Display PyInstaller logs and show them in a text area."""
    logs = result.stdout + "\n" + result.stderr
    log_to_file(logs)
    st.text_area("PyInstaller Logs", logs, height=300)

def convert_to_exe(script_path, custom_icon=None, add_data_files=False, show_progress=False, single_file=True):
    try:
        # Ensure output directories exist
        setup_directories()

        # Prepare PyInstaller arguments
        script_name = Path(script_path).stem
        pyinstaller_args = [
            "pyinstaller",
            "--distpath", OUTPUT_DIR,
            "--workpath", TEMP_DIR,
            "--name", script_name
        ]

        # Optional custom icon for the .exe file
        if custom_icon:
            pyinstaller_args.append(f"--icon={custom_icon}")

        # Option to add data files (if specified)
        if add_data_files:
            pyinstaller_args.append(f"--add-data=path/to/data;data")  # Customize for your needs

        # Set single file or multi-file options
        if single_file:
            pyinstaller_args.append("--onefile")
        else:
            pyinstaller_args.append("--onedir")

        # Show progress if enabled
        if show_progress:
            pyinstaller_args.append("--log-level=DEBUG")

        # Run PyInstaller
        result = subprocess.run(
            pyinstaller_args + [script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Show logs in the app
        show_logs(result)

        # Check if the process succeeded
        if result.returncode != 0:
            st.error("PyInstaller encountered an error. Check the logs.")
            return None

        # Look for the generated .exe file
        for file in os.listdir(OUTPUT_DIR):
            if file.startswith(script_name) and file.endswith(".exe"):
                exe_path = os.path.join(OUTPUT_DIR, file)
                st.success(f"Conversion successful! The .exe file is available at: {exe_path}")
                return exe_path

        # No .exe found
        st.error("Conversion failed: No .exe file found in the output directory.")
        return None

    except subprocess.CalledProcessError as e:
        st.error(f"PyInstaller failed with error: {str(e)}")
        log_to_file(f"PyInstaller failed with error: {str(e)}")
        return None

    except FileNotFoundError as e:
        st.error(f"Required file not found: {str(e)}")
        log_to_file(f"Required file not found: {str(e)}")
        return None

    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        log_to_file(f"Unexpected error: {str(e)}")
        return None

    finally:
        # Clean up temporary directories
        cleanup_directories()

# Advanced Feature Set

def extract_dependencies(exe_path):
    """Extract .exe dependencies into a folder."""
    if platform.system() == "Windows":
        try:
            zip_path = exe_path + ".zip"
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(os.path.join(OUTPUT_DIR, "dependencies"))
            st.success(f"Dependencies extracted to {OUTPUT_DIR}/dependencies")
        except Exception as e:
            st.error(f"Failed to extract dependencies: {str(e)}")
            log_to_file(f"Failed to extract dependencies from {exe_path}: {str(e)}")
    else:
        st.error("Dependency extraction is only supported on Windows.")

def bundle_dependencies(exe_path):
    """Bundle the executable along with its dependencies."""
    dependencies_dir = os.path.join(OUTPUT_DIR, "dependencies")
    if os.path.exists(dependencies_dir):
        zip_file_path = exe_path + "_dependencies.zip"
        try:
            with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zip_ref:
                for foldername, subfolders, filenames in os.walk(dependencies_dir):
                    for filename in filenames:
                        zip_ref.write(os.path.join(foldername, filename), os.path.relpath(os.path.join(foldername, filename), dependencies_dir))
            st.success(f"Dependencies bundled into {zip_file_path}")
        except Exception as e:
            st.error(f"Failed to bundle dependencies: {str(e)}")
            log_to_file(f"Failed to bundle dependencies for {exe_path}: {str(e)}")
    else:
        st.error("No dependencies folder found to bundle.")

def check_for_virus(exe_path):
    """Check the .exe file for possible virus/malware using an external service (like VirusTotal)."""
    st.warning("Virus scanning feature is not yet implemented but can be added.")

def create_versioned_exe(script_path):
    """Create a versioned executable with a timestamp."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    versioned_name = f"{Path(script_path).stem}_{timestamp}.exe"
    return os.path.join(OUTPUT_DIR, versioned_name)

def validate_script(script_path):
    """Check if the provided script exists."""
    if not os.path.isfile(script_path):
        st.error(f"Script not found: {script_path}")
        return False
    return True

def rename_exe(exe_path, new_name):
    """Rename the .exe file."""
    new_exe_path = os.path.join(OUTPUT_DIR, new_name)
    os.rename(exe_path, new_exe_path)
    st.success(f"Renamed {exe_path} to {new_exe_path}")
    return new_exe_path

def show_progress_bar(current, total):
    """Show a progress bar for long-running processes."""
    st.progress(current / total)

def compress_exe(exe_path):
    """Compress the .exe using UPX (optional)."""
    try:
        subprocess.run(["upx", exe_path], check=True)
        st.success(f"Successfully compressed {exe_path}")
    except subprocess.CalledProcessError as e:
        st.warning(f"Failed to compress {exe_path} with UPX: {str(e)}")

def check_file_hash(file_path, expected_hash):
    """Check if the hash of the file matches the expected hash."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    actual_hash = sha256_hash.hexdigest()
    if actual_hash == expected_hash:
        st.success(f"Hash for {file_path} matches the expected hash.")
    else:
        st.error(f"Hash mismatch for {file_path}. Expected: {expected_hash}, Found: {actual_hash}")

def store_configuration(config_data):
    """Store user settings in a configuration file."""
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config_data, config_file)
    st.success(f"Configuration stored in {CONFIG_FILE}")

def load_configuration():
    """Load user settings from the configuration file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    return {}

def verify_dependencies(exe_path):
    """Verify if all the dependencies required by the .exe are present."""
    st.info("Dependency verification feature is not implemented but could be added.")

def optimize_for_size(exe_path):
    """Optimize the executable for size using various tools or settings."""
    st.info("Executable size optimization is a feature to be added.")

def handle_dynamic_linking(exe_path):
    """Handle dynamic linking issues if detected."""
    st.info("Dynamic linking issues are not handled yet.")

def backup_previous_version(exe_path):
    """Backup the previous version of the .exe before replacing it."""
    backup_path = exe_path + ".bak"
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, backup_path)
        st.success(f"Backup created at {backup_path}")
    else:
        st.error(f"Executable {exe_path} not found to create backup.")

def remove_previous_version(exe_path):
    """Remove the previous version of the .exe."""
    if os.path.exists(exe_path):
        os.remove(exe_path)
        st.success(f"Removed previous version at {exe_path}")
    else:
        st.error(f"{exe_path} not found to remove.")

# Example usage
if __name__ == "__main__":
    # Upload script and icon
    script_file = st.file_uploader("Upload your Python script (.py)", type="py")
    custom_icon = st.file_uploader("Upload a custom icon (.ico)", type="ico")
    
    add_data_files = st.checkbox("Include additional data files")
    show_progress = st.checkbox("Show progress during conversion")
    single_file = st.checkbox("Create a single .exe file")

    # Process when user uploads a Python script
    if script_file is not None:
        # Save the uploaded script file to a temporary location
        script_path = os.path.join(OUTPUT_DIR, script_file.name)
        with open(script_path, "wb") as f:
            f.write(script_file.getbuffer())
        
        # Validate and process the script file
        if validate_script(script_path):
            exe_file = convert_to_exe(
                script_path,
                custom_icon=custom_icon,
                add_data_files=add_data_files,
                show_progress=show_progress,
                single_file=single_file
            )

            if exe_file:
                extract_dependencies(exe_file)
                bundle_dependencies(exe_file)
                compress_exe(exe_file)
                rename_exe(exe_file, "custom_name.exe")
                # Additional Features
                check_file_hash(exe_file, "expected_sha256_hash")
                store_configuration({"custom_icon": custom_icon.name})
                load_configuration()
                backup_previous_version(exe_file)
                remove_previous_version(exe_file)
