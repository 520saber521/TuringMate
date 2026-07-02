<!--
  LandingView v3 - TuringMate 入口页
  优化重点：
    1) 移除顶栏，单一主 CTA（点睛式）
    2) 副标题精简到一句
    3) 学科选择并入 Hero 区，胶囊行展示
    4) 移除假数据屏，只保留特性 + CTA
    5) 主色改为青绿 #0D9488，匹配参考站清新调性
    6) 标题字号 9vw，极致对比
    7) 视差 + 字符跟随鼠标移动
-->
<template>
  <div class="landing" @mousemove="onMouseMove" @mouseleave="resetMouse">
    <!-- 滚动进度条 -->
    <div class="scroll-progress" :style="{ transform: `scaleX(${scrollProgress})` }" />

    <!-- 顶部细线 -->
    <div class="top-accent" />

    <!-- 右上角单一入口 -->
    <div class="corner-action">
      <button class="btn-text" @click="goLogin">登录</button>
    </div>

    <!-- ─── 第 1 屏：Hero ─── -->
    <section id="hero" class="screen screen-hero">
      <div class="screen-inner">
        <!-- 社会认同徽章 -->
        <div class="badge reveal" data-reveal>
          <span class="badge-dot" />
          <span class="badge-text">已有 10,000+ 学生在使用</span>
        </div>

        <!-- 字符 Logo（带鼠标视差） -->
        <div class="logo">
          <div class="logo-grid" :style="parallaxStyle">
            <span>TU</span>
            <span>RI</span>
            <span>NG</span>
            <span>MA</span>
            <span>TE</span>
          </div>
        </div>

        <!-- 巨型主标题 -->
        <h1 class="title reveal" data-reveal>
          Learn&nbsp;<span class="title-accent">Forever</span>
        </h1>

        <!-- 一句话副标题 -->
        <p class="subtitle reveal" data-reveal>
          不直接给答案，只教会你思考。
        </p>

        <!-- 单一主 CTA -->
        <div class="cta-group reveal" data-reveal>
          <button class="cta-primary" @click="onGetStarted">
            <span>立即开始</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- 学科胶囊（并入 Hero 区） -->
        <div class="subjects-row reveal" data-reveal>
          <span class="subjects-label">支持学科</span>
          <button
            v-for="cat in categories"
            :key="cat.id"
            class="subject-pill"
            @click="onSelectCategory(cat.id)"
          >
            {{ cat.label }}
          </button>
        </div>

        <!-- 3 步引导流程 -->
        <div class="steps reveal" data-reveal>
          <div class="step" v-for="(s, i) in steps" :key="s.title">
            <div class="step-icon" v-html="s.icon" />
            <div class="step-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <h4 class="step-title">{{ s.title }}</h4>
            <p class="step-desc">{{ s.desc }}</p>
          </div>
        </div>

        <!-- 滚动提示 -->
        <div class="scroll-hint reveal" data-reveal>
          <span>向下探索更多特性</span>
          <div class="scroll-line" />
        </div>
      </div>
    </section>

    <!-- ─── 第 2 屏：核心特性（408os 风格 - 数字编号 + 左右交替） ─── -->
    <section id="features" class="screen screen-features">
      <div class="screen-inner">
        <p class="section-eyebrow reveal" data-reveal>WHY TURINGMATE</p>
        <h2 class="section-title reveal" data-reveal>让 AI 成为你的<br />私人导师</h2>
        <p class="section-subtitle reveal" data-reveal>每一项能力都为独立思考而设计</p>

        <div class="features-stack">
          <article
            v-for="(f, i) in features"
            :key="f.id"
            class="feature-row reveal"
            data-reveal
            :class="{ 'reverse': i % 2 === 1 }"
            :data-reveal-delay="i * 60"
          >
            <div class="feature-meta">
              <div class="feature-num-circle">{{ String(i + 1).padStart(2, '0') }}</div>
              <div class="feature-num-label">FEATURE</div>
            </div>
            <div class="feature-content">
              <p class="feature-eyebrow">{{ f.eyebrow }}</p>
              <h3 class="feature-title">{{ f.title }}</h3>
              <p class="feature-desc">{{ f.desc }}</p>
              <button v-if="f.link" class="feature-link feature-link-button" @click="goFeature(f.route)">
                <span>{{ f.linkText || '查看更多' }}</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M5 12h14" />
                  <path d="m12 5 7 7-7 7" />
                </svg>
              </button>
            </div>
            <div class="feature-visual" aria-hidden="true">
              <div class="feature-card" :class="`card-${f.id}`">
                <div class="card-glow" />
                <div class="card-content" v-html="f.visual" />
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- ─── 第 3 屏：CTA ─── -->
    <section class="screen screen-cta">
      <div class="screen-inner text-center">
        <!-- 模拟应用预览卡 -->
        <div class="cta-preview reveal" data-reveal>
          <div class="preview-bar">
            <div class="preview-dot" />
            <div class="preview-dot" />
            <div class="preview-dot" />
            <div class="preview-url">turingmate.app</div>
          </div>
          <div class="preview-body">
            <div class="preview-sidebar">
              <div class="preview-line" />
              <div class="preview-line short" />
              <div class="preview-line" />
              <div class="preview-line short" />
            </div>
            <div class="preview-main">
              <div class="preview-q">这道题的关键是什么？</div>
              <div class="preview-a">从边界条件开始思考</div>
            </div>
          </div>
        </div>

        <h2 class="cta-title reveal" data-reveal>
          准备开始了？
        </h2>
        <p class="cta-subtitle reveal" data-reveal>
          一道题，就从这里开始
        </p>
        <div class="cta-group reveal" data-reveal>
          <button class="cta-primary" @click="onGetStarted">
            <span>立即开始</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          </button>
          <button class="cta-link" @click="goLogin">已有账号？登录 →</button>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-inner">
        <p>© 2026 TuringMate</p>
        <div class="footer-links">
          <button type="button" @click="goFeature('/login')">隐私</button>
          <button type="button" @click="goFeature('/login')">条款</button>
          <button type="button" @click="goFeature('/community')">联系</button>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 学科分类（精简到 5 个核心）
