<template>
  <div class="pr-list-container">
    <a-page-header
      :title="repoName || '仓库PR列表'"
      :sub-title="repoName ? 'Pull Requests' : ''"
      @back="goBack"
    />

    <a-spin :spinning="loading" tip="加载中...">
      <a-empty v-if="pullRequests.length === 0 && !loading" description="暂无 Pull Requests" />
      
      <div v-else class="pr-list">
        <a-list
          itemLayout="vertical"
          size="large"
          :data-source="pullRequests"
        >
          <template #renderItem="{ item }">
            <a-list-item
              :key="item.number"
              class="pr-item"
              @click="viewPRDetail(item.number)"
            >
              <template #extra>
                <div class="pr-status">
                  <a-tag :color="getPRStatusColor(item.state)">{{ getPRStatusText(item.state) }}</a-tag>
                  <a-tag v-if="item.draft" color="grey">草稿</a-tag>
                </div>
              </template>

              <a-list-item-meta>
                <template #title>
                  <div class="pr-title">
                    <span class="pr-number">#{{ item.number }}</span>
                    {{ item.title }}
                  </div>
                </template>
                <template #description>
                  <div class="pr-meta">
                    <span class="pr-author">
                      <a-avatar :src="item.user.avatar_url" size="small" /> 
                      {{ item.user.login }}
                    </span>
                    <span class="pr-time">创建于 {{ formatDate(item.created_at) }}</span>
                    <span v-if="item.merged_at" class="pr-time">合并于 {{ formatDate(item.merged_at) }}</span>
                    <span v-else-if="item.closed_at" class="pr-time">关闭于 {{ formatDate(item.closed_at) }}</span>
                  </div>
                </template>
              </a-list-item-meta>

              <div class="pr-stats">
                <span class="pr-stat">
                  <message-outlined /> {{ item.comments }}
                </span>
                <span class="pr-stat">
                  <code-outlined /> {{ item.changed_files }} 文件
                </span>
                <span class="pr-stat">
                  <plus-outlined /> {{ item.additions }}
                </span>
                <span class="pr-stat">
                  <minus-outlined /> {{ item.deletions }}
                </span>
              </div>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { MessageOutlined, CodeOutlined, PlusOutlined, MinusOutlined } from '@ant-design/icons-vue';
import { repoApi } from '../services/api';
import { message } from 'ant-design-vue';

// 类型定义
interface User {
  login: string;
  avatar_url: string;
}

interface PullRequest {
  number: number;
  title: string;
  state: 'open' | 'closed' | 'merged';
  draft: boolean;
  user: User;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  merged_at: string | null;
  comments: number;
  changed_files: number;
  additions: number;
  deletions: number;
}

const router = useRouter();
const route = useRoute();
const repoId = ref<string>(route.params.id as string);
const repoName = ref<string>('');
const pullRequests = ref<PullRequest[]>([]);
const loading = ref<boolean>(false);

// 获取PR列表
const fetchPullRequests = async () => {
  try {
    if (!repoId.value) return;
    
    loading.value = true;
    const response = await repoApi.getRepoPullRequests(repoId.value);
    pullRequests.value = response.data.pulls;
    repoName.value = response.data.repo.name;
  } catch (error) {
    console.error('获取PR列表失败', error);
    message.error('获取Pull Requests失败');
  } finally {
    loading.value = false;
  }
};

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// 获取PR状态颜色
const getPRStatusColor = (state: string) => {
  switch (state) {
    case 'open':
      return 'green';
    case 'closed':
      return 'red';
    case 'merged':
      return 'purple';
    default:
      return 'default';
  }
};

// 获取PR状态文本
const getPRStatusText = (state: string) => {
  switch (state) {
    case 'open':
      return '开放';
    case 'closed':
      return '已关闭';
    case 'merged':
      return '已合并';
    default:
      return state;
  }
};

// 跳转到PR详情
const viewPRDetail = (prNumber: number) => {
  router.push(`/repos/${repoId.value}/pulls/${prNumber}`);
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};

onMounted(() => {
  fetchPullRequests();
});
</script>

<style scoped>
.pr-list-container {
  padding: 24px;
}

.pr-list {
  margin-top: 24px;
}

.pr-item {
  cursor: pointer;
  transition: background-color 0.3s;
  border-radius: 4px;
  padding: 16px;
}

.pr-item:hover {
  background-color: #f5f5f5;
}

.pr-title {
  font-weight: 500;
}

.pr-number {
  color: rgba(0, 0, 0, 0.45);
  margin-right: 8px;
}

.pr-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}

.pr-author {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pr-time {
  color: rgba(0, 0, 0, 0.45);
}

.pr-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
}

.pr-stat {
  display: flex;
  align-items: center;
  gap: 4px;
  color: rgba(0, 0, 0, 0.65);
}

.pr-status {
  display: flex;
  gap: 8px;
}
</style> 