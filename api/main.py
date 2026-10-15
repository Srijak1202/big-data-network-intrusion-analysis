import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import (
    CORS_ORIGINS,
    VISUALIZATIONS_DIR,
    RESULTS_DIR,
)
from api.db import db_manager
from api.ml_service import ml_service
from api.presets import PRESET_PROFILES
from api.schemas import (
    ConnectionFeatures,
    PredictionResult,
    SystemHealth,
    PresetProfile,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes Spark MLlib models and verifies database connectivity on startup."""
    logger.info("Starting Network Intrusion Detection API...")
    ml_service.initialize()
    db_manager.check_connection()
    logger.info("API Startup complete.")
    yield
    logger.info("Shutting down API...")
    if ml_service.spark:
        ml_service.spark.stop()
        logger.info("Spark session stopped.")


app = FastAPI(
    title="Network Intrusion Detection System API",
    description="Full-stack Big Data & PySpark MLlib Intrusion Detection Engine (NSL-KDD Review 3)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount precomputed visualizations and model evaluation plots
app.mount(
    "/api/static/visualizations",
    StaticFiles(directory=str(VISUALIZATIONS_DIR)),
    name="visualizations",
)
app.mount(
    "/api/static/results",
    StaticFiles(directory=str(RESULTS_DIR)),
    name="results",
)


@app.get("/", tags=["System"])
def root():
    return {
        "project": "Network Intrusion Detection System (Review 3)",
        "framework": "Apache Spark MLlib & FastAPI",
        "docs": "/docs",
        "status": "online",
        "disclaimer": "This system performs traffic classification on preprocessed NSL-KDD benchmark connection attributes and manual inputs. It does not monitor live interface network traffic.",
    }


@app.get("/api/health", response_model=SystemHealth, tags=["System"])
def health_check():
    """Returns system status, PySpark version, loaded models, and active database connection."""
    db_status = db_manager.get_status()
    spark_ver = ml_service.spark.version if ml_service.spark else "Not initialized"

    return {
        "status": "healthy" if ml_service.binary_model and ml_service.five_class_model else "degraded",
        "spark_version": spark_ver,
        "models_loaded": {
            "binary_detection": ml_service.binary_model is not None,
            "five_class_detection": ml_service.five_class_model is not None,
        },
        "database": db_status,
    }


@app.get("/api/presets", response_model=List[PresetProfile], tags=["Inference"])
def get_preset_profiles():
    """Returns pre-configured benchmark traffic profiles for 1-click demonstration."""
    return PRESET_PROFILES


@app.post("/api/predict/binary", response_model=PredictionResult, tags=["Inference"])
def predict_binary(features: ConnectionFeatures):
    """
    Executes binary classification (Normal vs Attack) using the PySpark MLlib Decision Tree Pipeline.
    Stores prediction in MongoDB (or local fallback).
    """
    try:
        feature_dict = features.model_dump()
        result = ml_service.predict_binary(feature_dict)

        record = {
            "id": f"pred_bin_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "binary",
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "probabilities": result["probabilities"],
            "inference_time_ms": result["inference_time_ms"],
            "features": feature_dict,
        }

        # Store in DB and identify storage type
        storage_type = db_manager.save_prediction(record)
        record["storage_type"] = storage_type

        return record
    except Exception as e:
        logger.error("Error during binary prediction: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}",
        )


@app.post("/api/predict/multiclass", response_model=PredictionResult, tags=["Inference"])
def predict_five_class(features: ConnectionFeatures):
    """
    Executes 5-class classification (Normal, DoS, Probe, R2L, U2R) using the PySpark MLlib Pipeline.
    Stores prediction in MongoDB (or local fallback).
    """
    try:
        feature_dict = features.model_dump()
        result = ml_service.predict_five_class(feature_dict)

        record = {
            "id": f"pred_multi_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "five_class",
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "probabilities": result["probabilities"],
            "inference_time_ms": result["inference_time_ms"],
            "features": feature_dict,
        }

        storage_type = db_manager.save_prediction(record)
        record["storage_type"] = storage_type

        return record
    except Exception as e:
        logger.error("Error during multiclass prediction: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}",
        )


@app.get("/api/history", tags=["History"])
def get_prediction_history(limit: int = 50):
    """Returns stored prediction history from MongoDB or local fallback."""
    records = db_manager.get_history(limit=limit)
    db_status = db_manager.get_status()
    return {
        "database_status": db_status["status"],
        "storage_message": db_status["message"],
        "count": len(records),
        "history": records,
    }


@app.delete("/api/history", tags=["History"])
def clear_prediction_history():
    """Clears stored prediction history."""
    deleted_count = db_manager.clear_history()
    return {"message": "Prediction history cleared", "deleted_count": deleted_count}


# ========================================================
# ANALYTICS & PRECOMPUTED EVALUATION RESULTS
# ========================================================

@app.get("/api/analytics/model-comparison", tags=["Analytics"])
def get_model_comparison():
    """Returns validation metrics comparison across Logistic Regression, Decision Tree, and Random Forest."""
    return ml_service.get_model_comparison()


@app.get("/api/analytics/test-metrics", tags=["Analytics"])
def get_test_metrics():
    """Returns held-out test set metrics and per-class precision, recall, and F1-score."""
    return ml_service.get_test_metrics()


@app.get("/api/analytics/feature-importance", tags=["Analytics"])
def get_feature_importance():
    """Returns top feature importance weights for tree-based models."""
    return ml_service.get_feature_importance()


@app.get("/api/analytics/spark-rdd-summary", tags=["Analytics"])
def get_spark_rdd_summary():
    """Returns Spark RDD aggregated statistics (protocol, category, flag distributions)."""
    return ml_service.get_spark_analytics_summary()


@app.get("/api/visualizations", tags=["Analytics"])
def get_visualizations_catalog():
    """Returns catalog of all saved EDA charts and evaluation figures."""
    return ml_service.get_visualizations_catalog()
