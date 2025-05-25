import nuke
import os


def validate_output_path(output_path):
    """
    Validates the output path to ensure it's a valid, absolute, writable file path.
    Adds checks for proper naming conventions for png.

    Args:
        output_path (str): The full file path specified by the user.

    Returns:
        bool: True if the path is valid, False otherwise.
    """
    output_path = output_path.strip()

    if not output_path:
        nuke.message("Please specify an output path.")
        return False
    
    
    # Extract the directory from the full file path
    output_folder = os.path.dirname(output_path)

    # Ensure the file name is not empty
    if not os.path.splitext(os.path.basename(output_path))[0]:
        nuke.message("You must assign a file name.")
        return False

    # Check if the directory exists and create it if it doesn't
    if not os.path.isdir(output_folder):
        try:
            os.makedirs(output_folder)
        except Exception as e:
            nuke.message(f"Invalid output directory: {e}")
            return False


    # Check if the path is writable
    if not os.access(output_folder, os.W_OK):
        nuke.message("The specified output path is not writable.")
        return False
    
    # Ensure the file has proper sequence numbering for png files
    if output_path.lower().endswith(".png"):
        if not ("%04d" in output_path or "%03d" in output_path):
            nuke.message("Path to files must contain '%04d' or '%03d' for sequence numbering.")
            return False
    else:
        nuke.message("Output file must be an PNG file or sequence.")
        return False

    return True



def create_read(output_path):

    # Extract the directory, base name, and extension from the output path
    output_dir = os.path.dirname(output_path)
    base_name = os.path.basename(output_path)
    file_extension = os.path.splitext(base_name)[-1]  # Extract the file extension (e.g., .png, .jpg, etc.)

    # Identify the actual first frame number from the files in the folder
    frames = [f for f in sorted(os.listdir(output_dir)) if f.endswith(file_extension)]
    if not frames:
        nuke.message(f"No frames with extension {file_extension} found in the output directory.")
        return False


    # Extract the frame numbers and calculate the offset
    first_frame_file = frames[0]
    first_frame_number = int(first_frame_file.split('.')[-2])  # Extract frame number
    first_frame = first_frame_number  # Start frame of the sequence
    last_frame_file = frames[-1]
    last_frame_number = int(last_frame_file.split('.')[-2])  # Extract last frame number
    last_frame = last_frame_number  # End frame of the sequence

    # Automatically create a Read node with the output path
    read_node = nuke.createNode("Read")
    read_node["file"].setValue(output_path)
    read_node["first"].setValue(first_frame)
    read_node["last"].setValue(last_frame)
    read_node["reload"].execute()

    return True
    