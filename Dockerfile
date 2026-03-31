FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for building some python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploaded_documents
RUN mkdir -p /app/chroma_db

COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL="sqlite:///./sql_app.db"
ENV CHROMA_DB_DIR="./chroma_db"
ENV SECRET_KEY="your-super-secret-key-change-it"

EXPOSE 8000

# Run migrations and start the app
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
