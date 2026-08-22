import { defineStore } from 'pinia'
import { listDocs, uploadDoc, deleteDoc } from '../api/index.js'

export const useDocsStore = defineStore('docs', {
	state: () => ({
		docs: [],
		loading: false,
	}),
	actions: {
		async fetchDocs() {
			this.loading = true
			try {
				this.docs = await listDocs()
			} finally {
				this.loading = false
			}
		},
		async addDoc(filePath) {
			const doc = await uploadDoc(filePath)
			this.docs.unshift(doc)
			return doc
		},
		async removeDoc(id) {
			await deleteDoc(id)
			this.docs = this.docs.filter((d) => d.id !== id)
		},
	},
})
