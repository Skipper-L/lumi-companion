<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  CalendarDays,
  ChevronRight,
  Heart,
  MessageCircle,
  Plus,
  Settings,
  Sparkles,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'

// Keep requests on the current host so Vite/ngrok can proxy /api to FastAPI.
const API_BASE_URL = ''

const router = useRouter()

const activeTab = ref('overview')
const checkedIn = ref(false)
const loading = ref(true)
const errorMessage = ref('')
const diaryEntries = ref([])
const selectedDiaryDate = ref('')
const diaryContent = ref('')
const diarySaving = ref(false)

const todayIso = computed(() => {
  const date = new Date()
  const offset = date.getTimezoneOffset()
  return new Date(date.getTime() - offset * 60000).toISOString().slice(0, 10)
})

const currentUser = ref({
  username: '你',
  email: '',
})

const profileSummary = ref({
  chat_character_count: 0,
  favorite_count: 0,
  login_day_count: 0,
})

const wallpaperUrl = new URL(
  '../assets/images/profile-wallpaper.jpg',
  import.meta.url,
).href

const currentDate = computed(() => {
  const date = new Date()

  return `${String(date.getMonth() + 1).padStart(2, '0')} / ${String(
    date.getDate(),
  ).padStart(2, '0')}`
})

const userAvatarText = computed(() => {
  return currentUser.value.username?.slice(0, 1) || '你'
})

const selectedCharacter = computed(() => {
  const saved = localStorage.getItem('selected_character')

  if (saved) {
    try {
      return JSON.parse(saved)
    } catch {
      return {
        name: '知夏',
        avatar: '知',
        subtitle: '温柔倾听者',
      }
    }
  }

  return {
    name: '知夏',
    avatar: '知',
    subtitle: '温柔倾听者',
  }
})

function getAuthHeaders() {
  const token = localStorage.getItem('lumi_access_token')

  return {
    Authorization: `Bearer ${token}`,
  }
}

function goToLogin() {
  localStorage.removeItem('lumi_access_token')
  localStorage.removeItem('lumi_current_user')

  router.replace({
    path: '/login',
    query: {
      redirect: '/profile',
    },
  })
}

async function loadProfileSummary() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/profile/summary`,
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
      throw new Error(result.detail || '读取我的空间数据失败。')
    }

    currentUser.value = result.data.user
    profileSummary.value = {
      chat_character_count: result.data.chat_character_count || 0,
      favorite_count: result.data.favorite_count || 0,
      login_day_count: result.data.login_day_count || 0,
    }

    // 同步更新左下角账号卡片读取的数据
    localStorage.setItem(
      'lumi_current_user',
      JSON.stringify(result.data.user),
    )
  } catch (error) {
    errorMessage.value =
      error.message || '无法连接后端，请确认 FastAPI 后端正在运行。'
  } finally {
    loading.value = false
  }
}

function checkIn() {
  checkedIn.value = true
}

function formatDiaryDate(dateText) {
  const date = new Date(`${dateText}T00:00:00`)
  return Number.isNaN(date.getTime())
    ? dateText
    : date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
}

function selectDiaryEntry(entry) {
  selectedDiaryDate.value = entry.diary_date
  diaryContent.value = entry.content
}

async function loadDiaries() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/profile/diaries`, {
      headers: getAuthHeaders(),
    })
    if (response.status === 401) {
      goToLogin()
      return
    }
    const result = await response.json()
    if (!response.ok || !result.success) {
      throw new Error(result.detail || '读取日记失败。')
    }
    diaryEntries.value = result.data || []
    const todayEntry = diaryEntries.value.find(
      (entry) => entry.diary_date === todayIso.value,
    )
    selectDiaryEntry(todayEntry || {
      diary_date: todayIso.value,
      content: '',
    })
  } catch (error) {
    errorMessage.value = error.message || '读取日记失败。'
  }
}

