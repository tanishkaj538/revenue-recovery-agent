"""
Pipeline — orchestrates the full loop: Detect -> Diagnose -> Act -> Measure.
Also enforces the Stopping Rule: max 3 attempts per payment.
"""

import csv
from datetime import datetime

from backend.classifier import classify
from backend.decision_engine import decide
from backend.action_executor import execute_action

MAX_ATTEMPTS = 3
DATA_PATH = "data/failed_payments.csv"
AUDIT_LOG_PATH = "data/audit_trail.csv"


def load_payments(path=DATA_PATH):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def save_payments(records, path=DATA_PATH):
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def append_audit_log(entry: dict, path=AUDIT_LOG_PATH):
    file_exists = False
    try:
        with open(path, "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    fieldnames = [
        "timestamp",
        "payment_id",
        "root_cause",
        "action_taken",
        "amount",
        "status_after",
    ]
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)


def run_recovery_cycle():
    """
    Runs one full pass over all 'pending' payments.
    Returns a summary dict for the dashboard.
    """
    payments = load_payments()
    total_recovered = 0.0
    total_amount_pending = 0.0
    recovered_count = 0
    processed_count = 0

    for record in payments:
        if record["status"] != "pending":
            continue

        attempts = int(record["attempt_history"])
        amount = float(record["amount"])
        total_amount_pending += amount

        # --- Stopping Rule ---
        if attempts >= MAX_ATTEMPTS:
            record["status"] = "unrecoverable"
            append_audit_log(
                {
                    "timestamp": datetime.now().isoformat(),
                    "payment_id": record["payment_id"],
                    "root_cause": "-",
                    "action_taken": "stopped_max_attempts",
                    "amount": amount,
                    "status_after": "unrecoverable",
                }
            )
            continue

        # --- Detect + Diagnose ---
        root_cause = classify(record["failure_code"])
        decision = decide(root_cause)

        # --- Act ---
        result = execute_action(
            record["payment_id"], amount, record["customer_contact"], decision
        )

        # --- Measure ---
        # Demo simulation: recovery succeeds with a weighted chance so the
        # dashboard shows realistic partial recovery, not 100%.
        import random

        record["attempt_history"] = str(attempts + 1)
        success = random.random() < 0.55  # ~55% recovery chance per attempt

        if success:
            record["status"] = "recovered"
            total_recovered += amount
            recovered_count += 1
        elif int(record["attempt_history"]) >= MAX_ATTEMPTS:
            record["status"] = "unrecoverable"
        else:
            record["status"] = "pending"

        processed_count += 1

        append_audit_log(
            {
                "timestamp": datetime.now().isoformat(),
                "payment_id": record["payment_id"],
                "root_cause": root_cause,
                "action_taken": result["action_taken"],
                "amount": amount,
                "status_after": record["status"],
            }
        )

    save_payments(payments)

    return {
        "processed_count": processed_count,
        "recovered_count": recovered_count,
        "total_recovered": round(total_recovered, 2),
        "total_amount_pending": round(total_amount_pending, 2),
    }


def get_summary():
    """Reads current state of all payments for the dashboard (no side effects)."""
    payments = load_payments()
    total = sum(float(r["amount"]) for r in payments)
    recovered = sum(float(r["amount"]) for r in payments if r["status"] == "recovered")
    unrecoverable = [r for r in payments if r["status"] == "unrecoverable"]
    pending = [r for r in payments if r["status"] == "pending"]

    success_rate = (
        len([r for r in payments if r["status"] == "recovered"]) / len(payments) * 100
        if payments
        else 0
    )

    return {
        "total_amount": round(total, 2),
        "total_recovered": round(recovered, 2),
        "success_rate": round(success_rate, 1),
        "unrecoverable_count": len(unrecoverable),
        "pending_count": len(pending),
        "unrecoverable_list": unrecoverable,
        "all_payments": payments,
    }
