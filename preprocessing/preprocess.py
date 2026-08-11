import pandas as pd

# NSL-KDD column names
columns = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "attack_label",
    "difficulty"
]

# Map individual attack types to broader categories
attack_category_map = {

    # -------------------------
    # DoS attacks
    # -------------------------
    "back": "DoS",
    "land": "DoS",
    "neptune": "DoS",
    "pod": "DoS",
    "smurf": "DoS",
    "teardrop": "DoS",
    "apache2": "DoS",
    "mailbomb": "DoS",
    "processtable": "DoS",
    "udpstorm": "DoS",
    "worm": "DoS",

    # -------------------------
    # Probe attacks
    # -------------------------
    "ipsweep": "Probe",
    "nmap": "Probe",
    "portsweep": "Probe",
    "satan": "Probe",
    "mscan": "Probe",
    "saint": "Probe",
    "snmpgetattack": "Probe",
    "snmpguess": "Probe",

    # -------------------------
    # R2L attacks
    # -------------------------
    "ftp_write": "R2L",
    "guess_passwd": "R2L",
    "imap": "R2L",
    "multihop": "R2L",
    "phf": "R2L",
    "warezclient": "R2L",
    "warezmaster": "R2L",
    "spy": "R2L",
    "named": "R2L",
    "sendmail": "R2L",
    "xlock": "R2L",
    "xsnoop": "R2L",

    # -------------------------
    # U2R attacks
    # -------------------------
    "buffer_overflow": "U2R",
    "loadmodule": "U2R",
    "perl": "U2R",
    "rootkit": "U2R",
    "httptunnel": "U2R",
    "ps": "U2R",
    "sqlattack": "U2R",
    "xterm": "U2R",

    # -------------------------
    # Normal traffic
    # -------------------------
    "normal": "Normal"
}


def process_dataset(input_path):
    """
    Read and preprocess an NSL-KDD dataset.
    """

    # Read dataset
    df = pd.read_csv(
        input_path,
        header=None,
        names=columns
    )

    # Create broader attack category
    df["attack_category"] = df["attack_label"].map(attack_category_map)

    return df

    # Detect unknown attack types
    unknown_attacks = df.loc[
        df["attack_category"].isnull(),
        "attack_label"
    ].unique()

    if len(unknown_attacks) > 0:
        print("\nWARNING: Unknown attack types found:")
        print(unknown_attacks)
    else:
        print("\nAll attack types successfully categorized.")
        

# Process training dataset
train_path = "data/raw/KDDTrain+.txt"
train_df = process_dataset(train_path)

# Process test dataset
test_path = "data/raw/KDDTest+.txt"
test_df = process_dataset(test_path)


# Display basic information
print("Training dataset shape:")
print(train_df.shape)

print("\nTest dataset shape:")
print(test_df.shape)


# Check for unmapped attack labels
print("\nUnmapped training attack labels:")
print(train_df[train_df["attack_category"].isnull()]["attack_label"].unique())

print("\nUnmapped test attack labels:")
print(test_df[test_df["attack_category"].isnull()]["attack_label"].unique())


# Display attack category counts
print("\nTraining attack categories:")
print(train_df["attack_category"].value_counts())

print("\nTest attack categories:")
print(test_df["attack_category"].value_counts())

# Save processed datasets
train_df.to_csv(
    "data/processed/KDDTrain_processed.csv",
    index=False
)

test_df.to_csv(
    "data/processed/KDDTest_processed.csv",
    index=False
)

print("\nProcessed datasets saved successfully.")