<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChevronRight,
  MessageCircleHeart,
  RefreshCw,
  Sparkles,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'
import lumiMoonIcon from '../assets/lumi-default-cover.jpeg'
import { resolveImageUrl } from '../utils/imageUrl'

// Keep requests on the current host so Vite/ngrok can proxy /api to FastAPI.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const router = useRouter()

const conversations = ref([])
const loading = ref(true)
const errorMessage = ref('')

function getAuthHeaders() {
  const token = localStorage.getItem('lumi_access_token')

  return {
    Authorization: `Bearer ${token}`,
  }
}

function getCharacterImageUrl(character) {
  const image = character?.background_image
  if (!image) return lumiMoonIcon
  return resolveImageUrl(image)
}

function formatTime(dateText) {
  const date = new Date(dateText)

  if (Number.isNaN(date.getTime())) {
    return '刚刚'
  }

  const now = new Date()

  const isToday =
    now.getFullYear() === date.getFullYear() &&
    now.getMonth() === date.getMonth() &&
    now.getDate() === date.getDate()

  if (isToday) {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })
  }

  const yesterday = new Date()
  yesterday.setDate(now.getDate() - 1)

  const isYesterday =
    yesterday.getFullYear() === date.getFullYear() &&
    yesterday.getMonth() === date.getMonth() &&
    yesterday.getDate() === date.getDate()

  if (isYesterday) {
    return '昨天'
  }

  return date.toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
  })
}

function goToLogin() {
  localStorage.removeItem('lumi_access_token')
  localStorage.removeItem('lumi_current_user')

  router.replace({
    path: '/login',
    query: {
      redirect: '/conversations',
    },
  })
}