const categories = [
  { id: 'data_structure', label: '数据结构' },
  { id: 'algorithm', label: '算法' },
  { id: 'network', label: '计算机网络' },
  { id: 'os', label: '操作系统' },
  { id: 'db', label: '数据库' },
]

// 3 步上手引导
const steps = [
  {
    title: '拍照上传',
    desc: '手机拍照或上传题目图片',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>',
  },
  {
    title: '苏格拉底引导',
    desc: 'AI 提问带出你的思路',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>',
  },
  {
    title: '薄弱点诊断',
    desc: '错题自动归集，知识图谱可视化',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
  },
]

// 核心特性（精简到 3 个）
const features = [
  {
    id: 'photo',
    eyebrow: 'PHOTO RECOGNITION',
    title: '拍照即解题',
    desc: '上传题目图片，AI 自动识别文字、公式、图表，启动引导式讲解。',
    link: true,
    linkText: '立即体验',
    route: '/camera',
    visual: `
      <div class="visual-photo">
        <div class="visual-photo-img">
          <div class="img-grid"></div>
          <div class="img-text">f(x) = x² + 2x + 1</div>
        </div>
        <div class="visual-photo-msg">
          <div class="msg-dot"></div>
          <div class="msg-line"></div>
          <div class="msg-line short"></div>
        </div>
      </div>
    `,
  },
  {
    id: 'socratic',
    eyebrow: 'SOCRATIC TUTOR',
    title: '苏格拉底引导',
    desc: '不直接给答案，通过层层提问激发你的独立思考。',
    link: true,
    linkText: '查看对话示例',
    route: '/chat/ask',
    visual: `
      <div class="visual-chat">
        <div class="bubble bubble-q">这道题的关键是什么？</div>
        <div class="bubble bubble-a">从边界条件开始思考</div>
        <div class="bubble bubble-q">边界条件是什么？</div>
      </div>
    `,
  },
  {
    id: 'mistake',
    eyebrow: 'KNOWLEDGE GRAPH',
    title: '薄弱点诊断',
    desc: '自动归集错题，AI 分析错误模式，定位知识盲区。',
    link: true,
    linkText: '查看诊断报告',
    route: '/diagnosis',
    visual: `
      <div class="visual-graph">
        <svg viewBox="0 0 200 200" width="100%" height="100%">
          <g stroke="currentColor" stroke-width="0.5" fill="none" opacity="0.3">
            <line x1="100" y1="40" x2="60" y2="100"/>
            <line x1="100" y1="40" x2="140" y2="100"/>
            <line x1="100" y1="40" x2="100" y2="160"/>
            <line x1="60" y1="100" x2="100" y2="160"/>
            <line x1="140" y1="100" x2="100" y2="160"/>
          </g>
          <g fill="currentColor">
            <circle cx="100" cy="40" r="6" class="node-main"/>
            <circle cx="60" cy="100" r="5" class="node"/>
            <circle cx="140" cy="100" r="5" class="node"/>
            <circle cx="100" cy="160" r="4" class="node-weak"/>
          </g>
        </svg>
      </div>
    `,
  },
]

