<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LogIn,
  UserPlus,
  Eye,
  EyeOff,
  Sparkles,
  ArrowRight,
  GraduationCap,
  Brain,
  FileCheck,
  Target,
  Code2
} from 'lucide-vue-next'
import LoginButton from '@/components/ui/LoginButton.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const isLogin = ref(true)
const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')

// Login form
const loginUsername = ref('')
const loginPassword = ref('')

// Register form
const regUsername = ref('')
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regConfirm = ref('')

const redirectPath = computed(() => (route.query.redirect as string) || '/')

async function handleLogin() {
  errorMsg.value = ''
  if (!loginUsername.value || !loginPassword.value) {
    errorMsg.value = '请填写用户名和密码'
    return
  }
  isLoading.value = true
  try {
    await auth.login({ username: loginUsername.value, password: loginPassword.value })
    router.push(redirectPath.value)
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '登录失败，请重试'
  } finally {
    isLoading.value = false
  }
}

async function handleRegister() {
  errorMsg.value = ''
  if (!regUsername.value || !regName.value || !regPassword.value) {
    errorMsg.value = '请填写必填项'
    return
  }
  if (regPassword.value !== regConfirm.value) {
    errorMsg.value = '两次密码不一致'
    return
  }
  if (regPassword.value.length < 6) {
    errorMsg.value = '密码长度至少6位'
    return
  }
  isLoading.value = true
  try {
    await auth.register({
      username: regUsername.value,
      password: regPassword.value,
      name: regName.value,
      email: regEmail.value,
    })
    router.push(redirectPath.value)
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '注册失败，请重试'
  } finally {
    isLoading.value = false
  }
}

function switchMode() {
  isLogin.value = !isLogin.value
  errorMsg.value = ''
}
</script>

