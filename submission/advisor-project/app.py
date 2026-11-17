from __future__ import annotations
import os
import re
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from calculator import route_calculation, format_calculator_block
from citations import audit_citations
from llm_client import answer
from logging_utils import append_log
from prompts import SYSTEM_PROMPT, POLICY_VERSION, build_user_prompt
from rag import Retriever, format_context
from runtime_manifest import build_manifest

load_dotenv()
ROOT = Path(__file__).parent
CORPUS = ROOT / "corpus"
TOP_K = int(os.getenv("RAG_TOP_K", "4"))
HISTORY_MESSAGES = int(os.getenv("CHAT_HISTORY_MESSAGES", "6"))


def _markdown_safe_currency(text: str) -> str:
    """Prevent currency dollar signs from being parsed as inline LaTeX math."""
    segments = re.split(r"(`[^`]*`)", text)
    return "".join(
        segment if segment.startswith("`") and segment.endswith("`") else segment.replace("$", "&#36;")
        for segment in segments
    )


def _show_inspection(inspection: dict, expanded: bool = False) -> None:
    """Show the evidence and audit attached to this specific assistant turn."""
    with st.expander("Inspect retrieval and system behavior", expanded=expanded):
        st.write("**Retrieved passages**")
        for hit in inspection.get("retrieved", []):
            st.markdown(f"**[{hit['chunk_id']}] {hit['source']} — score {hit['score']:.3f}**")
            st.write(hit["text"])
        st.write("**Citation audit**")
        st.write(inspection.get("citation_audit", {}))
        calculator = inspection.get("calculator")
        if calculator:
            st.write("**Calculator result**")
            st.write(calculator)
        st.write("**Prompt context sent to model**")
        st.code(inspection.get("prompt_context", ""))
        st.write(
            "**Backend/model:** "
            f"{inspection.get('backend', 'unknown')} / {inspection.get('model', 'unknown')}"
            f"   **Latency:** {inspection.get('latency_seconds', 0):.2f}s"
        )
        identity = inspection.get("run_identity", {})
        if identity:
            st.write(
                "**Run identity:** "
                f"prompt `{identity.get('system_prompt_sha256', '')[:12]}` / "
                f"corpus `{identity.get('corpus_fingerprint_sha256', '')[:12]}`"
            )


@st.cache_resource
def get_retriever():
    return Retriever(CORPUS)


st.set_page_config(page_title="94-879 Wealth Advisor Scaffold", layout="wide")
st.title("94-879 Wealth Advisor Scaffold v0.3")
st.caption("Inspectable RAG + bounded deterministic calculation + citations + logging")

backend = os.getenv("LLM_BACKEND", "mock")
with st.sidebar:
    st.subheader("Runtime")
    st.write(f"LLM backend: **{backend}**")
    if backend == "openai":
        st.write(f"Model: `{os.getenv('OPENAI_MODEL', 'gpt-5.6-luna')}`")
    elif backend == "ollama":
        st.write(f"Model: `{os.getenv('OLLAMA_MODEL', 'qwen3:4b')}`")
    st.write(f"Retrieval top-k: **{TOP_K}**")
    st.write(f"Conversation context: last **{HISTORY_MESSAGES}** messages")
    st.write(f"Policy version: `{POLICY_VERSION}`")
    st.caption("Calculator routing: CALC:, X% of Y, $X/month for Y months/years, and savings coverage vs. essential monthly expenses.")
    if st.button("Reload corpus"):
        get_retriever.clear()
        st.success("Corpus cache cleared. The next query will rebuild retrieval.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(_markdown_safe_currency(message["content"]))
        if message["role"] == "assistant" and message.get("inspection"):
            _show_inspection(message["inspection"])

query = st.chat_input("Ask a question about the supplied wealth-advisor corpus")
if query:
    prior_messages = list(st.session_state.messages)[-HISTORY_MESSAGES:]
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(_markdown_safe_currency(query))

    retriever = get_retriever()
    hits = retriever.search(query, TOP_K)
    context = format_context(hits)
    calc = route_calculation(query)
    calc_block = format_calculator_block(calc)
    user_prompt = build_user_prompt(query, context, calc_block, prior_messages)

    started = time.perf_counter()
    error = None
    try:
        response_text, used_backend, model = answer(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        response_text = f"LLM call failed: {e}"
        used_backend, model, error = backend, "unknown", repr(e)
    latency = time.perf_counter() - started

    retrieved_ids = [h.chunk_id for h in hits]
    citation_audit = audit_citations(response_text, retrieved_ids)
    manifest = build_manifest(ROOT, SYSTEM_PROMPT, TOP_K)
    inspection = {
        "retrieved": [h.to_dict() for h in hits],
        "citation_audit": citation_audit,
        "calculator": calc.to_dict() if calc else None,
        "prompt_context": user_prompt,
        "backend": used_backend,
        "model": model,
        "latency_seconds": latency,
        "run_identity": manifest,
    }

    with st.chat_message("assistant"):
        st.markdown(_markdown_safe_currency(response_text))
        if calc is not None:
            if calc.error:
                st.warning(f"Calculator error ({calc.route}): {calc.error}")
            else:
                st.info(f"Deterministic calculation ({calc.route}): `{calc.expression}` = **{calc.result:g}**")

        _show_inspection(inspection, expanded=True)

    st.session_state.messages.append({"role": "assistant", "content": response_text, "inspection": inspection})

    append_log({
        "query": query,
        "prior_messages": prior_messages,
        "backend": used_backend,
        "model": model,
        "retrieved": [h.to_dict() for h in hits],
        "calculator": calc.to_dict() if calc else None,
        "prompt_context": user_prompt,
        "response": response_text,
        "citation_audit": citation_audit,
        "latency_seconds": latency,
        "error": error,
        "run_identity": {
            "scaffold_version": manifest["scaffold_version"],
            "rag_top_k": manifest["rag_top_k"],
            "system_prompt_sha256": manifest["system_prompt_sha256"],
            "corpus_fingerprint_sha256": manifest["corpus_fingerprint_sha256"],
        },
    }, ROOT / "logs")
