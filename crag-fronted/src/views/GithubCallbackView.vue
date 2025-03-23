<template>
  <div class="callback-container">
    <a-spin :spinning="loading" tip="正在处理认证，请稍候...">
      <div v-if="!success && !error" class="content">
        <p>GitHub 认证处理中...</p>
      </div>
      
      <div v-if="success" class="success-content">
        <a-result
          status="success"
          title="登录成功！"
          sub-title="您已成功通过 GitHub 账号登录系统"
        >
          <template #icon>
            <a-avatar :size="64" style="background-color: #52c41a">
              {{ userName.charAt(0) || 'U' }}
            </a-avatar>
          </template>
          <template #extra>
            <div class="user-info">
              <h3>欢迎回来，{{ userName }}</h3>
              <p>您将在 {{ countdown }} 秒后自动跳转</p>
            </div>
            <a-button type="primary" @click="goToRepos">
              立即前往
            </a-button>
          </template>
        </a-result>
      </div>
    </a-spin>
    
    <a-alert v-if="error" type="error" :message="error" show-icon style="margin-top: 20px" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const error = ref('');
const success = ref(false);
const loading = ref(true);
const userName = ref('');
const countdown = ref(3);
let timer: number | null = null;

/**
 * 处理 GitHub OAuth 回调
 */
const handleGithubCallback = async () => {
  try {
    // 从 URL 获取令牌和用户信息
    const token = route.query.token as string;
    const userInfo = route.query.user_info as string;
    // 获取重定向URI，默认为前端路由/repos
    const redirectUri = route.query.redirect_uri as string || '/repos';
    
    if (!token) {
      error.value = '未收到有效的认证令牌，请重试';
      loading.value = false;
      return;
    }
    
    // 存储令牌
    localStorage.setItem('token', token);
    
    // 存储重定向URI
    localStorage.setItem('redirectAfterLogin', redirectUri);
    
    // 如果有用户信息，也存储它
    if (userInfo) {
      try {
        const user = JSON.parse(decodeURIComponent(userInfo));
        localStorage.setItem('user', JSON.stringify(user));
        userName.value = user.name || user.login || '用户';
      } catch (e) {
        console.error('解析用户信息失败', e);
        userName.value = '用户';
      }
    } else {
      userName.value = '用户';
    }
    
    // 显示成功界面
    success.value = true;
    loading.value = false;
    
    // 开始倒计时
    startCountdown();
  } catch (err) {
    console.error('GitHub 认证失败:', err);
    error.value = '认证处理失败，请重试';
    loading.value = false;
  }
};

// 开始倒计时
const startCountdown = () => {
  timer = window.setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(timer as number);
      goToRepos();
    }
  }, 1000);
};

// 跳转到目标页面
const goToRepos = () => {
  // 获取存储的重定向URI，默认为/repos前端路由
  const redirectPath = localStorage.getItem('redirectAfterLogin') || '/repos';
  // 清除存储的重定向URI
  localStorage.removeItem('redirectAfterLogin');
  
  // 确定最终的重定向路径
  let finalPath = redirectPath;
  
  // 处理特殊情况：如果是API路径，转换为相应的前端路由路径
  if (redirectPath.startsWith('/api/')) {
    // 如果是仓库API路径，重定向到仓库前端路由
    if (redirectPath === '/api/auth/github/repos') {
      finalPath = '/repos';
    } else {
      console.warn('检测到API路径重定向，默认重定向到仓库页面', redirectPath);
      finalPath = '/repos';
    }
  }
  
  // 执行路由跳转
  console.log('重定向到:', finalPath);
  router.push(finalPath);
};

onMounted(() => {
  handleGithubCallback();
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});
</script>

<style scoped>
.callback-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 20px;
}

.content {
  padding: 50px;
  text-align: center;
}

.success-content {
  padding: 20px;
  text-align: center;
  min-width: 500px;
}

.user-info {
  margin-bottom: 20px;
}

.user-info h3 {
  margin-bottom: 8px;
  color: #52c41a;
}

.user-info p {
  color: #999;
}
</style> 