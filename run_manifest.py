"""Write a reproducibility manifest for the current scaffold configuration."""
from pathlib import Path
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT
from runtime_manifest import write_manifest

load_dotenv()
ROOT = Path(__file__).parent
TOP_K = int(os.getenv("RAG_TOP_K", "4"))
manifest, path = write_manifest(ROOT, SYSTEM_PROMPT, TOP_K)
print(f"Wrote run manifest to {path}")
for key in ["scaffold_version", "backend", "model", "rag_top_k", "system_prompt_sha256", "corpus_fingerprint_sha256"]:
    print(f"{key}: {manifest[key]}")
