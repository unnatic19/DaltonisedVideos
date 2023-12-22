import cv2
import numpy as np
from PIL import Image
from daltonlens import simulate

def transform_colorspace(img, mat):
    return img @ mat.T

def enhance_red_green_contrast(frame, contrast_factor=1.5):
    # Extract red and green channels
    red_channel = frame[:, :, 2]
    green_channel = frame[:, :, 1]

    # Increase the contrast in the red channel
    red_channel = np.clip(contrast_factor * red_channel, 0, 255)

    # Replace the red channel in the original frame
    frame[:, :, 2] = red_channel

    return frame

def simulate_protanomaly(frame, severity=0.8):
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Create a simulator using the Viénot 1999 algorithm
    simulator = simulate.Simulator_Vienot1999()

    # Apply the simulator to the input frame to get a simulation of protanomaly
    protan_frame = simulator.simulate_cvd(frame_rgb, simulate.Deficiency.PROTAN, severity=severity)

    # Convert the NumPy array back to BGR
    protan_frame_bgr = cv2.cvtColor(protan_frame.astype(np.uint8), cv2.COLOR_RGB2BGR)

    return protan_frame_bgr

def process_video(input_path, output_path_contrast, output_path_protan, contrast_factor=1.5, severity=0.8):
    cap = cv2.VideoCapture(input_path)

    # Get the video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create VideoWriter objects
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_contrast = cv2.VideoWriter(output_path_contrast, fourcc, fps, (width, height))
    out_protan = cv2.VideoWriter(output_path_protan, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Enhance red/green contrast
        enhanced_frame = enhance_red_green_contrast(frame, contrast_factor)

        # Simulate protanomaly
        protan_frame = simulate_protanomaly(frame, severity)

        # Write frames to the output videos
        out_contrast.write(enhanced_frame)
        out_protan.write(protan_frame)

    # Release video capture and writer objects
    cap.release()
    out_contrast.release()
    out_protan.release()
