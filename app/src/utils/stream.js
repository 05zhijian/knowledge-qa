// 跨端 SSE 流式请求封装(本项目最难的一块,面试可讲)
// - H5: fetch + ReadableStream 读分块
// - 微信小程序: uni.request enableChunked + requestTask.onChunkReceived
// 后端以 text/event-stream 返回 "data: {json}\n\n",逐字/逐词推送 delta。

function parseBuffer(buf, onChunk) {
	let lines = buf.split('\n')
	const tail = lines.pop() // 可能是不完整的行,留到下个 chunk
	for (const line of lines) {
		if (!line.startsWith('data:')) continue
		const payload = line.slice(5).trim()
		if (!payload || payload === '[DONE]') continue
		try {
			onChunk(JSON.parse(payload))
		} catch { /* 忽略解析失败的行 */ }
	}
	return tail
}

// #ifdef H5
async function fetchStream(url, body, handlers) {
	const { onChunk, onDone, onError } = handlers
	try {
		const res = await fetch(url, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(body),
		})
		if (!res.ok) {
			let detail = ''
			try {
				detail = (await res.json()).detail || ''
			} catch { /* 非 JSON 响应体 */ }
			throw new Error('HTTP ' + res.status + (detail ? ': ' + detail : ''))
		}
		const reader = res.body.getReader()
		const decoder = new TextDecoder()
		let buf = ''
		while (true) {
			const { done, value } = await reader.read()
			if (done) break
			buf = parseBuffer(buf + decoder.decode(value, { stream: true }), onChunk)
		}
		if (onDone) onDone()
	} catch (e) {
		onError(e)
	}
}
// #endif

// #ifdef MP-WEIXIN
function mpStream(url, body, handlers) {
	const { onChunk, onDone, onError } = handlers
	const decoder = new TextDecoder('utf-8')
	let buf = ''
	const task = uni.request({
		url,
		method: 'POST',
		header: { 'Content-Type': 'application/json' },
		data: body,
		enableChunked: true,
		fail: (err) => onError(err),
		complete: () => { if (onDone) onDone() },
	})
	task.onChunkReceived((res) => {
		buf = parseBuffer(buf + decoder.decode(new Uint8Array(res.data), { stream: true }), onChunk)
	})
	return task
}
// #endif

// 统一入口:{ onChunk(delta) onDone() onError(err) }
export function streamJson(url, body, handlers) {
	// #ifdef H5
	return fetchStream(url, body, handlers)
	// #endif
	// #ifdef MP-WEIXIN
	return mpStream(url, body, handlers)
	// #endif
}
