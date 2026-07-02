<template>
  <div class="community-page">
    <header class="community-hero">
      <div>
        <p class="community-eyebrow">学习社区</p>
        <h1>把卡住的问题讲清楚</h1>
        <p>按科目浏览讨论、跟进热门问题，也可以把自己的思路发出来一起拆解。</p>
      </div>
      <button class="new-discussion-btn hero-new-btn" @click="showCreate = true">
        + 发起讨论
      </button>
    </header>

    <HotTopicBanner
      :topics="store.hotTopics"
      @select="onHotTopicSelect"
    />

    <div class="community-toolbar">
      <div class="toolbar-left">
        <select v-model="filters.subject" class="filter-select" @change="load">
          <option value="">全部科目</option>
          <option value="ds">数据结构</option>
          <option value="co">计算机组成原理</option>
          <option value="os">操作系统</option>
          <option value="cn">计算机网络</option>
        </select>
        <select v-model="filters.sort" class="filter-select" @change="load">
          <option value="latest">最新</option>
          <option value="hot">最热</option>
          <option value="unresolved">未解决</option>
        </select>
      </div>
      <button class="new-discussion-btn toolbar-new-btn" @click="showCreate = true">
        + 发起讨论
      </button>
    </div>

    <div v-if="store.loading" class="loading-hint">加载中...</div>
    <div v-else-if="!store.discussions.length" class="empty-state">
      <div class="empty-state__icon">?</div>
      <h3>暂时没有匹配的讨论</h3>
      <p>换一个筛选条件，或者直接发起一个新的问题。</p>
      <button class="new-discussion-btn" @click="showCreate = true">发起讨论</button>
    </div>
    <div v-else class="discussion-list">
      <DiscussionCard
        v-for="disc in store.discussions"
        :key="disc.id"
        :discussion="disc"
        @click="openDiscussion"
      />
    </div>

    <div v-if="store.total > 20" class="pagination">
      <button
        :disabled="page <= 1"
        @click="page--; load()"
      >
        上一页
      </button>
      <span>第 {{ page }} 页 / 共 {{ Math.ceil(store.total / 20) }} 页</span>
      <button
        :disabled="page >= Math.ceil(store.total / 20)"
        @click="page++; load()"
      >
        下一页
      </button>
    </div>

    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <h3>发起讨论</h3>
        <input v-model="createForm.title" placeholder="标题" class="form-input" />
        <textarea v-model="createForm.content" placeholder="描述你的问题..." rows="5" class="form-textarea" />
        <div class="form-row">
          <select v-model="createForm.subject" class="form-select">
            <option value="">选择科目</option>
            <option value="ds">数据结构</option>
            <option value="co">计算机组成原理</option>
            <option value="os">操作系统</option>
            <option value="cn">计算机网络</option>
          </select>
          <input v-model="tagInput" placeholder="标签，用逗号分隔" class="form-input tag-field" />
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCreate = false">取消</button>
          <button class="submit-btn" :disabled="!createForm.title" @click="submitCreate">发布</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCommunityStore } from '@/stores/community'
import type { HotTopicItem } from '@/api/community'
import DiscussionCard from '@/components/community/DiscussionCard.vue'
import HotTopicBanner from '@/components/community/HotTopicBanner.vue'

const store = useCommunityStore()
const router = useRouter()

const page = ref(1)
const filters = reactive({ subject: '', sort: 'latest' })
const showCreate = ref(false)
const tagInput = ref('')
const createForm = reactive({ title: '', content: '', subject: '' })

async function load() {
  await store.fetchDiscussions({
    subject: filters.subject,
    sort: filters.sort,
    page: page.value,
  })
}

async function submitCreate() {
  const tags = tagInput.value.split(',').map(t => t.trim()).filter(Boolean)
  const disc = await store.createDiscussion({
    title: createForm.title,
    content: createForm.content,
    subject: createForm.subject,
    tags,
  })
  showCreate.value = false
  createForm.title = ''
  createForm.content = ''
  createForm.subject = ''
  tagInput.value = ''
  router.push(`/community/discussion/${disc.id}`)
}

function openDiscussion(id: string | number) {
  router.push(`/community/discussion/${id}`)
}

function onHotTopicSelect(topic: HotTopicItem) {
  filters.subject = ''
  load()
}

onMounted(async () => {
  await Promise.all([
    store.fetchHotTopics(),
    load(),
  ])
})
</script>

<style scoped>
.community-page {
  max-width: 920px;
  margin: 0 auto;
  padding: 24px 16px;
}

.community-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
}

.community-eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  color: var(--td-brand-color);
}

.community-hero h1 {
  margin: 0;
  font-size: clamp(24px, 3vw, 34px);
  font-weight: 800;
}

.community-hero p:last-child {
  max-width: 560px;
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.7;
}

.community-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.toolbar-left {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-select {
  min-width: 148px;
  padding: 8px 12px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
  font-size: 13px;
  background: var(--td-bg-color-container);
  color: var(--td-text-color-primary);
}

.new-discussion-btn {
  padding: 9px 20px;
  background: var(--td-brand-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.discussion-list {
  display: flex;
  flex-direction: column;
}

.loading-hint,
.empty-state {
  text-align: center;
  padding: 42px 24px;
  color: var(--td-text-color-placeholder);
}

.empty-state__icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 12px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: rgba(13, 148, 136, 0.1);
  color: #0d9488;
  font-size: 22px;
  font-weight: 800;
}

.empty-state h3 {
  margin: 0 0 8px;
  color: var(--td-text-color-primary);
  font-size: 17px;
}

.empty-state p {
  margin: 0 0 18px;
  font-size: 13px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  font-size: 13px;
}

.pagination button {
  padding: 6px 14px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
  background: var(--td-bg-color-container);
  cursor: pointer;
  color: var(--td-text-color-primary);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: var(--td-bg-color-container);
  border-radius: 14px;
  padding: 24px;
  width: 520px;
  max-width: 100%;
}

.modal h3 {
  margin: 0 0 16px;
  font-size: 18px;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 12px;
  background: var(--td-bg-color-container);
  color: var(--td-text-color-primary);
  box-sizing: border-box;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.form-row {
  display: flex;
  gap: 8px;
}

.form-select {
  width: 168px;
  flex-shrink: 0;
}

.tag-field {
  flex: 1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.cancel-btn {
  padding: 8px 20px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
  background: var(--td-bg-color-container);
  cursor: pointer;
  color: var(--td-text-color-primary);
}

.submit-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  background: var(--td-brand-color);
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: default;
}

@media (max-width: 767px) {
  .community-page {
    padding: 14px 10px;
  }

  .community-hero {
    align-items: stretch;
    flex-direction: column;
  }

  .hero-new-btn {
    width: 100%;
  }

  .toolbar-new-btn {
    display: none;
  }

  .filter-select {
    flex: 1;
    min-width: 0;
  }

  .form-row {
    flex-direction: column;
  }

  .form-select {
    width: 100%;
  }
}
</style>
