<template>
  <div class="chat-container">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h2 v-if="!sidebarCollapsed">AI 智能客服</h2>
        <el-button link @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><Fold /></el-icon>
        </el-button>
      </div>

      <div class="new-chat-btn">
        <el-button type="primary" @click="handleNewChat" :disabled="!sidebarCollapsed">
          <el-icon><Plus /></el-icon>
          <span v-if="!sidebarCollapsed">新建会话</span>
        </el-button>
      </div>

      <div class="session-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: session.id === currentSessionId }"
          @click="handleSelectSession(session.id)"
        >
          <el-icon><ChatLineSquare /></el-icon>
          <span class="session-name" v-if="!sidebarCollapsed">{{ session.name }}</span>
          <el-button
            link
            class="delete-btn"
            @click.stop="handleDeleteSession(session.id)"
            v-if="!sidebarCollapsed"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>

      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <el-button link @click="showKnowledgePanel = true">
          <el-icon><Document /></el-icon>
          知识库管理
        </el-button>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="main-content">
      <div class="chat-header">
        <el-button link @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><Expand /></el-icon>
        </el-button>
        <span>AI 智能客服</span>
      </div>

      <div class="messages-container">
        <div v-if="messages.length === 0" class="welcome-message">
          <el-empty description="发送消息开始与 AI 对话" />
        </div>
        <div v-else class="messages">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar v-if="message.role === 'user'">
                <el-icon><User /></el-icon>
              </el-avatar>
              <el-avatar v-else color="#409EFF">
                <el-icon><Cpu /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="renderMarkdown(message.content)"></div>
              <div class="message-sources" v-if="message.sources && message.sources.length > 0">
                <div class="sources-title">参考文档:</div>
                <el-tag
                  v-for="(source, index) in message.sources"
                  :key="index"
                  size="small"
                  type="info"
                >
                  文档 {{ index + 1 }} (相关度：{{ Math.round(source.score * 100) }}%)
                </el-tag>
              </div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="inputMessage"
          placeholder="输入消息..."
          :disabled="isLoading"
          @keydown.enter.exact="handleSendMessage"
          :rows="2"
          type="textarea"
          resize="none"
        />
        <el-button
          type="primary"
          @click="handleSendMessage"
          :loading="isLoading"
          :disabled="!inputMessage.trim()"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>

    <!-- 知识库面板 -->
    <el-drawer
      v-model="showKnowledgePanel"
      title="知识库管理"
      size="400px"
    >
      <div class="knowledge-panel">
        <el-upload
          ref="uploadRef"
          :auto-upload="true"
          :on-change="handleFileUpload"
          :disabled="isUploading"
          :show-file-list="false"
          accept=".txt,.pdf,.doc,.docx,.md"
        >
          <el-button type="primary" :loading="isUploading">
            <el-icon><Upload /></el-icon>
            上传文档
          </el-button>
        </el-upload>

        <el-divider>文档列表</el-divider>

        <div class="document-list">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="document-item"
          >
            <div class="doc-info">
              <el-icon><Document /></el-icon>
              <span class="doc-name">{{ doc.filename }}</span>
              <el-tag size="small" :type="doc.status === 'completed' ? 'success' : 'warning'">
                {{ doc.status === 'completed' ? '已完成' : '处理中' }}
              </el-tag>
            </div>
            <el-button link type="danger" @click="handleDeleteDocument(doc.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-empty v-if="documents.length === 0" description="暂无文档" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import markdownIt from 'markdown-it'
import { useChatStore, useDocumentStore } from '@/stores'
import { storeToRefs } from 'pinia'

const md = markdownIt()

const chatStore = useChatStore()
const documentStore = useDocumentStore()

const { messages, sessions, currentSessionId, isLoading } = storeToRefs(chatStore)
const { documents, isUploading } = storeToRefs(documentStore)

const sidebarCollapsed = ref(false)
const showKnowledgePanel = ref(false)
const inputMessage = ref('')

const renderMarkdown = (content: string) => {
  return md.render(content)
}

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const message = inputMessage.value.trim()
  inputMessage.value = ''

  try {
    await chatStore.sendMessage(message)
  } catch (error) {
    ElMessage.error('发送失败，请稍后重试')
  }
}

const handleNewChat = async () => {
  try {
    await chatStore.createNewSession('新会话')
    ElMessage.success('已创建新会话')
  } catch (error) {
    ElMessage.error('创建会话失败')
  }
}

const handleSelectSession = async (sessionId: string) => {
  await chatStore.selectSession(sessionId)
}

const handleDeleteSession = async (sessionId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该会话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await chatStore.deleteSessionById(sessionId)
    ElMessage.success('已删除会话')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleFileUpload = async (file: any) => {
  try {
    await documentStore.uploadDocument(file.raw)
    ElMessage.success('文档上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const handleDeleteDocument = async (docId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await documentStore.deleteDocumentById(docId)
    ElMessage.success('已删除文档')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  chatStore.loadSessions()
  documentStore.loadDocuments()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 250px;
  background: #f5f5f5;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
}

.sidebar-header h2 {
  font-size: 18px;
  color: #333;
}

.new-chat-btn {
  padding: 15px;
}

.new-chat-btn .el-button {
  width: 100%;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 5px;
  transition: background 0.2s;
}

.session-item:hover {
  background: #e8e8e8;
}

.session-item.active {
  background: #e6f7ff;
  color: #409EFF;
}

.session-name {
  flex: 1;
  margin-left: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #e0e0e0;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.chat-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-header span {
  font-size: 18px;
  font-weight: 500;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-message {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 15px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-content {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 12px;
}

.message.user .message-content {
  background: #409EFF;
  color: #fff;
}

.message-text {
  line-height: 1.6;
}

.message-text :deep(p) {
  margin-bottom: 10px;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-sources {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(0,0,0,0.1);
}

.message.user .message-sources {
  border-top-color: rgba(255,255,255,0.3);
}

.sources-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.message.user .sources-title {
  color: rgba(255,255,255,0.8);
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  text-align: right;
}

.message.user .message-time {
  color: rgba(255,255,255,0.8);
}

.input-area {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 10px;
}

.input-area .el-input {
  flex: 1;
}

.input-area .el-button {
  width: 100px;
}

.knowledge-panel {
  padding: 10px;
}

.document-list {
  max-height: 500px;
  overflow-y: auto;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.doc-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
