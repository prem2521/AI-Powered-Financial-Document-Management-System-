# Deepfake Detection System

A production-ready Deepfake Detection System for videos using Artificial Intelligence. This system uses a state-of-the-art EfficientNet-based model to analyze videos frame-by-frame, extract faces, and classify whether a video is real or a deepfake.

## Features
- Upload and analyze video files (MP4, AVI, MOV).
- Frame extraction and face detection using MTCNN.
- Deepfake classification using EfficientNet.
- Confidence scores and frame-level analysis.
- Heatmap visualization for manipulated regions using Grad-CAM.
- Batch processing support.
- Fully dockerized deployment setup.

## Folder Structure
- `backend/`: FastAPI application, AI models, and inference pipeline.
- `frontend/`: React.js user interface.
- `training/`: Scripts for model training and evaluation.
- `uploads/`: Temporary storage for uploaded videos.
- `results/`: Processed outputs including extracted frames and heatmaps.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Node.js (for local frontend dev)
- Python 3.9+ (for local backend dev)

### Using Docker (Recommended)
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. Access the frontend at `http://localhost:3000`.
3. Access the API documentation at `http://localhost:8000/docs`.

### Manual Setup (Local)

**Backend:**
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run the API: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`.

**Frontend:**
1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`.
3. Start the dev server: `npm start`.

## Training
To fine-tune or train the model, navigate to the `training/` directory and check `train.py`. You'll need to set up datasets like FaceForensics++ or DFDC.
