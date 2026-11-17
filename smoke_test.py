"""Local structural smoke test that does not require an LLM endpoint."""
from pathlib import Path
import re
from calculator import safe_eval, route_calculation
from rag import Retriever
from prompts import SYSTEM_PROMPT

ROOT = Path(__file__).parent
r = Retriever(ROOT / "corpus")
assert len(r.chunks) > 0, "Corpus loaded no chunks"
assert len({c.chunk_id for c in r.chunks}) == len(r.chunks), "Chunk IDs are not unique"
assert all(re.fullmatch(r"[A-Za-z0-9_-]+-c\d+", c.chunk_id) for c in r.chunks), "Malformed chunk ID"
assert SYSTEM_PROMPT.strip(), "Shared system prompt is empty"

# Content-independent retrieval check: a chunk should retrieve itself (or an exact duplicate).
probe = r.chunks[0]
hits = r.search(probe.text, 1)
assert hits, "Retriever returned no result"
assert hits[0].text == probe.text, "Retriever failed self-query sanity check"
assert 0.0 <= hits[0].score <= 1.000001, "Retrieval score outside expected range"

value = safe_eval("1000000*0.008 + 400000*0.005")
assert value == 10000.0, f"Calculator returned {value}"
auto = route_calculation("What is 8% of $5,000?")
assert auto and auto.result == 400.0 and auto.route == "percent_of", "Automatic calculator routing failed"

print("SMOKE TEST PASSED")
print(f"Loaded {len(r.chunks)} corpus chunks from {len({c.source for c in r.chunks})} files")
print(f"Self-query top retrieval: {hits[0].chunk_id} score={hits[0].score:.3f}")
print(f"Calculator test: {value:.2f}; automatic route: {auto.expression} = {auto.result:.2f}")
