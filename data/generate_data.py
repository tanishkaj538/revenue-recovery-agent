"""
Generates synthetic failed-payment records for the Revenue Recovery Agent demo.
Run: python data/generate_data.py
Output: data/failed_payments.csv
"""

import csv
import random
from datetime import datetime, timedelta

FAILURE_CODES = ["insufficient_balance", "card_expired", "mandate_expired", "bank_decline"]

NUM_RECORDS = 60


def generate_records(n=NUM_RECORDS):
    records = []
    base_date = datetime(2026, 8, 1)
    for i in range(1, n + 1):
        payment_id = f"pay_{i:05d}"
        amount = round(random.uniform(199, 4999), 2)
        failure_code = random.choice(FAILURE_CODES)
        customer_contact = f"+91{random.randint(7000000000, 9999999999)}"
        attempt_history = 0
        status = "pending"
        created_at = (base_date + timedelta(days=random.randint(0, 25))).strftime("%Y-%m-%d")

        records.append(
            {
                "payment_id": payment_id,
                "amount": amount,
                "failure_code": failure_code,
                "customer_contact": customer_contact,
                "attempt_history": attempt_history,
                "status": status,
                "created_at": created_at,
            }
        )
    return records


def write_csv(records, path="data/failed_payments.csv"):
    fieldnames = [
        "payment_id",
        "amount",
        "failure_code",
        "customer_contact",
        "attempt_history",
        "status",
        "created_at",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} records to {path}")


if __name__ == "__main__":
    recs = generate_records()
    write_csv(recs)
