import httpx
import numpy as np

import config
import db

_BASE = "https://open.bigmodel.cn/api/paas/v4"


def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    result: list[list[float]] = []
    with httpx.Client(
        base_url=_BASE,
        headers={"Authorization": f"Bearer {config.ZHIPU_API_KEY}"},
        timeout=60,
    ) as client:
        # 智谱单次 embedding 有输入条数上限,分批调用
        for i in range(0, len(texts), 32):
            batch = texts[i : i + 32]
            r = client.post("/embeddings", json={"model": config.EMBED_MODEL, "input": batch})
            r.raise_for_status()
            result.extend(item["embedding"] for item in r.json()["data"])
    return result


def embed_one(text: str) -> list[float]:
    return embed([text])[0]


def cosine(a: list[float], b: list[float]) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if denom == 0 else float(a.dot(b) / denom)


def search(query_emb: list[float], query_text: str, chunks: list[tuple[int, str, str, list[float]]], top_k: int = 3, w: float = 0.6):
    """混合检索:向量余弦 + FTS5 关键词,加权取 top_k。
    chunks: [(doc_id, doc_name, text, embedding)]
    返回 top_k 个 {doc_id, doc_name, text, vec, kw, hybrid}。
    """
    scored = [
        {"doc_id": doc_id, "doc_name": doc_name, "text": text, "vec": cosine(query_emb, emb)}
        for doc_id, doc_name, text, emb in chunks
    ]

    try:
        kw = db.keyword_search(query_text)
    except Exception:
        kw = []
    kw_map = {(r["doc_id"], r["text"]): r["score"] for r in kw}
    raw = [r["score"] for r in kw]
    lo, hi = (min(raw), max(raw)) if raw else (0.0, 1.0)

    def norm(s: float) -> float:
        return (s - lo) / (hi - lo) if hi > lo else 0.0

    for s in scored:
        key = (s["doc_id"], s["text"])
        s["kw"] = norm(kw_map[key]) if key in kw_map else 0.0
        s["hybrid"] = w * s["vec"] + (1 - w) * s["kw"]

    return sorted(scored, key=lambda s: s["hybrid"], reverse=True)[:top_k]