async function saveDiary() {
  const content = diaryContent.value.trim()
  if (!content || diarySaving.value) return

  diarySaving.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(`${API_BASE_URL}/api/profile/diaries`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        diary_date: selectedDiaryDate.value || todayIso.value,
        content,
      }),
    })
    if (response.status === 401) {
      goToLogin()
      return
    }
    const result = await response.json()
    if (!response.ok || !result.success) {
      throw new Error(result.detail || '保存日记失败。')
    }
    const saved = result.data
    const index = diaryEntries.value.findIndex(
      (entry) => entry.diary_date === saved.diary_date,
    )
    if (index >= 0) diaryEntries.value[index] = saved
    else diaryEntries.value.unshift(saved)
    selectedDiaryDate.value = saved.diary_date
    diaryContent.value = saved.content
  } catch (error) {
    errorMessage.value = error.message || '保存日记失败。'
  } finally {
    diarySaving.value = false
  }
}

onMounted(() => {
  loadProfileSummary()
  loadDiaries()
})
</script>

<template>
  <PageLayout>
    <main
      class="profile-page"
      :style="{ '--wallpaper-url': `url(${wallpaperUrl})` }"
    >
      <section class="profile-hero">
        <div class="hero-top">
          <span class="space-badge">
            <Sparkles :size="15" />
            MY QUIET SPACE
          </span>

          <button class="settings-button" type="button" title="设置">
            <Settings :size="19" />
          </button>
        </div>

        <div class="hero-content">
          <div class="user-avatar">
            {{ userAvatarText }}
          </div>

          <div>
            <h1>
              {{ currentUser.username }}，今天也请好好照顾自己。
            </h1>
          </div>
        </div>
      </section>

      <section class="profile-content">
        <nav class="profile-tabs">
          <button
            type="button"
            :class="{ active: activeTab === 'overview' }"
            @click="activeTab = 'overview'"
          >
            <Sparkles :size="17" />
            空间概览
          </button>

          <button
            type="button"
            :class="{ active: activeTab === 'diary' }"
            @click="activeTab = 'diary'"
          >
            <CalendarDays :size="17" />
            情绪日记
          </button>
        </nav>

        <p v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </p>

        <section v-if="loading" class="loading-card">
          <Sparkles :size="32" class="loading-icon" />
          <p>正在读取你的陪伴数据…</p>
        </section>

        <template v-else-if="activeTab === 'overview'">
          <section class="stats-grid">
            <article class="glass-card stat-card">
              <span class="stat-icon purple">
                <MessageCircle :size="20" />
              </span>

              <div>
                <strong>{{ profileSummary.chat_character_count }}</strong>
                <p>位陪伴角色</p>
              </div>

              <small>聊过的不同角色</small>
            </article>

            <article class="glass-card stat-card">
              <span class="stat-icon pink">
                <Heart :size="20" />
              </span>

              <div>
                <strong>{{ profileSummary.favorite_count }}</strong>
                <p>个共同回忆</p>
              </div>

              <small>收藏的陪伴角色</small>
            </article>

            <article class="glass-card stat-card">
              <span class="stat-icon green">
                <CalendarDays :size="20" />
              </span>

              <div>
                <strong>{{ profileSummary.login_day_count }}</strong>
                <p>天陪伴记录</p>
              </div>

              <small>每天登录自动记录</small>
            </article>
          </section>

          <section class="two-column">
            <article class="glass-card section-card">
              <div class="section-heading">
                <div>
                  <p>当前最常陪伴你的角色</p>
                  <h2>我的陪伴者</h2>
                </div>

                <RouterLink to="/characters">
                  去看看
                  <ChevronRight :size="16" />
                </RouterLink>
              </div>

              <div class="favorite-character">
                <div class="character-avatar">
                  {{ selectedCharacter.avatar }}
                </div>

                <div>
                  <h3>{{ selectedCharacter.name }}</h3>
                  <p>{{ selectedCharacter.subtitle }}</p>
                  <span><i></i>正在等待你的消息</span>
                </div>

                <RouterLink class="chat-now" to="/chat">
                  继续聊天
                </RouterLink>
              </div>
            </article>

            <article class="glass-card section-card">
              <div class="section-heading">
                <div>
                  <p>给今天留下一点痕迹</p>
                  <h2>心情打卡</h2>
                </div>

                <span class="date">{{ currentDate }}</span>
              </div>

              <template v-if="!checkedIn">
                <p class="checkin-copy">
                  此刻的你，最接近哪一种心情？
                </p>

                <div class="mood-buttons">
                  <button type="button" @click="checkIn">平静</button>
                  <button type="button" @click="checkIn">疲惫</button>
                  <button type="button" @click="checkIn">开心</button>
                  <button type="button" @click="checkIn">复杂</button>
                </div>
              </template>

              <div v-else class="checked-result">
                <span>✦</span>

                <div>
                  <strong>已记录今天的心情</strong>
                  <p>感谢你愿意留意自己的感受。</p>
                </div>
              </div>
            </article>
          </section>

        </template>

        <template v-else>
          <section class="diary-layout">
            <article class="glass-card section-card diary-card">
              <p class="diary-label">
                {{ selectedDiaryDate === todayIso ? 'TODAY' : 'DIARY' }} ·
                {{ formatDiaryDate(selectedDiaryDate || todayIso) }}
              </p>

              <h2>写给这一天的自己</h2>

              <textarea
                v-model="diaryContent"
                rows="9"
                placeholder="今天发生了什么？你可以不用写得很好，只要写下真实的感受就够了…"
              ></textarea>

              <div class="diary-footer">
                <span>每一天的内容都会单独保存，可在右侧历史记录中查看。</span>
                <button type="button" :disabled="diarySaving" @click="saveDiary">
                  {{ diarySaving ? '保存中…' : '保存这一页' }}
                </button>
              </div>
            </article>

            <aside class="glass-card diary-history">
              <div class="history-heading">
                <span>☾</span>
                <div>
                  <h3>历史日记</h3>
                  <p>点击日期查看当天内容</p>
                </div>
              </div>
              <div v-if="diaryEntries.length" class="diary-date-list">
                <button
                  v-for="entry in diaryEntries"
                  :key="entry.diary_date"
                  type="button"
                  :class="{ active: selectedDiaryDate === entry.diary_date }"
                  @click="selectDiaryEntry(entry)"
                >
                  <span>{{ formatDiaryDate(entry.diary_date) }}</span>
                  <ChevronRight :size="15" />
                </button>
              </div>
              <p v-else class="history-empty">还没有保存过日记。</p>
            </aside>
          </section>
        </template>
      </section>
    </main>
  </PageLayout>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
  color: #f7fffb;
  background-image: var(--wallpaper-url);
  background-position: center;
  background-size: cover;
  background-attachment: fixed;
}

