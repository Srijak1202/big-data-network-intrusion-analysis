import os
import glob
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# Project paths
PROJECT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = PROJECT / "out" / "analysis"
OUTPUT_DIR = PROJECT / "out" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Find the most recent Spark analysis run
runs = sorted(
    [p for p in ANALYSIS_DIR.glob("run_*") if p.is_dir()],
    key=lambda p: p.stat().st_mtime,
)

if not runs:
    raise FileNotFoundError(f"No Spark analysis runs found in {ANALYSIS_DIR}")

LATEST_RUN = runs[-1]
print(f"Using Spark results: {LATEST_RUN}")


def read_spark_output(name, columns):
    """Read Spark part files, ignoring metadata and CRC files."""
    folder = LATEST_RUN / name
    files = sorted(folder.glob("part-*"))

    if not files:
        print(f"Skipping {name}: no part files found")
        return pd.DataFrame(columns=columns)

    rows = []
    for file in files:
        with file.open("r", encoding="utf-8") as stream:
            for line in stream:
                values = next(csv.reader([line.strip()]))
                if len(values) == len(columns):
                    rows.append(values)

    return pd.DataFrame(rows, columns=columns)


def save_bar_chart(df, label_col, value_col, title, filename,
                   horizontal=False, top_n=None):
    """Create and save a labelled bar chart."""
    if df.empty:
        print(f"Skipping chart: {title}")
        return

    data = df.copy()
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna(subset=[value_col])

    if top_n:
        data = data.nlargest(top_n, value_col)

    if data.empty:
        return

    plt.figure(figsize=(11, 6))

    if horizontal:
        data = data.sort_values(value_col)
        plt.barh(data[label_col].astype(str), data[value_col])
        plt.xlabel(value_col.replace("_", " ").title())
        plt.ylabel(label_col.replace("_", " ").title())
    else:
        plt.bar(data[label_col].astype(str), data[value_col])
        plt.xlabel(label_col.replace("_", " ").title())
        plt.ylabel(value_col.replace("_", " ").title())
        plt.xticks(rotation=35, ha="right")

    plt.title(title)
    plt.tight_layout()
    destination = OUTPUT_DIR / filename
    plt.savefig(destination, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {destination}")


# 1. Attack category distribution
df = read_spark_output(
    "attack_category_counts", ["attack_category", "count"]
)
save_bar_chart(
    df, "attack_category", "count",
    "NSL-KDD Training Set: Attack Category Distribution",
    "01_attack_category_distribution.png",
    horizontal=True,
)

# 2. Protocol distribution
df = read_spark_output("protocol_counts", ["protocol", "count"])
save_bar_chart(
    df, "protocol", "count",
    "Network Traffic by Protocol",
    "02_protocol_distribution.png",
)

# 3. Top services
df = read_spark_output("service_counts", ["service", "count"])
save_bar_chart(
    df, "service", "count",
    "Top 15 Network Services",
    "03_top_services.png",
    horizontal=True,
    top_n=15,
)

# 4. TCP flags
df = read_spark_output("flag_counts", ["flag", "count"])
save_bar_chart(
    df, "flag", "count",
    "Connection Flags Distribution",
    "04_flag_distribution.png",
    horizontal=True,
)

# 5. Protocol and attack category heatmap
df = read_spark_output(
    "protocol_category_counts", ["protocol", "category", "count"]
)

if not df.empty:
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    pivot = df.pivot_table(
        index="protocol",
        columns="category",
        values="count",
        aggfunc="sum",
        fill_value=0,
    )

    plt.figure(figsize=(10, 6))
    plt.imshow(pivot, aspect="auto")
    plt.colorbar(label="Connection Count")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=30)
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.xlabel("Attack Category")
    plt.ylabel("Protocol")
    plt.title("Protocol vs Attack Category")
    plt.tight_layout()
    path = OUTPUT_DIR / "05_protocol_category_heatmap.png"
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")

# 6. Service and category combinations: most frequent combinations
df = read_spark_output(
    "service_category_counts", ["service", "category", "count"]
)

if not df.empty:
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    df = df.dropna(subset=["count"]).nlargest(20, "count")
    df["label"] = df["service"] + " | " + df["category"]

    save_bar_chart(
        df, "label", "count",
        "Top 20 Service and Attack Category Combinations",
        "06_service_category_combinations.png",
        horizontal=True,
    )

# 7. Average duration and bytes by category, if saved
df = read_spark_output(
    "category_duration_bytes",
    ["category", "avg_duration", "avg_src_bytes", "avg_dst_bytes"],
)

if not df.empty:
    for column in ["avg_duration", "avg_src_bytes", "avg_dst_bytes"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    for metric, title, filename in [
        ("avg_duration", "Average Connection Duration by Category",
         "07_average_duration.png"),
        ("avg_src_bytes", "Average Source Bytes by Category",
         "08_average_source_bytes.png"),
        ("avg_dst_bytes", "Average Destination Bytes by Category",
         "09_average_destination_bytes.png"),
    ]:
        save_bar_chart(df, "category", metric, title, filename)

print(f"\nVisualization stage completed. Output folder: {OUTPUT_DIR}")
