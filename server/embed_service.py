import httpx
import numpy as np

import config

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


def search(query_emb: list[float], chunks: list[tuple[int, str, list[float]]], top_k: int = 3):
    """chunks: [(doc_id, text, emb)],返回 top-k 的 [(score, text)]。"""
    scored = sorted(
        ((cosine(query_emb, emb), text) for _, text, emb in chunks),
        key=lambda x: x[0],
        reverse=True,
    )
    return scored[:top_k]
