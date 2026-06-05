<template>
  <div class="chat-container">
    <el-card class="chat-card">
      <template #header>
        <div class="chat-header">
          <span>智能客服对话</span>
          <el-button size="small" @click="handleClear">清空对话</el-button>
        </div>
      </template>

      <div class="chat-messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="empty-hint">
          您好！我是扫地机器人智能客服，请问有什么可以帮您？
        </div>
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-item', msg.role === 'user' ? 'user-message' : 'assistant-message']"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>
        <div v-if="loading" class="message-item assistant-message">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text loading">正在思考中...</div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="请输入您的问题..."
          @keydown.enter.ctrl="handleSend"
          :disabled="loading"
        />
        <el-button type="primary" @click="handleSend" :loading="loading" :disabled="!inputText.trim()">
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { chatApi } from '../services/api.js'

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const messagesRef = ref(null)
const threadId = ref(null)

const formatTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const handleSend = async () => {
  const question = inputText.value.trim()
  if (!question || loading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: question,
    time: formatTime()
  })
  inputText.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const res = await chatApi.chat(question, 'user_001', threadId.value)
    const data = res.data

    if (threadId.value === null) {
      threadId.value = data.thread_id
    }

    messages.value.push({
      role: 'assistant',
      content: data.answer,
      time: formatTime()
    })
  } catch (err) {
    ElMessage.error('发送失败: ' + (err.message || '未知错误'))
    // 移除最后一条用户消息
    messages.value.pop()
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const handleClear = () => {
  messages.value = []
  threadId.value = null
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}
.chat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  min-height: 300px;
  max-height: calc(100vh - 280px);
}
.empty-hint {
  text-align: center;
  color: #999;
  padding: 40px 20px;
}
.message-item {
  display: flex;
  margin-bottom: 16px;
}
.user-message {
  flex-direction: row-reverse;
}
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.message-content {
  max-width: 70%;
  margin: 0 10px;
}
.message-text {
  padding: 10px 14px;
  border-radius: 8px;
  line-height: 1.5;
  word-break: break-word;
}
.user-message .message-text {
  background-color: #409EFF;
  color: white;
}
.assistant-message .message-text {
  background-color: #f5f5f5;
  color: #333;
}
.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}
.user-message .message-time {
  text-align: left;
}
.loading {
  color: #999;
  font-style: italic;
}
.chat-input {
  display: flex;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}
.chat-input .el-input {
  flex: 1;
}
</style>
