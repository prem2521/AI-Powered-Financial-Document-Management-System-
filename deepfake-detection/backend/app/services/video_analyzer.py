import os
import uuid
import asyncio
from typing import Dict, Any
import logging
from concurrent.futures import ProcessPoolExecutor
from app.core.face_extractor import FaceExtractor
from app.core.model import DeepfakeInference
from PIL import Image
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

def process_video_frames(video_path: str, interval_sec: float) -> list:
    """
    Wrapper function to run in a separate process
    """
    extractor = FaceExtractor(device='cpu') # Use CPU for extraction multiprocessing to avoid CUDA context issues
    return extractor.process_video(video_path, interval_sec)

class VideoAnalyzer:
    def __init__(self, model_path: str = None):
        self.device = 'cuda' if __import__('torch').cuda.is_available() else 'cpu'
        self.inference = DeepfakeInference(model_path=model_path, device=self.device)
        self.results_dir = os.path.join(os.path.dirname(__file__), '../../../results')
        os.makedirs(self.results_dir, exist_ok=True)

    def _pil_to_base64(self, img: Image) -> str:
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def _cv2_to_base64(self, img_array) -> str:
        # img_array is BGR
        import cv2
        _, buffer = cv2.imencode('.jpg', img_array)
        return base64.b64encode(buffer).decode("utf-8")

    async def analyze_video(self, video_path: str, interval_sec: float = 1.0) -> Dict[str, Any]:
        """
        Analyze a video for deepfakes.
        """
        logger.info(f"Starting analysis for {video_path}")

        # 1. Extract frames and faces using ProcessPoolExecutor for CPU bound work
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            extracted_data = await loop.run_in_executor(
                pool, process_video_frames, video_path, interval_sec
            )

        if not extracted_data:
            return {
                "status": "error",
                "message": "Could not extract faces from video."
            }

        logger.info(f"Extracted {len(extracted_data)} frames with faces.")

        # 2. Run inference on extracted faces
        frame_results = []
        total_fake_prob = 0.0

        for data in extracted_data:
            faces = data['faces']
            if not faces:
                continue

            # Taking the first face
            face_pil = faces[0]

            # Predict
            prob = self.inference.predict(face_pil)
            total_fake_prob += prob

            # Generate heatmap
            heatmap_bgr = self.inference.generate_gradcam(face_pil)

            # Store results
            frame_results.append({
                "time_sec": data['time_sec'],
                "frame_idx": data['frame_idx'],
                "fake_probability": prob,
                "is_fake": prob > 0.5,
                "face_image_b64": self._pil_to_base64(face_pil),
                "heatmap_b64": self._cv2_to_base64(heatmap_bgr)
            })

        if not frame_results:
             return {
                "status": "error",
                "message": "No valid faces found for analysis."
            }

        # 3. Aggregate results
        avg_fake_prob = total_fake_prob / len(frame_results)
        final_decision = "Deepfake Detected" if avg_fake_prob > 0.5 else "Real Video"

        logger.info(f"Analysis complete. Result: {final_decision} (Score: {avg_fake_prob:.2f})")

        return {
            "status": "success",
            "result": final_decision,
            "confidence": float(avg_fake_prob if avg_fake_prob > 0.5 else 1 - avg_fake_prob), # Confidence in its decision
            "fake_probability": float(avg_fake_prob),
            "frames_analyzed": len(frame_results),
            "frame_details": frame_results
        }
