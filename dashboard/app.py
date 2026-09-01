"""
Streamlit Dashboard — AI Revenue Recovery Agent

Run: streamlit run dashboard/app.py
(Run this from the project root so the data/ paths resolve correctly)
"""

import sys
import os
import pandas as pd
import streamlit as st

# allow importing backend/ when run from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pipeline import run_recovery_cycle, get_summary

st.set_page_config(page_title="AI Revenue Recovery Agent", layout="wide")

st.title("💳 AI Revenue Recovery Agent")
st.caption("Detect → Diagnose → Act → Measure — failed payment recovery, automated.")

col_btn, _ = st.columns([1, 4])
with col_btn:
    if st.button("▶ Run Recovery Cycle", type="primary"):
        with st.spinner("Running detect → diagnose → act → measure..."):
            result = run_recovery_cycle()
        st.success(
            f"Processed {result['processed_count']} payments — "
            f"recovered ₹{result['total_recovered']:,.2f} from {result['recovered_count']} payments."
        )

st.divider()

summary = get_summary()

m1, m2, m3, m4 = st.columns(4)
m1.metric("💰 Total ₹ Recovered", f"₹{summary['total_recovered']:,.2f}")
m2.metric("📊 Success Rate", f"{summary['success_rate']}%")
m3.metric("⏳ Still Pending", summary["pending_count"])
m4.metric("🚫 Unrecoverable", summary["unrecoverable_count"])

st.divider()

tab1, tab2, tab3 = st.tabs(["📋 All Payments", "🚫 Exception List", "🧾 Audit Trail"])

with tab1:
    df = pd.DataFrame(summary["all_payments"])
    st.dataframe(df, use_container_width=True)

with tab2:
    if summary["unrecoverable_list"]:
        st.dataframe(pd.DataFrame(summary["unrecoverable_list"]), use_container_width=True)
    else:
        st.info("No unrecoverable payments yet.")

with tab3:
    try:
        audit_df = pd.read_csv("data/audit_trail.csv")
        st.dataframe(audit_df.sort_values("timestamp", ascending=False), use_container_width=True)
    except FileNotFoundError:
        st.info("No actions taken yet — click 'Run Recovery Cycle' above.")
