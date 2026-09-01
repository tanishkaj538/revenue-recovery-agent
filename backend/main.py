"""
FastAPI backend for the Revenue Recovery Agent.

Run: uvicorn backend.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.pipeline import run_recovery_cycle, get_summary

app = FastAPI(title="AI Revenue Recovery Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Revenue Recovery Agent API is running"}


@app.post("/run-cycle")
def run_cycle():
    """Triggers one full detect->diagnose->act->measure pass over pending payments."""
    return run_recovery_cycle()


@app.get("/summary")
def summary():
    """Returns current dashboard metrics without running the pipeline."""
    return get_summary()
