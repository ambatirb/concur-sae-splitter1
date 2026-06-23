import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ----------------- CONFIGURATION -----------------
INPUT_FILE = "CONCUR20260623050305400.dat"  # Your original file name
OUTPUT_DIR = "split_batches"
DELIMITER = "|"
MAX_LINES_PER_BATCH = 200

REPORT_KEY_INDEX = 19    # Column 20 (0-based index)
JOURNAL_AMOUNT_INDEX = 168  # Column 169
# --------------------------------------------------

def parse_input_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    extract_header = lines[0] if lines[0].startswith("EXTRACT|") else ""
    detail_lines = [line for line in lines if line.startswith("DETAIL|")]
    return extract_header, detail_lines

def group_by_report_key(lines):
    groups = defaultdict(list)
    for line in lines:
        cols = line.split(DELIMITER)
        if len(cols) > REPORT_KEY_INDEX:
            report_key = cols[REPORT_KEY_INDEX]
            groups[report_key].append(line)
    return groups

def write_batch(batch_num, extract_header, batch_lines, total_amount, output_dir):
    batch_file = output_dir / f"batch_{batch_num:03d}.txt"
    batch_date = datetime.today().strftime("%Y-%m-%d")
    record_count = len(batch_lines)
    header_line = f"BATCH{batch_num:03d}|{batch_date}|{record_count}|{total_amount:.4f}"

    with open(batch_file, "w", encoding="utf-8") as f:
        f.write(header_line + "\n")
        f.write(extract_header + "\n")
        f.writelines(line + "\n" for line in batch_lines)
    print(f"✅ Created: {batch_file.name} with {record_count} records")

def split_batches(extract_header, grouped_lines):
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    batch_num = 1
    current_lines = []
    current_total = 0.0
    current_count = 0

    for report_key, lines in grouped_lines.items():
        if current_count + len(lines) > MAX_LINES_PER_BATCH:
            write_batch(batch_num, extract_header, current_lines, current_total, output_dir)
            batch_num += 1
            current_lines, current_total, current_count = [], 0.0, 0

        current_lines.extend(lines)
        current_count += len(lines)
        for line in lines:
            try:
                amt = float(line.split(DELIMITER)[JOURNAL_AMOUNT_INDEX])
                current_total += amt
            except (IndexError, ValueError):
                continue

    if current_lines:
        write_batch(batch_num, extract_header, current_lines, current_total, output_dir)

if __name__ == "__main__":
    extract_header, detail_lines = parse_input_file(INPUT_FILE)
    grouped = group_by_report_key(detail_lines)
    split_batches(extract_header, grouped)
