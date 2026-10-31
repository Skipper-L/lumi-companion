<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Heart,
  Mars,
  MessageCircleHeart,
  Search,
  SlidersHorizontal,
  Sparkles,
  Venus,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'
import lumiMoonIcon from '../assets/lumi-default-cover.jpeg'
import { resolveImageUrl } from '../utils/imageUrl'

// Keep requests on the current host so Vite/ngrok can proxy /api to FastAPI.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const router = useRouter()

const activeCategory = ref('全部')
const categoryList = ref(null)
const searchText = ref('')
const publicCustomCharacters = ref([])
const favoriteIds = ref([])
const chattedCharacterIds = ref([])
const loading = ref(true)
const errorMessage = ref('')
const CHARACTER_SQUARE_SCROLL_KEY = 'character_square_scroll_position'

const officialCharacters = [
  {
    id: 'zhixia',
    name: '知夏',
    subtitle: '温柔倾听者',
    category: '治愈',
    tags: ['耐心', '共情', '温柔'],
    message: '不用急着变好，先让我陪你坐一会儿。',
    description: '知夏是一位温柔而耐心的倾听者。她会陪你慢慢整理情绪，不催促、不评判，让每一次倾诉都能被认真接住。',
    status: '正在听雨',
    color: 'purple',
    avatar: '知',
    online: true,
    gender: 'female',
  },
  {
    id: 'linzhou',
    name: '临舟',
    subtitle: '深夜树洞',
    category: '倾诉',
    tags: ['安静', '可靠', '真诚'],
    message: '想说什么都可以，我会认真听完。',
    description: '临舟像深夜里始终亮着的一盏灯，安静、可靠，也愿意认真听完你的心事。适合在想倾诉或需要一点安静陪伴时相遇。',
    status: '等你开口',
    color: 'blue',
    avatar: '临',
    online: true,
    gender: 'male',
  },
  {
    id: 'xiaoye',
    name: '小夜',
    subtitle: '晚安陪伴者',
    category: '睡前',
    tags: ['轻声', '治愈', '晚安'],
    message: '今天辛苦了。睡前的时间，交给我吧。',
    description: '小夜会用轻柔的语气陪你结束一天。无论是睡前的疲惫、琐碎的心事，还是一句简单的晚安，都可以放心交给她。',
    status: '准备了一首晚安歌',
    color: 'pink',
    avatar: '夜',
    online: false,
    gender: 'female',
  },
  {
    id: 'chuchen',
    name: '初晨',
    subtitle: '元气搭子',
    category: '学习',
    tags: ['鼓励', '专注', '积极'],
    message: '把今天的小目标告诉我，我们一起完成。',
    description: '初晨是一位元气满满的学习搭子，擅长把复杂目标拆成容易开始的小步骤，陪你专注完成每一个今天。',
    status: '正在整理计划',
    color: 'yellow',
    avatar: '晨',
    online: true,
    gender: 'male',
  },
  {
    id: 'wanwan',
    name: '晚晚',
    subtitle: '浪漫来信人',
    category: '恋爱',
    tags: ['浪漫', '细腻', '心动'],
    message: '如果你愿意，今晚让我写一封信给你。',
    description: '晚晚擅长用细腻浪漫的方式回应你的心情。她愿意陪你收集日常里的小心动，也愿意认真倾听那些说不出口的想念。',
    status: '想和你散步',
    color: 'rose',
    avatar: '晚',
    online: true,
    gender: 'female',
  },
  {
    id: 'anran',
    name: '安然',
    subtitle: '情绪整理师',
    category: '治愈',
    tags: ['理性', '松弛', '清醒'],
    message: '我们不急着找答案，先理一理心里的声音。',
    description: '安然是一位情绪整理师，温和而清醒。她不会急着替你下结论，而是会陪你从纷乱的感受里找回自己的节奏。',
    status: '正在晒太阳',
    color: 'green',
    avatar: '安',
    online: false,
    gender: 'female',
  },
]

