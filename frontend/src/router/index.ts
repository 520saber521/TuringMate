import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      // 文字提问入口（从首页搜索框跳转）
      path: '/chat/ask',
      name: 'ask',
      component: () => import('@/views/GuidedChatView.vue'),
      props: (route) => ({ query: route.query.q }),
    },
    {
      path: '/photo-search',
      name: 'photo-search',
      component: () => import('@/views/PhotoSearchView.vue'),
    },
    {
      path: '/chat/:questionId',
      name: 'guided-chat',
      component: () => import('@/views/GuidedChatView.vue'),
      props: true,
    },
    {
      path: '/correction',
      name: 'correction',
      component: () => import('@/views/CorrectionView.vue'),
    },
    {
      path: '/diagnosis',
      name: 'diagnosis',
      component: () => import('@/views/DiagnosisView.vue'),
    },
    {
      path: '/visualize',
      name: 'code-visual',
      component: () => import('@/views/CodeVisualView.vue'),
    },
  ],
})

export default router
