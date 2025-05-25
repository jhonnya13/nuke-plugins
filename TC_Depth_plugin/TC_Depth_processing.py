import nuke
from TC_Depth.helpers import validate_output_path, create_read
import subprocess
import os
import platform



# Function to run depth estimation (MAIN pipeline)
def run_depth_estimation():
    """
        Main pipeline to run the code.
    """
    
    # Create a progress bar from the start
    task = nuke.ProgressTask("TC_Depth")

    try:
        # Step 1: Validate user input
        task.setMessage("Validating user input...")
        task.setProgress(1)  # Progress 1% during validation

        # Validate user input
        user_input = check_user_input()
        if not user_input:
            return  # Exit early if validation fails

        output_path, model_type = user_input
        task.setProgress(3)  # Update progress after successful validation



        # Step 2: Get the Read path
        task.setMessage("Checking input Read node...")
        stream_image_path = get_read_path()
        if not stream_image_path:
            nuke.message("Connect plugin to the Read node.")
            return  # Exit early if rendering fails
    
        stream_image_dir = os.path.dirname(stream_image_path)
        task.setProgress(5)  # Progress after checking the Read node



        # Step 3: Run depth estimation
        task.setMessage("Preparing the model...(allow 15 sec)")
        success = process_depth_estimation(stream_image_dir, output_path, model_type, task)

        if success:
            depth_path = output_path
            task.setMessage("Creating Read node for output...")
            create_read(depth_path)
            task.setMessage("Depth estimation completed successfully!")
            task.setProgress(100)
        else:
            nuke.message("Depth estimation failed. Read node was not created.")

    except Exception as e:
        nuke.message(f"Error during depth estimation: {e}")
        task.setMessage("An error occurred!")
        task.setProgress(100)

    finally:
        if task.isCancelled():
            task.setMessage("Process cancelled by user.")
        task.setProgress(100)  # Ensure progress reaches 100%



def get_read_path():
    """
        Get the path of the Read node
    """
    node = nuke.thisNode()
    read_node = node.input(0)
    if read_node:
        return read_node["file"].value()
    return None

def check_user_input():
    """
        Check user input before start processing
    """
    print("starting user input check")
    node = nuke.thisNode()
    node.setSelected(True)
    # Get the connected input
    input_node = node.input(0)


    if not input_node:
        nuke.message("Please connect an input image.")
        return None
    
    # Check user-defined output folder and model type before processing
    output_path = node['outputPath'].value()
    model_type = node['modelSelector'].value()

    if not validate_output_path(output_path):
        return None
    
    if not model_type:
        nuke.message("Please choose the model type")
        return None

    print("user input done")
    return output_path, model_type



def process_depth_estimation(stream_image_path, output_path, model_type, task):
    """
        Calls the ML processing script with the necessary arguments. Shows progress bar
    """
    # Get the directory of the current script
    # Get the directory of the current script
    current_dir = os.path.dirname(__file__)
    ml_script = os.path.join(current_dir, "ml_processing.py")
    #ml_script = os.path.join(current_dir, "ml_processing.exe")

    # Path to the Python executable of the desired environment. Add for the tests
    if platform.system() == "Darwin":  # macOS
        python_executable = os.path.join(current_dir, "TC_Depth_venv", "bin", "python")
    elif platform.system() == "Windows":  # Windows
        python_executable = os.path.join(current_dir, "TC_Depth_venv", "Scripts", "python.exe")



    # Command to call the ML script (remove python_executable if using .exe)
    command = [
        python_executable, ml_script,
        "--input", stream_image_path,
        "--output", output_path,
        "--model", model_type
    ]


    try:
        # Start the subprocess
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True, shell=False)

        for line in iter(process.stdout.readline, ''):
            if task.isCancelled():
                process.terminate()
                nuke.message("Depth estimation was cancelled.")
                return

            # Look for progress updates in the output
            if "Progress:" in line:
                try:
                    # Extract progress percentage from output (e.g., "Progress: 45%")
                    progress_value = int(line.strip().split(":")[1].strip().strip('%'))
                    task.setProgress(progress_value)
                    task.setMessage(f"Processing... {progress_value}%")
                except ValueError:
                    pass

        # Wait for the process to complete
        process.wait()

        # Check the return code
        if process.returncode == 0:
            #nuke.message(f"Depth estimation completed successfully.\nResults saved to: {output_path} and {model_type}")
            return True
        else:
            stderr = process.stderr.read()
            nuke.message(f"Error during depth estimation:\n{stderr}")
            return False 
    except Exception as e:
        nuke.message(f"Error: {e}")
        return False 

    finally:
        task.setProgress(100)
        task.setMessage("Done")