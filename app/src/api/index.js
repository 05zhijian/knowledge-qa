import { request, uploadFile } from '../utils/request.js'
import { streamJson } from '../utils/stream.js'
import { BASE_URL } from '../utils/config.js'

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
	streamJson(BASE_URL + '/chat', { doc_id: docId, question }, handlers)
}