.profile-hero {
  min-height: 330px;
  padding: 32px clamp(24px, 7vw, 90px);
}

.hero-top,
.hero-content,
.section-heading,
.favorite-character,
.memory-tip,
.diary-footer,
.privacy-footer {
  display: flex;
}

.hero-top,
.section-heading,
.diary-footer,
.privacy-footer {
  justify-content: space-between;
}

.space-badge,
.settings-button {
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.48);
  background: rgba(15, 34, 38, 0.22);
  backdrop-filter: blur(4px);
}

.space-badge {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  padding: 8px 11px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.2px;
}

.settings-button {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 12px;
  cursor: pointer;
}

.hero-content {
  justify-content: flex-start;
  gap: 18px;
  align-items: center;
  margin-top: 125px;
}

.user-avatar {
  display: grid;
  width: 66px;
  height: 66px;
  flex: 0 0 auto;
  place-items: center;
  border: 3px solid rgba(255, 255, 255, 0.78);
  border-radius: 24px;
  color: white;
  background: linear-gradient(135deg, #76cbb6, #4c91cd);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.3);
  font-size: 23px;
  font-weight: 800;
}

.hero-content h1 {
  margin: 0;
  color: white;
  font-size: clamp(27px, 3.3vw, 43px);
  letter-spacing: -1.2px;
  text-shadow: 0 2px 7px rgba(0, 0, 0, 0.8);
}

.profile-content {
  width: min(1120px, 100%);
  margin: 0 auto;
  padding: 31px clamp(22px, 6vw, 72px) 70px;
}

.profile-tabs {
  display: flex;
  gap: 6px;
  width: fit-content;
  margin-bottom: 28px;
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.38);
  border-radius: 14px;
  background: rgba(17, 42, 43, 0.32);
  backdrop-filter: blur(4px);
}

