# 💳 AI Revenue Recovery Agent

**Razorpay AI Buildathon — Track 1**

An agent that detects failed recurring payments (subscriptions/UPI mandates), diagnoses the root cause, executes a bounded recovery workflow, and reports measured revenue recovered.

> See [`design/ARCHITECTURE.md`](design/ARCHITECTURE.md) for the full system design.

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd revenue-recovery-agent

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate synthetic failed-payment data
python data/generate_data.py

# 5. Run the dashboard (this is the main demo entry point)
streamlit run dashboard/app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`) and click **"Run Recovery Cycle"**.

## Optional: Run the FastAPI backend separately

```bash
uvicorn backend.main:app --reload
```

- `GET /summary` — current dashboard metrics
- `POST /run-cycle` — runs one detect→diagnose→act→measure pass

## Project Structure

```
revenue-recovery-agent/
├── data/
│   ├── generate_data.py     # creates data/failed_payments.csv
│   └── failed_payments.csv  # generated
├── backend/
│   ├── classifier.py        # root-cause classification (rule-based + optional Claude API)
│   ├── decision_engine.py   # root cause -> recovery action
│   ├── action_executor.py   # executes the action (mock or real Razorpay test API)
│   ├── pipeline.py          # orchestrates the loop + enforces the stopping rule
│   └── main.py               # FastAPI app
├── dashboard/
│   └── app.py                # Streamlit UI
└── design/
    └── ARCHITECTURE.md       # full design doc
```

## Key Design Decisions

- **Stopping rule:** max 3 recovery attempts per payment, then tagged `unrecoverable` — the agent never spams a customer.
- **Mock-first:** `action_executor.py` defaults to `USE_MOCK = True` so the whole demo works offline with zero API keys. Flip to `False` once you have Razorpay test-mode credentials.
- **AI bonus layer:** `classifier.py` has an optional Claude-API-based classifier (`USE_CLAUDE_CLASSIFIER = True`) that falls back safely to rule-based logic on any error — safe to enable close to demo time.

## Next Steps / Stretch Goals

- [ ] Swap CSV storage for SQLite
- [ ] Real Razorpay test-mode payment link generation
- [ ] Real WhatsApp/SMS notification (Twilio or WhatsApp Business API)
- [ ] Enable Claude API classifier and compare accuracy vs rule-based
- [ ] Add charts (recovery over time) to the dashboard
