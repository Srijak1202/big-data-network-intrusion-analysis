#!/usr/bin/env python3

import sys

current_key = None
current_count = 0

for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    key, count = line.split("\t")

    count = int(count)

    if current_key == key:
        current_count += count
    else:
        if current_key is not None:
            protocol, attack_category = current_key.split(",", 1)
            print(f"{protocol}\t{attack_category}\t{current_count}")

        current_key = key
        current_count = count

if current_key is not None:
    protocol, attack_category = current_key.split(",", 1)
    print(f"{protocol}\t{attack_category}\t{current_count}")