<template>
  <div class="pr-detail-container">
    <a-page-header
      :title="prTitle"
      :sub-title="`#${prNumber}`"
      @back="goBack"
    />

    <a-spin :spinning="loading" tip="加载中...">
      <a-empty v-if="!pullRequest && !loading" description="无法获取PR信息" />
      
      <div v-else-if="pullRequest" class="pr-detail">
        <!-- PR 头部信息 -->
        <a-card class="pr-header-card">
          <div class="pr-header">
            <div class="pr-title-section">
              <a-typography-title :level="3">
                {{ pullRequest.title }}
                <a-tag class="pr-number-tag">#{{ pullRequest.number }}</a-tag>
              </a-typography-title>
              
              <div class="pr-status-tags">
                <a-tag :color="getPRStatusColor(pullRequest.state)">{{ getPRStatusText(pullRequest.state) }}</a-tag>
                <a-tag v-if="pullRequest.draft" color="grey">草稿</a-tag>
              </div>
            </div>
            
            <div class="pr-meta">
              <div class="pr-author">
                <a-avatar :src="pullRequest.user.avatar_url" /> 
                <a-typography-text strong>{{ pullRequest.user.login }}</a-typography-text>
                <a-typography-text type="secondary">创建于 {{ formatDateTime(pullRequest.created_at) }}</a-typography-text>
              </div>
              
              <div class="pr-stats">
                <a-statistic-card>
                  <template #statistic>
                    <a-statistic
                      title="修改文件"
                      :value="pullRequest.changed_files"
                      :value-style="{ color: '#1890ff' }"
                    >
                      <template #prefix>
                        <code-outlined />
                      </template>
                    </a-statistic>
                  </template>
                </a-statistic-card>
                
                <a-statistic-card>
                  <template #statistic>
                    <a-statistic
                      title="添加行数"
                      :value="pullRequest.additions"
                      :value-style="{ color: '#3f8600' }"
                    >
                      <template #prefix>
                        <plus-outlined />
                      </template>
                    </a-statistic>
                  </template>
                </a-statistic-card>
                
                <a-statistic-card>
                  <template #statistic>
                    <a-statistic
                      title="删除行数"
                      :value="pullRequest.deletions"
                      :value-style="{ color: '#cf1322' }"
                    >
                      <template #prefix>
                        <minus-outlined />
                      </template>
                    </a-statistic>
                  </template>
                </a-statistic-card>
                
                <a-statistic-card>
                  <template #statistic>
                    <a-statistic
                      title="评论数"
                      :value="pullRequest.comments"
                    >
                      <template #prefix>
                        <message-outlined />
                      </template>
                    </a-statistic>
                  </template>
                </a-statistic-card>
              </div>
            </div>
          </div>
        </a-card>
        
        <!-- PR 详情内容 -->
        <div class="pr-content">
          <a-tabs default-active-key="1">
            <a-tab-pane key="1" tab="描述">
              <a-card class="pr-description-card">
                <div class="markdown-content" v-html="formatMarkdown(pullRequest.body || '无描述')"></div>
              </a-card>
            </a-tab-pane>
            
            <a-tab-pane key="2" tab="文件变更">
              <a-card class="pr-files-card">
                <a-table
                  :columns="fileColumns"
                  :data-source="pullRequest.files || []"
                  :pagination="false"
                  size="middle"
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.dataIndex === 'filename'">
                      <a-typography-text code>{{ record.filename }}</a-typography-text>
                    </template>
                    <template v-if="column.dataIndex === 'status'">
                      <a-tag :color="getFileStatusColor(record.status)">{{ getFileStatusText(record.status) }}</a-tag>
                    </template>
                    <template v-if="column.dataIndex === 'changes'">
                      <span class="changes">
                        <span class="additions">+{{ record.additions }}</span>
                        <span class="deletions">-{{ record.deletions }}</span>
                      </span>
                    </template>
                  </template>
                </a-table>
              </a-card>
            </a-tab-pane>
            
            <a-tab-pane key="3" tab="AI 分析">
              <a-card class="pr-analysis-card">
                <template #extra>
                  <a-button 
                    type="primary" 
                    :loading="analyzing" 
                    @click="analyzePR"
                    :disabled="analyzed"
                  >
                    <template #icon><robot-outlined /></template>
                    {{ analyzed ? "已分析" : "AI 分析" }}
                  </a-button>
                </template>
                
                <a-empty v-if="!analyzed && !analyzing" description="点击右上角按钮进行 AI 分析" />
                
                <a-spin :spinning="analyzing" tip="AI 正在分析...">
                  <div v-if="analyzed" class="analysis-result">
                    <a-typography-title :level="4">分析结果</a-typography-title>
                    <div class="markdown-content" v-html="formatMarkdown(analysisResult.summary || '')"></div>
                    
                    <a-divider />
                    
                    <a-typography-title :level="4">代码质量评估</a-typography-title>
                    <a-row :gutter="16">
                      <a-col :span="8" v-for="(score, key) in analysisResult.scores" :key="key">
                        <a-card class="score-card">
                          <a-statistic
                            :title="getScoreTitle(key)"
                            :value="score"
                            :precision="1"
                            :value-style="{ color: getScoreColor(score) }"
                            suffix="/ 10"
                          />
                        </a-card>
                      </a-col>
                    </a-row>
                    
                    <a-divider />
                    
                    <a-typography-title :level="4">建议</a-typography-title>
                    <a-list
                      itemLayout="horizontal"
                      :data-source="analysisResult.suggestions || []"
                    >
                      <template #renderItem="{ item }">
                        <a-list-item>
                          <a-list-item-meta>
                            <template #title>{{ item.title }}</template>
                            <template #description>
                              <div class="markdown-content" v-html="formatMarkdown(item.description)"></div>
                            </template>
                            <template #avatar>
                              <a-avatar :style="{ backgroundColor: item.type === 'improvement' ? '#52c41a' : '#faad14' }">
                                {{ item.type === 'improvement' ? '改' : '建' }}
                              </a-avatar>
                            </template>
                          </a-list-item-meta>
                        </a-list-item>
                      </template>
                    </a-list>
                  </div>
                </a-spin>
              </a-card>
            </a-tab-pane>
          </a-tabs>
        </div>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  CodeOutlined, 
  PlusOutlined, 
  MinusOutlined, 
  MessageOutlined,
  RobotOutlined
} from '@ant-design/icons-vue';
import { repoApi } from '../services/api';
import { message } from 'ant-design-vue';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

