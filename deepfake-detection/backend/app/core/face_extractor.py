import cv2
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceExtractor:
    def __init__(self, device='cpu', margin=20, image_size=224):
        self.device = device
        self.margin = margin
        self.image_size = image_size

        # MTCNN for face detection
        self.mtcnn = MTCNN(
            image_size=image_size,
            margin=margin,
            keep_all=True,
            post_process=False,
            device=device
        )
        logger.info(f"Initialized MTCNN face detector on {self.device}")

    def extract_faces_from_frame(self, frame):
        """
        Extract faces from a single BGR frame (numpy array).
        Returns a list of cropped faces as PIL Images.
        """
        # Convert BGR (OpenCV) to RGB (PIL)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        try:
            # detect faces
            boxes, _ = self.mtcnn.detect(pil_image)

            faces = []
            if boxes is not None:
                for box in boxes:
                    # Apply margin
                    x1, y1, x2, y2 = [int(b) for b in box]
                    w = x2 - x1
                    h = y2 - y1

                    # Calculate new box with margin
                    x1 = max(0, x1 - self.margin)
                    y1 = max(0, y1 - self.margin)
                    x2 = min(pil_image.width, x2 + self.margin)
                    y2 = min(pil_image.height, y2 + self.margin)

                    face_crop = pil_image.crop((x1, y1, x2, y2))
                    # Resize to expected input size
                    face_crop = face_crop.resize((self.image_size, self.image_size), Image.Resampling.LANCZOS)
                    faces.append(face_crop)

            return faces, boxes
        except Exception as e:
            logger.error(f"Error extracting faces: {e}")
            return [], None

    def process_video(self, video_path, interval_sec=1.0):
        """
        Extract frames at optimal intervals and detect faces.
        Returns list of (frame_idx, face_pil, box)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video {video_path}")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval_sec)
        if frame_interval == 0:
            frame_interval = 1

        extracted_data = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                faces, boxes = self.extract_faces_from_frame(frame)
                if faces and boxes is not None:
                    # Just taking the largest face or first face for simplicity
                    # A more robust system might process all faces
                    extracted_data.append({
                        "frame_idx": frame_idx,
                        "time_sec": frame_idx / fps,
                        "faces": faces,
                        "boxes": boxes,
                        "original_frame": frame
                    })

            frame_idx += 1

        cap.release()
        return extracted_data