function onGetStarted() {
  router.push({ name: 'camera' })
}
function goLogin() {
  router.push({ name: 'login' })
}
function onSelectCategory(id: string) {
  router.push({ name: 'camera', query: { subject: id } })
}
function goFeature(route: string) {
  router.push(route)
}

// ── 鼠标视差
const mouseX = ref(0)
const mouseY = ref(0)
const parallaxStyle = computed(() => ({
  transform: `translate(${(mouseX.value - 0.5) * 8}px, ${(mouseY.value - 0.5) * 8}px)`,
  transition: 'transform 0.6s cubic-bezier(0.22, 1, 0.36, 1)',
}))

function onMouseMove(e: MouseEvent) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  mouseX.value = (e.clientX - rect.left) / rect.width
  mouseY.value = (e.clientY - rect.top) / rect.height
}
function resetMouse() {
  mouseX.value = 0.5
  mouseY.value = 0.5
}

// ── 滚动进度
const scrollProgress = ref(0)
function onScroll() {
  const doc = document.documentElement
  const max = doc.scrollHeight - doc.clientHeight
  scrollProgress.value = max > 0 ? doc.scrollTop / max : 0
}

// ── IntersectionObserver
let observer: IntersectionObserver | null = null
onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target as HTMLElement
          const delay = parseInt(el.dataset.revealDelay || '0', 10)
          setTimeout(() => el.classList.add('is-visible'), delay)
          observer?.unobserve(el)
        }
      })
    },
    { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
  )
  document.querySelectorAll('[data-reveal]').forEach((el) => observer?.observe(el))
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
})
onUnmounted(() => {
  observer?.disconnect()
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
/* ─────────────────────────────────────────────
   全局 - 青绿色主题
   ───────────────────────────────────────────── */
.landing {
  min-height: 100vh;
  background: var(--color-bg-page);
  position: relative;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

/* 背景光晕装饰 */
.landing::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  width: 1200px;
  height: 1200px;
  background: radial-gradient(
    circle at 50% 0%,
    rgba(13, 148, 136, 0.05) 0%,
    transparent 50%
  );
  transform: translateX(-50%);
  pointer-events: none;
  z-index: 0;
}

/* 滚动进度条（顶部细线下方） */
.scroll-progress {
  position: fixed;
  top: 2px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-primary);
  transform-origin: 0 50%;
  transform: scaleX(0);
  z-index: 61;
  transition: transform 0.1s linear;
}

/* 顶部细线（青绿） */
.top-accent {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg,
    transparent 0%,
    var(--color-primary) 20%,
    var(--color-primary) 80%,
    transparent 100%);
  opacity: 0.5;
  z-index: 60;
}

