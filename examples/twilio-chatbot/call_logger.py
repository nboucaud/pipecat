import csv
import os

LOG_FILE = "call_log.csv"

def log_call(timestamp_start, duration, summary, target_number, source_number):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        fieldnames = ['timestamp_start', 'duration_or_status', 'call_summary', 'target_number', 'source_number']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp_start': timestamp_start,
            'duration_or_status': duration,
            'call_summary': summary,
            'target_number': target_number,
            'source_number': source_number
        })
