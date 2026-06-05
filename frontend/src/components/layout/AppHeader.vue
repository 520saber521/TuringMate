<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Settings, Bell, Menu, LogOut, ChevronDown, Sparkles } from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'
import LoginButton from '@/components/ui/LoginButton.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const emit = defineEmits<{
  toggleSidebar: []
}>()

const showUserMenu = ref(false)

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/': '首页',
    '/chat': 'AI 对话',
    '/camera': '拍照识别',
    '/diagnosis': '薄弱点诊断',
    '/visualize': '代码实战',
    '/problem-gen': '举一反三',
    '/buddy': 'AI 研友',
    '/learning-path': '学习路径',
    '/thinking': '思维回放',
    '/code-challenge': '代码挑战',
    '/mistake-book': '错题本',
    '/login': '登录',
  }
  const path = route.path.startsWith('/chat') ? '/chat' : route.path
  return map[path] || 'TuringMate'
})

const userName = computed(() => auth.user?.name || '用户')

function handleLogout() {
  showUserMenu.value = false
  auth.logout()
  router.push('/login')
}

function handleLoginClick() {
  router.push('/login')
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}
</script>

<template>
  <header class="app-header">
    <!-- 顶部渐变装饰线 -->
    <div class="header-accent-line"></div>
    
    <!-- 主内容 -->
    <div class="header-content">
      <!-- Left: Logo + Page Title -->
      <div class="flex items-center gap-4">
        <!-- Mobile Menu Button -->
        <button
          class="mobile-menu-btn"
          aria-label="打开菜单"
          @click="emit('toggleSidebar')"
        >
          <Menu :size="20" />
        </button>

        <!-- Logo -->
        <div class="logo-wrapper">
          <div class="logo-icon">
            <div class="logo-glow"></div>
            <svg class="logo-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="logo-text">
            <span class="logo-name">TuringMate</span>
            <span class="logo-badge">AI</span>
          </div>
        </div>

        <!-- Divider -->
        <div class="header-divider"></div>

        <!-- Page Title -->
        <div class="page-title-wrapper">
          <span class="page-title-icon">
            <Sparkles :size="14" />
          </span>
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
      </div>

      <!-- Right: Actions -->
      <div class="flex items-center gap-1">
        <!-- Theme Toggle -->
        <ThemeToggle />

        <!-- Authenticated User Actions -->
        <template v-if="auth.isAuthenticated">
          <!-- Notification -->
          <button class="action-btn notification-btn" aria-label="通知">
            <Bell :size="18" />
            <span class="notification-dot"></span>
          </button>

          <!-- Settings -->
          <button class="action-btn" aria-label="设置">
            <Settings :size="18" />
          </button>

          <!-- User Menu -->
          <div class="user-menu-wrapper">
            <button 
              class="user-menu-trigger"
              @click="toggleUserMenu"
              aria-label="用户菜单"
            >
              <Avatar size="sm" :name="userName" />
              <span class="user-name">{{ userName }}</span>
              <ChevronDown 
                :size="14" 
                class="menu-arrow transition-transform duration-200"
                :class="{ 'rotate-180': showUserMenu }"
              />
            </button>

            <!-- Dropdown Menu -->
            <Transition name="dropdown">
              <div v-if="showUserMenu" class="user-dropdown">
                <div class="dropdown-header">
                  <Avatar size="md" :name="userName" />
                  <div class="dropdown-user-info">
                    <span class="dropdown-user-name">{{ userName }}</span>
                    <span class="dropdown-user-role">学习者</span>
                  </div>
                </div>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item" @click="showUserMenu = false">
                  <span>个人设置</span>
                </button>
                <button class="dropdown-item" @click="showUserMenu = false">
                  <span>学习报告</span>
                </button>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item logout-item" @click="handleLogout">
                  <LogOut :size="16" />
                  <span>退出登录</span>
                </button>
              </div>
            </Transition>
          </div>
        </template>

        <!-- Guest Actions -->
        <template v-else>
          <LoginButton
            size="sm"
            variant="primary"
            @click="handleLoginClick"
          />
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  height: 4rem;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(255, 255, 255, 0.85) 100%
  );
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