// 类型定义
interface User {
  login: string;
  avatar_url: string;
}

interface FileChange {
  filename: string;
  status: 'added' | 'modified' | 'removed';
  additions: number;
  deletions: number;
  changes: number;
}

interface PullRequest {
  number: number;
  title: string;
  body: string;
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
  files?: FileChange[];
}

interface Suggestion {
  title: string;
  description: string;
  type: 'improvement' | 'issue';
}

interface AnalysisResult {
  summary: string;
  scores: {
    readability: number;
    maintainability: number;
    performance: number;
  };
  suggestions: Suggestion[];
}

const router = useRouter();
const route = useRoute();
const repoId = ref<string>(route.params.repoId as string);
const prNumber = ref<number>(Number(route.params.pullNumber));
const prTitle = ref<string>('Pull Request 详情');
const pullRequest = ref<PullRequest | null>(null);
const loading = ref<boolean>(false);
const analyzing = ref<boolean>(false);
const analyzed = ref<boolean>(false);
const analysisResult = ref<AnalysisResult>({
  summary: '',
  scores: {
    readability: 0,
    maintainability: 0,
    performance: 0
  },
  suggestions: []
});

// 文件表格列定义
const fileColumns = [
  {
    title: '文件名',
    dataIndex: 'filename',
    key: 'filename',
    ellipsis: true,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '变更',
    dataIndex: 'changes',
    key: 'changes',
    width: 150,
  }
];

// 获取PR详情
const fetchPRDetail = async () => {
  try {
    if (!repoId.value || !prNumber.value) return;
    
    loading.value = true;
    const response = await repoApi.getPullRequest(repoId.value, prNumber.value);
    pullRequest.value = response.data;
    
    if (pullRequest.value) {
      prTitle.value = pullRequest.value.title;
    }
  } catch (error) {
    console.error('获取PR详情失败', error);
    message.error('获取Pull Request详情失败');
  } finally {
    loading.value = false;
  }
};

// 使用AI分析PR
const analyzePR = async () => {
  try {
    if (!repoId.value || !prNumber.value) return;
    
    analyzing.value = true;
    const response = await repoApi.analyzePullRequest(repoId.value, prNumber.value);
    analysisResult.value = response.data;
    analyzed.value = true;
    
    message.success('AI分析完成！');
  } catch (error) {
    console.error('分析PR失败', error);
    message.error('AI分析失败，请稍后再试');
  } finally {
    analyzing.value = false;
  }
};

// 格式化日期时间
const formatDateTime = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
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

// 获取文件状态颜色
const getFileStatusColor = (status: string) => {
  switch (status) {
    case 'added':
      return 'green';
    case 'modified':
      return 'blue';
    case 'removed':
      return 'red';
    default:
      return 'default';
  }
};

// 获取文件状态文本
const getFileStatusText = (status: string) => {
  switch (status) {
    case 'added':
      return '新增';
    case 'modified':
      return '修改';
    case 'removed':
      return '删除';
    default:
      return status;
  }
};

// 获取评分标题
const getScoreTitle = (key: string) => {
  switch (key) {
    case 'readability':
      return '可读性';
    case 'maintainability':
      return '可维护性';
    case 'performance':
      return '性能';
    default:
      return key;
  }
};

// 获取评分颜色
const getScoreColor = (score: number) => {
  if (score >= 8) return '#52c41a';
  if (score >= 6) return '#1890ff';
  if (score >= 4) return '#faad14';
  return '#f5222d';
};

// 格式化Markdown内容
const formatMarkdown = (content: string) => {
  const html = String(marked.parse(content));
  return DOMPurify.sanitize(html);
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};

onMounted(() => {
  fetchPRDetail();
});
</script>

<style scoped>
.pr-detail-container {
  padding: 24px;
}

.pr-header-card {
  margin-bottom: 24px;
}

.pr-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pr-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.pr-number-tag {
  margin-left: 8px;
  font-size: 14px;
  font-weight: normal;
}

.pr-status-tags {
  display: flex;
  gap: 8px;
}

.pr-meta {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.pr-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pr-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.pr-content {
  margin-top: 24px;
}

.pr-description-card,
.pr-files-card,
.pr-analysis-card {
  margin-bottom: 24px;
}

.changes {
  display: flex;
  gap: 16px;
}

.additions {
  color: #52c41a;
}

.deletions {
  color: #f5222d;
}

.score-card {
  margin-bottom: 16px;
  text-align: center;
}

.analysis-result {
  padding: 16px 0;
}

.markdown-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-content :deep(code) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 2px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .pr-stats {
    flex-direction: column;
  }
  
  .pr-title-section {
    flex-direction: column;
    gap: 16px;
  }
}
</style> 