/* 右上角登录 */
.corner-action {
  position: fixed;
  top: 1.25rem;
  right: var(--spacing-5);
  z-index: 50;
}
.btn-text {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 0 var(--spacing-3);
  height: 36px;
  cursor: pointer;
  border-radius: var(--radius-md);
  font-family: inherit;
  transition: all var(--transition-fast);
}
.btn-text:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-subtle);
}

/* ─────────────────────────────────────────────
   屏幕通用
   ───────────────────────────────────────────── */
.screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 120px var(--spacing-5) var(--spacing-16);
  position: relative;
}
.screen-inner {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}
.screen-cta .screen-inner,
.screen-hero .screen-inner {
  text-align: center;
}

.section-eyebrow {
  font-size: 0.7rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  letter-spacing: 0.18em;
  margin-bottom: var(--spacing-3);
  text-transform: uppercase;
}
.section-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin-bottom: var(--spacing-3);
}
.section-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  max-width: 600px;
  margin: 0 0 var(--spacing-12);
}
.text-center .section-subtitle { margin-left: auto; margin-right: auto; }
.text-center { text-align: center; }

/* ─────────────────────────────────────────────
   第 1 屏：Hero（极致字号 + 极简）
   ───────────────────────────────────────────── */
.logo {
  margin-bottom: var(--spacing-10);
}
.logo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  width: 96px;
  margin: 0 auto;
  font-family: var(--font-family-display);
  font-size: 0.875rem;
  font-weight: var(--font-weight-medium);
  letter-spacing: 0.05em;
  color: var(--color-text-primary);
  line-height: 1.4;
}

/* 极致大标题 */
.title {
  font-family: var(--font-family-display);
  font-size: clamp(3rem, 9vw, 6rem);
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.04em;
  line-height: 1.02;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-6);
}
.title-accent {
  color: var(--color-primary);
  font-style: italic;
  font-weight: 500;
}

/* 一句话副标题 */
.subtitle {
  font-size: var(--font-size-lg);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-secondary);
  max-width: 540px;
  margin: 0 auto var(--spacing-10);
  font-weight: 300;
}

.cta-group {
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
  margin-bottom: var(--spacing-12);
  flex-wrap: wrap;
}
.cta-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border: 1px solid var(--color-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  padding: 0 var(--spacing-8);
  min-height: 52px;
  border-radius: 9999px;  /* 完全圆角，胶囊形 */
  cursor: pointer;
  font-family: inherit;
  transition: all var(--transition-fast);
}
.cta-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 12px 24px -6px rgba(13, 148, 136, 0.35);
}

/* 学科胶囊行 */
.subjects-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-16);
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}
.subjects-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-right: var(--spacing-2);
}
.subject-pill {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 0 var(--spacing-4);
  height: 36px;
  border-radius: 9999px;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--transition-fast);
}
.subject-pill:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(13, 148, 136, 0.05);
}

/* 副标题下方装饰线（青绿短横线） */
.subtitle::after {
  content: '';
  display: block;
  width: 40px;
  height: 2px;
  background: var(--color-primary);
  margin: var(--spacing-4) auto 0;
  border-radius: 2px;
}