/* Top accent line */
.header-accent-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    #8b5cf6 0%,
    #a855f7 25%,
    #ec4899 50%,
    #f59e0b 75%,
    #10b981 100%
  );
  background-size: 200% 100%;
  animation: gradientFlow 8s ease infinite;
}

@keyframes gradientFlow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 1rem;
  max-width: 100%;
}

/* Mobile Menu Button */
.mobile-menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.2s ease;
  background: transparent;
  border: none;
  cursor: pointer;
}

.mobile-menu-btn:hover {
  background: rgba(139, 92, 246, 0.08);
  color: #8b5cf6;
}

.mobile-menu-btn:active {
  transform: scale(0.95);
}

@media (min-width: 1024px) {
  .mobile-menu-btn {
    display: none;
  }
}

/* Logo */
.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  position: relative;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 4px 12px rgba(139, 92, 246, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transition: all 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.05);
  box-shadow: 
    0 6px 20px rgba(139, 92, 246, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}

.logo-glow {
  position: absolute;
  inset: -2px;
  border-radius: 0.85rem;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  opacity: 0;
  filter: blur(8px);
  transition: opacity 0.3s ease;
}

.logo-icon:hover .logo-glow {
  opacity: 0.3;
}

.logo-svg {
  width: 1.25rem;
  height: 1.25rem;
  color: white;
  position: relative;
  z-index: 1;
}

.logo-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-name {
  font-size: 1rem;
  font-weight: 700;
  background: linear-gradient(135deg, #1f2937 0%, #4b5563 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

@media (max-width: 640px) {
  .logo-name {
    display: none;
  }
}

.logo-badge {
  padding: 0.15rem 0.4rem;
  font-size: 0.6rem;
  font-weight: 700;
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  color: white;
  border-radius: 999px;
  letter-spacing: 0.05em;
}

/* Header Divider */
.header-divider {
  width: 1px;
  height: 1.5rem;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(148, 163, 184, 0.3) 50%,
    transparent 100%
  );
  margin: 0 0.5rem;
}

@media (max-width: 768px) {
  .header-divider {
    display: none;
  }
}

/* Page Title */
.page-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-title-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 0.375rem;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 85, 247, 0.05) 100%);
  color: #8b5cf6;
}

@media (max-width: 768px) {
  .page-title-wrapper {
    display: none;
  }
}

.page-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  letter-spacing: -0.01em;
}

/* Action Buttons */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.625rem;
  color: var(--color-text-secondary, #6b7280);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.action-btn:hover {
  background: rgba(139, 92, 246, 0.08);
  color: #8b5cf6;
  transform: translateY(-1px);
}

.action-btn:active {
  transform: scale(0.95);
}

/* Notification */
.notification-btn .notification-dot {
  position: absolute;
  top: 0.35rem;
  right: 0.35rem;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
  border: 1.5px solid white;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

/* User Menu */
.user-menu-wrapper {
  position: relative;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem 0.25rem 0.25rem;
  border-radius: 999px;
  background: rgba(139, 92, 246, 0.04);
  border: 1px solid rgba(139, 92, 246, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-menu-trigger:hover {
  background: rgba(139, 92, 246, 0.08);
  border-color: rgba(139, 92, 246, 0.2);
}

.user-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
}

.menu-arrow {
  color: var(--color-text-tertiary, #9ca3af);
}

@media (max-width: 640px) {
  .user-name {
    display: none;
  }
  
  .menu-arrow {
    display: none;
  }
}

/* User Dropdown */
.user-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 14rem;
  background: white;
  border-radius: 0.875rem;
  border: 1px solid rgba(148, 163, 184, 0.1);
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.1),
    0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 0.5rem;
  z-index: 100;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
}

.dropdown-user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
}

.dropdown-user-role {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #9ca3af);
}

.dropdown-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.1);
  margin: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(139, 92, 246, 0.06);
  color: #8b5cf6;
}

.dropdown-item.logout-item:hover {
  background: rgba(239, 68, 68, 0.06);
  color: #ef4444;
}

/* Dropdown Animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}
</style>
