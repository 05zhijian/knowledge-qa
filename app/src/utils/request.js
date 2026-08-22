import { BASE_URL } from './config.js'

export function request(path, options = {}) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: BASE_URL + path,
			method: options.method || 'GET',
			data: options.data,
			header: {
				'Content-Type': 'application/json',
				...(options.header || {}),
			},
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data)
				} else {
					reject(new Error((res.data && res.data.detail) || ('HTTP ' + res.statusCode)))
				}
			},
			fail: (err) => reject(err),
		})
	})
}

export function uploadFile(path, filePath, name = 'file') {
	return new Promise((resolve, reject) => {
		uni.uploadFile({
			url: BASE_URL + path,
			filePath,
			name,
			success: (res) => {
				if (res.statusCode < 200 || res.statusCode >= 300) {
					reject(new Error((res.data && res.data.detail) || ('HTTP ' + res.statusCode)))
					return
				}
				try {
					resolve(JSON.parse(res.data))
				} catch {
					resolve(res.data)
				}
			},
			fail: (err) => reject(err),
		})
	})
}