const allCharacters = computed(() => {
  return [...publicCustomCharacters.value, ...officialCharacters]
})

const categories = computed(() => {
  const allTags = allCharacters.value.flatMap((character) => character.tags || [])
  return ['全部', ...Array.from(new Set(allTags.filter(Boolean)))]
})

function selectCategory(category, event) {
  activeCategory.value = category

  // 点击靠近右边缘的标签时，将该标签平滑带到可视区域，继续显示后续标签。
  const container = categoryList.value
  const button = event.currentTarget
  if (!container || !button) return

  const containerRect = container.getBoundingClientRect()
  const buttonRect = button.getBoundingClientRect()
  const isAtLeftEdge = buttonRect.left <= containerRect.left + 20
  const isAtRightEdge = buttonRect.right >= containerRect.right - 20
  const scrollDistance = Math.max(
    button.offsetWidth * 2,
    container.clientWidth * 0.55,
  )

  if (isAtRightEdge) {
    container.scrollBy({
      left: scrollDistance,
      behavior: 'smooth',
    })
  } else if (isAtLeftEdge) {
    container.scrollBy({
      left: -scrollDistance,
      behavior: 'smooth',
    })
  }
}

const filteredCharacters = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()

  return allCharacters.value.filter((character) => {
    const categoryMatched =
      activeCategory.value === '全部' ||
      (character.tags || []).includes(activeCategory.value)

    const textMatched =
      !keyword ||
      character.name.includes(keyword) ||
      character.subtitle.includes(keyword) ||
      character.description?.includes(keyword) ||
      character.tags.some((tag) => tag.includes(keyword))

    return categoryMatched && textMatched
  })
})

function getHeaders() {
  const token = localStorage.getItem('lumi_access_token')

  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

function isFavorite(characterId) {
  return favoriteIds.value.includes(characterId)
}

function hasChatHistory(characterId) {
  return chattedCharacterIds.value.includes(characterId)
}

function getBackgroundImageUrl(character) {
  return resolveImageUrl(character.background_image)
}

async function loadCharacters() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [publicResponse, favoriteResponse, conversationResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/api/custom-characters/public`),
      fetch(`${API_BASE_URL}/api/favorites`, {
        headers: getHeaders(),
      }),
      fetch(`${API_BASE_URL}/api/conversations`, {
        headers: getHeaders(),
      }),
    ])

    const publicResult = await publicResponse.json()
    const favoriteResult = await favoriteResponse.json()
    const conversationResult = conversationResponse.ok
      ? await conversationResponse.json()
      : null

    if (!publicResponse.ok) {
      throw new Error(publicResult.detail || '获取公开角色失败。')
    }

    publicCustomCharacters.value = publicResult.data || []

    if (favoriteResponse.ok) {
      favoriteIds.value = favoriteResult.data || []
    }

    // 会话状态仅属于当前登录账号：有历史消息才在广场卡片显示提示。
    if (conversationResult?.success) {
      chattedCharacterIds.value = (conversationResult.data || []).map(
        (conversation) => conversation.character_id,
      )
    }
  } catch (error) {
    errorMessage.value = error.message || '无法连接后端，请确认后端正在运行。'
  } finally {
    loading.value = false
  }
}

async function toggleFavorite(character) {
  const wasFavorite = isFavorite(character.id)

  errorMessage.value = ''

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/favorites/${character.id}`,
      {
        method: wasFavorite ? 'DELETE' : 'POST',
        headers: getHeaders(),
      },
    )

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.detail || '收藏操作失败。')
    }

    if (wasFavorite) {
      favoriteIds.value = favoriteIds.value.filter(
        (id) => id !== character.id,
      )
    } else {
      favoriteIds.value = [...favoriteIds.value, character.id]
    }
  } catch (error) {
    errorMessage.value = error.message || '收藏操作失败，请稍后重试。'
  }
}

