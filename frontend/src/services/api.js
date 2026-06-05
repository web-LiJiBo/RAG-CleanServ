import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000
})

// 知识库接口
export const knowledgeApi = {
  uploadFiles(files) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    return api.post('/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  rebuildVectorStore() {
    return api.post('/knowledge/rebuild')
  },
  getStats() {
    return api.get('/knowledge/stats')
  }
}

// 聊天接口
export const chatApi = {
  chat(question, userId = 'user_001', threadId = null) {
    return api.post('/chat/chat', { question, user_id: userId, thread_id: threadId })
  }
}

export default api
