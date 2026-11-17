"""Run sample evaluation prompts and save inspectable evidence for manual review."""
from __future__ import annotations
import json
import os
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv

from calculator import route_calculation, format_calculator_block
from citations import audit_citations
from llm_client import answer
from prompts import SYSTEM_PROMPT, build_user_prompt
from rag import Retriever, format_context
from runtime_manifest import write_manifest

load_dotenv()
ROOT = Path(__file__).parent
parser = argparse.ArgumentParser(description="Run one split of the advisor evaluation set.")
parser.add_argument(
    "--split",
    choices=("development", "heldout"),
    default="development",
    help="Evaluation split to run. Defaults to development; run heldout only after Part 6 is complete.",
)
args = parser.parse_args()
retriever = Retriever(ROOT / "corpus")
top_k = int(os.getenv("RAG_TOP_K", "4"))

cases = json.loads((ROOT / "eval_cases.json").read_text(encoding="utf-8"))
cases = [case for case in cases if case.get("split") == args.split]
if not cases:
    raise SystemExit(f"No evaluation cases found for split: {args.split}")
manifest, manifest_path = write_manifest(ROOT, SYSTEM_PROMPT, top_k)
results = []

for case in cases:
    query = case["prompt"]
    history = case.get("history", [])
    hits = retriever.search(query, top_k)
    context = format_context(hits)
    calc = route_calculation(query)
    prompt = build_user_prompt(query, context, format_calculator_block(calc), history)

    t0 = time.perf_counter()
    try:
        text, backend, model = answer(SYSTEM_PROMPT, prompt)
        error = None
    except Exception as e:
        text, backend, model, error = "", os.getenv("LLM_BACKEND", "mock"), "unknown", repr(e)
    latency = time.perf_counter() - t0

    retrieved_ids = [h.chunk_id for h in hits]
    results.append({
        **case,
        "answer": text,
        "backend": backend,
        "model": model,
        "retrieved": [h.to_dict() for h in hits],
        "retrieved_ids": retrieved_ids,
        "needed_evidence_present": None,
        "primary_failure": None,
        "manual_review_notes": "",
        "calculator": calc.to_dict() if calc else None,
        "prompt_context": prompt,
        "citation_audit": audit_citations(text, retrieved_ids),
        "latency_seconds": latency,
        "error": error,
    })

payload = {"manifest": manifest, "results": results}
out = ROOT / "logs" / f"eval_results_{args.split}.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Wrote {len(results)} evaluation results to {out}")
print(f"Wrote run manifest to {manifest_path}")
print("Manual review reminder: for each failure, first mark whether the evidence needed for a good answer was present in the retrieved context.")
