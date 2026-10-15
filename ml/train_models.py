from pathlib import Path
import json
import time
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StringIndexerModel
from pyspark.ml.classification import (
    LogisticRegression,
    DecisionTreeClassifier,
    RandomForestClassifier,
)
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
)

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    roc_auc_score,
)

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "out" / "ml"
MODELS = ROOT / "ml" / "models"

OUTPUT.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "duration", "protocol_type", "service", "flag",
    "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
    "hot", "num_failed_logins", "logged_in", "num_compromised",
    "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count",
    "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
    "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
    "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate", "attack_label", "difficulty",
]

CATEGORICAL = ["protocol_type", "service", "flag"]

DOS = {
    "back", "land", "neptune", "pod", "smurf", "teardrop",
    "apache2", "mailbomb", "processtable", "udpstorm", "worm",
}
PROBE = {"ipsweep", "nmap", "portsweep", "satan", "mscan", "saint"}
R2L = {
    "ftp_write", "guess_passwd", "imap", "multihop", "phf", "spy",
    "warezclient", "warezmaster", "named", "sendmail",
    "snmpgetattack", "snmpguess", "xlock", "xsnoop", "httptunnel",
}
U2R = {
    "buffer_overflow", "loadmodule", "perl", "rootkit",
    "ps", "sqlattack", "xterm",
}


def locate_dataset(filename):
    candidates = [
        ROOT / "data" / "raw" / filename,
        ROOT.parent / "big-data-network-intrusion-analysis"
        / "data" / "raw" / filename,
        ROOT.parent / "NSL-KDD-Dataset-master" / filename,
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        f"Could not locate {filename}. Checked:\n"
        + "\n".join(str(p) for p in candidates)
    )


def category_expression():
    label = F.lower(F.regexp_replace(F.col("attack_label"), r"\.$", ""))

    return (
        F.when(label == "normal", "Normal")
        .when(label.isin(*sorted(DOS)), "DoS")
        .when(label.isin(*sorted(PROBE)), "Probe")
        .when(label.isin(*sorted(R2L)), "R2L")
        .when(label.isin(*sorted(U2R)), "U2R")
        .otherwise("Unknown")
    )


def load_dataset(spark, filename):
    path = locate_dataset(filename)
    print(f"\nReading {path}")

    df = (
        spark.read
        .option("header", "false")
        .option("inferSchema", "false")
        .option("mode", "PERMISSIVE")
        .csv(str(path))
    )

    if len(df.columns) != 43:
        raise ValueError(
            f"{filename}: expected 43 columns, found {len(df.columns)}"
        )

    df = df.toDF(*COLUMNS)

    for col in CATEGORICAL + ["attack_label"]:
        df = df.withColumn(col, F.trim(F.col(col)))

    df = df.withColumn(
        "attack_label",
        F.regexp_replace(F.col("attack_label"), r"\.$", ""),
    )

    numeric_columns = [
        c for c in COLUMNS
        if c not in CATEGORICAL + ["attack_label"]
    ]

    for col in numeric_columns:
        df = df.withColumn(
            col,
            F.col(col).cast(DoubleType()),
        )

    df = df.withColumn("attack_category", category_expression())

    # Exclude rows with missing or invalid numeric values.
    valid_condition = F.col("attack_label").isNotNull()

    for col in numeric_columns:
        valid_condition = valid_condition & F.col(col).isNotNull()

    df = df.filter(valid_condition)

    # Do not silently include labels that cannot be mapped to a known class.
    unknown_labels = (
        df.filter(F.col("attack_category") == "Unknown")
        .select("attack_label")
        .distinct()
        .collect()
    )

    if unknown_labels:
        labels = sorted(row["attack_label"] for row in unknown_labels)
        print(f"WARNING: Unmapped labels found: {labels}")
        print("These records will be excluded from five-class modelling.")

    df = df.withColumn(
        "binary_label",
        F.when(F.col("attack_category") == "Normal", "Normal")
        .otherwise("Attack"),
    )

    print(f"Valid records in {filename}: {df.count():,}")
    return df


def get_feature_columns():
    return [
        c for c in COLUMNS
        if c not in ["attack_label", "difficulty"]
    ]


