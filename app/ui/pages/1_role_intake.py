from __future__ import annotations

import os

import httpx
import streamlit as st


st.session_state["current_step"] = 1
st.header("1) Role Intake  ·  角色解析与知识检索")
st.caption("输入一段客户需求 / JD，系统会解析为结构化 role spec，并从内部知识库检索相关公司 /市场上下文。")

api_base = st.session_state.get("api_base") or os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

with st.container():
    col_left, col_right = st.columns([2, 1])

    with col_left:
        raw = st.text_area(
            "输入客户需求 / JD 段落",
            value="Find senior infrastructure portfolio managers in Australia with institutional funds management experience",
            height=180,
            help="可以粘贴一整段英文 JD 或内部 role briefing。",
        )
        run = st.button("解析并检索上下文", type="primary", use_container_width=True)

    with col_right:
        st.markdown("**API 设置**")
        st.text_input("API_BASE_URL", value=api_base, key="api_base", help="一般保持默认即可。")
        st.markdown("---")
        st.markdown("**提示**")
        st.markdown(
            "- 尽量包含：客户类型、地区、职责范围、必须/加分条件\n"
            "- 示例：*Senior infrastructure portfolio manager for Australian super funds...*"
        )

if run:
    with st.spinner("Running intake..."):
        r = httpx.post(f"{api_base}/search/intake", json={"raw_input": raw}, timeout=60)
        r.raise_for_status()
        data = r.json()
        st.session_state["role_spec"] = data["role_spec"]
        st.session_state["retrieval_context"] = data.get("retrieval_context", [])
        st.session_state["vector_store_mode"] = data.get("vector_store_mode")
        st.session_state["step_1_done"] = True

if "role_spec" in st.session_state:
    role_spec = st.session_state["role_spec"]
    retrieval_context = st.session_state.get("retrieval_context", [])

    tab_summary, tab_raw = st.tabs(["解析结果概览", "原始 JSON 视图"])

    with tab_summary:
        st.subheader("👤 结构化 Role Spec")
        top_cols = st.columns(4)
        top_cols[0].metric("Title", role_spec.get("title") or "-")
        top_cols[1].metric("Seniority", role_spec.get("seniority") or "-")
        top_cols[2].metric("Sector", role_spec.get("sector") or "-")
        top_cols[3].metric("Location", role_spec.get("location") or "-")

        col_req, col_pref = st.columns(2)
        col_req.markdown("**Must-have skills**")
        col_req.write(", ".join(role_spec.get("required_skills") or []) or "未识别出必须技能")
        col_pref.markdown("**Nice-to-have skills**")
        col_pref.write(", ".join(role_spec.get("preferred_skills") or []) or "未识别出加分技能")

        if role_spec.get("disqualifiers"):
            st.markdown("**Disqualifiers / 明确排除项**")
            st.write(", ".join(role_spec["disqualifiers"]))

        st.markdown("---")
        st.subheader("📚 检索到的上下文（RAG）")
        st.caption(f"vector_store_mode = {st.session_state.get('vector_store_mode')}")

        if retrieval_context:
            for idx, doc in enumerate(retrieval_context, start=1):
                title = doc.get("title") or doc.get("doc_id") or f"doc-{idx}"
                meta = doc.get("metadata") or {}
                sector = meta.get("sector") or "-"
                region = meta.get("region") or "-"
                with st.expander(f"{idx}. {title}  ·  {sector} · {region}", expanded=(idx == 1)):
                    st.markdown(doc.get("text", ""))
                    if meta:
                        st.caption(f"metadata: {meta}")
        else:
            st.info("当前没有检索到上下文文档（可以检查是否已运行 `scripts/ingest_documents.py`）。")

    with tab_raw:
        st.markdown("#### Role Spec JSON")
        st.json(role_spec)
        st.markdown("#### Retrieval Context JSON")
        st.json(retrieval_context)

st.markdown("---")
col_prev, col_next = st.columns([1, 1])
with col_next:
    disabled = not bool(st.session_state.get("step_1_done"))
    help_text = "请先完成一次解析。" if disabled else None
    if st.button("下一步：Candidate Search →", type="primary", disabled=disabled, help=help_text, use_container_width=True):
        try:
            st.switch_page("pages/2_candidate_search.py")
        except Exception:
            st.warning("无法自动跳转，请在左侧点击 “2) Candidate Search”。")

