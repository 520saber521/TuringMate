# TuringMate Design System

> TuringMate 前端设计系统 - 统一的设计语言和组件库

## 目录

1. [设计原则](#设计原则)
2. [色彩系统](#色彩系统)
3. [排版系统](#排版系统)
4. [间距系统](#间距系统)
5. [圆角系统](#圆角系统)
6. [阴影系统](#阴影系统)
7. [玻璃态效果](#玻璃态效果)
8. [过渡动画](#过渡动画)
9. [组件库](#组件库)
10. [响应式规则](#响应式规则)

---

## 1. 设计原则

### 核心价值观
- **清晰性**: 界面信息层次分明，易于理解
- **一致性**: 统一的设计语言贯穿整个产品
- **可访问性**: 确保所有用户都能顺畅使用
- **性能优先**: 轻量级设计，快速加载

### 设计风格
- **现代简洁**: 简洁的视觉语言，减少视觉噪音
- **毛玻璃效果**: 使用玻璃态效果增加层次感
- **柔和渐变**: 使用柔和的渐变过渡，避免生硬边界
- **微交互**: 精致的悬停和点击反馈

---

## 2. 色彩系统

### 主色调 (Primary)

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--color-primary` | `#7C3AED` (600) | 主按钮、链接、强调文字 |
| `--color-primary-50` | `#f5f3ff` | 背景、悬停状态 |
| `--color-primary-100` | `#ede9fe` | 边框、分割线 |
| `--color-primary-400` | `#a78bfa` | 图标、次要强调 |
| `--color-primary-500` | `#8b5cf6` | 主要交互元素 |
| `--color-primary-700` | `#6d28d9` | 深色按钮、文字 |

### 辅助色 (Secondary)

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--color-secondary-500` | `#06b6d4` | 次要按钮、装饰元素 |

### 功能色

| 类型 | 变量名 | 值 | 用途 |
|------|--------|-----|------|
| 成功 | `--color-success` | `#16a34a` | 成功状态、完成提示 |
| 警告 | `--color-warning` | `#d97706` | 警告提示、待处理 |
| 危险 | `--color-danger` | `#dc2626` | 错误状态、删除操作 |
| 信息 | `--color-info` | `#2563eb` | 信息提示、说明文字 |

### 中性色

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--color-text-primary` | `#171717` | 主要文字 |
| `--color-text-secondary` | `#525252` | 次要文字 |
| `--color-text-tertiary` | `#a3a3a3` | 辅助文字、占位符 |
| `--color-bg-primary` | `#fafafa` | 页面背景 |
| `--color-bg-card` | `#ffffff` | 卡片背景 |
| `--color-border` | `rgba(108, 92, 231, 0.12)` | 边框 |

### 渐变预设

| 变量名 | 值 |
|--------|-----|
| `--gradient-primary` | `linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)` |
| `--gradient-text` | `linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)` |
| `--gradient-bg` | `linear-gradient(135deg, rgba(108,92,231,0.06) 0%, rgba(167,139,250,0.04) 40%, rgba(59,130,246,0.04) 100%)` |

---

## 3. 排版系统

### 字体

| 变量名 | 值 |
|--------|-----|
| `--font-family-sans` | `'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` |
| `--font-family-mono` | `'SF Mono', 'JetBrains Mono', 'Fira Code', monospace` |

### 字号

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--font-size-xs` | `0.75rem` (12px) | 辅助文字 |
| `--font-size-sm` | `0.875rem` (14px) | 正文、按钮 |
| `--font-size-base` | `1rem` (16px) | 基础文字 |
| `--font-size-lg` | `1.125rem` (18px) | 小标题 |
| `--font-size-xl` | `1.25rem` (20px) | 标题 |
| `--font-size-2xl` | `1.5rem` (24px) | 大标题 |
| `--font-size-3xl` | `1.875rem` (30px) | 页面标题 |

### 字重

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--font-weight-normal` | `400` | 正文 |
| `--font-weight-medium` | `500` | 按钮、标签 |
| `--font-weight-semibold` | `600` | 标题、强调 |
| `--font-weight-bold` | `700` | 重要标题 |

### 行高

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--line-height-tight` | `1.25` | 标题 |
| `--line-height-normal` | `1.5` | 正文 |
| `--line-height-relaxed` | `1.75` | 长文本 |

---

## 4. 间距系统

| 变量名 | 值 |
|--------|-----|
| `--spacing-0` | `0` |
| `--spacing-1` | `0.25rem` (4px) |
| `--spacing-2` | `0.5rem` (8px) |
| `--spacing-3` | `0.75rem` (12px) |
| `--spacing-4` | `1rem` (16px) |
| `--spacing-5` | `1.25rem` (20px) |
| `--spacing-6` | `1.5rem` (24px) |
| `--spacing-8` | `2rem` (32px) |
| `--spacing-10` | `2.5rem` (40px) |
| `--spacing-12` | `3rem` (48px) |
| `--spacing-16` | `4rem` (64px) |

---

## 5. 圆角系统

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--radius-sm` | `0.375rem` (6px) | 小按钮、输入框 |
| `--radius-md` | `0.5rem` (8px) | 徽章、小卡片 |
| `--radius-lg` | `0.75rem` (12px) | 按钮、输入框 |
| `--radius-xl` | `1rem` (16px) | 卡片、模态框 |
| `--radius-2xl` | `1.25rem` (20px) | 大卡片、容器 |
| `--radius-3xl` | `1.5rem` (24px) | 页面容器 |
| `--radius-full` | `9999px` | 圆形按钮、头像 |

---

## 6. 阴影系统

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--shadow-sm` | `0 1px 2px 0 rgba(108, 92, 231, 0.05)` | 轻微悬浮 |
| `--shadow-md` | `0 4px 6px -1px rgba(108, 92, 231, 0.08)` | 卡片默认 |
| `--shadow-lg` | `0 10px 15px -3px rgba(108, 92, 231, 0.1)` | 悬停效果 |
| `--shadow-xl` | `0 20px 25px -5px rgba(108, 92, 231, 0.1)` | 弹窗、下拉 |
| `--shadow-glow-sm` | `0 0 15px rgba(108, 92, 231, 0.15)` | 发光效果 |
| `--shadow-glow-md` | `0 0 30px rgba(108, 92, 231, 0.25)` | 强发光效果 |

---

## 7. 玻璃态效果

| 变量名 | 值 |
|--------|-----|
| `--glass-bg` | `rgba(255, 255, 255, 0.75)` |
| `--glass-bg-strong` | `rgba(255, 255, 255, 0.85)` |
| `--glass-border` | `rgba(255, 255, 255, 0.3)` |
| `--glass-shadow` | `0 8px 32px rgba(108, 92, 231, 0.08)` |
| `--glass-blur` | `blur(16px)` |

---

## 8. 过渡动画

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--transition-fast` | `150ms ease` | 快速交互 |
| `--transition-normal` | `250ms ease` | 常规过渡 |
| `--transition-slow` | `350ms ease` | 页面切换 |
| `--transition-bounce` | `350ms cubic-bezier(0.34, 1.56, 0.64, 1)` | 弹性效果 |

### 动画类

| 类名 | 效果 |
|------|------|
| `animate-fade-in-up` | 淡入向上 |
| `animate-fade-in` | 淡入 |
| `animate-slide-in-right` | 从右滑入 |
| `animate-bounce-in` | 弹入 |
| `animate-shake` | 抖动 |

---

## 9. 组件库

### 组件列表

| 组件 | 路径 | 说明 |
|------|------|------|
| Button | `src/components/ui/Button.vue` | 按钮组件 |
| Card | `src/components/ui/Card.vue` | 卡片组件 |
| Badge | `src/components/ui/Badge.vue` | 徽章组件 |
| Input | `src/components/ui/Input.vue` | 输入框组件 |
| Avatar | `src/components/ui/Avatar.vue` | 头像组件 |
| Progress | `src/components/ui/Progress.vue` | 进度条组件 |

### Button 组件

**属性**:
- `variant`: `primary` | `secondary` | `outline` | `ghost` | `danger` | `success` | `warning`
- `size`: `sm` | `md` | `lg`
- `disabled`: boolean
- `loading`: boolean
- `icon`: Component
- `iconRight`: Component

### Card 组件

**属性**:
- `hoverable`: boolean
- `shadow`: `none` | `sm` | `md` | `lg`
- `padding`: `none` | `sm` | `md` | `lg`

### Badge 组件

**属性**:
- `variant`: `primary` | `success` | `warning` | `danger` | `info`
- `size`: `sm` | `md`
- `icon`: Component

---

## 10. 响应式规则

### 断点定义

| 断点 | 尺寸 | 设备类型 |
|------|------|----------|
| sm | ≥ 640px | 小屏幕手机 |
| md | ≥ 768px | 平板 |
| lg | ≥ 1024px | 桌面 |
| xl | ≥ 1280px | 大屏幕 |

### 布局策略

- **移动端**: 单栏布局，底部导航
- **平板端**: 自适应布局
- **桌面端**: 侧边栏 + 主内容区域

### 安全区域

```css
.safe-area-bottom {
  padding-bottom: max(12px, env(safe-area-inset-bottom));
}
```

---

## 文件结构

```
src/
├── assets/
│   └── styles/
│       ├── tokens.css      # 设计令牌
│       └── global.css      # 全局样式
├── components/
│   ├── ui/                 # 基础组件
│   │   ├── Button.vue
│   │   ├── Card.vue
│   │   ├── Badge.vue
│   │   ├── Input.vue
│   │   ├── Avatar.vue
│   │   └── Progress.vue
│   └── layout/             # 布局组件
│       ├── AppLayout.vue
│       ├── AppHeader.vue
│       ├── AppSidebar.vue
│       └── BottomNav.vue
├── views/                  # 页面视图
├── stores/                 # 状态管理
├── api/                    # API 请求
└── types/                  # 类型定义
```

---

## 使用指南

### 引入设计令牌

```css
@import "./assets/styles/tokens.css";
```

### 使用 CSS 变量

```css
.element {
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  padding: var(--spacing-4);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}
```

### 使用组件

```vue
<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
</script>

<template>
  <Card shadow="md" padding="lg">
    <h3 class="text-lg font-semibold text-text-primary mb-4">卡片标题</h3>
    <p class="text-sm text-text-secondary mb-4">卡片内容</p>
    <Badge variant="primary" size="sm">标签</Badge>
    <Button variant="primary" class="mt-4">点击按钮</Button>
  </Card>
</template>
```

---

**版本**: v1.0.0  
**更新日期**: 2024年  
**适用项目**: TuringMate 前端应用
