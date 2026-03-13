from __future__ import annotations

import os

import httpx
import pandas as pd
import streamlit as st


st.session_state["current_step"] = 2
st.header("2) Candidate Search  ·  候选人检索与浏览")

api_base = st.session_state.get("api_base") or os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
role_spec = st.session_state.get("role_spec")

if not role_spec:
    st.info("请先到页面 1 完成 Role Intake。")
    st.stop()

run = st.button("从 demo 候选池检索", type="primary")

if run:
    with st.spinner("Searching candidates..."):
        r = httpx.post(f"{api_base}/search/candidates", json={"role_spec": role_spec, "project_id": "demo"}, timeout=60)
        r.raise_for_status()
        data = r.json()
        st.session_state["candidates"] = data["candidates"]

candidates = st.session_state.get("candidates") or []
st.subheader(f"候选人列表（{len(candidates)}）")

if candidates:
    # 表格视图
    table_data = []
    for c in candidates:
        table_data.append(
            {
                "ID": c.get("candidate_id"),
                "Name": c.get("full_name"),
                "Title": c.get("current_title"),
                "Company": c.get("current_company"),
                "Location": c.get("location"),
                "Sectors": ", ".join(c.get("sectors") or []),
                "Functions": ", ".join(c.get("functions") or []),
                "Confidence": c.get("confidence_score"),
            }
        )

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 详情视图
    st.markdown("#### 候选人详情")
    selected_id = st.selectbox(
        "选择一个候选人查看详情",
        options=[row["ID"] for row in table_data],
        format_func=lambda cid: next((r["Name"] for r in table_data if r["ID"] == cid), cid),
    )

    detail = next((c for c in candidates if c.get("candidate_id") == selected_id), None)
    if detail:
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.markdown(f"**{detail.get('full_name')}**")
            st.caption(f"{detail.get('current_title')} @ {detail.get('current_company')}")
            st.markdown(f"- 🌍 Location: {detail.get('location')}")
            st.markdown(f"- 🧩 Sectors: {', '.join(detail.get('sectors') or []) or '-'}")
            st.markdown(f"- 🎯 Functions: {', '.join(detail.get('functions') or []) or '-'}")
            st.markdown("**Summary**")
            st.write(detail.get("summary") or "-")

        with col_right:
            st.metric("Confidence score", f"{(detail.get('confidence_score') or 0) * 100:.0f}")
            if detail.get("source_urls"):
                st.markdown("**Source URLs**")
                for url in detail["source_urls"]:
                    st.markdown(f"- `{url}`")

        with st.expander("查看完整 JSON（调试用）", expanded=False):
            st.json(detail)

    st.session_state["step_2_done"] = True

st.markdown("---")
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.button("← 返回：Role Intake", use_container_width=True):
        try:
            st.switch_page("pages/1_role_intake.py")
        except Exception:
            st.warning("无法自动跳转，请在左侧点击 “1) Role Intake”。")
with col_next:
    disabled = not bool(st.session_state.get("step_2_done"))
    if st.button("下一步：Market Map →", type="primary", disabled=disabled, use_container_width=True):
        try:
            st.switch_page("pages/3_market_map.py")
        except Exception:
            st.warning("无法自动跳转，请在左侧点击 “3) Market Map”。")

