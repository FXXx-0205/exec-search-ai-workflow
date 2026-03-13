from __future__ import annotations

import os

import streamlit as st


st.set_page_config(page_title="PPP AI Search Copilot", layout="wide")

st.title("PPP AI Search Copilot")
st.caption("Demo: Role intake → Retrieval → Candidate ranking → Brief generation")

api_base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
st.session_state.setdefault("api_base", api_base)

with st.sidebar:
    st.markdown("### Workflow")
    steps = [
        (1, "Role Intake"),
        (2, "Candidate Search"),
        (3, "Market Map"),
        (4, "Client Brief"),
    ]
    current = st.session_state.get("current_step", 1)
    done_flags = {
        1: bool(st.session_state.get("step_1_done")),
        2: bool(st.session_state.get("step_2_done")),
        3: bool(st.session_state.get("step_3_done")),
        4: bool(st.session_state.get("step_4_done")),
    }
    for idx, label in steps:
        if idx == current:
            prefix = "👉"
        elif done_flags.get(idx):
            prefix = "✅"
        else:
            prefix = "⬜"
        st.markdown(f"{prefix} **{idx}. {label}**")

st.markdown(
    """
**使用方式（本地）**
- 先启动 API：`uvicorn app.main:app --reload`
- 再启动 UI：`streamlit run app/ui/streamlit_app.py`

按照页面底部的“下一步”按钮逐步完成流程；左侧 Workflow 仅作为进度指示。
"""
)

