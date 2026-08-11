#!/usr/bin/env python3

import sys

for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    fields = line.split(",")

    # Skip the header row
    if fields[0] == "duration":
        continue

    # Skip malformed records
    if len(fields) < 44:
        continue

    protocol_type = fields[1]
    attack_category = fields[43]

    # Use one combined key
    print(f"{protocol_type},{attack_category}\t1")