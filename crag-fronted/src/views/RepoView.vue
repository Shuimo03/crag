<template>
  <div class="repo-container">
    <a-page-header
      title="我的仓库"
      sub-title="查看并管理您的GitHub仓库"
      :backIcon="false"
    />

    <a-spin :spinning="loading" tip="加载中...">
      <a-empty 
        v-if="repos.length === 0 && !loading" 
        description="暂无仓库" 
      >
        <template #description>
          <span>暂无仓库</span>
          <p class="empty-desc">查看并管理您的GitHub仓库</p>
        </template>
      </a-empty>
      
      <div v-else class="repo-list">
        <a-list
          :grid="{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 }"
          :data-source="repos"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <a-card hoverable class="repo-card" @click="viewRepoPRs(item.id)">
                <template #cover>
                  <div class="repo-card-cover">
                    <github-outlined class="repo-icon" />
                    <a-badge
                      v-if="item.pull_count > 0"
                      :count="item.pull_count"
                      color="#1890ff"
                      class="pr-badge"
                    />
                  </div>
                </template>
                <a-card-meta :title="item.name">
                  <template #description>
                    <div class="repo-description">
                      <div class="repo-desc-text">{{ item.description || '暂无描述' }}</div>
                      <div class="repo-stats">
                        <span class="repo-stat">
                          <star-outlined /> {{ item.stars }}
                        </span>
                        <span class="repo-stat">
                          <fork-outlined /> {{ item.forks }}
                        </span>
                        <span class="repo-stat">
                          <eye-outlined /> {{ item.watchers }}
                        </span>
                      </div>
                      <div class="repo-footer">
                        <a-tag color="green">{{ item.language }}</a-tag>
                        <a-tag v-if="item.private" color="blue">私有</a-tag>
                        <a-tag v-else color="cyan">公开</a-tag>
                      </div>
                    </div>
                  </template>
                </a-card-meta>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { GithubOutlined, StarOutlined, ForkOutlined, EyeOutlined } from '@ant-design/icons-vue';
import { repoApi } from '../services/api';
import { message } from 'ant-design-vue';

// 类型定义
interface Repository {
  id: string;
  name: string;
  description?: string;
  language: string;
  stars: number;
  forks: number;
  watchers: number;
  private: boolean;
  pull_count: number;
  updated_at: string;
}

const router = useRouter();
const repos = ref<Repository[]>([]);
const loading = ref<boolean>(false);

// 获取用户的仓库列表
const fetchUserRepos = async () => {
  try {
    loading.value = true;
    console.log('正在请求仓库数据: /api/auth/github/repos');
    const response = await repoApi.getUserRepos();
    console.log('获取到仓库数据:', response.data);
    repos.value = response.data;
  } catch (error) {
    console.error('获取仓库列表失败', error);
    message.error('获取仓库列表失败');
  } finally {
    loading.value = false;
  }
};

// 查看仓库的PR列表
const viewRepoPRs = (repoId: string) => {
  router.push(`/repos/${repoId}/pulls`);
};

onMounted(() => {
  fetchUserRepos();
});
</script>

<style scoped>
.repo-container {
  padding: 24px;
  width: 100%;
}

.empty-desc {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
  margin-top: 8px;
}

.repo-list {
  margin-top: 24px;
}

.repo-card {
  transition: all 0.3s;
}

.repo-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.repo-card-cover {
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  position: relative;
}

.repo-icon {
  font-size: 48px;
  color: #1890ff;
}

.pr-badge {
  position: absolute;
  right: 12px;
  top: 12px;
}

.repo-description {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.repo-desc-text {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 40px;
}

.repo-stats {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.repo-stat {
  color: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  gap: 4px;
}

.repo-footer {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style> 