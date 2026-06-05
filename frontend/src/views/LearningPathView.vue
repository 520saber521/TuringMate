<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Map, Calendar, Clock, CheckCircle2, Circle, TrendingUp, ChevronRight, Loader2, Target, BookOpen, Sparkles } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Progress from '@/components/ui/Progress.vue'
import { generatePath } from '@/api/learningPath'
import type { LearningPath, PathPhase, DailyTask } from '@/api/learningPath'

const router = useRouter()
const isLoading = ref(false)
const errorMsg = ref('')
const pathData = ref<LearningPath | null>(null)
const expandedPhase = ref(0)

async function handleGenerate() {
  isLoading.value = true
  errorMsg.value = ''
  try {
    // Use a placeholder diagnosis report ID - in production from diagnosis page
    pathData.value = await generatePath('latest')
    expandedPhase.value = 0
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '生成学习路径失败，请先完成薄弱点诊断'
  } finally {
    isLoading.value = false
  }
}

function togglePhase(index: number) {
  expandedPhase.value = expandedPhase.value === index ? -1 : index
}

function getSubjectBadge(subject: string) {
  const map: Record<string, string> = { 'ds': 'primary', 'co': 'warning', 'os': 'success', 'cn': 'amber' }
  return map[subject] || 'primary'
}

const overallProgress = computed(() => {
  if (!pathData.value) return 0
  const allTasks = pathData.value.phases.flatMap(p => p.tasks)
  if (!allTasks.length) return 0
  return Math.round((allTasks.filter(t => t.completed).length / allTasks.length) * 100)
})
</script>