async function loadConversations() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/conversations`,
      {
        headers: getAuthHeaders(),
      },
    )

    if (response.status === 401) {
      goToLogin()
      return
    }

    const result = await response.json()

    if (!response.ok || !result.success) {
      throw new Error(result.detail || '读取会话记录失败。')
    }

    conversations.value = result.data || []
  } catch (error) {
    errorMessage.value =
      error.message || '无法连接后端，请确认 FastAPI 正在运行。'
  } finally {
    loading.value = false
  }
}

function openConversation(conversation) {
  localStorage.setItem(
    'selected_character',
    JSON.stringify(conversation.character),
  )

  router.push({
    name: 'conversation-chat',
    params: {
      characterId: conversation.character.id,
    },
  })
}

onMounted(() => {
  loadConversations()
})
</script>

<template>
  <PageLayout>
    <main class="conversation-page">
      <header class="page-header">
        <div>
          <p class="eyebrow">
            <MessageCircleHeart :size="15" />
            CONVERSATION HISTORY
          </p>

         

         
        </div>

        <button
          class="refresh-button"
          type="button"
          :disabled="loading"
          @click="loadConversations"
        >
          <RefreshCw
            :size="16"
            :class="{ spinning: loading }"
          />
          刷新
        </button>
      </header>

      <p v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </p>

      <section v-if="loading" class="loading-state">
        <Sparkles :size="30" class="spinning" />
        <span>正在读取会话记录…</span>
      </section>

      <section
        v-else-if="conversations.length"
        class="conversation-list"
      >
        <button
          v-for="conversation in conversations"
          :key="conversation.conversation_id"
          class="conversation-row"
          type="button"
          @click="openConversation(conversation)"
        >
          <div
            class="character-icon"
            :class="conversation.character.color"
          >
            <img
              :src="getCharacterImageUrl(conversation.character)"
              :alt="`${conversation.character.name} 头像`"
            />
          </div>

          <strong class="character-name">
            {{ conversation.character.name }}
          </strong>

          <p class="last-message">
            “{{ conversation.last_message || '开始一段新的聊天吧。' }}”
          </p>

          <time>
            {{ formatTime(conversation.updated_at) }}
          </time>

          <ChevronRight class="row-arrow" :size="18" />
        </button>
      </section>

      <section v-else class="empty-state">
        <MessageCircleHeart :size="42" />

        <h2>还没有会话记录</h2>

        <p>去角色广场选择一位陪伴者，开始第一段聊天吧。</p>

        <RouterLink to="/characters">
          前往角色广场
        </RouterLink>
      </section>
    </main>
  </PageLayout>
</template>

<style scoped>
.conversation-page {
  width: min(1500px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  box-sizing: border-box;
  padding: 72px 56px 80px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  margin-bottom: 45px;
}

.eyebrow {
  display: flex;
  gap: 7px;
  align-items: center;
  margin: 0 0 13px;
  color: #a89dff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.7px;
}

h1,
h2,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 12px;
  color: #f3f2ff;
  font-size: clamp(35px, 4vw, 51px);
  letter-spacing: -1.6px;
}

.page-header > div > p:last-child {
  margin-bottom: 0;
  color: #a7b0cc;
}

.refresh-button {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  padding: 11px 14px;
  border: 1px solid rgba(180, 166, 255, 0.24);
  border-radius: 11px;
  color: #d9d6ff;
  cursor: pointer;
  background: rgba(128, 110, 255, 0.1);
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  transition: 0.2s ease;
}

.refresh-button:hover:not(:disabled) {
  color: white;
  background: rgba(128, 110, 255, 0.2);
  transform: translateY(-2px);
}

.refresh-button:disabled {
  cursor: wait;
  opacity: 0.6;
}

.error-message {
  margin: 0 0 16px;
  padding: 11px 13px;
  border: 1px solid rgba(255, 116, 150, 0.22);
  border-radius: 11px;
  color: #ffb5c7;
  background: rgba(238, 88, 130, 0.1);
  font-size: 13px;
}

.conversation-list {
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
}

.conversation-row {
  display: grid;
  grid-template-columns: 46px 120px minmax(0, 1fr) 62px 20px;
  gap: 16px;
  width: 100%;
  align-items: center;
  padding: 15px 20px;
  border: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: inherit;
  cursor: pointer;
  background: transparent;
  font: inherit;
  text-align: left;
  transition: 0.2s ease;
}

.conversation-row:last-child {
  border-bottom: 0;
}

.conversation-row:hover {
  background: linear-gradient(
    90deg,
    rgba(116, 99, 241, 0.16),
    rgba(255, 255, 255, 0.02)
  );
}

.character-icon {
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 15px;
  color: white;
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.28),
    rgba(255, 255, 255, 0.08)
  );
  font-size: 18px;
  font-weight: 800;
  overflow: hidden;
}

.character-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-icon.purple {
  box-shadow: 0 0 22px rgba(132, 104, 255, 0.3);
}

.character-icon.blue {
  box-shadow: 0 0 22px rgba(82, 156, 224, 0.28);
}

.character-icon.pink,
.character-icon.rose {
  box-shadow: 0 0 22px rgba(231, 120, 176, 0.25);
}

.character-icon.green {
  box-shadow: 0 0 22px rgba(78, 185, 156, 0.25);
}

.character-icon.yellow,
.character-icon.orange {
  box-shadow: 0 0 22px rgba(220, 174, 83, 0.25);
}

.character-name {
  overflow: hidden;
  color: #ececff;
  font-size: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.last-message {
  overflow: hidden;
  margin: 0;
  color: #b2bad3;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

time {
  color: #8893b1;
  font-size: 12px;
  text-align: right;
  white-space: nowrap;
}

.row-arrow {
  color: #929cc0;
  transition: 0.2s ease;
}

.conversation-row:hover .row-arrow {
  color: #d5ccff;
  transform: translateX(3px);
}

.loading-state,
.empty-state {
  display: grid;
  min-height: 270px;
  place-content: center;
  justify-items: center;
  border: 1px dashed rgba(255, 255, 255, 0.14);
  border-radius: 18px;
  color: #9fa9c7;
  text-align: center;
}

.loading-state {
  gap: 13px;
}

.empty-state h2 {
  margin: 16px 0 8px;
  color: #e9e9f8;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 13px;
}

.empty-state a {
  padding: 11px 15px;
  border-radius: 11px;
  color: white;
  background: linear-gradient(135deg, #7768ff, #b86ee9);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

.spinning {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 700px) {
  .conversation-page {
    padding: 46px 20px 85px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
    margin-bottom: 30px;
  }

  .conversation-row {
    grid-template-columns: 42px minmax(0, 1fr) 20px;
    gap: 12px;
    padding: 14px;
  }

  .character-icon {
    width: 42px;
    height: 42px;
  }

  .character-name {
    grid-column: 2;
  }

  .last-message {
    grid-row: 2;
    grid-column: 2;
  }

  time {
    grid-row: 2;
    grid-column: 3;
    font-size: 10px;
  }

  .row-arrow {
    grid-row: 1;
    grid-column: 3;
  }
}
/* 会话记录主标题：紫蓝星夜字体 */
h1 {
  display: inline-block;
  margin: 0;
  color: #d8d3ff;
  background: linear-gradient(
    115deg,
    #dcd7ff 0%,
    #a892ff 28%,
    #7b9dff 55%,
    #c28cff 78%,
    #edeaff 100%
  );
  background-size: 220% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family:
    "STSong",
    "Songti SC",
    "Noto Serif SC",
    "Microsoft YaHei",
    serif;
  font-size: clamp(34px, 3.4vw, 50px);
  font-weight: 800;
  letter-spacing: 0.08em;
  line-height: 1.15;
  text-shadow:
    0 0 18px rgba(139, 119, 255, 0.18),
    0 0 32px rgba(91, 151, 255, 0.1);
  animation: conversation-title-shine 7s ease-in-out infinite;
}

@keyframes conversation-title-shine {
  0%,
  100% {
    background-position: 0% center;
    filter: brightness(1);
  }

  50% {
    background-position: 100% center;
    filter: brightness(1.16);
  }
}

@media (prefers-reduced-motion: reduce) {
  h1 {
    animation: none;
  }
}
</style>
