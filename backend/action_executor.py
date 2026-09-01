"""
Action Executor — actually performs the recovery action.

USE_MOCK = True  -> everything is simulated locally (safe for demo, no keys needed)
USE_MOCK = False -> calls real Razorpay test-mode API (requires RAZORPAY_KEY_ID / SECRET)
"""

import os
import random
import string

USE_MOCK = True


def _random_link_id(n=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def generate_payment_link_mock(payment_id: str, amount: float) -> str:
    return f"https://rzp.io/mock/{_random_link_id()}"


def generate_payment_link_real(payment_id: str, amount: float) -> str:
    """
    Real Razorpay test-mode integration. Requires:
        pip install razorpay
        RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET env vars
    """
    import razorpay

    client = razorpay.Client(
        auth=(os.environ["RAZORPAY_KEY_ID"], os.environ["RAZORPAY_KEY_SECRET"])
    )
    link = client.payment_link.create(
        {
            "amount": int(amount * 100),  # paise
            "currency": "INR",
            "description": f"Recovery for {payment_id}",
            "reference_id": payment_id,
        }
    )
    return link["short_url"]


def send_notification_mock(customer_contact: str, message: str) -> bool:
    print(f"[MOCK SMS/WhatsApp] -> {customer_contact}: {message}")
    return True


def execute_action(payment_id: str, amount: float, customer_contact: str, decision: dict) -> dict:
    """
    Runs the action decided by the decision engine.
    Returns a result dict used for the audit trail.
    """
    action = decision["action"]
    message = decision["message"]

    if action in ("send_update_card_link", "send_new_mandate_link", "retry_payment"):
        link = (
            generate_payment_link_mock(payment_id, amount)
            if USE_MOCK
            else generate_payment_link_real(payment_id, amount)
        )
        full_message = f"{message} Link: {link}"
    else:
        link = None
        full_message = message

    notified = send_notification_mock(customer_contact, full_message)

    return {
        "payment_id": payment_id,
        "action_taken": action,
        "link": link,
        "notified": notified,
        "message": full_message,
    }
