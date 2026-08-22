# 知识库问答 (uni-app + FastAPI)

多端 AI 知识库问答 demo:上传 PDF/txt/md → 服务端解析分块 → 向量化入库 → 基于文档语义问答(SSE 流式)。

**特点:零框架自建 RAG 链路**——不用 LangChain/FastGPT,解析→分块→embedding→余弦检索→prompt→SSE 每段自己写,面试可逐行讲。

## 技术栈

| 层 | 选型 |
|---|---|
| 前端 | uni-app (Vue3 + Vite + Pinia),一套代码出 微信小程序 / H5 / App |
| 后端 | Python FastAPI + PyMuPDF + SQLite |
| AI | 智谱 embedding-2(向量) + GLM-4-Flash(流式问答) |
| 检索 | SQLite 存 chunk+向量,余弦线性扫描(demo 量级够,可换 Chroma) |

## 目录结构

```
knowledge_qa_demo/
├── app/        # uni-app 前端
│   └── src/
│       ├── pages/index    # 知识库列表(上传/删除/进入问答)
│       ├── pages/chat     # 问答聊天(SSE 流式渲染)
│       ├── stores/        # Pinia(docs / chat)
│       └── utils/stream.js # 跨端 SSE 封装(小程序 enableChunked / H5 fetch)
└── server/     # FastAPI 后端
    ├── main.py          # 路由 + SSE
    ├── doc_parser.py    # 按格式分派解析 + 分块
    ├── embed_service.py # 智谱 embedding + 余弦检索
    ├── db.py            # SQLite(docs / chunks)
    └── config.py        # 环境变量
```

## 快速开始

### 后端

```bash
cd server
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env   # 填入智谱 ZHIPU_API_KEY
.venv/Scripts/python -m uvicorn main:app --port 8000
```

### 前端(H5 演示)

```bash
cd app
npm install
npm run dev:h5   # 默认 http://localhost:5173, /api 已代理到 8000
```

### 微信小程序

```bash
npm run dev:mp-weixin   # 用微信开发者工具打开 app/dist/dev/mp-weixin
```
个人主体在开发者工具里勾「不校验合法域名」即可本地联调。

## 数据流

上传 → PyMuPDF 抽文字 → 500 字分块(50 重叠)→ 智谱 embedding → SQLite → 提问 embedding → 余弦 top3 → 拼 prompt → GLM 流式回答 → 前端逐字渲染

## 迭代计划

- [x] 骨架:前后端工程 + PDF/txt/md 上传 + SSE 流式问答
- [ ] 答案引用来源(命中片段高亮)
- [ ] 混合检索(FTS5 关键词 + 向量)
- [ ] 扫码件 OCR(pdf 图片型)
- [ ] 上 GitHub + 作品集
