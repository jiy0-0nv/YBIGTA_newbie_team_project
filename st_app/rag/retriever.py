from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI
from st_app.utils.state import Doc

load_dotenv()

BASE_URL = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1")
API_KEY  = os.getenv("UPSTAGE_API_KEY")
MODEL_QUERY = os.getenv("UPSTAGE_EMBED_MODEL_QUERY", "solar-embedding-1-large-query")
OVERFETCH = int(os.getenv("RETRIEVER_OVERFETCH", "5"))

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def _require_key():
    if not API_KEY:
        raise RuntimeError("UPSTAGE_API_KEY 환경변수가 설정되어 있지 않습니다.")

def _embed_query(q: str) -> np.ndarray:
    _require_key()
    resp = client.embeddings.create(model=MODEL_QUERY, input=q)
    v = np.asarray(resp.data[0].embedding, dtype=np.float32)[None, :]
    v /= (np.linalg.norm(v, axis=1, keepdims=True) + 1e-12)  # L2 정규화
    return np.ascontiguousarray(v, dtype=np.float32)

class Retriever:
    def __init__(self, index_dir: str = "st_app/db/faiss_index", overfetch: int = OVERFETCH):
        self.index_dir = Path(index_dir)
        self.index = faiss.read_index(str(self.index_dir / "index.faiss"))
        # 메타
        self.meta: List[Dict[str, Any]] = []
        with open(self.index_dir / "meta.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                self.meta.append(json.loads(line))
        self.overfetch = max(1, int(overfetch))

    def retrieve(self, query: str, k: int = 6, filters: Optional[Dict[str, Any]] = None) -> List[Doc]:
        filters = filters or {}
        sites = set(filters.get("sites") or []) or None
        min_rating = float(filters.get("min_rating") or 0.0)

        qv = _embed_query(query)
        topn = max(k * self.overfetch, k)
        scores, idxs = self.index.search(qv, topn)
        out: List[Doc] = []
        for i in idxs[0].tolist():
            if i < 0: continue
            m = self.meta[i]
            if sites and m["source"] not in sites:  # 필터
                continue
            if m["rating"] < min_rating:
                continue
            out.append({
                "text": m["text"],
                "meta": {
                    "site": m["source"], "author": m["author"], "date": m["date"],
                    "rating": m["rating"], "url": m["url"],
                    "review_id": m["review_id"], "chunk_id": m["chunk_id"]
                }
            })
            if len(out) >= k: break
        return out
