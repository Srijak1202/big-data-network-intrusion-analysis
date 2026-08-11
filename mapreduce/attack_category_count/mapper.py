#!/usr/bin/env python3

import sys

for line in sys.stdin:

    # Skip the CSV header
    if line.startswith("duration,"):
        continue

    # Split the CSV record
    fields = line.strip().split(",")

    # attack_category is the last column
    attack_category = fields[-1]

    # Emit: attack_category    1
    print(f"{attack_category}\t1")