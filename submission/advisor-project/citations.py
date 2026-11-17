"""Small citation helpers shared by the app and evaluation runner."""
from __future__ import annotations
import re

_CITATION_RE = re.compile(r"\[([A-Za-z0-9_-]+-c\d+)\]")


def extract_citations(text: str) -> list[str]:
    return sorted(set(_CITATION_RE.findall(text or "")))


def audit_citations(text: str, retrieved_ids: list[str]) -> dict:
    citations = extract_citations(text)
    invalid = [c for c in citations if c not in retrieved_ids]
    return {
        "citations_in_answer": citations,
        "invalid_citations": invalid,
        "retrieved_ids": list(retrieved_ids),
    }
