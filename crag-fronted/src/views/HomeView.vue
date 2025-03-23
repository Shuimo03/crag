<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { UserOutlined, ApiOutlined, ThunderboltOutlined } from '@ant-design/icons-vue';
import { useRouter } from 'vue-router';

// 用户类型定义
interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

// 用户数据，实际应用中应该从 API 获取
const user = ref<User | null>(null);

const router = useRouter();

onMounted(() => {
  // 从 localStorage 获取用户信息
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      user.value = JSON.parse(userStr);
    } catch (e) {
      console.error('解析用户信息失败', e);
    }
  }
});
</script>

<template>
  <div class="home-container">
    <a-row :gutter="[24, 24]">
      <a-col :xs="24" :md="24">
        <a-card title="欢迎使用 Crag 平台" bordered>
          <template #extra>
            <a-tag color="blue">Beta</a-tag>
          </template>
          
          <div class="welcome-message">
            <h2>{{ user ? `欢迎回来，${user.name}` : '欢迎访问 Crag 平台' }}</h2>
            <p>这是一个基于 Vue 3、TypeScript 和 Ant Design Vue 构建的前端应用。</p>
          </div>
          
          <a-divider />
          
          <a-alert
            message="快速开始"
            description="您已成功登录系统，现在可以开始使用平台提供的各项功能。"
            type="success"
            show-icon
          />
          
          <div class="feature-list">
            <h3>平台特性</h3>
            <a-row :gutter="[16, 16]">
              <a-col :span="8">
                <a-card hoverable>
                  <template #cover>
                    <div class="feature-icon">
                      <a-avatar shape="square" :size="64" style="background-color: #1890ff">
                        <template #icon><user-outlined /></template>
                      </a-avatar>
                    </div>
                  </template>
                  <a-card-meta title="用户认证">
                    <template #description>支持 GitHub 账号认证</template>
                  </a-card-meta>
                </a-card>
              </a-col>
              
              <a-col :span="8">
                <a-card hoverable>
                  <template #cover>
                    <div class="feature-icon">
                      <a-avatar shape="square" :size="64" style="background-color: #52c41a">
                        <template #icon><api-outlined /></template>
                      </a-avatar>
                    </div>
                  </template>
                  <a-card-meta title="API 集成">
                    <template #description>与后端 API 无缝集成</template>
                  </a-card-meta>
                </a-card>
              </a-col>
              
              <a-col :span="8">
                <a-card hoverable>
                  <template #cover>
                    <div class="feature-icon">
                      <a-avatar shape="square" :size="64" style="background-color: #722ed1">
                        <template #icon><thunderbolt-outlined /></template>
                      </a-avatar>
                    </div>
                  </template>
                  <a-card-meta title="高性能">
                    <template #description>基于 Vue 3 的高性能架构</template>
                  </a-card-meta>
                </a-card>
              </a-col>
            </a-row>
          </div>
          
          <a-divider />
          
          <div class="action-buttons">
            <a-button type="primary" size="large" @click="router.push('/chat')">
              开始聊天
            </a-button>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
.home-container {
  width: 100%;
}

.welcome-message {
  margin-bottom: 24px;
  text-align: center;
}

.feature-list {
  margin-top: 24px;
}

.feature-icon {
  display: flex;
  justify-content: center;
  padding: 24px 0;
  background-color: #fafafa;
}

.action-buttons {
  margin-top: 24px;
  text-align: center;
}
</style>
