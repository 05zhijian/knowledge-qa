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
				<view class="col">
					<view class="bubble">{{ m.content || (m.role === 'assistant' ? '…' : '') }}</view>
					<view
						v-if="m.role === 'assistant' && m.sources && m.sources.length"
						class="sources"
						@click="toggle(i)"
					>
						<view class="sources-title">
							来源 {{ m.sources.length }} 条{{ expanded.includes(i) ? ' ▾' : ' ▸' }}
						</view>
						<view v-if="expanded.includes(i)">
							<view v-for="(src, si) in m.sources" :key="si" class="src-item">
								<view class="src-name">{{ src.doc_name }} · 相关度 {{ src.score }}</view>
								<view class="src-text">{{ src.text }}</view>
							</view>
						</view>
					</view>
				</view>
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
const expanded = ref([])

onLoad((q) => {
	docId.value = q.docId
	if (q.name) uni.setNavigationBarTitle({ title: decodeURIComponent(q.name) })
})

function toggle(i) {
	if (expanded.value.includes(i)) {
		expanded.value = expanded.value.filter((x) => x !== i)
	} else {
		expanded.value = [...expanded.value, i]
	}
}

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

.col {
	display: flex;
	flex-direction: column;
	max-width: 80%;
}

.row.user .col {
	align-items: flex-end;
}

.row.assistant .col {
	align-items: flex-start;
}

.bubble {
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

.sources {
	margin-top: 12rpx;
	padding: 12rpx 16rpx;
	background: #fff;
	border: 1rpx solid #eee;
	border-radius: 10rpx;
	width: 100%;
	box-sizing: border-box;
}

.sources-title {
	font-size: 24rpx;
	color: #2f9e6e;
}

.src-item {
	margin-top: 10rpx;
}

.src-name {
	font-size: 22rpx;
	color: #999;
}

.src-text {
	font-size: 24rpx;
	color: #666;
	margin-top: 4rpx;
	display: -webkit-box;
	-webkit-box-orient: vertical;
	-webkit-line-clamp: 3;
	overflow: hidden;
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
