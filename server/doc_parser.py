from pathlib import Path

import pymupdf


def parse(path: str) -> str:
    """按后缀分派解析。新增格式只需加一个分支。"""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(path)
    if suffix in (".txt", ".md"):
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"暂不支持格式: {suffix}")


def _parse_pdf(path: str) -> str:
    doc = pymupdf.open(path)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """按字符切块,重叠窗口保留上下文边界。"""
    text = text.replace("\n", " ").strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks
