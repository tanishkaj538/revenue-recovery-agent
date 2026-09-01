# AI Revenue Recovery Agent — Full Design Doc

## 1. Problem
Jab recurring payment (subscription/UPI mandate) fail hota hai, ye agent:
1. **Detect** karta hai payment fail hua
2. **Diagnose** karta hai kyun fail hua (root cause)
3. **Act** karta hai — sahi recovery action leta hai
4. **Measure** karta hai — kitna ₹ recover hua

Loop: `Detect → Diagnose → Act → Measure`

---

## 2. System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│   Data Layer     │────▶│  Classifier       │────▶│  Decision Engine   │
│ (CSV/DB of       │     │  Module           │     │  (cause → action   │
│  failed payments)│     │ (rule / Claude API)│     │   mapping)         │
└─────────────────┘     └──────────────────┘     └─────────┬──────────┘
                                                              │
                                                              ▼
                                                   ┌────────────────────┐
                                                   │  Action Executor    │
                                                   │ (Razorpay test API  │
                                                   │  / mock + SMS/WA)   │
                                                   └─────────┬──────────┘
                                                              │
                                                              ▼
                                                   ┌────────────────────┐
                                                   │  Stopping Rule      │
                                                   │ (max 3 attempts →   │
                                                   │  mark unrecoverable)│
                                                   └─────────┬──────────┘
                                                              │
                                                              ▼
                                                   ┌────────────────────┐
                                                   │  Dashboard          │
                                                   │ (₹ recovered,       │
                                                   │  success rate,      │
                                                   │  audit trail)       │
                                                   └────────────────────┘
```

---

## 3. Data Layer

**File:** `data/failed_payments.csv`

| Column | Type | Description |
|---|---|---|
| payment_id | string | Unique ID (e.g. `pay_00123`) |
| amount | float | Payment amount in ₹ |
| failure_code | string | `insufficient_balance` / `card_expired` / `mandate_expired` / `bank_decline` |
| customer_contact | string | Phone number (mock) |
| attempt_history | int | Number of retry attempts already made (0–3) |
| status | string | `pending` / `recovered` / `unrecoverable` |
| created_at | date | When the failure happened |

50+ synthetic rows, generated via `data/generate_data.py`.

---

## 4. Classifier Module

Maps `failure_code` → root cause bucket. Two versions:

- **v1 (default, fast, demo-safe):** Rule-based dictionary lookup. No API calls, zero latency, zero failure risk.
- **v2 (bonus, AI-powered):** Sends failure description to Claude API, gets back a structured root-cause label. Use this to show "real AI" in the judging round, but keep v1 as fallback.

```python
FAILURE_MAP = {
    "insufficient_balance": "insufficient_balance",
    "card_expired": "card_expired",
    "mandate_expired": "mandate_expired",
    "bank_decline": "bank_decline",
}
```

---

## 5. Decision Engine

| Root Cause | Recovery Action | Wait Time |
|---|---|---|
| insufficient_balance | Retry payment | 3 days |
| card_expired | Send "update card" link | Immediate |
| mandate_expired | Send "create new mandate" link | Immediate |
| bank_decline | Suggest alternate payment method | Immediate |

---

## 6. Action Executor

- Calls **Razorpay test-mode API** to create a payment link (or a **mock function** returning a fake link if API keys aren't set up in time — keeps the demo unblockable).
- Sends notification via SMS/WhatsApp (mock: just log/print + show in dashboard "notification sent" — real Twilio/WhatsApp API is a stretch goal, not required for judging).

---

## 7. Stopping Rule (Guardrail)

- Max **3 recovery attempts** per `payment_id`.
- After 3rd failed attempt → tag `unrecoverable`, stop retrying.
- This is a judged criterion — shows the agent isn't spamming customers. **Do not skip this.**

---

## 8. Dashboard

Streamlit app showing:
- **Total ₹ Recovered** (big metric card)
- **Success Rate %**
- **Exception list** (unrecoverable payments + reason)
- **Full audit trail** — every action taken, timestamped, per payment_id
- Button: "Run Recovery Cycle" → triggers the whole pipeline on demand (great for live demo)

---

## 9. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python + FastAPI | Fast to build, clean API for dashboard to call |
| Classification | Rule-based (+ optional Claude API) | Reliable demo, AI bonus layer |
| Storage | CSV (or SQLite if time permits) | Zero setup, easy to inspect |
| Dashboard | Streamlit | Fastest way to get a working UI in hours not days |
| Payment mock | Razorpay test-mode API / local mock | Real integration impresses judges, mock de-risks demo |

---

## 10. Folder Structure (this repo)

```
revenue-recovery-agent/
├── README.md
├── requirements.txt
├── data/
│   ├── generate_data.py       # creates synthetic failed_payments.csv
│   └── failed_payments.csv    # generated (gitignored, or commit sample)
├── backend/
│   ├── classifier.py          # root-cause classification
│   ├── decision_engine.py     # cause -> action mapping
│   ├── action_executor.py     # executes recovery action (real/mock)
│   ├── pipeline.py            # orchestrates detect->diagnose->act->measure
│   └── main.py                # FastAPI app exposing endpoints
├── dashboard/
│   └── app.py                 # Streamlit dashboard
└── design/
    └── ARCHITECTURE.md        # this file
```

---

## 11. Build Order (suggested, ~4 days)

| Day | Task |
|---|---|
| 1 | Data layer + classifier (rule-based) |
| 2 | Decision engine + action executor (mock) + stopping rule |
| 3 | FastAPI pipeline endpoint + connect to Streamlit dashboard |
| 4 | Polish demo data, add Claude API classifier (bonus), rehearse demo |

---

## 12. Demo Script (for judges)

1. Show `failed_payments.csv` — "50 real-looking failed payments"
2. Click "Run Recovery Cycle" on dashboard
3. Show live: classify → decide → act → recovered ₹ ticking up
4. Show exception list — "these 5 are unrecoverable after 3 tries, we stop, no spam"
5. End on the big number: "We recovered ₹X out of ₹Y — a Z% recovery rate"
