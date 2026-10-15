import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
RESULTS_DIR = ML_DIR / "results"
VISUALIZATIONS_DIR = ML_DIR / "visualizations"
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"

BINARY_MODEL_PATH = MODELS_DIR / "binary_detection"
FIVE_CLASS_MODEL_PATH = MODELS_DIR / "five_class_detection"
FALLBACK_HISTORY_PATH = DATA_DIR / "prediction_history_fallback.json"

# Database Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "intrusion_detection_db")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "prediction_history")
MONGODB_TIMEOUT_MS = int(os.getenv("MONGODB_TIMEOUT_MS", "1500"))

# Server Configuration
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