def build_pipeline(target, algorithm):
    categorical_indexers = [
        StringIndexer(
            inputCol=c,
            outputCol=f"{c}_index",
            handleInvalid="keep",
        )
        for c in CATEGORICAL
    ]

    encoder = OneHotEncoder(
        inputCols=[f"{c}_index" for c in CATEGORICAL],
        outputCols=[f"{c}_encoded" for c in CATEGORICAL],
        handleInvalid="keep",
    )

    numeric_columns = [
        c for c in get_feature_columns()
        if c not in CATEGORICAL
    ]

    assembler = VectorAssembler(
        inputCols=[
            f"{c}_encoded" for c in CATEGORICAL
        ] + numeric_columns,
        outputCol="features",
        handleInvalid="error",
    )

    label_indexer = StringIndexer(
        inputCol=target,
        outputCol="label",
        handleInvalid="error",
    )

    if algorithm == "Logistic Regression":
        classifier = LogisticRegression(
            featuresCol="features",
            labelCol="label",
            maxIter=40,
            regParam=0.01,
        )

    elif algorithm == "Decision Tree":
        classifier = DecisionTreeClassifier(
            featuresCol="features",
            labelCol="label",
            maxDepth=12,
            seed=42,
        )

    elif algorithm == "Random Forest":
        classifier = RandomForestClassifier(
            featuresCol="features",
            labelCol="label",
            numTrees=60,
            maxDepth=12,
            seed=42,
        )

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    return Pipeline(stages=[
        *categorical_indexers,
        encoder,
        assembler,
        label_indexer,
        classifier,
    ])


