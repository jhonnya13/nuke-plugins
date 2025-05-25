import argparse
import sys
import os
from typing import Tuple
import torch
from torchvision.transforms import Compose
import numpy as np
import cv2

# Add the MiDaS folder to the Python path
current_dir = os.path.dirname(__file__)
midas_path = os.path.join(current_dir, "MiDaS")
sys.path.append(midas_path)


from midas.dpt_depth import DPTDepthModel
from hubconf import transforms

def load_midas_model(model_type: str = "DPT_Hybrid") -> Tuple[torch.nn.Module, Compose]:
    """Function to load MiDaS model for depth map generation.

    Possible options for model_type: "DPT_Large", "DPT_Hybrid", "MiDaS_small"

    Args:
        model_type (str, optional): Model type. Defaults to "DPT_Hybrid".

    Returns:
        Tuple[torch.nn.Module, Compose]: Model and transform
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    if model_type == "DPT_Hybrid":
        model_path = os.path.join(current_dir, 'models', 'dpt_hybrid_384.pt')
        backbone = "vitb_rn50_384"
    elif model_type == "DPT_Large":
        model_path = os.path.join(current_dir, 'models', 'dpt_large_384.pt')
        backbone = "vitl16_384"
    #elif model_type == "MiDaS_small":
        #model_path = os.path.join(current_dir, 'models', 'midas_v21_small_256.pt')
        #backbone = "efficientnet_lite3"
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    model = DPTDepthModel(
        path=model_path,
        backbone=backbone,
        non_negative=True,
    )

    model.to('cpu')
    model.eval()

    transforms_list = transforms()
    transform = transforms_list.dpt_transform

    return model, transform

def get_depth_map(image: np.array, model: torch.nn.Module, transform: Compose) -> np.array:
    """Function to get depth map of an image given Midas model is used

    Args:
        image (np.array): initial frame
        model (torch.nn.Module): Midas model
        transform (Compose): transform

    Returns:
        np.array: depth map of an image, has the same shape as original
    """

    # Select device: GPU if available, otherwise CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Move model to the selected device
    model.to(device)

    input_batch = transform(image).to(device)

    with torch.no_grad():
        prediction = model(input_batch)

    prediction = torch.nn.functional.interpolate(
        prediction.unsqueeze(1),
        size=image.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

    depth_map = prediction.cpu().numpy()

    return depth_map

def process_frames(input_dir, output_path, model_type):
    """
    Process all frames in the input directory and save depth maps to the output path.

    Args:
        input_dir (str): Directory containing input images (png only).
        output_path (str): Base path for output images.
        model_type (str): Model type for depth estimation.
    """

    model, transform = load_midas_model(model_type)

    
    # Get list of all frames in the input directory
    frames = [f for f in sorted(os.listdir(input_dir)) if f.endswith((".png"))]
    total_frames = len(frames)


    for idx, filename in enumerate(frames):

        # Extract frame number from the input filename
        try:
            frame_number = int(filename.split('.')[-2])  # Assuming format 'frame.####.ext'
        except ValueError:
            print(f"Skipping file with unexpected format: {filename}")
            continue


        input_path = os.path.join(input_dir, filename)
        # Construct the full output path using the input frame number
        output_full_path = output_path % frame_number

        # Read the image
        image = cv2.imread(input_path)
        if image is None:
            print(f"Failed to read {input_path}")
            continue

        # Convert image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Get depth map
        depth_map = get_depth_map(image_rgb, model, transform)

        # Normalize and save depth map
        depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
        depth_map_uint8 = depth_map_normalized.astype(np.uint8)
        cv2.imwrite(output_full_path, depth_map_uint8)
        # print(f"Saved depth map to: {output_full_path}")

        # Print progress
        progress = int(((idx + 1) / total_frames) * 100)
        print(f"Progress: {progress}%")
        sys.stdout.flush()  # Ensure the output is flushed immediately


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input frames directory")
    parser.add_argument("--output", required=True, help="Path to save depth maps directory")
    parser.add_argument("--model", required=True, help="Model type: MiDaS Low, MiDaS High")

    args = parser.parse_args()
    process_frames(args.input, args.output, args.model)

if __name__ == "__main__":
    main()


