<template>
	<view class="page">
		<view class="toolbar">
			<button class="btn" size="mini" @click="chooseFile">上传 PDF</button>
			<text v-if="docsStore.loading" class="hint">加载中…</text>
		</view>

		<view v-if="!docsStore.loading && docsStore.docs.length === 0" class="empty">
			<text>还没有文档,点「上传 PDF」开始</text>
		</view>

		<view
			v-for="doc in docsStore.docs"
			:key="doc.id"
			class="doc-card"
			@click="openChat(doc)"
		>
			<view class="doc-main">
				<view class="doc-name">{{ doc.name }}</view>
				<view class="doc-meta">{{ doc.chunk_count }} 个分块 · {{ doc.created_at }}</view>
			</view>
			<view class="doc-del" @click.stop="removeDoc(doc.id)">删除</view>
		</view>
	</view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { useDocsStore } from '../../stores/docs.js'

const docsStore = useDocsStore()

onShow(() => {
	docsStore.fetchDocs()
})

function chooseFile() {
	const onChoose = (res) => upload(res.tempFiles[0].path)
	// #ifdef H5
	uni.chooseFile({ count: 1, extension: ['pdf', 'txt', 'md'], success: onChoose })
	// #endif
	// #ifdef MP-WEIXIN
	uni.chooseMessageFile({ count: 1, extension: ['pdf', 'txt', 'md'], success: onChoose })
	// #endif
}

async function upload(path) {
	uni.showLoading({ title: '解析入库中…' })
	try {
		await docsStore.addDoc(path)
		uni.showToast({ title: '入库成功', icon: 'success' })
	} catch (e) {
		uni.showToast({ title: e.message || '上传失败', icon: 'none' })
	} finally {
		uni.hideLoading()
	}
}

function removeDoc(id) {
	uni.showModal({
		title: '确认删除?',
		success: async (r) => {
			if (r.confirm) await docsStore.removeDoc(id)
		},
	})
}

function openChat(doc) {
	uni.navigateTo({
		url: '/pages/chat/chat?docId=' + doc.id + '&name=' + encodeURIComponent(doc.name),
	})
}
</script>

<style>
.page {
	padding: 20rpx;
}

.toolbar {
	display: flex;
	align-items: center;
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.hint {
	color: #999;
	font-size: 24rpx;
}

.empty {
	margin-top: 200rpx;
	text-align: center;
	color: #bbb;
	font-size: 28rpx;
}

.doc-card {
	display: flex;
	align-items: center;
	background: #fff;
	border-radius: 12rpx;
	padding: 24rpx;
	margin-bottom: 16rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.doc-main {
	flex: 1;
	min-width: 0;
}

.doc-name {
	font-size: 30rpx;
	color: #333;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.doc-meta {
	font-size: 24rpx;
	color: #999;
	margin-top: 6rpx;
}

.doc-del {
	font-size: 24rpx;
	color: #e64340;
	padding: 8rpx 16rpx;
}
</style>