<template>
  <div class="learning-path-page">
    <div class="lp-intro">
      <p class="lp-intro__overline font-serif">你的专属学习路线</p>
      <h1 class="lp-intro__title">每一步，都算数</h1>
      <p class="lp-intro__desc">AI 诊断薄弱点后，为你规划千人千面的学习路径</p>
    </div>

    <div v-if="errorMsg" class="error-toast">{{ errorMsg }}</div>

    <!-- Not generated yet -->
    <div v-if="!pathData && !isLoading" class="empty-stage">
      <div class="empty-card surface-paper">
        <div class="empty-card__icon">
          <Target :size="48" />
        </div>
        <h2 class="font-serif">还没有学习路径</h2>
        <p>AI 会基于你的薄弱点诊断结果，生成个性化的每日学习计划</p>
        <div class="empty-actions">
          <Button variant="primary" size="lg" @click="handleGenerate">
            <Sparkles :size="18" />
            生成我的学习路径
          </Button>
          <Button variant="outline" size="lg" @click="router.push('/diagnosis')">
            先去完成诊断
          </Button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading-stage">
      <div class="loading-spinner">
        <Loader2 :size="40" class="spinning" />
      </div>
      <p>AI 正在基于诊断报告规划学习路径...</p>
    </div>

    <!-- Path generated -->
    <div v-if="pathData" class="path-stage">
      <!-- Overall progress -->
      <div class="progress-card surface-glow">
        <div class="progress-header">
          <div class="progress-header__info">
            <h3>总体进度</h3>
            <p>{{ pathData.summary }}</p>
          </div>
          <div class="progress-ring-container">
            <svg viewBox="0 0 80 80" class="progress-ring" aria-label="总体进度 {{ overallProgress }}%">
              <circle cx="40" cy="40" r="34" fill="none" stroke="var(--color-border-light)" stroke-width="6" />
              <circle
                cx="40" cy="40" r="34" fill="none"
                stroke="url(#ringGradient)" stroke-width="6"
                stroke-linecap="round"
                :stroke-dasharray="2 * Math.PI * 34"
                :stroke-dashoffset="2 * Math.PI * 34 * (1 - overallProgress / 100)"
                transform="rotate(-90 40 40)"
                style="transition: stroke-dashoffset 0.8s cubic-bezier(0.22, 1, 0.36, 1);"
              />
              <text x="40" y="44" text-anchor="middle" font-size="17" font-weight="700" fill="var(--color-text-primary)">{{ overallProgress }}%</text>
            </svg>
            <defs>
              <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="var(--color-primary-400)" />
                <stop offset="100%" stop-color="var(--color-amber-400)" />
              </linearGradient>
            </defs>
          </div>
        </div>
      </div>

      <!-- Timeline -->
      <div class="timeline">
        <div
          v-for="(phase, pi) in pathData.phases" :key="pi"
          :class="['phase-card', { expanded: expandedPhase === pi }]"
        >
          <div class="phase-trigger surface-paper" @click="togglePhase(pi)">
            <div class="phase-left">
              <div class="phase-indicator" :class="`phase-indicator--${pi}`">
                <span class="phase-num">{{ pi + 1 }}</span>
              </div>
              <div>
                <h3 class="phase-name">{{ phase.name }}</h3>
                <div class="phase-meta">
                  <span><Calendar :size="14" /> {{ phase.duration_days }} 天</span>
                  <span><BookOpen :size="14" /> {{ phase.tasks.length }} 个任务</span>
                </div>
              </div>
            </div>
            <ChevronRight :size="18" :class="['chevron', { rotated: expandedPhase === pi }]" />
          </div>

          <!-- Expanded tasks -->
          <div v-if="expandedPhase === pi" class="tasks-list">
            <div
              v-for="(task, ti) in phase.tasks" :key="ti"
              :class="['task-item', { completed: task.completed }]"
            >
              <div class="task-check">
                <CheckCircle2 v-if="task.completed" :size="20" class="check-icon check-icon--done" />
                <Circle v-else :size="20" class="check-icon check-icon--pending" />
              </div>
              <div class="task-body">
                <div class="task-top">
                  <Badge :variant="getSubjectBadge(task.subject)" size="sm">{{ task.subject }}</Badge>
                  <span class="task-type">{{ task.task_type === 'review' ? '复习' : task.task_type === 'practice' ? '练习' : '总结' }}</span>
                  <span class="task-time"><Clock :size="12" /> {{ task.estimated_minutes }}分钟</span>
                </div>
                <p class="task-topic">Day {{ task.day }} · {{ task.topic }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Encouragement -->
      <div class="lp-encouragement font-serif">
        <p>路虽远，行则将至。每一天的坚持都在靠近你的目标。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.learning-path-page { max-width: 800px; margin: 0 auto; padding: 1.5rem; }

/* ============================
   INTRO — Journey feel
   ============================ */
.lp-intro {
  text-align: center;
  margin-bottom: 2rem;
}
.lp-intro__overline {
  font-size: 0.88rem;
  color: var(--color-amber-600);
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
}
.lp-intro__title {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
  margin-bottom: 0.3rem;
}
.lp-intro__desc {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.error-toast {
  background: var(--color-bg-danger-soft);
  color: var(--color-danger-600);
  padding: 0.7rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  font-size: 0.85rem;
  border: 1px solid var(--color-danger-200);
}

/* ============================
   EMPTY STATE
   ============================ */
.empty-stage { text-align: center; padding: 3rem 0; }
.empty-card {
  max-width: 480px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.empty-card__icon {
  color: var(--color-text-muted);
  opacity: 0.3;
  margin-bottom: 0.5rem;
}
.empty-card h2 {
  font-size: 1.2rem;
  color: var(--color-text-primary);
}
.empty-card p {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.empty-actions {
  display: flex;
  gap: 0.8rem;
  margin-top: 1rem;
}

/* ============================
   LOADING
   ============================ */
.loading-stage { text-align: center; padding: 5rem 0; }
.loading-spinner {
  color: var(--color-primary-500);
  margin-bottom: 1rem;
}
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-stage p { color: var(--color-text-secondary); font-size: 0.95rem; }

/* ============================
   PROGRESS CARD
   ============================ */
.progress-card {
  margin-bottom: 1.5rem;
  padding: 1.25rem 1.5rem;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}
.progress-header__info h3 {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.3rem;
}
.progress-header__info p {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.progress-ring-container { flex-shrink: 0; }
.progress-ring { width: 80px; height: 80px; display: block; }

/* ============================
   TIMELINE
   ============================ */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  padding-left: 0;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 26px;
  top: 30px;
  bottom: 30px;
  width: 2px;
  background: linear-gradient(180deg,
    var(--color-border) 0%,
    var(--color-primary-200) 50%,
    var(--color-border) 100%);
  z-index: 0;
}

.phase-card {
  position: relative;
  z-index: 1;
  margin-bottom: 0.5rem;
}
.phase-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.2rem;
  cursor: pointer;
  transition: all var(--transition-normal);
}
.phase-trigger:hover {
  box-shadow: var(--shadow-md);
}
.phase-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.phase-indicator {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);
  background: linear-gradient(135deg, var(--color-primary-400), var(--color-primary-600));
}
.phase-indicator--0 {
  background: linear-gradient(135deg, var(--color-primary-400), var(--color-primary-600));
}
.phase-indicator--1 {
  background: linear-gradient(135deg, var(--color-amber-400), var(--color-amber-600));
}
.phase-indicator--2 {
  background: linear-gradient(135deg, var(--color-success-400), var(--color-success-600));
}

.phase-num { line-height: 1; }

.phase-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}
.phase-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.2rem;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
.phase-meta span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.chevron {
  color: var(--color-text-muted);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}
.chevron.rotated {
  transform: rotate(90deg);
}

/* Tasks */
.tasks-list {
  margin-top: 0.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding-left: 1.5rem;
}
.task-item {
  display: flex;
  gap: 0.6rem;
  padding: 0.7rem 0.85rem;
  border-radius: var(--radius-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-fast);
}
.task-item:hover {
  border-color: var(--color-border);
}
.task-item.completed {
  opacity: 0.55;
}
.task-check {
  padding-top: 2px;
  flex-shrink: 0;
}
.check-icon--done { color: var(--color-success-500); }
.check-icon--pending { color: var(--color-text-muted); }

.task-body { flex: 1; min-width: 0; }
.task-top {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.2rem;
  flex-wrap: wrap;
}
.task-type {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.task-time {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  gap: 0.15rem;
  margin-left: auto;
}
.task-topic {
  font-size: 0.88rem;
  color: var(--color-text-primary);
  font-weight: 500;
  line-height: 1.4;
}

/* ============================
   ENCOURAGEMENT
   ============================ */
.lp-encouragement {
  text-align: center;
  padding: 2rem 1rem 1rem;
  font-size: 0.95rem;
  color: var(--color-text-muted);
  line-height: 1.6;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 640px) {
  .learning-path-page { padding: 1rem; }
  .progress-header { flex-direction: column; text-align: center; }
  .lp-intro__title { font-size: 1.3rem; }
}
</style>