<template>
  <div class="auth-page">
    <!-- Background decorations -->
    <div class="bg-decoration">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="grid-pattern"></div>
    </div>

    <div class="auth-container">
      <!-- Left: Brand -->
      <div class="auth-brand">
        <!-- Floating shapes -->
        <div class="floating-shape shape-1"></div>
        <div class="floating-shape shape-2"></div>
        <div class="floating-shape shape-3"></div>
        
        <div class="brand-content">
          <div class="brand-logo">
            <div class="logo-inner">
              <Sparkles :size="28" class="text-white" />
            </div>
            <div class="logo-glow"></div>
          </div>
          
          <h1 class="brand-name">
            <span class="name-highlight">Turing</span>Mate
          </h1>
          <p class="brand-desc">AI-Powered Computer Science Exam Prep</p>
          
          <div class="brand-tagline">
            <span class="tagline-badge">🎯 408 计算机考研</span>
            <span class="tagline-badge">✨ 1对1 智能私教</span>
          </div>

          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-icon">
                <Brain :size="18" />
              </div>
              <div class="feature-text">
                <span class="feature-title">苏格拉底式引导</span>
                <span class="feature-desc">不直接给答案，引导你自己想通</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <FileCheck :size="18" />
              </div>
              <div class="feature-text">
                <span class="feature-title">手写批改诊断</span>
                <span class="feature-desc">拍照上传，AI精准找出薄弱点</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <Code2 :size="18" />
              </div>
              <div class="feature-text">
                <span class="feature-title">代码实战</span>
                <span class="feature-desc">在线编程环境 + AI 评判</span>
              </div>
            </div>
          </div>

          <div class="brand-stats">
            <div class="stat-item">
              <span class="stat-value">50K+</span>
              <span class="stat-label">考研学子</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">98%</span>
              <span class="stat-label">满意度</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">10K+</span>
              <span class="stat-label">真题题库</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Form -->
      <div class="auth-form-card">
        <!-- Decorative header -->
        <div class="card-header">
          <h2 class="card-title">{{ isLogin ? '欢迎回来' : '加入我们' }}</h2>
          <p class="card-subtitle">{{ isLogin ? '登录您的账号继续学习' : '创建账号，开启智能学习之旅' }}</p>
        </div>

        <!-- Tabs -->
        <div class="form-tabs" role="tablist">
          <button
            :class="['tab-btn', { active: isLogin }]"
            role="tab"
            :aria-selected="isLogin"
            @click="isLogin = true"
          >
            <LogIn :size="16" />
            登录
          </button>
          <button
            :class="['tab-btn', { active: !isLogin }]"
            role="tab"
            :aria-selected="!isLogin"
            @click="isLogin = false"
          >
            <UserPlus :size="16" />
            注册
          </button>
          <div 
            class="tab-indicator" 
            :class="{ 'indicator-right': !isLogin }"
          ></div>
        </div>

        <!-- Error -->
        <Transition name="error-slide">
          <div v-if="errorMsg" class="error-msg" role="alert" aria-live="polite">
            <span class="error-icon">⚠️</span>
            {{ errorMsg }}
          </div>
        </Transition>

        <!-- Login Form -->
        <Transition name="form-fade" mode="out-in">
          <form v-if="isLogin" @submit.prevent="handleLogin" class="auth-form" key="login">
            <div class="form-field">
              <label class="field-label" for="login-username">
                <span class="label-icon">👤</span>
                用户名
              </label>
              <div class="input-wrapper">
                <input
                  id="login-username"
                  v-model="loginUsername"
                  type="text"
                  class="field-input"
                  placeholder="请输入用户名"
                  autocomplete="username"
                  required
                />
              </div>
            </div>
            <div class="form-field">
              <label class="field-label" for="login-password">
                <span class="label-icon">🔒</span>
                密码
              </label>
              <div class="input-wrapper">
                <input
                  id="login-password"
                  v-model="loginPassword"
                  :type="showPassword ? 'text' : 'password'"
                  class="field-input"
                  placeholder="请输入密码"
                  autocomplete="current-password"
                  required
                  @keyup.enter="handleLogin"
                />
                <button 
                  type="button" 
                  class="eye-btn" 
                  :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                  @click="showPassword = !showPassword"
                >
                  <EyeOff v-if="showPassword" :size="18" />
                  <Eye v-else :size="18" />
                </button>
              </div>
            </div>
            
            <div class="form-actions">
              <label class="remember-me">
                <input type="checkbox" />
                <span class="checkbox-custom"></span>
                记住我
              </label>
              <button type="button" class="forgot-link">忘记密码？</button>
            </div>
            
            <LoginButton
              size="xl"
              variant="primary"
              :loading="isLoading"
              full-width
              show-arrow
              class="submit-btn"
              @click="handleLogin"
            >
              <span class="btn-text-bold">LOGIN</span>
            </LoginButton>
          </form>

          <!-- Register Form -->
          <form v-else @submit.prevent="handleRegister" class="auth-form" key="register">
            <div class="form-row">
              <div class="form-field">
                <label class="field-label" for="reg-username">
                  <span class="label-icon">👤</span>
                  用户名 <span class="required">*</span>
                </label>
                <div class="input-wrapper">
                  <input
                    id="reg-username"
                    v-model="regUsername"
                    type="text"
                    class="field-input"
                    placeholder="3-50位字符"
                    required
                  />
                </div>
              </div>
              <div class="form-field">
                <label class="field-label" for="reg-name">
                  <span class="label-icon">✏️</span>
                  昵称 <span class="required">*</span>
                </label>
                <div class="input-wrapper">
                  <input
                    id="reg-name"
                    v-model="regName"
                    type="text"
                    class="field-input"
                    placeholder="怎么称呼你？"
                    required
                  />
                </div>
              </div>
            </div>
            <div class="form-field">
              <label class="field-label" for="reg-email">
                <span class="label-icon">📧</span>
                邮箱
              </label>
              <div class="input-wrapper">
                <input
                  id="reg-email"
                  v-model="regEmail"
                  type="email"
                  class="field-input"
                  placeholder="选填，便于找回密码"
                />
              </div>
            </div>
            <div class="form-field">
              <label class="field-label" for="reg-password">
                <span class="label-icon">🔐</span>
                密码 <span class="required">*</span>
              </label>
              <div class="input-wrapper">
                <input
                  id="reg-password"
                  v-model="regPassword"
                  :type="showPassword ? 'text' : 'password'"
                  class="field-input"
                  placeholder="至少6位"
                  required
                  minlength="6"
                />
                <button 
                  type="button" 
                  class="eye-btn"
                  :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                  @click="showPassword = !showPassword"
                >
                  <EyeOff v-if="showPassword" :size="18" />
                  <Eye v-else :size="18" />
                </button>
              </div>
            </div>
            <div class="form-field">
              <label class="field-label" for="reg-confirm">
                <span class="label-icon">✅</span>
                确认密码 <span class="required">*</span>
              </label>
              <div class="input-wrapper">
                <input
                  id="reg-confirm"
                  v-model="regConfirm"
                  :type="showPassword ? 'text' : 'password'"
                  class="field-input"
                  placeholder="再次输入密码"
                  required
                />
              </div>
            </div>
            
            <LoginButton
              size="xl"
              variant="primary"
              :loading="isLoading"
              full-width
              show-arrow
              class="submit-btn"
              @click="handleRegister"
            >
              <span class="btn-text-bold">REGISTER</span>
            </LoginButton>
          </form>
        </Transition>

        <p class="switch-hint">
          {{ isLogin ? '还没有账号？' : '已有账号？' }}
          <button class="switch-link" type="button" @click="switchMode">
            {{ isLogin ? '立即注册' : '去登录' }}
            <ArrowRight :size="14" />
          </button>
        </p>

        <p class="terms-hint">
          登录即表示同意
          <a href="#" class="terms-link">《服务条款》</a>
          和
          <a href="#" class="terms-link">《隐私政策》</a>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ================================
 * AUTH PAGE - Modern UI Design
 * ================================ */

