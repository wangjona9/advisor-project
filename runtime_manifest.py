"""Reproducibility manifest helpers."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path


def _sha_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_manifest(root: str | Path, system_prompt: str, top_k: int) -> dict:
    root = Path(root)
    version_path = root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"
    corpus_files = sorted((root / "corpus").glob("*.md"))
    corpus = [{"file": p.name, "sha256": _file_sha(p)} for p in corpus_files]
    corpus_fingerprint = _sha_text(json.dumps(corpus, sort_keys=True))
    backend = os.getenv("LLM_BACKEND", "mock").strip().lower()
    if backend == "openai":
        model = os.getenv("OPENAI_MODEL", "")
    elif backend == "ollama":
        model = os.getenv("OLLAMA_MODEL", "")
    else:
        model = "mock"
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scaffold_version": version,
        "backend": backend,
        "model": model,
        "model_sampling_settings": "provider defaults; scaffold does not set temperature/seed",
        "rag_top_k": int(top_k),
        "system_prompt_sha256": _sha_text(system_prompt),
        "corpus_fingerprint_sha256": corpus_fingerprint,
        "corpus_files": corpus,
    }


def write_manifest(root: str | Path, system_prompt: str, top_k: int) -> tuple[dict, Path]:
    root = Path(root)
    manifest = build_manifest(root, system_prompt, top_k)
    out = root / "logs" / "run_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest, out