/* ── 社会认同徽章 ── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: 6px var(--spacing-4);
  background: rgba(13, 148, 136, 0.08);
  border: 1px solid rgba(13, 148, 136, 0.18);
  border-radius: 9999px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
  margin-bottom: var(--spacing-6);
}
.badge-dot {
  width: 6px;
  height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(13, 148, 136, 0.6);
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(13, 148, 136, 0.6); }
  50%      { box-shadow: 0 0 0 6px rgba(13, 148, 136, 0); }
}

/* ── 3 步引导流程 ── */
.steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-4);
  max-width: 720px;
  margin: 0 auto var(--spacing-10);
  position: relative;
}
.steps::before {
  /* 步骤连接线 */
  content: '';
  position: absolute;
  top: 28px;
  left: 18%;
  right: 18%;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    var(--color-border) 20%,
    var(--color-border) 80%,
    transparent 100%);
  z-index: 0;
}
.step {
  text-align: center;
  position: relative;
  z-index: 1;
  padding: 0 var(--spacing-3);
}
.step-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto var(--spacing-3);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  color: var(--color-primary);
  transition: all 0.3s ease;
}
.step:hover .step-icon {
  transform: translateY(-4px) scale(1.05);
  border-color: var(--color-primary);
  background: rgba(13, 148, 136, 0.05);
  box-shadow: 0 8px 16px -4px rgba(13, 148, 136, 0.2);
}
.step-num {
  font-size: 0.7rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-muted);
  letter-spacing: 0.1em;
  margin-bottom: var(--spacing-1);
  font-feature-settings: "tnum";
}
.step-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 4px;
}
.step-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  line-height: 1.5;
}

/* ── 特性圆形编号 ── */
.feature-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--spacing-2);
}
.feature-num-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(13, 148, 136, 0.08);
  border: 1px solid rgba(13, 148, 136, 0.18);
  color: var(--color-primary);
  font-size: 1.5rem;
  font-weight: var(--font-weight-bold);
  font-feature-settings: "tnum";
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: -0.02em;
  transition: all 0.3s ease;
}
.feature-row:hover .feature-num-circle {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  transform: scale(1.05);
}
.feature-num-label {
  font-size: 0.7rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  letter-spacing: 0.18em;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

/* ── 特性链接（带箭头） ── */
.feature-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
  text-decoration: none;
  padding: 6px 0;
  position: relative;
  transition: all 0.3s ease;
}
.feature-link-button {
  border: 0;
  background: transparent;
  font-family: inherit;
  cursor: pointer;
}
.feature-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: var(--color-primary);
  transition: width 0.3s ease;
}
.feature-link:hover { gap: 10px; }
.feature-link:hover::after { width: 100%; }

/* 滚动提示 */
.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
  color: var(--color-text-muted);
  font-size: 0.7rem;
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.18em;
}
.scroll-line {
  width: 1px;
  height: 48px;
  background: linear-gradient(to bottom, var(--color-text-muted), transparent);
  position: relative;
  overflow: hidden;
}
.scroll-line::after {
  content: '';
  position: absolute;
  top: -16px;
  left: 0;
  width: 100%;
  height: 16px;
  background: var(--color-primary);
  animation: scrollDown 2s ease-in-out infinite;
}
@keyframes scrollDown {
  0%   { transform: translateY(0); opacity: 1; }
  100% { transform: translateY(64px); opacity: 0; }
}

/* ─────────────────────────────────────────────
   第 2 屏：特性（Sticky 翻页 + 数字编号 + 左右交替）
   ───────────────────────────────────────────── */
.screen-features {
  background: linear-gradient(180deg,
    var(--color-bg-page) 0%,
    var(--color-bg-subtle) 100%);
}
.features-stack {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.feature-row {
  display: grid;
  grid-template-columns: 100px 1fr 1fr;
  gap: var(--spacing-10);
  align-items: center;
  min-height: 100vh;
  padding: var(--spacing-12) 0;
  position: relative;
  /* Sticky 翻页：第 1 屏飞走，第 2 屏 sticky 顶部，依次类推 */
}
.feature-row.reverse .feature-content { order: 2; }
.feature-row.reverse .feature-visual  { order: 1; }

/* ── 视觉卡片悬浮增强 ── */
.feature-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.feature-card {
  position: relative;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-8);
  width: 100%;
  max-width: 380px;
  aspect-ratio: 4 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1),
              box-shadow 0.4s cubic-bezier(0.22, 1, 0.36, 1),
              border-color 0.4s ease;
  will-change: transform;
}
.feature-row:hover .feature-card {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px -8px rgba(13, 148, 136, 0.18),
              0 8px 16px -4px rgba(13, 148, 136, 0.08);
  border-color: var(--color-primary);
}
.card-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(13, 148, 136, 0.1) 0%,
    transparent 60%
  );
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.4s ease;
}
.feature-row:hover .card-glow { opacity: 1; }

