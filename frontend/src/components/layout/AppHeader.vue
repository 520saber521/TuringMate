<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Settings, Bell, Menu, LogOut, ChevronDown } from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'
import LoginButton from '@/components/ui/LoginButton.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

defineEmits<{
  toggleSidebar: []
}>()

const showUserMenu = ref(false)

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/': '首页',
    '/home': '主页',
    '/chat': 'AI 对话',
    '/camera': '拍照识别',
    '/diagnosis': '薄弱诊断',
    '/visualize': '代码可视化',
    '/bank': '题库',
    '/wiki': '知识点',
    '/community': '社区',
    '/problem-gen': '举一反三',
    '/learning-path': '学习路径',
    '/code-challenge': '代码实战',
    '/mistake-book': '错题本',
    '/login': '登录',
  }

  if (route.path.startsWith('/chat')) return map['/chat']
  if (route.path.startsWith('/bank')) return map['/bank']
  if (route.path.startsWith('/wiki')) return map['/wiki']
  if (route.path.startsWith('/community')) return map['/community']
  return map[route.path] || 'TuringMate'
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
    <div class="header-content">
      <div class="header-left">
        <button
          class="mobile-menu-btn"
          aria-label="打开菜单"
          @click="$emit('toggleSidebar')"
        >
          <Menu :size="20" />
        </button>

        <div class="logo-wrapper">
          <div class="logo-icon">
            <svg class="logo-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="logo-name">TuringMate</span>
        </div>

        <div class="header-divider"></div>
        <span class="page-title">{{ pageTitle }}</span>
      </div>

      <div class="header-right">
        <ThemeToggle />

        <template v-if="auth.isAuthenticated">
          <button class="action-btn notification-btn" aria-label="通知">
            <Bell :size="18" />
            <span class="notification-dot"></span>
          </button>

          <button class="action-btn" aria-label="设置">
            <Settings :size="18" />
          </button>

          <div class="user-menu-wrapper">
            <button
              class="user-menu-trigger"
              aria-label="用户菜单"
              @click="toggleUserMenu"
            >
              <Avatar size="sm" :name="userName" />
              <span class="user-name">{{ userName }}</span>
              <ChevronDown
                :size="14"
                class="menu-arrow"
                :class="{ 'is-open': showUserMenu }"
              />
            </button>

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
                  <LogOut :size="15" />
                  <span>退出登录</span>
                </button>
              </div>
            </Transition>
          </div>
        </template>

        <LoginButton
          v-else
          size="md"
          variant="primary"
          shape="pill"
          label="立即登录"
          @click="handleLoginClick"
        />
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
  height: 4.5rem;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  height: 100%;
  padding: 0 1.25rem;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  min-width: 0;
}

.header-left {
  gap: 0.875rem;
}

.header-right {
  gap: 0.6rem;
  flex-shrink: 0;
}

.mobile-menu-btn,
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border: 0;
  border-radius: 10px;
  color: #64748b;
  background: transparent;
  cursor: pointer;
  transition:
    transform var(--transition-fast),
    background var(--transition-fast),
    color var(--transition-fast);
}

.mobile-menu-btn:hover,
.action-btn:hover {
  background: rgba(15, 23, 42, 0.05);
  color: #0d9488;
}

.mobile-menu-btn:active,
.action-btn:active {
  transform: scale(0.95);
}

@media (min-width: 1024px) {
  .mobile-menu-btn {
    display: none;
  }
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  min-width: 0;
}

.logo-icon {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 9px;
  color: #fff;
  background: #0d9488;
}

.logo-svg {
  width: 1.125rem;
  height: 1.125rem;
}

.logo-name {
  font-size: 0.9375rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 0;
}

.header-divider {
  width: 1px;
  height: 1.25rem;
  background: rgba(15, 23, 42, 0.1);
}

.page-title {
  max-width: 12rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
}

.notification-btn {
  position: relative;
}

.notification-dot {
  position: absolute;
  top: 0.55rem;
  right: 0.55rem;
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 50%;
  background: #ef4444;
  border: 1.5px solid white;
}

.user-menu-wrapper {
  position: relative;
}

.user-menu-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2.25rem;
  padding: 0.2rem 0.55rem 0.2rem 0.25rem;
  border: 1px solid transparent;
  border-radius: 999px;
  font-family: inherit;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0f172a;
  background: transparent;
  cursor: pointer;
}

.user-menu-trigger:hover {
  background: rgba(15, 23, 42, 0.05);
  border-color: rgba(15, 23, 42, 0.06);
}

.user-name {
  max-width: 7rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-arrow {
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.menu-arrow.is-open {
  transform: rotate(180deg);
  color: #0d9488;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  z-index: 100;
  min-width: 220px;
  padding: 0.375rem;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 14px;
  background: white;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.06),
    0 16px 24px -4px rgba(0, 0, 0, 0.08);
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.dropdown-user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}

.dropdown-user-role {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #94a3b8;
}

.dropdown-divider {
  height: 1px;
  margin: 0.25rem 0;
  background: rgba(15, 23, 42, 0.06);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  text-align: left;
  background: transparent;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(15, 23, 42, 0.04);
  color: #0f172a;
}

.dropdown-item.logout-item {
  color: #dc2626;
}

.dropdown-item.logout-item:hover {
  background: rgba(239, 68, 68, 0.06);
  color: #b91c1c;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.18s ease;
  transform-origin: top right;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 0.875rem;
  }

  .header-divider,
  .page-title {
    display: none;
  }
}

@media (max-width: 640px) {
  .logo-name,
  .user-name {
    display: none;
  }

  .header-right {
    gap: 0.45rem;
  }
}
</style>
