from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc
import csv
import os
import json

# --------------------------------------------------
# 1. Initialize Spark
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("NSLKDDNetworkIntrusionAnalytics")
    .master("local[*]")
    .getOrCreate()
)

sc = spark.sparkContext
sc.setLogLevel("WARN")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "KDDTrain+.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\n========== NSL-KDD SPARK ANALYTICS ==========")

# --------------------------------------------------
# 2. Load the dataset as an RDD
# --------------------------------------------------

raw_rdd = sc.textFile(DATA_PATH)

def parse_record(line):
    try:
        row = next(csv.reader([line.strip()]))
        if len(row) != 43:
            return None
        return row
    except Exception:
        return None

records_rdd = raw_rdd.map(parse_record).filter(lambda row: row is not None)
records_rdd.cache()

total_records = records_rdd.count()

if total_records == 0:
    raise ValueError(
        "No valid records found. Check the dataset path and record format."
    )

print(f"\nTotal valid records: {total_records}")

# --------------------------------------------------
# 3. Attack category distribution
# --------------------------------------------------

def get_category(row):
    attack = row[41].strip().lower()

    if attack == "normal":
        return "Normal"

    dos = {
        "back", "land", "neptune", "pod", "smurf", "teardrop",
        "apache2", "udpstorm", "processtable", "mailbomb", "worm"
    }

    probe = {
        "ipsweep", "nmap", "portsweep", "satan", "mscan",
        "saint", "snmpgetattack", "snmpguess"
    }

    r2l = {
        "ftp_write", "guess_passwd", "imap", "multihop", "phf",
        "warezclient", "warezmaster", "spy", "named", "sendmail",
        "xlock", "xsnoop", "worm"
    }

    u2r = {
        "buffer_overflow", "loadmodule", "perl", "rootkit",
        "httptunnel", "ps", "sqlattack", "xterm"
    }

    if attack in dos:
        return "DoS"
    if attack in probe:
        return "Probe"
    if attack in r2l:
        return "R2L"
    if attack in u2r:
        return "U2R"

    return "Unknown"

category_counts = (
    records_rdd
    .map(lambda row: (get_category(row), 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: -x[1])
    .collect()
)

print("\n--- Attack Category Distribution ---")
for category, count_value in category_counts:
    print(f"{category}: {count_value}")

with open(os.path.join(OUTPUT_DIR, "attack_category_counts.csv"), "w") as f:
    f.write("attack_category,count\n")
    for category, count_value in category_counts:
        f.write(f"{category},{count_value}\n")

# --------------------------------------------------
# 4. Protocol distribution
# --------------------------------------------------

protocol_counts = (
    records_rdd
    .map(lambda row: (row[1], 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: -x[1])
    .collect()
)

print("\n--- Protocol Distribution ---")
for protocol, count_value in protocol_counts:
    print(f"{protocol}: {count_value}")

with open(os.path.join(OUTPUT_DIR, "protocol_counts.csv"), "w") as f:
    f.write("protocol,count\n")
    for protocol, count_value in protocol_counts:
        f.write(f"{protocol},{count_value}\n")

# --------------------------------------------------
# 5. Service distribution
# --------------------------------------------------

service_counts = (
    records_rdd
    .map(lambda row: (row[2], 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: -x[1])
    .collect()
)

with open(os.path.join(OUTPUT_DIR, "service_counts.csv"), "w") as f:
    f.write("service,count\n")
    for service, count_value in service_counts:
        f.write(f"{service},{count_value}\n")

print("\n--- Top 10 Services ---")
for service, count_value in service_counts[:10]:
    print(f"{service}: {count_value}")

# --------------------------------------------------
# 6. Protocol and attack category analysis
# --------------------------------------------------

protocol_category_counts = (
    records_rdd
    .map(lambda row: ((row[1], get_category(row)), 1))
    .reduceByKey(lambda a, b: a + b)
    .collect()
)

with open(
    os.path.join(OUTPUT_DIR, "protocol_attack_category_counts.csv"), "w"
) as f:
    f.write("protocol,attack_category,count\n")
    for (protocol, category), count_value in protocol_category_counts:
        f.write(f"{protocol},{category},{count_value}\n")

# --------------------------------------------------
# 7. Connection flag distribution
# --------------------------------------------------

flag_counts = (
    records_rdd
    .map(lambda row: (row[3], 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: -x[1])
    .collect()
)

with open(os.path.join(OUTPUT_DIR, "flag_counts.csv"), "w") as f:
    f.write("flag,count\n")
    for flag, count_value in flag_counts:
        f.write(f"{flag},{count_value}\n")

# --------------------------------------------------
# 8. Attack category by protocol
# --------------------------------------------------

print("\n--- Protocol and Attack Category ---")
for (protocol, category), count_value in sorted(
    protocol_category_counts,
    key=lambda x: -x[1]
)[:15]:
    print(f"{protocol} | {category}: {count_value}")

# --------------------------------------------------
# 9. RDD partition information
# --------------------------------------------------

print("\n--- RDD Information ---")
print(f"Number of partitions: {records_rdd.getNumPartitions()}")
print(f"Number of valid records: {records_rdd.count()}")

# --------------------------------------------------
# 10. Save a summary
# --------------------------------------------------

summary = {
    "dataset": "NSL-KDD KDDTrain+.txt",
    "valid_records": total_records,
    "rdd_partitions": records_rdd.getNumPartitions(),
    "attack_categories": dict(category_counts),
    "protocols": dict(protocol_counts),
    "services": len(service_counts),
    "connection_flags": dict(flag_counts)
}

with open(os.path.join(OUTPUT_DIR, "analytics_summary.json"), "w") as f:
    json.dump(summary, f, indent=4)

print("\nAnalytics completed successfully.")
print(f"Results saved to: {OUTPUT_DIR}")

records_rdd.unpersist()
spark.stop()
