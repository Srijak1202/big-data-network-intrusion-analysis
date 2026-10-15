from pathlib import Path
import csv
import json
import sys

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "out" / "visualizations"
OUTPUT.mkdir(parents=True, exist_ok=True)

# NSL-KDD has 43 columns and no header in the TXT dataset.
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
    "dst_host_srv_rerror_rate", "attack_label", "difficulty"
]

DOS = {
    "back", "land", "neptune", "pod", "smurf", "teardrop",
    "apache2", "mailbomb", "processtable", "udpstorm", "worm"
}
PROBE = {"ipsweep", "nmap", "portsweep", "satan", "mscan", "saint"}
R2L = {
    "ftp_write", "guess_passwd", "imap", "multihop", "phf", "spy",
    "warezclient", "warezmaster", "named", "sendmail",
    "snmpgetattack", "snmpguess", "xlock", "xsnoop", "httptunnel"
}
U2R = {
    "buffer_overflow", "loadmodule", "perl", "rootkit",
    "ps", "sqlattack", "xterm"
}

def categorize(label):
    label = str(label).strip().rstrip(".").lower()
    if label == "normal":
        return "Normal"
    if label in DOS:
        return "DoS"
    if label in PROBE:
        return "Probe"
    if label in R2L:
        return "R2L"
    if label in U2R:
        return "U2R"
    return "Unknown"

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(OUTPUT / filename, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Saved: {OUTPUT / filename}")

def load_spark_results():
    base = ROOT / "out" / "analysis"
    runs = sorted(
        [p for p in base.glob("run_*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime
    )
    if not runs:
        return None

    run = runs[-1]
    print(f"Using Spark results: {run}")

    def read_result(name, expected_columns):
        folder = run / name
        if not folder.exists():
            print(f"Spark output not found: {name}")
            return pd.DataFrame()

        rows = []
        for part in sorted(folder.glob("part-*")):
            with part.open("r", encoding="utf-8") as f:
                for line in f:
                    values = next(csv.reader([line.strip()]))
                    if len(values) == expected_columns:
                        rows.append(values)

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(rows)

    results = {
        "categories": read_result("attack_category_counts", 2),
        "protocols": read_result("protocol_counts", 2),
        "services": read_result("service_counts", 2),
        "flags": read_result("flag_counts", 2),
        "protocol_category": read_result("protocol_category_counts", 3),
        "service_category": read_result("service_category_counts", 3),
    }

    return results

def load_dataset():
    candidates = [
        ROOT / "data" / "raw" / "KDDTrain+.txt",
        ROOT.parent / "big-data-network-intrusion-analysis"
             / "data" / "raw" / "KDDTrain+.txt",
    ]

    dataset_path = next((p for p in candidates if p.exists()), None)

    if dataset_path is None:
        print("ERROR: Could not locate KDDTrain+.txt.")
        print("Expected it in data/raw/ or the existing project data/raw/.")
        sys.exit(1)

    print(f"Reading dataset: {dataset_path}")

    df = pd.read_csv(
        dataset_path,
        header=None,
        names=COLUMNS,
        sep=",",
        skipinitialspace=True,
        dtype={"protocol_type": "string", "service": "string",
               "flag": "string", "attack_label": "string"},
        low_memory=False
    )

    df = df.dropna(subset=["attack_label"]).copy()
    df["attack_label"] = df["attack_label"].str.strip().str.rstrip(".")
    df["attack_category"] = df["attack_label"].map(categorize)

    numeric_columns = [
        "duration", "src_bytes", "dst_bytes", "count", "srv_count",
        "serror_rate", "rerror_rate", "num_failed_logins"
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    print(f"Loaded {len(df):,} records.")
    print("Category counts:")
    print(df["attack_category"].value_counts().to_string())

    unknown = sorted(
        df.loc[df["attack_category"] == "Unknown", "attack_label"].unique()
    )
    if unknown:
        print(f"WARNING: Unmapped attack labels: {unknown}")

    return df

def chart_category_distribution(df):
    counts = df["attack_category"].value_counts().sort_values(ascending=False)

    plt.figure(figsize=(9, 6))
    plt.bar(counts.index, counts.values)
    plt.title("Attack Category Distribution")
    plt.xlabel("Category")
    plt.ylabel("Number of records")
    plt.xticks(rotation=20)
    save_plot("01_attack_category_distribution.png")

    plt.figure(figsize=(8, 8))
    plt.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"width": 0.42}
    )
    plt.title("Proportion of Network Traffic by Category")
    save_plot("02_attack_category_donut.png")

def chart_protocol_distribution(df):
    counts = df["protocol_type"].value_counts()

    plt.figure(figsize=(8, 5))
    plt.bar(counts.index, counts.values)
    plt.title("Network Protocol Distribution")
    plt.xlabel("Protocol")
    plt.ylabel("Number of records")
    save_plot("03_protocol_distribution.png")

def chart_top_services(df):
    counts = df["service"].value_counts().head(15).sort_values()

    plt.figure(figsize=(10, 7))
    plt.barh(counts.index, counts.values)
    plt.title("Top 15 Network Services by Traffic Volume")
    plt.xlabel("Number of records")
    plt.ylabel("Service")
    save_plot("04_top_services.png")

def chart_flag_distribution(df):
    counts = df["flag"].value_counts().head(15)

    plt.figure(figsize=(10, 5))
    plt.bar(counts.index, counts.values)
    plt.title("Connection Flag Distribution")
    plt.xlabel("TCP connection flag")
    plt.ylabel("Number of records")
    plt.xticks(rotation=35)
    save_plot("05_flag_distribution.png")

def chart_protocol_category(df):
    table = pd.crosstab(df["protocol_type"], df["attack_category"])
    table.plot(kind="bar", stacked=True, figsize=(10, 6))
    plt.title("Attack Categories Across Network Protocols")
    plt.xlabel("Protocol")
    plt.ylabel("Number of records")
    plt.xticks(rotation=0)
    plt.legend(title="Category")
    save_plot("06_protocol_category_stacked.png")

def chart_service_category(df):
    top_services = df["service"].value_counts().head(12).index
    subset = df[df["service"].isin(top_services)]
    table = pd.crosstab(subset["service"], subset["attack_category"])
    table.plot(kind="bar", stacked=True, figsize=(13, 7))
    plt.title("Attack Categories Across the Top 12 Services")
    plt.xlabel("Service")
    plt.ylabel("Number of records")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Category")
    save_plot("07_service_category_stacked.png")

def chart_attack_rate_by_service(df):
    # Calculate the percentage of records labelled as attacks per service.
    subset = df[df["attack_category"] != "Unknown"].copy()
    subset["is_attack"] = (subset["attack_category"] != "Normal").astype(int)

    summary = subset.groupby("service")["is_attack"].agg(["mean", "count"])
    summary = summary[summary["count"] >= 100]
    summary = summary.sort_values("mean", ascending=False).head(15)
    summary = summary.sort_values("mean")

    plt.figure(figsize=(10, 7))
    plt.barh(summary.index, summary["mean"] * 100)
    plt.title("Services with Highest Attack Percentage")
    plt.xlabel("Records labelled as attacks (%)")
    plt.ylabel("Service")
    plt.xlim(0, 100)
    save_plot("08_service_attack_percentage.png")

def chart_duration_by_category(df):
    categories = [
        c for c in ["Normal", "DoS", "Probe", "R2L", "U2R"]
        if (df["attack_category"] == c).any()
    ]
    data = [
        df.loc[df["attack_category"] == c, "duration"]
          .dropna().clip(upper=df["duration"].quantile(0.99))
        for c in categories
    ]

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, tick_labels=categories, showfliers=False)
    plt.title("Connection Duration by Attack Category")
    plt.xlabel("Category")
    plt.ylabel("Duration (seconds; capped at 99th percentile)")
    plt.xticks(rotation=20)
    save_plot("09_duration_boxplot.png")

def chart_bytes_distribution(df):
    plt.figure(figsize=(10, 6))
    for category in ["Normal", "DoS", "Probe", "R2L", "U2R"]:
        values = df.loc[
            df["attack_category"] == category, "src_bytes"
        ].dropna()
        if not values.empty:
            # log1p handles zero-byte records safely.
            plt.hist(
                np.log1p(values.clip(lower=0)),
                bins=50,
                alpha=0.45,
                label=category
            )

    plt.title("Source Byte Distribution by Category")
    plt.xlabel("log(1 + source bytes)")
    plt.ylabel("Number of records")
    plt.legend(title="Category")
    save_plot("10_source_bytes_distribution.png")

    plt.figure(figsize=(10, 6))
    for category in ["Normal", "DoS", "Probe", "R2L", "U2R"]:
        values = df.loc[
            df["attack_category"] == category, "dst_bytes"
        ].dropna()
        if not values.empty:
            plt.hist(
                np.log1p(values.clip(lower=0)),
                bins=50,
                alpha=0.45,
                label=category
            )

    plt.title("Destination Byte Distribution by Category")
    plt.xlabel("log(1 + destination bytes)")
    plt.ylabel("Number of records")
    plt.legend(title="Category")
    save_plot("11_destination_bytes_distribution.png")

def chart_error_rates(df):
    columns = ["serror_rate", "rerror_rate"]
    table = df.groupby("attack_category")[columns].mean()
    table = table.reindex(["Normal", "DoS", "Probe", "R2L", "U2R", "Unknown"])
    table = table.dropna(how="all")

    table.plot(kind="bar", figsize=(10, 6))
    plt.title("Average Connection Error Rates by Category")
    plt.xlabel("Attack category")
    plt.ylabel("Average rate")
    plt.xticks(rotation=20)
    plt.legend(["SYN error rate", "REJ error rate"])
    save_plot("12_error_rates_by_category.png")

def chart_correlation(df):
    features = [
        "duration", "src_bytes", "dst_bytes", "count", "srv_count",
        "serror_rate", "rerror_rate", "num_failed_logins"
    ]
    corr = df[features].corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(corr, aspect="auto", vmin=-1, vmax=1)
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels(features, rotation=45, ha="right")
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features)
    ax.set_title("Correlation Heatmap of Selected Numeric Features")
    fig.colorbar(image, ax=ax, label="Pearson correlation")

    for i in range(len(features)):
        for j in range(len(features)):
            value = corr.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=7)

    save_plot("13_numeric_correlation_heatmap.png")

