"""
Classifier Module — maps a raw failure_code into a root-cause bucket.

v1: rule-based (default, fast, zero external dependency)
v2: Claude-API based (optional bonus layer, set USE_CLAUDE_CLASSIFIER=True)
"""

import os

USE_CLAUDE_CLASSIFIER = False  # flip to True once ANTHROPIC_API_KEY is set

# --- v1: rule-based classifier -------------------------------------------

RULE_MAP = {
    "insufficient_balance": "insufficient_balance",
    "card_expired": "card_expired",
    "mandate_expired": "mandate_expired",
    "bank_decline": "bank_decline",
}


def classify_rule_based(failure_code: str) -> str:
    return RULE_MAP.get(failure_code, "unknown")


# --- v2: Claude API classifier (bonus / optional) -------------------------

def classify_with_claude(failure_description: str) -> str:
    """
    Sends a short failure description to Claude and asks for a single
    root-cause label. Falls back to rule-based on any error so the
    pipeline never breaks during a live demo.
    """
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        prompt = (
            "Classify this payment failure into EXACTLY one of these labels: "
            "insufficient_balance, card_expired, mandate_expired, bank_decline. "
            "Reply with ONLY the label, nothing else.\n\n"
            f"Failure description: {failure_description}"
        )
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}],
        )
        label = response.content[0].text.strip()
        if label in RULE_MAP:
            return label
        return "unknown"
    except Exception:
        # graceful fallback — never let the demo crash on an API hiccup
        return classify_rule_based(failure_description)


def classify(failure_code: str) -> str:
    """Single entry point used by the pipeline."""
    if USE_CLAUDE_CLASSIFIER:
        return classify_with_claude(failure_code)
    return classify_rule_based(failure_code)
