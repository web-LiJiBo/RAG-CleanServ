<template>
  <div class="knowledge-container">
    <el-card>
      <template #header>
        <span>文档上传知识库</span>
      </template>

      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :multiple="true"
        :auto-upload="false"
        :limit="20"
        accept=".txt"
        v-model:file-list="fileList"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 .txt 格式文件，支持多文件上传</div>
        </template>
      </el-upload>

      <div class="action-buttons">
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          上传文件
        </el-button>
        <el-button type="success" @click="handleRebuild" :loading="rebuilding">
          重建向量库
        </el-button>
        <el-button @click="handleClear">清空列表</el-button>
      </div>

      <el-divider />

      <div class="stats-section">
        <h3>知识库状态</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文档数量">{{ stats.total_documents }}</el-descriptions-item>
          <el-descriptions-item label="切片数量">{{ stats.total_chunks }}</el-descriptions-item>
          <el-descriptions-item label="向量库状态">
            <el-tag :type="stats.vector_store_ready ? 'success' : 'danger'">
              {{ stats.vector_store_ready ? '就绪' : '未就绪' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <el-card v-if="uploadResult" class="result-card">
      <el-alert :title="uploadResult.message" :type="uploadResult.success ? 'success' : 'error'" show-icon />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { knowledgeApi } from '../services/api.js'

const uploadRef = ref(null)
const fileList = ref([])
const uploading = ref(false)
const rebuilding = ref(false)
const uploadResult = ref(null)
const stats = ref({
  total_documents: 0,
  total_chunks: 0,
  vector_store_ready: false
})

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  uploadResult.value = null

  try {
    const files = fileList.value.map(f => f.raw)
    const res = await knowledgeApi.uploadFiles(files)
    uploadResult.value = res.data
    if (res.data.success) {
      ElMessage.success(res.data.message)
      fileList.value = []
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (err) {
    ElMessage.error('上传失败: ' + (err.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

const handleRebuild = async () => {
  rebuilding.value = true
  try {
    const res = await knowledgeApi.rebuildVectorStore()
    uploadResult.value = res.data
    if (res.data.success) {
      ElMessage.success('向量库重建成功')
      await fetchStats()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (err) {
    ElMessage.error('重建失败: ' + (err.message || '未知错误'))
  } finally {
    rebuilding.value = false
  }
}

const handleClear = () => {
  fileList.value = []
  uploadResult.value = null
}

const fetchStats = async () => {
  try {
    const res = await knowledgeApi.getStats()
    stats.value = res.data
  } catch (err) {
    console.error('获取统计失败', err)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.knowledge-container {
  max-width: 800px;
  margin: 0 auto;
}
.upload-area {
  margin-bottom: 20px;
}
.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
.stats-section {
  margin-top: 20px;
}
.stats-section h3 {
  margin-bottom: 10px;
}
.result-card {
  margin-top: 20px;
}
</style>
