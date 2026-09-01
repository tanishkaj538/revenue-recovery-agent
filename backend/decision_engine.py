"""
Decision Engine — maps a root cause to the correct recovery action.
"""

DECISION_TABLE = {
    "insufficient_balance": {
        "action": "retry_payment",
        "wait_days": 3,
        "message": "We'll auto-retry your payment in 3 days once your balance is topped up.",
    },
    "card_expired": {
        "action": "send_update_card_link",
        "wait_days": 0,
        "message": "Your card has expired. Please update your card to continue.",
    },
    "mandate_expired": {
        "action": "send_new_mandate_link",
        "wait_days": 0,
        "message": "Your UPI mandate has expired. Please set up a new mandate.",
    },
    "bank_decline": {
        "action": "suggest_alternate_method",
        "wait_days": 0,
        "message": "Your bank declined the payment. Try an alternate payment method.",
    },
}

DEFAULT_DECISION = {
    "action": "manual_review",
    "wait_days": 0,
    "message": "Unrecognized failure — flagged for manual review.",
}


def decide(root_cause: str) -> dict:
    return DECISION_TABLE.get(root_cause, DEFAULT_DECISION)