.auth-page {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f0f23;
  position: relative;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

/* Background Decoration */
.bg-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  pointer-events: none;
}

.blob-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
  top: -200px;
  right: -200px;
  animation: float 15s ease-in-out infinite;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%);
  bottom: -150px;
  left: -150px;
  animation: float 18s ease-in-out infinite reverse;
}

.blob-3 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 12s ease-in-out infinite;
  opacity: 0.3;
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 60px 60px;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -40px) scale(1.05); }
  66% { transform: translate(-20px, 30px) scale(0.95); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.5; }
}

/* ================================
 * AUTH CONTAINER
 * ================================ */

.auth-container {
  display: flex;
  max-width: 1000px;
  width: 100%;
  border-radius: 24px;
  overflow: hidden;
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 
    0 25px 60px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
}

/* ================================
 * BRAND SIDE
 * ================================ */

.auth-brand {
  flex: 1.1;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
  position: relative;
  overflow: hidden;
}

/* Floating shapes */
.floating-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.shape-1 {
  width: 200px;
  height: 200px;
  background: #a855f7;
  top: -50px;
  right: -50px;
  animation: float 10s ease-in-out infinite;
}

.shape-2 {
  width: 150px;
  height: 150px;
  background: #06b6d4;
  bottom: 50px;
  left: -30px;
  animation: float 12s ease-in-out infinite reverse;
}

.shape-3 {
  width: 100px;
  height: 100px;
  background: #f59e0b;
  bottom: -20px;
  right: 30%;
  animation: float 8s ease-in-out infinite;
}

.brand-content {
  position: relative;
  z-index: 1;
}

/* Logo */
.brand-logo {
  position: relative;
  width: 72px;
  height: 72px;
  margin-bottom: 1.5rem;
}

