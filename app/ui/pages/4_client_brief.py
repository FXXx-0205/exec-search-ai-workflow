from __future__ import annotations

import os

import httpx
import pandas as pd
import streamlit as st


st.session_state["current_step"] = 4
st.header("4) Client Brief  ·  排名与客户备忘录")

api_base = st.session_state.get("api_base") or os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
role_spec = st.session_state.get("role_spec")
candidates = st.session_state.get("candidates") or []

if not role_spec:
    st.info("请先完成页面 1（Role Intake）。")
    st.stop()

candidate_ids = [c.get("candidate_id") for c in candidates if c.get("candidate_id")]
default_pick = candidate_ids[:3]

st.markdown("**选择参与 ranking / brief 的候选人（不选则默认用全池）**")
picked = st.multiselect("候选人 ID", options=candidate_ids, default=default_pick)

col1, col2 = st.columns([1, 1])
with col1:
    run_rank = st.button("先打分（Ranking）", type="secondary", use_container_width=True)
with col2:
    run_brief = st.button("生成 Brief（markdown）", type="primary", use_container_width=True)

if run_rank:
    with st.spinner("Ranking..."):
        r = httpx.post(
            f"{api_base}/search/rank",
            json={"role_spec": role_spec, "candidate_ids": picked or candidate_ids},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        st.session_state["ranked_candidates"] = data["ranked_candidates"]

ranked = st.session_state.get("ranked_candidates") or []
if ranked:
    st.subheader("Ranking Results（Top 10）")
    table = [
        {
            "ID": r.get("candidate_id"),
            "Fit": r.get("fit_score"),
            "Skill": r.get("skill_match_score"),
            "Sector": r.get("sector_relevance_score"),
            "Location": r.get("location_score"),
            "Reason": (r.get("reasoning") or [""])[0],
        }
        for r in ranked[:10]
    ]
    st.dataframe(pd.DataFrame(table), hide_index=True, use_container_width=True)

    with st.expander("查看完整 ranking JSON（调试用）", expanded=False):
        st.json(ranked[:10])

if run_brief:
    with st.spinner("Generating brief..."):
        r = httpx.post(
            f"{api_base}/brief/generate",
            json={"role_spec": role_spec, "candidate_ids": picked or None, "project_id": "demo"},
            timeout=90,
        )
        r.raise_for_status()
        data = r.json()
        st.session_state["brief_md"] = data["markdown"]
        st.session_state["brief_id"] = data.get("brief_id")
        st.session_state["brief_approved"] = False

if "brief_md" in st.session_state:
    st.subheader("Brief 生成与审批")
    brief_id = st.session_state.get("brief_id")

    status_col, action_col = st.columns([1, 2])
    with status_col:
        approved = bool(st.session_state.get("brief_approved"))
        if approved:
            st.success(f"✅ 已审批 · brief_id = {brief_id}")
        else:
            st.warning(f"待审批 · brief_id = {brief_id}")

    with action_col:
        cols = st.columns([1, 1, 2])
        with cols[0]:
            approve = st.button("Approve（允许对外导出）", type="primary", disabled=not bool(brief_id))
        with cols[1]:
            refresh = st.button("刷新审批状态", disabled=not bool(brief_id))

        if approve and brief_id:
            r = httpx.post(f"{api_base}/brief/approve/{brief_id}", timeout=60)
            r.raise_for_status()
            st.session_state["brief_approved"] = True
            st.success("已审批。现在允许导出。")

        if refresh and brief_id:
            r = httpx.get(f"{api_base}/brief/{brief_id}", timeout=60)
            r.raise_for_status()
            st.session_state["brief_approved"] = bool(r.json().get("approved"))

    approved = bool(st.session_state.get("brief_approved"))

    if approved:
        st.download_button(
            "下载 markdown（approved）",
            data=st.session_state["brief_md"],
            file_name=f"{brief_id or 'brief'}.md",
            use_container_width=True,
        )
    else:
        st.info("未审批：为模拟 regulated 流程，下载/导出被 gate。请先点击 Approve。")

    st.markdown("---")
    st.markdown("#### Brief 预览")
    st.markdown(st.session_state["brief_md"])

    st.session_state["step_4_done"] = True

st.markdown("---")
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.button("← 返回：Market Map", use_container_width=True):
        try:
            st.switch_page("pages/3_market_map.py")
        except Exception:
            st.warning("无法自动跳转，请在左侧点击 “3) Market Map”。")
with col_next:
    if st.button("回到开头：Role Intake →", use_container_width=True):
        try:
            st.switch_page("pages/1_role_intake.py")
        except Exception:
            st.warning("无法自动跳转，请在左侧点击 “1) Role Intake”。")

