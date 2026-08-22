<template>
	<view class="page">
		<scroll-view
			class="msgs"
			scroll-y
			:scroll-into-view="scrollInto"
			:scroll-with-animation="true"
		>
			<view
				v-for="(m, i) in chatStore.messages"
				:id="'m' + i"
				:key="i"
				class="row"
				:class="m.role"
			>
				<view class="bubble">{{ m.content || (m.role === 'assistant' ? '…' : '') }}</view>
			</view>
		</scroll-view>

		<view class="inputbar">
			<input
				v-model="text"
				class="input"
				placeholder="基于文档提问…"
				confirm-type="send"
				@confirm="send"
			/>
			<button class="send" size="mini" :disabled="chatStore.streaming" @click="send">发送</button>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useChatStore } from '../../stores/chat.js'

const chatStore = useChatStore()
const docId = ref('')
const text = ref('')
const scrollInto = ref('')

onLoad((q) => {
	docId.value = q.docId
	if (q.name) uni.setNavigationBarTitle({ title: decodeURIComponent(q.name) })
})

function send() {
	const t = text.value.trim()
	if (!t || chatStore.streaming) return
	text.value = ''
	chatStore.send(docId.value, t)
	// 消息 push 后滚到底部
	setTimeout(() => {
		scrollInto.value = 'm' + (chatStore.messages.length - 1)
	}, 50)
}
</script>

<style>
.page {
	display: flex;
	flex-direction: column;
	height: 100vh;
}

.msgs {
	flex: 1;
	padding: 20rpx;
	box-sizing: border-box;
}

.row {
	display: flex;
	margin-bottom: 20rpx;
}

.row.user {
	justify-content: flex-end;
}

.row.assistant {
	justify-content: flex-start;
}

.bubble {
	max-width: 80%;
	padding: 16rpx 20rpx;
	border-radius: 12rpx;
	font-size: 28rpx;
	line-height: 1.5;
	white-space: pre-wrap;
	word-break: break-word;
}

.row.user .bubble {
	background: #dcf3e8;
	color: #333;
}

.row.assistant .bubble {
	background: #f2f2f2;
	color: #333;
}

.inputbar {
	display: flex;
	align-items: center;
	gap: 16rpx;
	padding: 16rpx 20rpx;
	border-top: 1rpx solid #eee;
}

.input {
	flex: 1;
	height: 64rpx;
	background: #f5f5f5;
	border-radius: 32rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
}
</style>
