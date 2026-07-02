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
      path: '/home',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/',
      name: 'landing',
      component: () => import('@/views/LandingView.vue'),
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
    // ── 题库 (Question Bank) ──
    {
      path: '/bank',
      name: 'question-bank',
      component: () => import('@/views/QuestionBankView.vue'),
    },
    {
      path: '/bank/list',
      name: 'question-list',
      component: () => import('@/views/QuestionListView.vue'),
    },
    {
      path: '/bank/question/:questionId',
      name: 'question-solve',
      component: () => import('@/views/QuestionSolveView.vue'),
      props: true,
    },
    {
      path: '/bank/exam/:year',
      name: 'exam-paper',
      component: () => import('@/views/ExamPaperView.vue'),
      props: true,
    },
    // ── 知识点 Wiki ──
    {
      path: '/wiki',
      name: 'wiki',
      component: () => import('@/views/KnowledgeWikiView.vue'),
      children: [
        {
          path: ':nodeId',
          name: 'knowledge-node',
          component: () => import('@/views/KnowledgeNodeDetailView.vue'),
          props: true,
        },
      ],
    },
    // ── 社区 (Community) ──
    {
      path: '/community',
      name: 'community',
      component: () => import('@/views/CommunityView.vue'),
    },
    {
      path: '/community/discussion/:discussionId',
      name: 'discussion-detail',
      component: () => import('@/views/DiscussionDetailView.vue'),
      props: true,
    },
    // ── 错题本 (Mistake Book) ──
    {
      path: '/mistake-book',
      name: 'mistake-book',
      component: () => import('@/views/MistakeBookView.vue'),
    },
    // ── 6 Differentiated Feature Routes ──
    {
      path: '/problem-gen',
      name: 'problem-gen',
      component: () => import('@/views/ProblemGenView.vue'),
    },
    {
      path: '/learning-path',
      name: 'learning-path',
      component: () => import('@/views/LearningPathView.vue'),
    },
    {
      path: '/code-challenge',
      name: 'code-challenge',
      component: () => import('@/views/CodeChallengeView.vue'),
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
