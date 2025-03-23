import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import GithubCallbackView from '../views/GithubCallbackView.vue'
import RepoView from '../views/RepoView.vue'
import PRListView from '../views/PRListView.vue'
import PRDetailView from '../views/PRDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true }
    },
    {
      path: '/auth/github/callback',
      name: 'github-callback',
      component: GithubCallbackView,
      meta: { guest: true }
    },
    {
      path: '/api/auth/github/callback',
      redirect: to => {
        return { path: '/auth/github/callback', query: to.query };
      }
    },
    // 处理API路径重定向
    {
      path: '/api/auth/github/repos',
      redirect: '/repos'
    },
    // 仓库相关路由
    {
      path: '/repos',
      name: 'repos',
      component: RepoView,
      meta: { requiresAuth: false }
    },
    {
      path: '/repos/:id/pulls',
      name: 'repo-pulls',
      component: PRListView,
      meta: { requiresAuth: true }
    },
    {
      path: '/repos/:repoId/pulls/:pullNumber',
      name: 'pull-request-detail',
      component: PRDetailView,
      meta: { requiresAuth: true }
    },
  ],
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token')
  
  // 需要认证但用户未登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 保存用户尝试访问的页面，登录后重定向回来
    next({ 
      name: 'login', 
      query: { redirect_uri: to.fullPath }
    })
  } 
  // 已登录用户不能访问游客页面
  else if (to.meta.guest && isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
