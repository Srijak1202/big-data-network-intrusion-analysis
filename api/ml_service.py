import csv
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
)
from pyspark.ml import PipelineModel

from api.config import (
    BINARY_MODEL_PATH,
    FIVE_CLASS_MODEL_PATH,
    RESULTS_DIR,
    OUTPUTS_DIR,
    VISUALIZATIONS_DIR,
)

logger = logging.getLogger("api.ml_service")

# NSL-KDD Feature Column Definitions
CATEGORICAL_COLS = ["protocol_type", "service", "flag"]

NUMERIC_COLS = [
    "duration", "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
    "hot", "num_failed_logins", "logged_in", "num_compromised", "root_shell",
    "su_attempted", "num_root", "num_file_creations", "num_shells",
    "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login",
    "count", "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate",
    "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
    "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate"
]

ALL_FEATURE_COLS = CATEGORICAL_COLS + NUMERIC_COLS


class MLService:
    def __init__(self):
        self.spark: Optional[SparkSession] = None
        self.binary_model: Optional[PipelineModel] = None
        self.five_class_model: Optional[PipelineModel] = None
        self.binary_labels: List[str] = ["Normal", "Attack"]
        self.five_class_labels: List[str] = ["Normal", "DoS", "Probe", "R2L", "U2R"]
        self.spark_schema: Optional[StructType] = None

    def initialize(self):
        """Initializes SparkSession and loads the saved PySpark PipelineModels."""
        logger.info("Initializing Apache Spark session...")
        self.spark = (
            SparkSession.builder
            .appName("IntrusionDetectionInference")
            .master("local[1]")
            .config("spark.ui.enabled", "false")
            .config("spark.driver.memory", "1g")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )
        self.spark.sparkContext.setLogLevel("ERROR")

        # Build explicit PySpark schema for incoming feature dictionaries
        fields = []
        for col in ALL_FEATURE_COLS:
            if col in CATEGORICAL_COLS:
                fields.append(StructField(col, StringType(), True))
            else:
                fields.append(StructField(col, DoubleType(), True))
        self.spark_schema = StructType(fields)

        # Load Binary Detection Model
        if Path(BINARY_MODEL_PATH).exists():
            logger.info("Loading binary detection model from %s", BINARY_MODEL_PATH)
            self.binary_model = PipelineModel.load(str(BINARY_MODEL_PATH))
            try:
                # Stage 5 is the label StringIndexerModel
                self.binary_labels = list(self.binary_model.stages[5].labels)
            except Exception as e:
                logger.warning("Could not read labels from binary model stage 5: %s", e)
        else:
            logger.error("Binary model path not found: %s", BINARY_MODEL_PATH)

        # Load Five-Class Detection Model
        if Path(FIVE_CLASS_MODEL_PATH).exists():
            logger.info("Loading five-class detection model from %s", FIVE_CLASS_MODEL_PATH)
            self.five_class_model = PipelineModel.load(str(FIVE_CLASS_MODEL_PATH))
            try:
                self.five_class_labels = list(self.five_class_model.stages[5].labels)
            except Exception as e:
                logger.warning("Could not read labels from five-class model stage 5: %s", e)
        else:
            logger.error("Five-class model path not found: %s", FIVE_CLASS_MODEL_PATH)

        logger.info("MLService initialized successfully.")

    def _prepare_dataframe(self, features: Dict[str, Any]):
        """Formats the input dictionary into a PySpark DataFrame with correct types."""
        row_dict = {}
        for col in ALL_FEATURE_COLS:
            val = features.get(col)
            if col in CATEGORICAL_COLS:
                row_dict[col] = str(val if val is not None else "normal")
            else:
                try:
                    row_dict[col] = float(val if val is not None else 0.0)
                except (ValueError, TypeError):
                    row_dict[col] = 0.0

        return self.spark.createDataFrame([Row(**row_dict)], schema=self.spark_schema)

    def predict_binary(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Runs binary classification (Normal vs Attack) using the saved pipeline model."""
        if not self.binary_model or not self.spark:
            raise RuntimeError("Binary model or Spark session is not loaded.")

        start_time = time.time()
        df = self._prepare_dataframe(features)
        predictions = self.binary_model.transform(df).collect()
        elapsed_ms = (time.time() - start_time) * 1000.0

        if not predictions:
            raise RuntimeError("Model returned no predictions.")

        res = predictions[0]
        pred_idx = int(res["prediction"])
        probs = [float(p) for p in res["probability"].toArray()]

        pred_class = (
            self.binary_labels[pred_idx]
            if pred_idx < len(self.binary_labels)
            else "Unknown"
        )
        confidence = probs[pred_idx] if pred_idx < len(probs) else 0.0

        prob_dict = {}
        for idx, label in enumerate(self.binary_labels):
            if idx < len(probs):
                prob_dict[label] = round(probs[idx], 4)

        return {
            "predicted_class": pred_class,
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "inference_time_ms": round(elapsed_ms, 2),
        }

    def predict_five_class(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Runs 5-class classification (Normal, DoS, Probe, R2L, U2R) using the saved pipeline model."""
        if not self.five_class_model or not self.spark:
            raise RuntimeError("Five-class model or Spark session is not loaded.")

        start_time = time.time()
        df = self._prepare_dataframe(features)
        predictions = self.five_class_model.transform(df).collect()
        elapsed_ms = (time.time() - start_time) * 1000.0

        if not predictions:
            raise RuntimeError("Model returned no predictions.")

        res = predictions[0]
        pred_idx = int(res["prediction"])
        probs = [float(p) for p in res["probability"].toArray()]

        pred_class = (
            self.five_class_labels[pred_idx]
            if pred_idx < len(self.five_class_labels)
            else "Unknown"
        )
        confidence = probs[pred_idx] if pred_idx < len(probs) else 0.0

        prob_dict = {}
        for idx, label in enumerate(self.five_class_labels):
            if idx < len(probs):
                prob_dict[label] = round(probs[idx], 4)

        return {
            "predicted_class": pred_class,
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "inference_time_ms": round(elapsed_ms, 2),
        }

    # ========================================================
    # ACCESSORS FOR PRECOMPUTED EVALUATION & ANALYTICS RESULTS
    # ========================================================

    def get_model_comparison(self) -> Dict[str, Any]:
        """Loads and returns the validation comparison table for all tested algorithms."""
        binary_path = RESULTS_DIR / "binary_detection_model_comparison.csv"
        five_class_path = RESULTS_DIR / "five_class_detection_model_comparison.csv"

        binary_data = []
        if binary_path.exists():
            binary_data = pd.read_csv(binary_path).to_dict(orient="records")

        five_class_data = []
        if five_class_path.exists():
            five_class_data = pd.read_csv(five_class_path).to_dict(orient="records")

        return {
            "binary_comparison": binary_data,
            "five_class_comparison": five_class_data,
        }

    def get_test_metrics(self) -> Dict[str, Any]:
        """Loads and returns the official held-out test set metrics and per-class stats."""
        summary_path = RESULTS_DIR / "final_ml_summary.json"
        summary = {}
        if summary_path.exists():
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)

        binary_per_class = RESULTS_DIR / "binary_detection_test_per_class_metrics.csv"
        five_per_class = RESULTS_DIR / "five_class_detection_test_per_class_metrics.csv"

        binary_classes = []
        if binary_per_class.exists():
            binary_classes = pd.read_csv(binary_per_class).to_dict(orient="records")

        five_classes = []
        if five_per_class.exists():
            five_classes = pd.read_csv(five_per_class).to_dict(orient="records")

        return {
            "summary": summary,
            "binary_test_per_class": binary_classes,
            "five_class_test_per_class": five_classes,
            "note": "Evaluation on NSL-KDD held-out KDDTest+. Low recall on R2L and U2R stems from novel zero-day attack variants introduced in the test benchmark.",
        }

    def get_feature_importance(self) -> Dict[str, Any]:
        """Returns top feature importance weights for the winning Decision Tree models."""
        binary_imp_path = RESULTS_DIR / "binary_detection_feature_importance.csv"
        five_imp_path = RESULTS_DIR / "five_class_detection_feature_importance.csv"

        binary_imp = []
        if binary_imp_path.exists():
            df = pd.read_csv(binary_imp_path).head(15)
            binary_imp = df.to_dict(orient="records")

        five_imp = []
        if five_imp_path.exists():
            df = pd.read_csv(five_imp_path).head(15)
            five_imp = df.to_dict(orient="records")

        return {
            "binary_top_features": binary_imp,
            "five_class_top_features": five_imp,
        }

    def get_spark_analytics_summary(self) -> Dict[str, Any]:
        """Returns the distributed Spark RDD aggregated counts."""
        summary_path = OUTPUTS_DIR / "analytics_summary.json"
        summary = {}
        if summary_path.exists():
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)

        def read_csv(filename):
            p = OUTPUTS_DIR / filename
            if p.exists():
                return pd.read_csv(p).to_dict(orient="records")
            return []

        return {
            "summary": summary,
            "attack_categories": read_csv("attack_category_counts.csv"),
            "protocols": read_csv("protocol_counts.csv"),
            "services": read_csv("service_counts.csv")[:15],
            "flags": read_csv("flag_counts.csv"),
        }

    def get_visualizations_catalog(self) -> List[Dict[str, str]]:
        """Returns a list of all available precomputed visualization images."""
        catalog = []
        titles = {
            "01_attack_category_distribution.png": "Attack Category Distribution",
            "02_attack_category_donut.png": "Proportion of Network Traffic by Category",
            "03_protocol_distribution.png": "Network Protocol Distribution",
            "04_top_services.png": "Top 15 Network Services by Traffic Volume",
            "05_flag_distribution.png": "TCP Connection Flag Distribution",
            "06_protocol_category_stacked.png": "Attack Categories Across Network Protocols",
            "07_service_category_stacked.png": "Attack Categories Across Top Services",
            "08_service_attack_percentage.png": "Services with Highest Attack Percentage",
            "09_duration_boxplot.png": "Connection Duration by Attack Category",
            "10_source_bytes_distribution.png": "Source Byte Distribution by Category",
            "11_destination_bytes_distribution.png": "Destination Byte Distribution by Category",
            "12_error_rates_by_category.png": "Average Connection Error Rates by Category",
            "13_numeric_correlation_heatmap.png": "Correlation Heatmap of Selected Numeric Features",
            "14_top_attack_labels.png": "Top 15 Individual Attack Labels",
            "15_normal_vs_attack_by_protocol.png": "Normal Traffic vs Attack Traffic by Protocol",
            "binary_detection_model_comparison.png": "Binary Detection: Algorithm Macro-F1 Comparison",
            "five_class_detection_model_comparison.png": "Five-Class Detection: Algorithm Macro-F1 Comparison",
            "binary_detection_test_confusion_matrix.png": "Binary Detection: Held-Out Test Confusion Matrix",
            "five_class_detection_test_confusion_matrix.png": "Five-Class Detection: Held-Out Test Confusion Matrix",
            "binary_detection_feature_importance.png": "Binary Detection: Feature Importance Distribution",
            "five_class_detection_feature_importance.png": "Five-Class Detection: Feature Importance Distribution",
        }

        # Scan visualizations folder
        for file in sorted(VISUALIZATIONS_DIR.glob("*.png")):
            name = file.name
            catalog.append({
                "filename": name,
                "title": titles.get(name, name.replace("_", " ").replace(".png", "").title()),
                "category": "EDA & Spark Analysis",
                "url": f"/api/static/visualizations/{name}",
            })

        # Scan ML results folder for charts
        for file in sorted(RESULTS_DIR.glob("*.png")):
            name = file.name
            catalog.append({
                "filename": name,
                "title": titles.get(name, name.replace("_", " ").replace(".png", "").title()),
                "category": "Model Evaluation",
                "url": f"/api/static/results/{name}",
            })

        return catalog


# Singleton instance
ml_service = MLService()
