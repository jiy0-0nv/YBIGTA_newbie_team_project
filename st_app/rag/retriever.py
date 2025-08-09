from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from st_app.utils.state import Doc

class MockRetriever:
    def __init__(self,
                 index_dir: str = "st_app/db/faiss_index",
                 model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
                 overfetch: int = 5):
        self.index_dir = Path(index_dir)
        self.index = faiss.read_index(str(self.index_dir / "index.faiss"))
        self.model = SentenceTransformer(model_name)
        # meta.jsonl 로드
        self.meta: List[Dict[str, Any]] = []
        with open(self.index_dir / "meta.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                self.meta.append(json.loads(line))
        self.overfetch = max(1, int(overfetch))

    def _embed(self, q: str) -> np.ndarray:
        v = self.model.encode([q], normalize_embeddings=True, convert_to_numpy=True)
        return v.astype(np.float32)

    def retrieve(self, query: str, k: int = 6, filters: Optional[Dict[str, Any]] = None) -> List[Doc]:
        filters = filters or {}
        sites = set(filters.get("sites") or []) or None
        min_rating = float(filters.get("min_rating") or 0.0)

        q = self._embed(query)
        # 초과 조회 후 필터링
        over_k = max(k * self.overfetch, k)
        scores, idxs = self.index.search(q, over_k)  # (1, over_k)
        result: List[Doc] = []
        for i in idxs[0].tolist():
            if i < 0: continue
            m = self.meta[i]
            if sites and m["source"] not in sites:
                continue
            if m["rating"] < min_rating:
                continue
            result.append({"text": m["text"], "meta": {
                "site": m["source"], "author": m["author"], "date": m["date"],
                "rating": m["rating"], "url": m["url"], "review_id": m["review_id"], "chunk_id": m["chunk_id"]
            }})
            if len(result) >= k: break
        return result