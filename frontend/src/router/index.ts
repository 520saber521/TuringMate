import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/AuthView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/chat/ask',
      name: 'ask',
      component: () => import('@/views/GuidedChatView.vue'),
      props: (route) => ({ query: route.query.q }),
    },
    {
      path: '/camera',
      name: 'camera',
      component: () => import('@/views/CameraView.vue'),
    },
    {
      path: '/chat/:questionId',
      name: 'guided-chat',
      component: () => import('@/views/GuidedChatView.vue'),
      props: true,
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
    // ── 6 Differentiated Feature Routes ──
    {
      path: '/problem-gen',
      name: 'problem-gen',
      component: () => import('@/views/ProblemGenView.vue'),
    },
    {
      path: '/buddy',
      name: 'buddy',
      component: () => import('@/views/BuddyView.vue'),
    },
    {
      path: '/learning-path',
      name: 'learning-path',
      component: () => import('@/views/LearningPathView.vue'),
    },
    {
      path: '/thinking',
      name: 'thinking',
      component: () => import('@/views/ThinkingTraceView.vue'),
    },
    {
      path: '/code-challenge',
      name: 'code-challenge',
      component: () => import('@/views/CodeChallengeView.vue'),
    },
    {
      path: '/mistake-book',
      name: 'mistake-book',
      component: () => import('@/views/MistakeBookView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  if (!auth.user && auth.accessToken) {
    await auth.fetchUser()
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return next('/')
  }

  next()
})

export default router
