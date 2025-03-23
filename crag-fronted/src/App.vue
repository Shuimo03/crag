<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { RouterView, useRouter, useRoute } from 'vue-router';
import { DownOutlined } from '@ant-design/icons-vue';
import { authApi } from './services/api';
import { message } from 'ant-design-vue';

// 用户类型定义
interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

const router = useRouter();
const route = useRoute();
const currentUser = ref<User | null>(null);
const loading = ref(true);

// 计算用户是否已登录
const isLoggedIn = computed(() => {
  return !!localStorage.getItem('token');
});

// 获取当前用户信息
const fetchCurrentUser = async () => {
  if (isLoggedIn.value) {
    try {
      loading.value = true;
      
      // 尝试从本地存储获取用户信息
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          currentUser.value = JSON.parse(userStr);
          loading.value = false;
          return;
        } catch (e) {
          console.error('解析用户信息失败', e);
        }
      }
      
      // 如果本地没有用户信息，则从 API 获取
      const response = await authApi.getCurrentUser();
      currentUser.value = response.data;
      
      // 存储用户信息到本地
      localStorage.setItem('user', JSON.stringify(response.data));
    } catch (error) {
      console.error('获取用户信息失败', error);
      message.error('获取用户信息失败');
    } finally {
      loading.value = false;
    }
  } else {
    loading.value = false;
  }
};

// 处理登出
const handleLogout = async () => {
  try {
    await authApi.logout();
  } catch (error) {
    console.error('登出失败', error);
  } finally {
    // 清除本地存储的认证信息
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    currentUser.value = null;
    
    // 显示登出成功消息
    message.success('已成功登出');
    
    // 重定向到登录页
    router.push('/login');
  }
};

// 监听路由变化，如果从登录页面跳转到其他页面，刷新用户信息
watch(
  () => route.path,
  (newPath, oldPath) => {
    if (oldPath === '/auth/github/callback' && newPath === '/') {
      fetchCurrentUser();
    }
  }
);

onMounted(() => {
  fetchCurrentUser();
});
</script>

<template>
  <a-config-provider>
    <!-- 登录路由不使用应用布局 -->
    <template v-if="$route.meta.guest">
      <RouterView />
    </template>
    
    <!-- 应用主布局 -->
    <a-layout v-else class="app-layout">
      <!-- 顶部导航 -->
      <a-layout-header class="app-header">
        <div class="logo">Crag Platform</div>
        <a-menu
          theme="dark"
          mode="horizontal"
          :selectedKeys="[$route.name]"
          :style="{ lineHeight: '64px', flex: 1 }"
        >
          <a-menu-item key="chat" @click="router.push('/chat')">聊天</a-menu-item>
          <a-menu-item key="repos" @click="router.push('/repos')">仓库</a-menu-item>
          <a-menu-item key="about" @click="router.push('/about')">关于</a-menu-item>
        </a-menu>
        
        <div class="header-right">
          <template v-if="isLoggedIn">
            <a-avatar :size="32" style="background-color: #87d068; margin-right: 12px">
              {{ currentUser?.name?.charAt(0) || 'U' }}
            </a-avatar>
            <span class="username">{{ currentUser?.name || '用户' }}</span>
            <a-button type="primary" danger @click="handleLogout" class="logout-btn">登出</a-button>
          </template>
          <a-button v-else type="primary" @click="router.push('/login')">登录</a-button>
        </div>
      </a-layout-header>
      
      <!-- 内容区域 -->
      <a-layout-content class="app-content">
        <a-spin :spinning="loading" tip="加载中..." size="large">
          <div class="content-container">
            <RouterView />
          </div>
        </a-spin>
      </a-layout-content>
      
      <!-- 页脚 -->
      <a-layout-footer class="app-footer">
        Crag Platform ©{{ new Date().getFullYear() }} Created with Vue3 & Ant Design Vue
      </a-layout-footer>
    </a-layout>
  </a-config-provider>
</template>

<style>
#app {
  width: 100%;
  height: 100%;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

.app-layout {
  min-height: 100vh;
  width: 100%;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 0 24px;
  width: 100%;
}

.logo {
  color: white;
  font-size: 18px;
  font-weight: bold;
  margin-right: 24px;
}

.header-right {
  display: flex;
  align-items: center;
}

.username {
  color: white;
  margin-right: 16px;
}

.logout-btn {
  margin-left: 8px;
}

.app-content {
  padding: 24px;
  background: #f0f2f5;
  width: 100%;
}

.content-container {
  padding: 24px;
  background: #fff;
  min-height: 360px;
  border-radius: 2px;
  width: 100%;
}

.app-footer {
  text-align: center;
  width: 100%;
}
</style>
