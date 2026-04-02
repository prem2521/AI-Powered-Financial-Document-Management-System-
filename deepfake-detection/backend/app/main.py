import os
import uuid
import shutil
from typing import Dict
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.services.video_analyzer import VideoAnalyzer

app = FastAPI(title="Deepfake Detection API")

# Setup CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../uploads'))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store results in memory (in production, use a database or Redis)
RESULTS_STORE: Dict[str, dict] = {}

# Initialize analyzer (model loading is done here)
analyzer = VideoAnalyzer()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Deepfake Detection API"}

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Endpoint to upload a video file.
    """
    # Validate file extension
    allowed_extensions = ['.mp4', '.avi', '.mov']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file format. Allowed formats: {allowed_extensions}")

    # Generate unique ID for this analysis task
    task_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}{ext}")

    try:
        # Save uploaded file safely
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Initialize status
    RESULTS_STORE[task_id] = {
        "status": "pending",
        "file_path": file_path,
        "filename": file.filename
    }

    return {"task_id": task_id, "message": "Video uploaded successfully. Call /analyze to start processing."}

async def process_video_background(task_id: str, file_path: str):
    """
    Background task to analyze the video
    """
    try:
        RESULTS_STORE[task_id]["status"] = "processing"

        # Analyze video (extracts frames, runs inference, aggregates)
        result = await analyzer.analyze_video(file_path, interval_sec=1.0)

        if result["status"] == "success":
            RESULTS_STORE[task_id].update(result)
        else:
            RESULTS_STORE[task_id]["status"] = "error"
            RESULTS_STORE[task_id]["message"] = result.get("message", "Unknown error")

    except Exception as e:
        RESULTS_STORE[task_id]["status"] = "error"
        RESULTS_STORE[task_id]["message"] = str(e)
    finally:
        # Clean up the uploaded file to save space
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/analyze/{task_id}")
async def analyze(task_id: str, background_tasks: BackgroundTasks):
    """
    Start analysis for a given task ID.
    """
    if task_id not in RESULTS_STORE:
        raise HTTPException(status_code=404, detail="Task ID not found")

    task_info = RESULTS_STORE[task_id]
    if task_info["status"] != "pending":
        return {"message": f"Task is already {task_info['status']}"}

    # Schedule the analysis in the background
    background_tasks.add_task(process_video_background, task_id, task_info["file_path"])

    return {"message": "Analysis started in the background."}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """
    Get the result of an analysis task.
    """
    if task_id not in RESULTS_STORE:
        raise HTTPException(status_code=404, detail="Task ID not found")

    task_data = RESULTS_STORE[task_id]

    # We don't want to return the internal file path
    response_data = {k: v for k, v in task_data.items() if k != 'file_path'}
    return response_data