def chart_attack_labels(df):
    counts = df["attack_label"].value_counts().head(15).sort_values()

    plt.figure(figsize=(11, 7))
    plt.barh(counts.index, counts.values)
    plt.title("Top 15 Individual Attack Labels")
    plt.xlabel("Number of records")
    plt.ylabel("Attack label")
    save_plot("14_top_attack_labels.png")

def chart_normal_vs_attack(df):
    subset = df[df["attack_category"] != "Unknown"].copy()
    subset["traffic_type"] = np.where(
        subset["attack_category"] == "Normal", "Normal", "Attack"
    )

    table = pd.crosstab(subset["protocol_type"], subset["traffic_type"])
    table.plot(kind="bar", stacked=True, figsize=(9, 6))
    plt.title("Normal Traffic vs Attack Traffic by Protocol")
    plt.xlabel("Protocol")
    plt.ylabel("Number of records")
    plt.xticks(rotation=0)
    plt.legend(title="Traffic type")
    save_plot("15_normal_vs_attack_by_protocol.png")

def main():
    df = load_dataset()

    chart_category_distribution(df)
    chart_protocol_distribution(df)
    chart_top_services(df)
    chart_flag_distribution(df)
    chart_protocol_category(df)
    chart_service_category(df)
    chart_attack_rate_by_service(df)
    chart_duration_by_category(df)
    chart_bytes_distribution(df)
    chart_error_rates(df)
    chart_correlation(df)
    chart_attack_labels(df)
    chart_normal_vs_attack(df)

    summary = {
        "dataset": "NSL-KDD KDDTrain+.txt",
        "records_loaded": int(len(df)),
        "categories": {
            str(k): int(v)
            for k, v in df["attack_category"].value_counts().items()
        },
        "unknown_attack_labels": sorted(
            df.loc[df["attack_category"] == "Unknown", "attack_label"]
              .dropna().unique().tolist()
        ),
        "visualization_count": len(list(OUTPUT.glob("*.png")))
    }

    with (OUTPUT / "visualization_summary.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2)

    print("\nVisualization stage completed.")
    print(f"Charts and summary saved to: {OUTPUT}")
    print(f"Total PNG files present: {summary['visualization_count']}")

if __name__ == "__main__":
    main()