def evaluate_predictions(predictions, label_indexer_model, task):
    actual = np.array([
        int(row["label"]) for row in predictions.select("label").collect()
    ])

    predicted = np.array([
        int(row["prediction"])
        for row in predictions.select("prediction").collect()
    ])

    labels = list(range(len(label_indexer_model.labels)))
    class_names = label_indexer_model.labels

    accuracy = float(accuracy_score(actual, predicted))

    precision, recall, f1, support = precision_recall_fscore_support(
        actual,
        predicted,
        labels=labels,
        zero_division=0,
    )

    macro_f1 = float(np.mean(f1))
    weighted_f1 = float(
        precision_recall_fscore_support(
            actual,
            predicted,
            labels=labels,
            average="weighted",
            zero_division=0,
        )[2]
    )

    macro_precision = float(np.mean(precision))
    macro_recall = float(np.mean(recall))

    metrics = {
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
    }

    print("\nClassification report:")
    print(classification_report(
        actual,
        predicted,
        labels=labels,
        target_names=class_names,
        zero_division=0,
    ))

    matrix = confusion_matrix(actual, predicted, labels=labels)

    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(matrix, aspect="auto")
    ax.set_title(f"{task}: Confusion Matrix")
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("Actual class")
    ax.set_xticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=35, ha="right")
    ax.set_yticks(range(len(class_names)))
    ax.set_yticklabels(class_names)
    fig.colorbar(image, ax=ax, label="Records")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, str(matrix[i, j]),
                    ha="center", va="center", fontsize=8)

    fig.tight_layout()
    safe_task = task.lower().replace(" ", "_")
    fig.savefig(
        OUTPUT / f"{safe_task}_confusion_matrix.png",
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(fig)

    class_rows = []
    for i, name in enumerate(class_names):
        class_rows.append({
            "class": name,
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        })

    pd.DataFrame(class_rows).to_csv(
        OUTPUT / f"{safe_task}_per_class_metrics.csv",
        index=False,
    )

    return metrics


def run_task(train_df, test_df, target, task_name, spark):
    print("\n" + "=" * 70)
    print(f"STARTING TASK: {task_name}")
    print("=" * 70)

    if target == "attack_category":
        train_data = train_df.filter(
            F.col("attack_category") != "Unknown"
        )
        test_data = test_df.filter(
            F.col("attack_category") != "Unknown"
        )
    else:
        train_data = train_df
        test_data = test_df

    # The official test set is held back until model selection is complete.
    training, validation = train_data.randomSplit(
        [0.8, 0.2],
        seed=42,
    )

    training.cache()
    validation.cache()
    test_data.cache()

    print(f"Training split:   {training.count():,}")
    print(f"Validation split: {validation.count():,}")
    print(f"Test records:     {test_data.count():,}")

    algorithms = [
        "Logistic Regression",
        "Decision Tree",
        "Random Forest",
    ]

    results = []
    fitted_models = {}

    for algorithm in algorithms:
        print(f"\nTraining {algorithm} for {task_name}...")
        start = time.time()

        pipeline = build_pipeline(target, algorithm)
        model = pipeline.fit(training)

        elapsed = time.time() - start
        validation_predictions = model.transform(validation)

        # Find the fitted label StringIndexerModel for this target.
        label_indexer_model = next(
            (
                stage
                for stage in model.stages
                if isinstance(stage, StringIndexerModel)
                and stage.getInputCol() == target
            ),
            None,
        )

        metrics = evaluate_predictions(
            validation_predictions,
            label_indexer_model,
            f"{task_name}_{algorithm}_validation",
        )

        metrics.update({
            "task": task_name,
            "model": algorithm,
            "training_seconds": round(elapsed, 2),
        })

        results.append(metrics)
        fitted_models[algorithm] = model

        print(
            f"Validation macro-F1: {metrics['macro_f1']:.4f} | "
            f"weighted-F1: {metrics['weighted_f1']:.4f} | "
            f"accuracy: {metrics['accuracy']:.4f}"
        )

    results_df = pd.DataFrame(results)
    safe_task = task_name.lower().replace(" ", "_")

    results_df.to_csv(
        OUTPUT / f"{safe_task}_model_comparison.csv",
        index=False,
    )

    # Select the model using validation macro-F1, not test performance.
    winner = results_df.sort_values(
        ["macro_f1", "weighted_f1"],
        ascending=False,
    ).iloc[0]

    best_name = winner["model"]
    best_model = fitted_models[best_name]

    print(f"\nSelected model for {task_name}: {best_name}")
    print(f"Validation macro-F1: {winner['macro_f1']:.4f}")

    # Evaluate the chosen model once on the held-out official test set.
    test_predictions = best_model.transform(test_data)

    test_metrics = evaluate_predictions(
        test_predictions,
        label_indexer_model=next(
            stage for stage in best_model.stages
            if isinstance(stage, StringIndexerModel)
            and stage.getInputCol() == target
        ),
        task=f"{task_name}_test",
    )

    test_metrics.update({
        "task": task_name,
        "selected_model": best_name,
    })

    with (OUTPUT / f"{safe_task}_test_metrics.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(test_metrics, f, indent=2)

    best_model.write().overwrite().save(
        str(MODELS / safe_task)
    )

    print("\nHeld-out test metrics:")
    for name, value in test_metrics.items():
        print(f"{name}: {value}")

    # Feature importance is available for tree-based models.
    classifier = best_model.stages[-1]

    if hasattr(classifier, "featureImportances"):
        importances = classifier.featureImportances.toArray()

        assembler = next(
            stage for stage in best_model.stages
            if isinstance(stage, VectorAssembler)
        )

        feature_names = []
        for name in assembler.getInputCols():
            if name.endswith("_encoded"):
                feature_names.append(name)
            else:
                feature_names.append(name)

        # One-hot encoding expands categorical variables into multiple
        # vector dimensions, so report importance by vector index here.
        importance_df = pd.DataFrame({
            "feature_vector_index": range(len(importances)),
            "importance": importances,
        }).sort_values("importance", ascending=False)

        importance_df.to_csv(
            OUTPUT / f"{safe_task}_feature_importance.csv",
            index=False,
        )

        top = importance_df.head(20).sort_values("importance")

        plt.figure(figsize=(10, 7))
        plt.barh(
            top["feature_vector_index"].astype(str),
            top["importance"],
        )
        plt.title(f"{task_name}: Top 20 Feature Vector Importances")
        plt.xlabel("Feature importance")
        plt.ylabel("Vector index")
        plt.tight_layout()
        plt.savefig(
            OUTPUT / f"{safe_task}_feature_importance.png",
            dpi=180,
            bbox_inches="tight",
        )
        plt.close()

    # Model-comparison chart.
    ordered = results_df.sort_values("macro_f1")

    plt.figure(figsize=(9, 5))
    plt.barh(ordered["model"], ordered["macro_f1"])
    plt.xlabel("Validation macro-F1")
    plt.title(f"{task_name}: Model Comparison")
    plt.xlim(0, 1)
    plt.tight_layout()
    plt.savefig(
        OUTPUT / f"{safe_task}_model_comparison.png",
        dpi=180,
        bbox_inches="tight",
    )
    plt.close()

    training.unpersist()
    validation.unpersist()
    test_data.unpersist()

    return test_metrics


def main():
    spark = (
        SparkSession.builder
        .appName("NSL-KDD Machine Learning Comparison")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:
        train_df = load_dataset(spark, "KDDTrain+.txt")
        test_df = load_dataset(spark, "KDDTest+.txt")

        print("\nTraining category distribution:")
        train_df.groupBy("attack_category").count().orderBy(
            "attack_category"
        ).show(truncate=False)

        print("\nOfficial test category distribution:")
        test_df.groupBy("attack_category").count().orderBy(
            "attack_category"
        ).show(truncate=False)

        binary_results = run_task(
            train_df,
            test_df,
            "binary_label",
            "Binary Detection",
            spark,
        )

        multiclass_results = run_task(
            train_df,
            test_df,
            "attack_category",
            "Five Class Detection",
            spark,
        )

        final_summary = {
            "dataset": "NSL-KDD",
            "binary_test_metrics": binary_results,
            "five_class_test_metrics": multiclass_results,
            "model_directory": str(MODELS),
            "results_directory": str(OUTPUT),
        }

        with (OUTPUT / "final_ml_summary.json").open(
            "w", encoding="utf-8"
        ) as f:
            json.dump(final_summary, f, indent=2)

        print("\n" + "=" * 70)
        print("MACHINE-LEARNING EXPERIMENTS COMPLETED")
        print(f"Metrics and charts: {OUTPUT}")
        print(f"Saved models: {MODELS}")
        print("=" * 70)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