.feature-num {
  font-size: 5rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  opacity: 0.18;
  font-feature-settings: "tnum";
  letter-spacing: -0.04em;
  line-height: 1;
}
.feature-content { max-width: 440px; }
.feature-eyebrow {
  font-size: 0.7rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  letter-spacing: 0.18em;
  margin-bottom: var(--spacing-3);
}
.feature-title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
  margin-bottom: var(--spacing-4);
}
.feature-desc {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-5);
}
.feature-link {
  display: inline-flex;
  align-items: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
  text-decoration: none;
  transition: gap var(--transition-fast);
}
.feature-link:hover { gap: var(--spacing-2); }

/* 视觉卡片 */
.feature-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}
.feature-card {
  position: relative;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-8);
  width: 100%;
  max-width: 380px;
  aspect-ratio: 4 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: transform var(--transition-normal);
}
.feature-row:hover .feature-card { transform: translateY(-4px); }
.card-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(13, 148, 136, 0.08) 0%,
    transparent 60%
  );
  pointer-events: none;
}
.card-content {
  position: relative;
  z-index: 1;
  width: 100%;
  color: var(--color-text-primary);
}

/* 视觉1：拍照 */
.visual-photo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  width: 100%;
}
.visual-photo-img {
  width: 100%;
  aspect-ratio: 16/9;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-md);
  position: relative;
  overflow: hidden;
}
.img-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(45deg, transparent 49%, var(--color-border) 49%, var(--color-border) 51%, transparent 51%),
    linear-gradient(-45deg, transparent 49%, var(--color-border) 49%, var(--color-border) 51%, transparent 51%);
  background-size: 24px 24px;
  opacity: 0.4;
}
.img-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-family-mono);
  font-size: 1.25rem;
  color: var(--color-text-primary);
  font-weight: 500;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(2px);
}
.visual-photo-msg {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: var(--spacing-3);
  background: var(--color-bg-subtle);
  border-radius: var(--radius-md);
}
.msg-dot {
  width: 8px;
  height: 8px;
  background: var(--color-primary);
  border-radius: 50%;
}
.msg-line {
  height: 6px;
  background: var(--color-border-strong);
  border-radius: 3px;
  width: 90%;
}
.msg-line.short { width: 60%; }

/* 视觉2：对话 */
.visual-chat {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  width: 100%;
}
.bubble {
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  max-width: 80%;
  line-height: var(--line-height-relaxed);
}
.bubble-q {
  align-self: flex-start;
  background: var(--color-bg-subtle);
  color: var(--color-text-primary);
}
.bubble-a {
  align-self: flex-end;
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

/* 视觉3：图谱 */
.visual-graph { width: 100%; height: 100%; color: var(--color-primary); }
.visual-graph .node { fill: var(--color-primary); opacity: 0.4; }
.visual-graph .node-main { fill: var(--color-primary); opacity: 1; }
.visual-graph .node-weak { fill: #F59E0B; opacity: 0.8; }

/* ─────────────────────────────────────────────
   第 3 屏：CTA
   ───────────────────────────────────────────── */
.screen-cta {
  background: linear-gradient(180deg,
    var(--color-bg-page) 0%,
    var(--color-bg-subtle) 100%);
}
.cta-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: var(--spacing-4);
}
.cta-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  max-width: 600px;
  margin: 0 auto var(--spacing-10);
  font-weight: 300;
}