.logo-inner {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8px 32px rgba(124, 58, 237, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

.logo-glow {
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.3) 0%, transparent 70%);
  animation: pulse-glow 3s ease-in-out infinite;
  z-index: -1;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

/* Typography */
.brand-name {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.name-highlight {
  background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-desc {
  font-size: 0.85rem;
  opacity: 0.6;
  margin-bottom: 1rem;
  letter-spacing: 0.05em;
}

.brand-tagline {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tagline-badge {
  font-size: 0.7rem;
  padding: 0.35rem 0.75rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(8px);
}

/* Features */
.brand-features {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  margin-bottom: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #a855f7;
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.feature-title {
  font-size: 0.85rem;
  font-weight: 600;
  opacity: 0.95;
}

.feature-desc {
  font-size: 0.7rem;
  opacity: 0.5;
}

/* Stats */
.brand-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 14px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #a855f7 0%, #22d3ee 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.65rem;
  opacity: 0.5;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
}

/* ================================
 * FORM CARD
 * ================================ */

.auth-form-card {
  flex: 0.9;
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e1b4b;
  margin-bottom: 0.35rem;
}

.card-subtitle {
  font-size: 0.85rem;
  color: #64748b;
}

/* Tabs */
.form-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: #f1f5f9;
  border-radius: 14px;
  padding: 5px;
  position: relative;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 1;
}

.tab-btn.active {
  color: #7c3aed;
  background: white;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.15);
}

.tab-indicator {
  position: absolute;
  top: 5px;
  left: 5px;
  width: calc(50% - 5px);
  height: calc(100% - 10px);
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.15);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-indicator.indicator-right {
  transform: translateX(100%);
}

/* Error Message */
.error-msg {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fef2f2;
  color: #dc2626;
  padding: 0.7rem 0.9rem;
  border-radius: 12px;
  font-size: 0.8rem;
  margin-bottom: 1rem;
  border: 1px solid #fecaca;
}

.error-icon {
  font-size: 1rem;
}

.error-slide-enter-active,
.error-slide-leave-active {
  transition: all 0.3s ease;
}

.error-slide-enter-from,
.error-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Form */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.label-icon {
  font-size: 0.9rem;
}

.required {
  color: #ef4444;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
}

.field-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.9rem;
  background: #f8fafc;
  color: #1e293b;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: #a78bfa;
  background: white;
  box-shadow: 0 0 0 4px rgba(167, 139, 250, 0.1);
}

.field-input::placeholder {
  color: #94a3b8;
}

.field-input:hover:not(:focus) {
  border-color: #cbd5e1;
}

.eye-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 6px;
  display: flex;
  border-radius: 8px;
  transition: all 0.2s;
}

.eye-btn:hover {
  color: #7c3aed;
  background: #f1f5f9;
}

/* Form Actions */
.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #64748b;
  cursor: pointer;
}

.remember-me input {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e1;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remember-me input:checked + .checkbox-custom {
  background: #7c3aed;
  border-color: #7c3aed;
}

.remember-me input:checked + .checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 0.7rem;
  font-weight: bold;
}

.forgot-link {
  font-size: 0.8rem;
  color: #7c3aed;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

.submit-btn {
  margin-top: 0.5rem;
}

/* Switch Hint */
.switch-hint {
  text-align: center;
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 1.25rem;
}

.switch-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  color: #7c3aed;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.switch-link:hover {
  color: #6d28d9;
  gap: 0.5rem;
}

/* 按钮粗体文本 */
.btn-text-bold {
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

/* 提交按钮大气效果 */
.submit-btn {
  margin-top: 1rem;
  padding: 1.25rem 2rem;
}

.submit-btn:hover {
  transform: translateY(-3px);
}

/* Terms Hint */
.terms-hint {
  text-align: center;
  font-size: 0.7rem;
  color: #94a3b8;
  margin-top: 0.75rem;
}

.terms-link {
  color: #7c3aed;
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

/* Form Transitions */
.form-fade-enter-active,
.form-fade-leave-active {
  transition: all 0.25s ease;
}

.form-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.form-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* ================================
 * RESPONSIVE
 * ================================ */

@media (max-width: 768px) {
  .auth-container {
    flex-direction: column;
    max-width: 420px;
  }
  
  .auth-brand {
    padding: 2rem 1.5rem;
    text-align: center;
    align-items: center;
  }
  
  .brand-features {
    display: none;
  }
  
  .brand-stats {
    display: none;
  }
  
  .auth-form-card {
    padding: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .blob-1,
  .blob-2 {
    width: 300px;
    height: 300px;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .auth-form-card {
    background: rgba(30, 30, 50, 0.95);
  }
  
  .card-title {
    color: #f1f5f9;
  }
  
  .card-subtitle {
    color: #94a3b8;
  }
  
  .field-label {
    color: #e2e8f0;
  }
  
  .field-input {
    background: #1e293b;
    border-color: #334155;
    color: #f1f5f9;
  }
  
  .field-input::placeholder {
    color: #64748b;
  }
  
  .form-tabs {
    background: #1e293b;
  }
  
  .tab-btn {
    color: #94a3b8;
  }
  
  .tab-btn.active {
    background: #334155;
    color: #a78bfa;
  }
  
  .tab-indicator {
    background: #334155;
  }
  
  .switch-hint,
  .terms-hint {
    color: #94a3b8;
  }
  
  .eye-btn:hover {
    background: #334155;
  }
  
  .remember-me {
    color: #94a3b8;
  }
}
</style>
