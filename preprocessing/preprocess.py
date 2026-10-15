import os
import json
import pandas as pd

# Project paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

# NSL-KDD contains 41 input features, attack_label and difficulty.
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

# Five-class mapping. Unmapped labels are preserved and reported;
# they are never silently converted into a known attack category.
ATTACK_CATEGORIES = {
    # DoS
    "back": "DoS", "land": "DoS", "neptune": "DoS",
    "pod": "DoS", "smurf": "DoS", "teardrop": "DoS",
    "apache2": "DoS", "udpstorm": "DoS",
    "processtable": "DoS", "mailbomb": "DoS", "worm": "DoS",
    # Probe
    "ipsweep": "Probe", "nmap": "Probe",
    "portsweep": "Probe", "satan": "Probe",
    "mscan": "Probe", "saint": "Probe",

    # R2L
    "ftp_write": "R2L", "guess_passwd": "R2L",
    "imap": "R2L", "multihop": "R2L", "phf": "R2L",
    "spy": "R2L", "warezclient": "R2L",
    "warezmaster": "R2L", "named": "R2L",
    "sendmail": "R2L", "snmpgetattack": "R2L",
    "snmpguess": "R2L", "xlock": "R2L",
    "xsnoop": "R2L", "httptunnel": "R2L",

    # U2R
    "buffer_overflow": "U2R", "loadmodule": "U2R",
    "perl": "U2R", "rootkit": "U2R",
    "ps": "U2R", "sqlattack": "U2R",
    "xterm": "U2R",

    # Normal traffic
    "normal": "Normal"
}


def load_and_validate(filename):
    path = os.path.join(RAW_DIR, filename)

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    print(f"\nReading {filename} ...")

    # The NSL-KDD TXT files have no header row.
    df = pd.read_csv(
        path,
        header=None,
        names=COLUMNS,
        skipinitialspace=True
    )

    original_count = len(df)

    # Normalize textual fields and attack labels.
    for column in ["protocol_type", "service", "flag", "attack_label"]:
        df[column] = df[column].astype("string").str.strip()

    df["attack_label"] = (
        df["attack_label"]
        .str.lower()
        .str.removesuffix(".")
    )

    # Identify malformed or incomplete records.
    df.replace(r"^\s*$", pd.NA, regex=True, inplace=True)
    invalid_mask = df.isna().any(axis=1)
    invalid_count = int(invalid_mask.sum())

    # Exclude malformed records consistently.
    df = df.loc[~invalid_mask].copy()

    # Validate numeric fields.
    numeric_columns = [
        c for c in COLUMNS
        if c not in ["protocol_type", "service", "flag", "attack_label"]
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    numeric_invalid = df[numeric_columns].isna().any(axis=1)
    numeric_invalid_count = int(numeric_invalid.sum())
    df = df.loc[~numeric_invalid].copy()

    # Preserve original attack labels and map categories.
    df["attack_category"] = df["attack_label"].map(ATTACK_CATEGORIES)
    unknown_labels = sorted(
        df.loc[df["attack_category"].isna(), "attack_label"].unique().tolist()
    )

    print(f"Original records: {original_count}")
    print(f"Records with missing fields: {invalid_count}")
    print(f"Records with invalid numeric values: {numeric_invalid_count}")
    print(f"Valid records retained: {len(df)}")
    print(f"Columns: {len(COLUMNS)}")

    print("\nAttack label counts:")
    print(df["attack_label"].value_counts().head(20))

    print("\nAttack category counts:")
    print(df["attack_category"].value_counts(dropna=False))

    if unknown_labels:
        print("\nWARNING: Unmapped attack labels:")
        print(unknown_labels)

    # Save the processed file even if unknown labels exist,
    # so we can inspect and correct the mapping before modeling.
    output_name = filename.replace(".txt", "_processed.csv")
    output_path = os.path.join(PROCESSED_DIR, output_name)
    df.to_csv(output_path, index=False)

    report = {
        "filename": filename,
        "original_records": original_count,
        "missing_field_records": invalid_count,
        "invalid_numeric_records": numeric_invalid_count,
        "valid_records": len(df),
        "column_count_before_category": len(COLUMNS),
        "unknown_attack_labels": unknown_labels,
        "attack_category_counts": {
            str(k): int(v)
            for k, v in df["attack_category"].value_counts(dropna=False).items()
        }
    }

    report_path = os.path.join(
        PROCESSED_DIR,
        filename.replace(".txt", "_validation.json")
    )

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nSaved processed dataset: {output_path}")
    print(f"Saved validation report: {report_path}")

    return report


if __name__ == "__main__":
    train_report = load_and_validate("KDDTrain+.txt")
    test_report = load_and_validate("KDDTest+.txt")

    print("\n========== PREPROCESSING SUMMARY ==========")
    print(f"Training records: {train_report['valid_records']}")
    print(f"Test records: {test_report['valid_records']}")
    print("\nPreprocessing completed. Review any unmapped labels before modeling.")
