from __future__ import annotations

import pandas as pd
import streamlit as st


st.session_state["current_step"] = 3
st.header("3) Market Map  ·  市场与机构视图（简化版）")
st.caption("基于当前候选人池和检索到的公司 profile，粗略展示机构分布和上下文。")

candidates = st.session_state.get("candidates") or []
retrieval_context = st.session_state.get("retrieval_context") or []

if not candidates and not retrieval_context:
    st.info("请先完成页面 1（Role Intake）和页面 2（Candidate Search）。")
    st.stop()

col_firms, col_context = st.columns([1.2, 1])

with col_firms:
    st.subheader("Top Firms（按候选人数量）")
    firms = {}
    for c in candidates:
        firm = c.get("current_company") or "Unknown"
        firms[firm] = firms.get(firm, 0) + 1

    if firms:
        df_firms = pd.DataFrame(
            sorted([{"Firm": k, "Candidates": v} for k, v in firms.items()], key=lambda x: x["Candidates"], reverse=True)
        )
        st.bar_chart(df_firms.set_index("Firm"))
        st.dataframe(df_firms, hide_index=True, use_container_width=True)
    else:
        st.write("当前没有候选人数据。")

with col_context:
    st.subheader("RAG Grounding Context（公司 / 机构）")
    if retrieval_context:
        for d in retrieval_context:
            meta = d.get("metadata") or {}
            title = d.get("title") or d.get("doc_id") or meta.get("company") or "firm"
            sector = meta.get("sector") or "-"
            region = meta.get("region") or "-"
            with st.expander(f"{title} · {sector} · {region}", expanded=False):
                st.write(d.get("text", ""))
                if meta:
                    st.caption(f"metadata: {meta}")
    else:
        st.write("当前没有检索上下文（可能尚未运行 `scripts/ingest_documents.py` 或检索条件过窄）。")

st.session_state["step_3_done"] = True

st.markdown("---")
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.button("← 返回：Candidate Search", use_container_width=True):
        try:
            st.switch_page("pages/2_candidate_search.py")
        except Exception:
            st.warning("无法自动跳转，请在左侧点击 “2) Candidate Search”。")
with col_next:
    if st.button("下一步：Client Brief →", type="primary", use_container_width=True):
        try:
            st.switch_page("pages/4_client_brief.py")
        except Exception:
            st.warning("无法自动跳转，请在左侧点击 “4) Client Brief”。")