function selectCharacter(character) {
  sessionStorage.setItem(
    CHARACTER_SQUARE_SCROLL_KEY,
    JSON.stringify({
      top: window.scrollY,
      categoryLeft: categoryList.value?.scrollLeft || 0,
    }),
  )

  localStorage.setItem(
    'selected_character',
    JSON.stringify(character),
  )

  router.push({
    path: '/chat',
    query: {
      character: character.id,
      from: 'characters',
    },
  })
}

async function restoreScrollPosition() {
  const saved = sessionStorage.getItem(CHARACTER_SQUARE_SCROLL_KEY)
  if (!saved) return

  try {
    const position = JSON.parse(saved)
    await nextTick()
    window.scrollTo(0, Number(position.top) || 0)
    if (categoryList.value) {
      categoryList.value.scrollLeft = Number(position.categoryLeft) || 0
    }
  } catch {
    // 忽略无效的旧滚动位置，避免影响角色广场正常打开。
  } finally {
    sessionStorage.removeItem(CHARACTER_SQUARE_SCROLL_KEY)
  }
}

onMounted(async () => {
  await loadCharacters()
  await restoreScrollPosition()
})
</script>

<template>
  <PageLayout>
    <main class="character-page">
      <section class="filter-section">
        <div ref="categoryList" class="categories">
          <button
            v-for="category in categories"
            :key="category"
            type="button"
            :class="{ active: activeCategory === category }"
            @click="selectCategory(category, $event)"
          >
            {{ category }}
          </button>
        </div>

        <label class="search-box">
          <Search :size="18" />

          <input
            v-model="searchText"
            type="text"
            placeholder="搜索角色或特质"
          />
        </label>
      </section>

      <p v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </p>

      <section class="recommendation">
        <div class="section-title">
          <div>
            <p></p>
            
          </div>

         
        </div>

        <div v-if="loading" class="empty-state">
          <Sparkles :size="34" class="loading-icon" />
          <h3>正在加载角色…</h3>
        </div>

        <div
          v-else-if="filteredCharacters.length"
          class="character-grid"
        >
          <article
            v-for="character in filteredCharacters"
            :key="character.id"
            class="character-card"
            :class="character.color"
            @click="selectCharacter(character)"
          >
            <div class="card-background"></div>
            <img
              v-if="!character.background_image"
              class="default-lumi-cover"
              :src="lumiMoonIcon"
              alt="Lumi 默认角色封面"
            />
            <div
              v-if="character.background_image"
              class="card-cover"
              :style="{ backgroundImage: `url(&quot;${getBackgroundImageUrl(character)}&quot;)` }"
            ></div>
            <div class="card-cover-shade"></div>

            <div class="card-top">
              <button
                type="button"
                class="heart-button"
                :class="{ liked: isFavorite(character.id) }"
                :title="isFavorite(character.id) ? '取消收藏' : '收藏角色'"
                @click.stop="toggleFavorite(character)"
              >
                <Heart
                  :size="20"
                  :fill="isFavorite(character.id) ? 'currentColor' : 'none'"
                />
              </button>

              <span v-if="hasChatHistory(character.id)" class="status">
                <i></i>
                正在等你的消息
              </span>
            </div>

            <div class="card-content">
              <div class="name-row">
                <h3>{{ character.name }}</h3>
                <span
                  class="gender-badge"
                  :class="character.gender === 'male' ? 'male' : 'female'"
                  :title="character.gender === 'male' ? '男性角色' : '女性角色'"
                >
                  <Mars v-if="character.gender === 'male'" :size="20" />
                  <Venus v-else :size="20" />
                </span>
              </div>

              <p class="character-description">
                {{ character.description || character.message }}
              </p>

              <span
                v-if="character.owner_username"
                class="created-by"
              >
                创建者：{{ character.owner_username }}
              </span>
            </div>
          </article>
        </div>

        <div v-else class="empty-state">
          <MessageCircleHeart :size="35" />

          <h3>暂时没有找到这个角色</h3>

          <p>换一个关键词，或者尝试选择其他场景。</p>

          <button
            type="button"
            @click="searchText = ''; activeCategory = '全部'"
          >
            查看全部角色
          </button>
        </div>
      </section>
    </main>
  </PageLayout>
