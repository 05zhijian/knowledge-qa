import { defineStore } from 'pinia'
import { chatStream } from '../api/index.js'

export const useChatStore = defineStore('chat', {
	state: () => ({
		messages: [],
		streaming: false,
	}),
	actions: {
		async send(docId, text) {
			this.messages.push({ role: 'user', content: text })
			this.messages.push({ role: 'assistant', content: '', sources: [] })
			this.streaming = true
			const last = this.messages[this.messages.length - 1]
			try {
				await chatStream(docId, text, {
					onChunk: (part) => {
						if (part.sources) {
							last.sources = part.sources
						} else {
							last.content += part.delta || ''
						}
					},
					onError: (err) => {
						last.content += '\n[请求失败] ' + (err.message || err.errMsg || '网络错误')
					},
				})
			} finally {
				this.streaming = false
			}
		},
		clear() {
			this.messages = []
		},
	},
})
