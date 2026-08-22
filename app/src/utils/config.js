// 后端地址
// H5 走 vite 代理(见 vite.config.js),避免跨域;小程序/App 直连完整地址
let base = 'http://127.0.0.1:8000/api'

// #ifdef H5
base = '/api'
// #endif

export const BASE_URL = base