/* CTA 链接（次要操作） */
.cta-link {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: var(--spacing-3) var(--spacing-4);
  cursor: pointer;
  font-family: inherit;
  transition: color 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.cta-link:hover { color: var(--color-primary); }

/* ── 模拟应用预览卡 ── */
.cta-preview {
  max-width: 520px;
  margin: 0 auto var(--spacing-12);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: 0 20px 40px -12px rgba(13, 148, 136, 0.15),
              0 4px 12px -2px rgba(0, 0, 0, 0.04);
  transform: perspective(1200px) rotateX(2deg);
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.cta-preview:hover {
  transform: perspective(1200px) rotateX(0deg) translateY(-4px);
}
.preview-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px var(--spacing-4);
  background: var(--color-bg-subtle);
  border-bottom: 1px solid var(--color-border);
}
.preview-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border-strong);
}
.preview-dot:nth-child(1) { background: #FF5F57; }
.preview-dot:nth-child(2) { background: #FEBC2E; }
.preview-dot:nth-child(3) { background: #28C840; }
.preview-url {
  flex: 1;
  text-align: center;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  font-family: var(--font-family-mono);
}
.preview-body {
  display: grid;
  grid-template-columns: 100px 1fr;
  height: 160px;
}
.preview-sidebar {
  padding: var(--spacing-3);
  background: var(--color-bg-subtle);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.preview-line {
  height: 6px;
  background: var(--color-border-strong);
  border-radius: 3px;
  width: 80%;
  opacity: 0.5;
}
.preview-line.short { width: 50%; }
.preview-main {
  padding: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  justify-content: center;
}
.preview-q {
  font-size: 0.8rem;
  padding: 6px 10px;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-sm);
  align-self: flex-start;
  max-width: 80%;
  color: var(--color-text-primary);
}
.preview-a {
  font-size: 0.8rem;
  padding: 6px 10px;
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-radius: var(--radius-sm);
  align-self: flex-end;
  max-width: 80%;
}

/* ─────────────────────────────────────────────
   底部
   ───────────────────────────────────────────── */
.footer {
  padding: var(--spacing-6) var(--spacing-5);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-page);
}
.footer-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}
.footer-links {
  display: flex;
  gap: var(--spacing-5);
}
.footer-links button {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  border: 0;
  background: transparent;
  font-family: inherit;
  cursor: pointer;
  transition: color var(--transition-fast);
}
.footer-links button:hover { color: var(--color-text-primary); }

/* ─────────────────────────────────────────────
   滚动揭示动画
   ───────────────────────────────────────────── */
.reveal {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1),
              transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* ─────────────────────────────────────────────
   响应式
   ───────────────────────────────────────────── */
@media (max-width: 960px) {
  .feature-row { grid-template-columns: 1fr; gap: var(--spacing-5); }
  .feature-row.reverse .feature-content { order: 1; }
  .feature-row.reverse .feature-visual  { order: 2; }
  .feature-meta { flex-direction: row; align-items: center; }
  .feature-num-label { writing-mode: horizontal-tb; }
  .feature-visual { max-width: 380px; margin: 0 auto; }
  .steps { grid-template-columns: 1fr; max-width: 320px; }
  .steps::before { display: none; }
  .preview-body { grid-template-columns: 1fr; height: auto; }
  .preview-sidebar { border-right: none; border-bottom: 1px solid var(--color-border); }
}

@media (max-width: 640px) {
  .screen { padding: 80px var(--spacing-4) var(--spacing-12); }
  .subjects-row { flex-direction: column; align-items: stretch; }
  .subjects-label { text-align: center; margin-bottom: var(--spacing-2); }
  .cta-group { flex-direction: column; width: 100%; }
  .cta-primary { width: 100%; justify-content: center; }
  .footer-inner { flex-direction: column; text-align: center; }
  .cta-preview { margin-left: 0; margin-right: 0; }
}
</style>
