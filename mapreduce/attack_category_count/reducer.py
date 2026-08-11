#!/usr/bin/env python3

import sys

current_category = None
current_count = 0

for line in sys.stdin:

    line = line.strip()

    if not line:
        continue

    category, count = line.split("\t")
    count = int(count)

    if current_category == category:
        current_count += count

    else:
        if current_category is not None:
            print(f"{current_category}\t{current_count}")

        current_category = category
        current_count = count

# Output the final category
if current_category is not None:
    print(f"{current_category}\t{current_count}")