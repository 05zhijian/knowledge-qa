import json
from pathlib import Path

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import config
import db
import doc_parser
import embed_service

app = FastAPI(title="知识库问答 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()
Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)

SUPPORTED = {".pdf", ".txt", ".md"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/docs")
def list_docs():
    return db.list_docs()


@app.delete("/api/docs/{doc_id}")
def remove_doc(doc_id: int):
    db.delete_doc(doc_id)
    return {"ok": True}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    name = file.filename
    if Path(name).suffix.lower() not in SUPPORTED:
        raise HTTPException(400, f"仅支持 {', '.join(sorted(SUPPORTED))}")
    path = Path(config.DATA_DIR) / name
    path.write_bytes(await file.read())

    try:
        text = doc_parser.parse(str(path))
    except ValueError as e:
        raise HTTPException(400, str(e))

    chunks = doc_parser.chunk_text(text)
    if not chunks:
        raise HTTPException(400, "扫描件/图片型 PDF 无法提取文字(需 OCR,暂不支持)")

    embeddings = embed_service.embed(chunks)
    return db.add_doc(name, chunks, embeddings)


@app.post("/api/chat")
async def chat(payload: dict):
    doc_id = payload.get("doc_id")
    question = (payload.get("question") or "").strip()
    if not question:
        raise HTTPException(400, "问题为空")

    chunks = db.load_chunks()
    if doc_id:
        chunks = [c for c in chunks if c[0] == doc_id]
    if not chunks:
        raise HTTPException(400, "知识库为空,请先上传文档")

    query_emb = embed_service.embed_one(question)
    top = embed_service.search(query_emb, question, chunks, config.TOP_K)
    sources = [
        {"doc_name": s["doc_name"], "score": round(s["hybrid"], 3), "text": s["text"][:150]}
        for s in top
    ]
    context = "\n\n".join(f"[{i + 1}] {s['text']}" for i, s in enumerate(top))
    messages = [
        {
            "role": "system",
            "content": "你是知识库问答助手,只依据下面的资料回答;资料不足时直接说明,不要编造。",
        },
        {"role": "user", "content": f"资料:\n{context}\n\n问题:{question}"},
    ]

    async def gen():
        # 先推引用来源,再逐字推正文
        yield f"data: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"
        async with httpx.AsyncClient(
            base_url="https://open.bigmodel.cn/api/paas/v4",
            headers={"Authorization": f"Bearer {config.ZHIPU_API_KEY}"},
            timeout=120,
        ) as client:
            async with client.stream(
                "POST",
                "/chat/completions",
                json={"model": config.CHAT_MODEL, "messages": messages, "stream": True},
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        delta = json.loads(data)["choices"][0]["delta"].get("content", "")
                    except Exception:
                        continue
                    if delta:
                        yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
