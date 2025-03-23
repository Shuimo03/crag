<template>
  <div class="chat-container">
    <a-row :gutter="16">
      <!-- 侧边栏 - 对话列表 -->
      <a-col :span="6" class="sidebar">
        <div class="sidebar-header">
          <h2>对话列表</h2>
          <a-button type="primary" @click="createNewConversation">
            <template #icon><plus-outlined /></template>
            新对话
          </a-button>
        </div>
        
        <a-spin :spinning="loadingConversations">
          <a-list class="conversation-list">
            <a-list-item 
              v-for="conversation in conversations" 
              :key="conversation.id"
              :class="{ 'active-conversation': currentConversationId === conversation.id }"
              @click="selectConversation(conversation.id)"
            >
              <a-list-item-meta>
                <template #title>{{ conversation.title || '新对话' }}</template>
                <template #description>{{ formatDate(conversation.created_at) }}</template>
                <template #avatar>
                  <a-avatar><template #icon><message-outlined /></template></a-avatar>
                </template>
              </a-list-item-meta>
            </a-list-item>
            
            <div v-if="conversations.length === 0" class="empty-list">
              <a-empty description="暂无对话" />
            </div>
          </a-list>
        </a-spin>
      </a-col>
      
      <!-- 主要内容区 - 聊天界面 -->
      <a-col :span="18" class="main-content">
        <div class="chat-header">
          <div class="model-selector">
            <a-select
              v-model:value="selectedModelId"
              style="width: 200px"
              placeholder="选择模型"
              :options="models.map(model => ({ value: model.id, label: model.name }))"
              :disabled="!!currentConversationId"
            />
          </div>
        </div>
        
        <div class="messages-container" ref="messagesContainer">
          <a-spin :spinning="loadingMessages">
            <div v-if="messages.length === 0" class="empty-chat">
              <a-empty description="开始一个新对话">
                <template #description>
                  <p>选择一个模型并发送消息开始对话</p>
                </template>
              </a-empty>
            </div>
            
            <div v-else class="messages-list">
              <div 
                v-for="(message, index) in messages" 
                :key="index"
                :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
              >
                <div class="message-avatar">
                  <a-avatar :style="{ backgroundColor: message.role === 'user' ? '#1890ff' : '#52c41a' }">
                    {{ message.role === 'user' ? 'U' : 'A' }}
                  </a-avatar>
                </div>
                <div class="message-content">
                  <div class="message-text" v-html="formatMessage(message.content)"></div>
                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
              </div>
            </div>
          </a-spin>
        </div>
        
        <div class="input-container">
          <a-input-group compact>
            <a-textarea
              v-model:value="userInput"
              placeholder="输入消息..."
              :auto-size="{ minRows: 2, maxRows: 6 }"
              :disabled="!selectedModelId || isProcessing"
              @keydown.enter.prevent="sendMessage"
              class="message-input"
            />
            <a-button 
              type="primary" 
              :disabled="!userInput.trim() || !selectedModelId || isProcessing"
              @click="sendMessage"
              class="send-button"
            >
              <template #icon><send-outlined /></template>
              发送
            </a-button>
          </a-input-group>
          <div class="input-footer">
            <span class="hint">按 Enter 发送，Shift + Enter 换行</span>
            <a-spin v-if="isProcessing" size="small" />
          </div>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue';
import { PlusOutlined, MessageOutlined, SendOutlined } from '@ant-design/icons-vue';
import { modelApi } from '../services/api';
import { message } from 'ant-design-vue';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

// 类型定义
interface Model {
  id: string;
  name: string;
  description?: string;
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  conversation_id: string;
  timestamp: string;
}

// 状态
const models = ref<Model[]>([]);
const conversations = ref<Conversation[]>([]);
const messages = ref<Message[]>([]);
const selectedModelId = ref<string>('');
const currentConversationId = ref<string | null>(null);
const userInput = ref<string>('');
const isProcessing = ref<boolean>(false);
const loadingModels = ref<boolean>(false);
const loadingConversations = ref<boolean>(false);
const loadingMessages = ref<boolean>(false);
const messagesContainer = ref<HTMLElement | null>(null);

