<template>
  <div class="login-container">
    <div class="login-box">
      <a-card :bordered="false" class="login-card">
        <div class="login-header">
          <div class="logo">
            <a-typography-title :level="2">Crag 平台</a-typography-title>
          </div>
          <a-typography-paragraph class="subtitle">连接全球领先的大语言模型</a-typography-paragraph>
        </div>
        
        <div class="login-content">
          <a-typography-title :level="4">账号登录</a-typography-title>
          <a-typography-paragraph class="description">
            使用您的 GitHub 账号快速登录，体验 Crag
          </a-typography-paragraph>
          
          <a-button 
            type="primary" 
            block 
            @click="handleGithubLogin"
            size="large"
            class="github-login-btn"
          >
            <template #icon>
              <GithubOutlined />
            </template>
            使用 GitHub 登录
          </a-button>
          
          <div v-if="error" class="login-error">
            <a-alert type="error" :message="error" show-icon />
          </div>
        </div>
        
        <div class="login-footer">
          <a-typography-paragraph type="secondary" style="text-align: center">
            登录即表示您同意我们的 <a href="#">服务条款</a> 和 <a href="#">隐私政策</a> <!-- 添加链接 -->
          </a-typography-paragraph>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { GithubOutlined } from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
const error = ref('');

// API 基础 URL
const BASE_API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';

/**
 * 处理GitHub登录请求
 */
const handleGithubLogin = () => {
  try {
    // 从路由查询参数获取redirect_uri，默认为前端路由/repos
    // 注意：使用前端路由路径，而不是API路径
    const redirectParam = route.query.redirect_uri as string;
    const redirectUri = encodeURIComponent(redirectParam || '/repos');
    
    // 直接重定向到后端提供的 GitHub 登录接口
    // 这个接口会将用户重定向到 GitHub 授权页面
    window.location.href = `${BASE_API_URL}/api/auth/github/login?redirect_uri=${redirectUri}`;
  } catch (e) {
    console.error('GitHub 登录失败', e);
    error.value = '登录请求失败，请稍后再试';
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(to right, #f0f2f5, #e6f7ff);
  padding: 24px;
}

.login-box {
  width: 100%;
  max-width: 420px;
}

.login-card {
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  margin-bottom: 8px;
}

.subtitle {
  color: rgba(0, 0, 0, 0.45);
  font-size: 16px;
  margin-bottom: 0;
}

.login-content {
  margin-bottom: 24px;
}

.description {
  margin-bottom: 24px;
  color: rgba(0, 0, 0, 0.65);
}

.github-login-btn {
  height: 44px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-error {
  margin-top: 16px;
}

.login-footer {
  margin-top: 24px;
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}
</style> 