</template>

<style scoped>
.character-page {
  position: relative;
  isolation: isolate;
  width: min(1680px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  box-sizing: border-box;
  padding: 72px 56px 80px;
  overflow: hidden;
  background:
    radial-gradient(circle at 15% 8%, rgba(106, 82, 218, 0.2), transparent 27%),
    radial-gradient(circle at 84% 25%, rgba(54, 123, 210, 0.14), transparent 26%),
    radial-gradient(circle at 52% 92%, rgba(112, 67, 189, 0.1), transparent 31%);
}

.character-page > * {
  position: relative;
  z-index: 1;
}

.filter-section,
.section-title,
.card-top {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.filter-section {
  align-items: center;
  margin-top: 0;
  padding: 15px 17px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
}

.categories {
  display: flex;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  overflow-y: hidden;
  gap: 8px;
  scroll-behavior: smooth;
  scrollbar-width: none;
}

.categories::-webkit-scrollbar {
  display: none;
}

.categories button {
  flex: none;
  white-space: nowrap;
  padding: 9px 14px;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #aeb7d2;
  cursor: pointer;
  background: transparent;
}

.categories button.active {
  border-color: rgba(160, 144, 255, 0.38);
  color: #fff;
  background: linear-gradient(
    135deg,
    rgba(118, 104, 255, 0.42),
    rgba(183, 110, 237, 0.22)
  );
}

.search-box {
  display: flex;
  gap: 9px;
  align-items: center;
  width: 225px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 11px;
  color: #7f89aa;
  background: rgba(8, 12, 29, 0.48);
}

.search-box input {
  width: 100%;
  padding: 0;
  border: 0;
  outline: 0;
  color: #e9eaff;
  background: transparent;
}

.error-message {
  margin: 18px 0 0;
  padding: 11px 13px;
  border: 1px solid rgba(255, 116, 150, 0.2);
  border-radius: 11px;
  color: #ffb5c7;
  background: rgba(238, 88, 130, 0.1);
  font-size: 13px;
}

.recommendation {
  margin-top: 42px;
}

.section-title {
  align-items: flex-end;
  margin-bottom: 22px;
}

.section-title p {
  margin: 0 0 7px;
  color: #8c96b6;
  font-size: 13px;
}

.section-title h2 {
  margin: 0;
  color: #e9eaff;
  font-size: 23px;
}

.filter-button {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  padding: 8px 11px;
  border: 0;
  color: #9ea8c8;
  cursor: pointer;
  background: transparent;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.character-card {
  position: relative;
  min-height: 345px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 23px;
  background: rgba(255, 255, 255, 0.045);
  cursor: pointer;
  z-index: 0;
  box-shadow:
    0 8px 22px rgba(2, 7, 25, 0.16),
    0 0 10px rgba(116, 105, 255, 0.035);
  transform: translateY(0) scale(1);
  transform-origin: center center;
  transition:
    transform 420ms cubic-bezier(0.22, 0.8, 0.25, 1),
    border-color 420ms ease,
    box-shadow 420ms ease;
}

.character-card:hover {
  z-index: 5;
  border-color: rgba(209, 201, 255, 0.32);
  transform: translateY(-4px) scale(1.1);
}

.card-background {
  position: absolute;
  top: -75px;
  left: 50%;
  width: 260px;
  height: 220px;
  border-radius: 50%;
  opacity: 0.75;
  transform: translateX(-50%);
}

.card-cover,
.card-cover-shade {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.default-lumi-cover {
  position: absolute;
  z-index: 1;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 1;
  pointer-events: none;
  filter: saturate(0.94) brightness(0.9);
}

.card-cover {
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.card-cover-shade {
  z-index: 0;
  background: linear-gradient(180deg, rgba(8, 11, 29, 0.06) 16%, rgba(9, 12, 32, 0.32) 49%, rgba(8, 10, 28, 0.96) 100%);
}

.purple .card-background {
  background: radial-gradient(circle, #886cff, transparent 66%);
}

.blue .card-background {
  background: radial-gradient(circle, #529ce0, transparent 66%);
}

.pink .card-background {
  background: radial-gradient(circle, #e778b0, transparent 66%);
}

.yellow .card-background {
  background: radial-gradient(circle, #dcae53, transparent 66%);
}

.rose .card-background {
  background: radial-gradient(circle, #ec8398, transparent 66%);
}

.green .card-background {
  background: radial-gradient(circle, #4eb99c, transparent 66%);
}

.orange .card-background {
  background: radial-gradient(circle, #e99c61, transparent 66%);
}

.card-top {
  position: relative;
  z-index: 2;
  padding: 17px;
}

.status {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  color: #c0c7e0;
  font-size: 11px;
}

.status i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #57dbbd;
  box-shadow: 0 0 8px #57dbbd;
}

.status i.offline {
  background: #8791ad;
  box-shadow: none;
}

.heart-button {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  margin: -8px -8px 0 0;
  padding: 0;
  border: 0;
  border-radius: 50%;
  color: #c7c9e8;
  cursor: pointer;
  background: rgba(11, 15, 35, 0.18);
  transition: 0.2s ease;
}

.heart-button:hover,
.heart-button.liked {
  color: #ff698f;
}

.heart-button.liked {
  background: rgba(255, 105, 143, 0.1);
  filter: drop-shadow(0 0 7px rgba(255, 87, 140, 0.3));
}

.card-content {
  position: absolute;
  z-index: 2;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18px;
  background: linear-gradient(
    transparent,
    rgba(13, 17, 40, 0.93) 28%
  );
}

.name-row {
  position: relative;
  display: flex;
  align-items: center;
}

.name-row h3 { margin: 0; }

.gender-badge {
  position: absolute;
  top: 50%;
  right: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: auto;
  height: auto;
  background: transparent;
  transform: translateY(-50%);
}

.gender-badge.male { color: #60ddff; }
.gender-badge.female { color: #ff9bb9; }

.card-content h3 {
  margin: 0;
  color: #f3f3ff;
  font-size: 22px;
}

.character-description {
  display: -webkit-box;
  min-height: 42px;
  overflow: hidden;
  margin: 11px 0 0;
  color: #e0e5f5;
  font-size: 13px;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.created-by {
  display: block;
  margin-top: 11px;
  color: #8f87d4;
  font-size: 10px;
}

.empty-state {
  display: grid;
  min-height: 310px;
  place-content: center;
  justify-items: center;
  border: 1px dashed rgba(255, 255, 255, 0.13);
  border-radius: 22px;
  color: #98a3c3;
  text-align: center;
}

.empty-state h3 {
  margin: 14px 0 7px;
  color: #e5e6f7;
}

.empty-state button {
  padding: 9px 13px;
  border: 0;
  border-radius: 10px;
  color: #e4e1ff;
  cursor: pointer;
  background: rgba(135, 116, 255, 0.18);
}

.loading-icon {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1550px) {
  .character-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .character-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 780px) {
  .character-page {
    padding: 46px 20px 85px;
  }

  .filter-section {
    align-items: flex-start;
    flex-direction: column;
  }

  .categories {
    width: 100%;
  }

  .search-box {
    width: 100%;
  }

  .character-grid {
    grid-template-columns: 1fr;
  }
}
/* 角色广场内容区域 */
.character-page {
  position: relative;
  isolation: isolate;
  width: min(1680px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  box-sizing: border-box;
  padding: 72px 56px 80px;
  overflow: visible;
  background: transparent;
}

.character-page > * {
  position: relative;
  z-index: 1;
}

/* 夜空背景：固定铺满导航栏右侧的整个可视区域 */
.character-page::before,
.character-page::after {
  position: fixed;
  z-index: 0;
  left: 250px;
  right: 0;
  pointer-events: none;
  content: '';
}

.character-page::before {
  top: 0;
  bottom: 0;
  opacity: 0.85;
  background-color: #0a1020;
  background-image:
    radial-gradient(circle at 15% 8%, rgba(106, 82, 218, 0.22), transparent 27%),
    radial-gradient(circle at 84% 25%, rgba(54, 123, 210, 0.16), transparent 26%),
    radial-gradient(circle at 52% 92%, rgba(112, 67, 189, 0.1), transparent 31%),
    radial-gradient(circle, rgba(255, 255, 255, 0.88) 0 1px, transparent 1.8px),
    radial-gradient(circle, rgba(191, 177, 255, 0.75) 0 1px, transparent 1.8px),
    radial-gradient(circle, rgba(117, 205, 255, 0.58) 0 1px, transparent 1.8px),
    radial-gradient(circle, rgba(255, 218, 245, 0.65) 0 1px, transparent 1.8px);
  background-position:
    center,
    center,
    center,
    20px 35px,
    125px 95px,
    260px 45px,
    355px 165px;
  background-size:
    auto,
    auto,
    auto,
    420px 280px,
    510px 340px,
    610px 390px,
    730px 460px;
  animation: lumi-star-drift 45s linear infinite;
}

.character-page::after {
  top: -30%;
  bottom: -30%;
  opacity: 0.5;
  background:
    radial-gradient(ellipse at 22% 20%, rgba(184, 156, 255, 0.14), transparent 15%),
    radial-gradient(ellipse at 74% 30%, rgba(94, 177, 255, 0.1), transparent 17%),
    radial-gradient(ellipse at 48% 76%, rgba(214, 122, 230, 0.08), transparent 19%);
  filter: blur(18px);
  animation: lumi-nebula-breathe 12s ease-in-out infinite alternate;
}

.character-card {
  backdrop-filter: blur(2px);
}

.character-card:hover {
  box-shadow: 0 19px 38px rgba(3, 8, 27, 0.35);
}

.character-card.purple:hover {
  box-shadow:
    0 19px 38px rgba(3, 8, 27, 0.35),
    0 0 20px rgba(111, 105, 255, 0.25),
    0 0 42px rgba(177, 111, 255, 0.16);
}

.character-card.blue:hover {
  box-shadow:
    0 19px 38px rgba(3, 8, 27, 0.35),
    0 0 20px rgba(73, 162, 255, 0.25),
    0 0 42px rgba(86, 115, 255, 0.14);
}

.character-card.pink:hover,
.character-card.rose:hover {
  box-shadow:
    0 19px 38px rgba(3, 8, 27, 0.35),
    0 0 20px rgba(237, 112, 179, 0.22),
    0 0 42px rgba(178, 102, 255, 0.14);
}

.character-card.green:hover,
.character-card.yellow:hover,
.character-card.orange:hover {
  box-shadow:
    0 19px 38px rgba(3, 8, 27, 0.35),
    0 0 20px rgba(91, 169, 211, 0.16),
    0 0 38px rgba(157, 106, 255, 0.12);
}

@keyframes lumi-star-drift {
  from {
    background-position:
      center,
      center,
      center,
      20px 35px,
      125px 95px,
      260px 45px,
      355px 165px;
  }

  to {
    background-position:
      center,
      center,
      center,
      340px 245px,
      465px 305px,
      580px 255px,
      695px 375px;
  }
}

@keyframes lumi-nebula-breathe {
  from {
    opacity: 0.3;
    transform: scale(0.96) rotate(-2deg);
  }

  to {
    opacity: 0.7;
    transform: scale(1.06) rotate(2deg);
  }
}

@media (max-width: 800px) {
  .character-page::before,
  .character-page::after {
    left: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .character-page::before,
  .character-page::after {
    animation: none;
  }

  .character-card:hover {
    animation: none;
    transform: none;
  }
}
</style>