// 获取模型列表
const fetchModels = async () => {
  try {
    loadingModels.value = true;
    const response = await modelApi.getModels();
    models.value = response.data;
    
    // 如果有模型，默认选择第一个
    if (models.value.length > 0) {
      selectedModelId.value = models.value[0].id;
    }
  } catch (error) {
    console.error('获取模型列表失败', error);
    message.error('获取模型列表失败');
  } finally {
    loadingModels.value = false;
  }
};

// 获取对话列表
const fetchConversations = async () => {
  try {
    loadingConversations.value = true;
    const response = await modelApi.getConversations();
    conversations.value = response.data;
  } catch (error) {
    console.error('获取对话列表失败', error);
    message.error('获取对话列表失败');
  } finally {
    loadingConversations.value = false;
  }
};

// 获取特定对话的消息
const fetchMessages = async (conversationId: string) => {
  try {
    loadingMessages.value = true;
    const response = await modelApi.getConversationMessages(conversationId);
    messages.value = response.data;
    
    // 滚动到底部
    await nextTick();
    scrollToBottom();
  } catch (error) {
    console.error('获取消息失败', error);
    message.error('获取消息失败');
  } finally {
    loadingMessages.value = false;
  }
};

// 选择对话
const selectConversation = (conversationId: string) => {
  currentConversationId.value = conversationId;
  fetchMessages(conversationId);
  
  // 找到对应的对话，获取其使用的模型
  const conversation = conversations.value.find(c => c.id === conversationId);
  if (conversation && conversation.model_id) {
    selectedModelId.value = conversation.model_id;
  }
};

// 创建新对话
const createNewConversation = () => {
  // 清空当前对话和消息
  currentConversationId.value = null;
  messages.value = [];
  userInput.value = '';
  
  // 允许用户选择模型
  if (models.value.length > 0 && !selectedModelId.value) {
    selectedModelId.value = models.value[0].id;
  }
};

// 发送消息
const sendMessage = async () => {
  const messageText = userInput.value.trim();
  if (!messageText || !selectedModelId.value) return;
  
  try {
    isProcessing.value = true;
    
    // 添加用户消息到列表
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      conversation_id: currentConversationId.value || '',
      timestamp: new Date().toISOString()
    };
    
    messages.value.push(userMessage);
    userInput.value = '';
    
    // 滚动到底部
    await nextTick();
    scrollToBottom();
    
    // 发送消息到后端
    const response = await modelApi.sendMessage(
      selectedModelId.value,
      messageText,
      currentConversationId.value || undefined
    );
    
    // 如果是新对话，更新对话ID并获取对话列表
    if (!currentConversationId.value && response.data.conversation_id) {
      currentConversationId.value = response.data.conversation_id;
      fetchConversations();
    }
    
    // 添加助手回复到列表
    const assistantMessage: Message = {
      id: response.data.id || Date.now().toString() + 1,
      role: 'assistant',
      content: response.data.content || response.data.message,
      conversation_id: currentConversationId.value || response.data.conversation_id,
      timestamp: new Date().toISOString()
    };
    
    messages.value.push(assistantMessage);
    
    // 滚动到底部
    await nextTick();
    scrollToBottom();
  } catch (error) {
    console.error('发送消息失败', error);
    message.error('发送消息失败');
  } finally {
    isProcessing.value = false;
  }
};

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString();
};

// 格式化消息内容（支持 Markdown）
const formatMessage = (content: string) => {
  // 使用 marked 将 Markdown 转换为 HTML
  const html = marked(content);
  // 使用 DOMPurify 清理 HTML，防止 XSS 攻击
  return DOMPurify.sanitize(html);
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 生命周期钩子
onMounted(() => {
  fetchModels();
  fetchConversations();
});
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
}

.sidebar {
  border-right: 1px solid #f0f0f0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.conversation-list {
  overflow-y: auto;
  flex: 1;
}

.active-conversation {
  background-color: #e6f7ff;
}

.main-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.empty-chat {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.messages-list {
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 12px;
}

.message-content {
  max-width: 70%;
  padding: 12px;
  border-radius: 8px;
}

.user-message .message-content {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
}

.assistant-message .message-content {
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
}

.message-text {
  word-break: break-word;
}

.message-text :deep(pre) {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
}

.message-text :deep(code) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.input-container {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.message-input {
  width: calc(100% - 100px);
}

.send-button {
  width: 100px;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.hint {
  font-size: 12px;
  color: #999;
}

.empty-list {
  padding: 24px;
  text-align: center;
}
</style> 