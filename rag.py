"""Tiny, inspectable TF-IDF retrieval pipeline for the course scaffold."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class Chunk:
    source: str
    chunk_id: str
    text: str

@dataclass
class Hit:
    source: str
    chunk_id: str
    text: str
    score: float

    def to_dict(self):
        return asdict(self)


def load_chunks(corpus_dir: str | Path) -> List[Chunk]:
    corpus_dir = Path(corpus_dir)
    chunks: List[Chunk] = []
    for path in sorted(corpus_dir.glob("*.md")):
        body = path.read_text(encoding="utf-8")
        paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body)]
        paragraphs = [p for p in paragraphs if p and not p.startswith("#")]
        for i, paragraph in enumerate(paragraphs, 1):
            chunks.append(Chunk(path.name, f"{path.stem}-c{i}", paragraph))
    return chunks


class Retriever:
    def __init__(self, corpus_dir: str | Path):
        self.chunks = load_chunks(corpus_dir)
        if not self.chunks:
            raise ValueError("No corpus chunks found")
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([c.text for c in self.chunks])

    def search(self, query: str, top_k: int = 4) -> List[Hit]:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        order = scores.argsort()[::-1][:top_k]
        return [
            Hit(
                source=self.chunks[i].source,
                chunk_id=self.chunks[i].chunk_id,
                text=self.chunks[i].text,
                score=float(scores[i]),
            )
            for i in order
        ]


def format_context(hits: List[Hit]) -> str:
    sections = []
    for hit in hits:
        sections.append(f"SOURCE [{hit.chunk_id}] ({hit.source})\n{hit.text}")
    return "\n\n".join(sections)
