import argparse, json, os, time
from pathlib import Path
import numpy as np
import pandas as pd
import faiss
from dotenv import load_dotenv
from openai import OpenAI, BadRequestError

load_dotenv()

OUT_DIR_DEFAULT = "st_app/db/faiss_index"

# Upstage OpenAI-호환 엔드포인트
BASE_URL = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1")
API_KEY  = os.getenv("UPSTAGE_API_KEY")
MODEL_DOC = os.getenv("UPSTAGE_EMBED_MODEL_DOC", "solar-embedding-1-large-passage")
BATCH = int(os.getenv("EMBED_BATCH", "64"))
MAX_CHARS = int(os.getenv("EMBED_MAX_CHARS", "5000"))

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def _require_key():
    if not API_KEY:
        raise RuntimeError("UPSTAGE_API_KEY not set")

def _l2_norm(a: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(a, axis=1, keepdims=True) + 1e-12
    return (a / n).astype(np.float32)

def _sanitize_texts(texts: list[str]) -> list[str]:
    clean = []
    for t in texts:
        s = ("" if t is None else str(t)).strip()
        if not s:
            continue
        if len(s) > MAX_CHARS:
            s = s[:MAX_CHARS]  # 너무 긴 입력은 자름
        clean.append(s)
    return clean

def _embed_batch(batch: list[str], model: str, retry=0) -> np.ndarray:
    # 문제가 되는 배치를 자동으로 쪼개 재시도
    try:
        resp = client.embeddings.create(model=model, input=batch)
        vecs = [d.embedding for d in resp.data]
        return np.asarray(vecs, dtype=np.float32)
    except BadRequestError as e:
        # '$.input' invalid 같은 400 에러 → 절반으로 쪼개 재귀
        if len(batch) > 1:
            mid = len(batch) // 2
            left = _embed_batch(batch[:mid], model, retry)
            right = _embed_batch(batch[mid:], model, retry)
            return np.vstack([left, right])
        raise
    except Exception:
        # 일시적 오류는 간단 백오프 후 1회 재시도
        if retry < 2:
            time.sleep(1.5 * (retry + 1))
            return _embed_batch(batch, model, retry+1)
        raise
    
def _embed_texts(texts: list[str], model: str, batch_size: int = BATCH) -> np.ndarray:
    _require_key()
    texts = _sanitize_texts(texts)
    if not texts:
        raise RuntimeError("임베딩할 유효 텍스트가 없습니다.")
    chunks = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        vecs = _embed_batch(batch, model)
        chunks.append(vecs)
    embs = np.vstack(chunks)
    return np.ascontiguousarray(_l2_norm(embs), dtype=np.float32)

def chunk_text(t: str, size: int = 800, overlap: int = 100) -> list[str]:
    t = (t or "").strip()
    if not t: return []
    if overlap < 0 or size <= 0 or overlap >= size:
        raise ValueError(f"Invalid chunk params: size={size}, overlap={overlap}")
    if len(t) <= size: return [t]
    step = size - overlap
    return [t[i:i+size] for i in range(0, len(t), step)]

def build(args):
    in_path = Path(args.input)
    out_dir = Path(args.out or OUT_DIR_DEFAULT)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(in_path)
    req = {"review_id","source","author","rating_norm","review_text","created_at","url"}
    missing = req - set(df.columns)
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")

    # 레코드 → 청크
    records, texts = [], []
    for _, r in df.iterrows():
        for j, c in enumerate(chunk_text(str(r["review_text"]), size=args.chunk_size, overlap=args.overlap)):
            records.append({
                "review_id": r["review_id"],
                "chunk_id": f"{r['review_id']}#{j}",
                "source": r["source"],
                "author": r["author"],
                "rating": float(r["rating_norm"]),
                "date": str(r["created_at"]),
                "url": r["url"],
                "text": c
            })
            texts.append(c)

    if not records:
        raise RuntimeError("청크가 생성되지 않았습니다. 입력을 확인하세요.")

    # 임베딩(API) → FAISS
    embs = _embed_texts(texts, model=MODEL_DOC, batch_size=args.batch)
    if embs.shape[0] != len(records):
        raise RuntimeError("임베딩 수와 레코드 수가 일치하지 않습니다.")
    d = embs.shape[1]
    index = faiss.IndexFlatIP(d)   # 코사인 = 내적 (정규화 완료)
    index.add(embs)
    faiss.write_index(index, str(out_dir / "index.faiss"))

    # 메타/세팅 저장
    with open(out_dir / "meta.jsonl", "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    with open(out_dir / "settings.json", "w", encoding="utf-8") as f:
        json.dump({
            "embed_model_doc": MODEL_DOC,
            "normalized": True,
            "index_type": "IndexFlatIP",
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "n_chunks": len(records),
            "base_url": BASE_URL
        }, f, ensure_ascii=False, indent=2)

    print(f"[OK] index:{len(records)} chunks  dim:{d}")
    print(f" - {out_dir/'index.faiss'}")
    print(f" - {out_dir/'meta.jsonl'}")
    print(f" - {out_dir/'settings.json'}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="reviews_ready.parquet")
    p.add_argument("--out", default=OUT_DIR_DEFAULT)
    p.add_argument("--chunk_size", type=int, default=800)
    p.add_argument("--overlap", type=int, default=100)
    p.add_argument("--batch", type=int, default=BATCH)
    args = p.parse_args()
    build(args)