.profile-tabs button {
  display: flex;
  gap: 7px;
  align-items: center;
  padding: 10px 12px;
  border: 0;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  background: transparent;
  font-size: 12px;
  font-weight: 700;
}

.profile-tabs button.active {
  color: #123e38;
  background: rgba(223, 250, 235, 0.84);
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.32);
  background: rgba(14, 36, 38, 0.25);
  box-shadow: 0 7px 20px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(3px);
}

.error-message {
  margin: 0 0 16px;
  padding: 11px 13px;
  border: 1px solid rgba(255, 164, 185, 0.35);
  border-radius: 12px;
  color: #ffe3ea;
  background: rgba(126, 31, 61, 0.5);
  font-size: 13px;
}

.loading-card,
.empty-page {
  display: grid;
  min-height: 260px;
  place-content: center;
  justify-items: center;
  border-radius: 18px;
  text-align: center;
}

.loading-card p,
.empty-page p {
  color: #e0f0e8;
}

.loading-icon {
  animation: spin 0.9s linear infinite;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.stat-card {
  position: relative;
  display: flex;
  gap: 12px;
  align-items: center;
  min-height: 108px;
  padding: 19px;
  border-radius: 18px;
}

.stat-icon {
  display: grid;
  width: 40px;
  height: 40px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 13px;
}

.purple {
  color: #c2b4ff;
  background: rgba(148, 124, 255, 0.25);
}

.pink {
  color: #ffb9d2;
  background: rgba(255, 119, 173, 0.23);
}

.green {
  color: #72e3bd;
  background: rgba(77, 206, 160, 0.18);
}

.stat-card strong {
  display: block;
  color: white;
  font-size: 25px;
}

.stat-card p,
.stat-card small,
.section-heading p {
  color: #e0f0e8;
  font-size: 11px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
}

.stat-card p {
  margin: 2px 0 0;
}

.stat-card small {
  position: absolute;
  right: 15px;
  bottom: 13px;
}

.two-column,
.diary-layout {
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
  gap: 15px;
  margin-top: 15px;
}

.section-card {
  padding: 23px;
  border-radius: 18px;
}

.section-heading {
  align-items: flex-start;
}

.section-heading h2,
.empty-page h2,
.diary-card h2,
.diary-tip h3 {
  margin: 0;
  color: white;
}

.section-heading p {
  margin: 0 0 7px;
}

.section-heading a,
.text-button {
  display: flex;
  gap: 3px;
  align-items: center;
  border: 0;
  color: #b5f4d6;
  cursor: pointer;
  background: transparent;
  font-size: 11px;
  font-weight: 700;
  text-decoration: none;
}

.favorite-character {
  gap: 12px;
  align-items: center;
  margin-top: 23px;
  padding: 13px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 14px;
  background: rgba(230, 239, 255, 0.1);
}

.character-avatar {
  display: grid;
  width: 44px;
  height: 44px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 15px;
  color: white;
  background: linear-gradient(145deg, #a187e1, #7162ba);
  font-size: 17px;
  font-weight: 800;
}

.favorite-character h3 {
  margin: 0;
  color: white;
  font-size: 15px;
}

.favorite-character p,
.favorite-character span,
.checkin-copy,
.checked-result p,
.memory-tip p,
.diary-tip p {
  color: #e0f0e8;
  font-size: 11px;
}

.favorite-character p {
  margin: 3px 0;
}

.favorite-character span {
  display: flex;
  gap: 5px;
  align-items: center;
}

.favorite-character span i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #56d5a7;
}

.chat-now,
.empty-page a {
  margin-left: auto;
  padding: 9px 11px;
  border-radius: 9px;
  color: #153c35;
  background: rgba(168, 239, 203, 0.9);
  font-size: 11px;
  font-weight: 800;
  text-decoration: none;
}

.date {
  padding: 5px 7px;
  border-radius: 7px;
  color: #153e36;
  background: rgba(215, 249, 232, 0.78);
  font-size: 10px;
}

.checkin-copy {
  margin: 21px 0 13px;
  font-size: 13px;
}

.mood-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.mood-buttons button {
  padding: 8px 10px;
  border: 1px solid rgba(255, 255, 255, 0.33);
  border-radius: 9px;
  color: white;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.06);
  font-size: 11px;
}

