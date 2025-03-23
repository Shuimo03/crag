import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// 请求拦截器 - 添加认证信息
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 处理 401 未授权错误
    if (error.response && error.response.status === 401) {
      // 清除本地存储的认证信息
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // 重定向到登录页
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// 身份验证 API
export const authApi = {
  // 获取当前用户信息
  getCurrentUser: () => {
    return api.get('/api/user/current');
  },
  
  // 登出
  logout: () => {
    return api.post('/api/auth/logout');
  },
};

// 大模型 API
export const modelApi = {
  // 获取模型列表
  getModels: () => {
    return api.get('/api/models');
  },
  
  // 发送消息到模型
  sendMessage: (modelId: string, message: string, conversationId?: string) => {
    return api.post('/api/chat', {
      model_id: modelId,
      message,
      conversation_id: conversationId
    });
  },
  
  // 获取对话历史
  getConversations: () => {
    return api.get('/api/conversations');
  },
  
  // 获取特定对话的消息
  getConversationMessages: (conversationId: string) => {
    return api.get(`/api/conversations/${conversationId}/messages`);
  }
};

// 仓库和PR API
export const repoApi = {
  // 获取用户的仓库列表
  getUserRepos: () => {
    return api.get('/api/auth/github/repos');
  },
  
  // 获取仓库的PR列表
  getRepoPullRequests: (repoId: string) => {
    return api.get(`/api/repos/${repoId}/pulls`);
  },
  
  // 获取PR详情
  getPullRequest: (repoId: string, pullNumber: number) => {
    return api.get(`/api/repos/${repoId}/pulls/${pullNumber}`);
  },
  
  // 分析PR (Mock API)
  analyzePullRequest: (repoId: string, pullNumber: number) => {
    return api.post(`/api/repos/${repoId}/pulls/${pullNumber}/analyze`);
  }
};

export default api; 