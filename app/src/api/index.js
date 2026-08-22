import { request, uploadFile } from '../utils/request.js'
import { streamJson } from '../utils/stream.js'

export function listDocs() {
	return request('/docs')
}

export function deleteDoc(id) {
	return request('/docs/' + id, { method: 'DELETE' })
}

export function uploadDoc(filePath) {
	return uploadFile('/upload', filePath)
}

export function chatStream(docId, question, handlers) {
	streamJson('/chat', { doc_id: docId, question }, handlers)
}