.checked-result {
  display: flex;
  gap: 9px;
  align-items: center;
  margin-top: 21px;
  padding: 13px;
  border-radius: 12px;
  background: rgba(143, 226, 186, 0.12);
}

.checked-result strong {
  color: white;
  font-size: 12px;
}

.checked-result p {
  margin: 4px 0 0;
}

.memory-preview {
  margin-top: 15px;
}

.memory-tip {
  gap: 13px;
  align-items: center;
  margin-top: 18px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  background: rgba(230, 239, 255, 0.09);
}

.memory-tip > svg {
  flex: 0 0 auto;
  color: #ffb8d0;
}

.memory-tip strong {
  display: block;
  color: white;
  font-size: 13px;
}

.memory-tip p {
  margin: 4px 0 0;
}

.memory-tip a {
  margin-left: auto;
  color: #b5f4d6;
  font-size: 11px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}

.empty-page {
  padding: 25px;
}

.empty-page h2 {
  margin: 14px 0 8px;
}

.empty-page a {
  margin: 10px 0 0;
}

.diary-layout {
  grid-template-columns: 1fr 250px;
  margin-top: 0;
}

.diary-label {
  margin: 0 0 8px;
  color: #b5f4d6;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.4px;
}

.diary-card textarea {
  width: 100%;
  margin-top: 24px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 13px;
  outline: none;
  color: white;
  background: rgba(0, 20, 22, 0.16);
  font: inherit;
  line-height: 1.7;
  resize: vertical;
}

.diary-card textarea::placeholder {
  color: #d4e7dc;
}

.diary-footer {
  align-items: center;
  margin-top: 13px;
}

.diary-footer span {
  color: #d6eadd;
  font-size: 10px;
}

.diary-footer button {
  padding: 9px 11px;
  border: 0;
  border-radius: 9px;
  color: #163e37;
  cursor: pointer;
  background: rgba(168, 239, 203, 0.9);
  font-size: 11px;
}

.diary-history {
  padding: 23px;
  border-radius: 17px;
}

.history-heading {
  display: flex;
  gap: 11px;
  align-items: center;
}

.history-heading > span {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 12px;
  color: #d2c5ff;
  background: rgba(176, 148, 255, 0.18);
  font-size: 21px;
}

.history-heading h3 {
  margin: 0;
  font-size: 15px;
}

.history-heading p,
.history-empty {
  margin: 0;
  color: #e0f0e8;
  font-size: 11px;
}

.diary-date-list {
  display: grid;
  gap: 7px;
  max-height: 250px;
  margin-top: 20px;
  overflow-y: auto;
}

.diary-date-list button {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 11px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: white;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.07);
  font: inherit;
  font-size: 11px;
  text-align: left;
}

.diary-date-list button.active,
.diary-date-list button:hover {
  border-color: rgba(182, 244, 213, 0.55);
  background: rgba(168, 239, 203, 0.2);
}

.history-empty {
  margin-top: 22px;
  line-height: 1.7;
}

.privacy-footer {
  align-items: center;
  margin-top: 31px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.36);
  color: white;
  font-size: 11px;
}

.privacy-footer div,
.privacy-footer button {
  display: flex;
  gap: 7px;
  align-items: center;
}

.privacy-footer button {
  border: 0;
  color: white;
  cursor: pointer;
  background: transparent;
  font-size: 11px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 860px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .two-column,
  .diary-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .profile-page {
    background-attachment: scroll;
  }

  .profile-hero {
    min-height: 300px;
    padding: 22px 20px;
  }

  .hero-content {
    align-items: flex-start;
    margin-top: 110px;
  }

  .hero-content h1 {
    font-size: 27px;
  }

  .user-avatar {
    width: 53px;
    height: 53px;
    border-radius: 19px;
    font-size: 18px;
  }

  .profile-content {
    padding: 21px 16px 82px;
  }

  .profile-tabs {
    width: 100%;
    overflow-x: auto;
  }

  .profile-tabs button {
    flex: 0 0 auto;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .memory-tip,
  .privacy-footer {
    align-items: flex-start;
    flex-direction: column;
  }

  .memory-tip a {
    margin-left: 0;
  }
}
</style>
