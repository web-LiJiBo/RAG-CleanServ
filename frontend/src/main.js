import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import KnowledgeUpload from './views/KnowledgeUpload.vue'
import ChatPage from './views/ChatPage.vue'

const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/knowledge', name: 'Knowledge', component: KnowledgeUpload },
  { path: '/chat', name: 'Chat', component: ChatPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
