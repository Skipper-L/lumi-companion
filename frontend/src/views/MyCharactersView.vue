<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowUpRight,
  Eye,
  EyeOff,
  Heart,
  MessageCircleHeart,
  PlusCircle,
  Sparkles,
  Trash2,
  X,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'
import lumiMoonIcon from '../assets/lumi-default-cover.jpeg'
import { resolveImageUrl } from '../utils/imageUrl'

// Keep requests on the current host so Vite/ngrok can proxy /api to FastAPI.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const router = useRouter()

const activeTab = ref('favorites')
const createdFilter = ref('all')
const myCharacters = ref([])
const publicCharacters = ref([])
const favoriteIds = ref([])
const loading = ref(true)
const errorMessage = ref('')
const deleteTarget = ref(null)
const isDeleting = ref(false)

const officialCharacters = [
  {
    id: 'zhixia',
    name: '知夏',
    subtitle: '温柔倾听者',
    category: '治愈',
    tags: ['耐心', '共情', '温柔'],
    message: '不用急着变好，先让我陪你坐一会儿。',
    status: '正在听雨',
    color: 'purple',
    avatar: '知',
    online: true,
  },
  {
    id: 'linzhou',
    name: '临舟',
    subtitle: '深夜树洞',
    category: '倾诉',
    tags: ['安静', '可靠', '真诚'],
    message: '想说什么都可以，我会认真听完。',
    status: '等你开口',
    color: 'blue',
    avatar: '临',
    online: true,
  },
  {
    id: 'xiaoye',
    name: '小夜',
    subtitle: '晚安陪伴者',
    category: '睡前',
    tags: ['轻声', '治愈', '晚安'],
    message: '今天辛苦了。睡前的时间，交给我吧。',
    status: '准备了一首晚安歌',
    color: 'pink',
    avatar: '夜',
    online: false,
  },
  {
    id: 'chuchen',
    name: '初晨',
    subtitle: '元气搭子',
    category: '学习',
    tags: ['鼓励', '专注', '积极'],
    message: '把今天的小目标告诉我，我们一起完成。',
    status: '正在整理计划',
    color: 'yellow',
    avatar: '晨',
    online: true,
  },
  {
    id: 'wanwan',
    name: '晚晚',
    subtitle: '浪漫来信人',
    category: '恋爱',
    tags: ['浪漫', '细腻', '心动'],
    message: '如果你愿意，今晚让我写一封信给你。',
    status: '想和你散步',
    color: 'rose',
    avatar: '晚',
    online: true,
  },
  {
    id: 'anran',
    name: '安然',
    subtitle: '情绪整理师',
    category: '治愈',
    tags: ['理性', '松弛', '清醒'],
    message: '我们不急着找答案，先理一理心里的声音。',
    status: '正在晒太阳',
    color: 'green',
    avatar: '安',
    online: false,
  },
]

const filteredMyCharacters = computed(() => {
  if (createdFilter.value === 'all') {
    return myCharacters.value
  }

  return myCharacters.value.filter(
    (character) => character.visibility === createdFilter.value,
  )
})

const allAvailableCharacters = computed(() => {
  const combined = [
    ...myCharacters.value,
    ...publicCharacters.value,
    ...officialCharacters,
  ]

  return combined.filter(
    (character, index, array) =>
      array.findIndex((item) => item.id === character.id) === index,
  )
})

const favoriteCharacters = computed(() => {
  return favoriteIds.value
    .map((id) =>
      allAvailableCharacters.value.find(
        (character) => character.id === id,
      ),
    )
    .filter(Boolean)
})

const displayedCharacters = computed(() => {
  return activeTab.value === 'favorites'
    ? favoriteCharacters.value
    : filteredMyCharacters.value
})

function getHeaders() {
  const token = localStorage.getItem('lumi_access_token')

  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

function getCharacterImageUrl(character) {
  const image = character?.background_image
  if (!image) return lumiMoonIcon
  return resolveImageUrl(image)
}

async function loadPageData() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [myResponse, squareResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/api/custom-characters/mine`, {
        headers: getHeaders(),
      }),
      fetch(`${API_BASE_URL}/api/character-square`, {
        headers: getHeaders(),
      }),
    ])

    const myResult = await myResponse.json()
    const squareResult = await squareResponse.json()

    if (myResponse.status === 401 || squareResponse.status === 401) {
      localStorage.removeItem('lumi_access_token')
      localStorage.removeItem('lumi_current_user')

      router.replace('/login')
      return
    }

    if (!myResponse.ok) {
      throw new Error(myResult.detail || '获取我的角色失败。')
    }

    myCharacters.value = myResult.data || []
    publicCharacters.value = squareResult.data?.characters || []
    favoriteIds.value = squareResult.data?.favorite_ids || []
  } catch (error) {
    errorMessage.value = error.message || '网络连接失败，请确认后端正在运行。'
  } finally {
    loading.value = false
  }
}

function selectCharacter(character) {
  localStorage.setItem(
    'selected_character',
    JSON.stringify(character),
  )

  router.push({
    path: '/chat',
    query: {
      character: character.id,
    },
  })
}

async function removeFavorite(characterId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/favorites/${characterId}`,
      {
        method: 'DELETE',
        headers: getHeaders(),
      },
    )

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.detail || '取消收藏失败。')
    }

    favoriteIds.value = favoriteIds.value.filter(
      (id) => id !== characterId,
    )
  } catch (error) {
    errorMessage.value = error.message || '取消收藏失败。'
  }
}

function openDeleteModal(character) {
  deleteTarget.value = character
}

function closeDeleteModal() {
  if (!isDeleting.value) {
    deleteTarget.value = null
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return

  isDeleting.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/custom-characters/${deleteTarget.value.id}`,
      {
        method: 'DELETE',
        headers: getHeaders(),
      },
    )

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.detail || '删除角色失败。')
    }

    const deletedId = deleteTarget.value.id

    myCharacters.value = myCharacters.value.filter(
      (character) => character.id !== deletedId,
    )

    favoriteIds.value = favoriteIds.value.filter(
      (id) => id !== deletedId,
    )

    deleteTarget.value = null
  } catch (error) {
    errorMessage.value = error.message || '删除角色失败。'
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  loadPageData()
})
</script>

<template>
  <PageLayout>
    <main class="my-characters-page">
      <section class="tabs-area">
        <div class="tabs-row">
          <div class="tabs">
            <button
              type="button"
              :class="{ active: activeTab === 'favorites' }"
              @click="activeTab = 'favorites'"
            >
              <Heart :size="17" />
              我的收藏
              <span>{{ favoriteCharacters.length }}</span>
            </button>

            <button
              type="button"
              :class="{ active: activeTab === 'created' }"
              @click="activeTab = 'created'"
            >
              <PlusCircle :size="17" />
              我的创建
              <span>{{ myCharacters.length }}</span>
            </button>
          </div>

          <RouterLink to="/create" class="create-button">
            <PlusCircle :size="18" />
            创建新角色
          </RouterLink>
        </div>

        <Transition name="filter-slide">
          <div
            v-if="activeTab === 'created'"
            class="created-filters"
          >
            <span class="filter-label">机器人类型</span>

            <button
              type="button"
              :class="{ active: createdFilter === 'all' }"
              @click="createdFilter = 'all'"
            >
              全部
              <span>{{ myCharacters.length }}</span>
            </button>

            <button
              type="button"
              class="public-filter"
              :class="{ active: createdFilter === 'public' }"
              @click="createdFilter = 'public'"
            >
              <Eye :size="14" />
              公开
              <span>
                {{
                  myCharacters.filter(
                    (character) => character.visibility === 'public',
                  ).length
                }}
              </span>
            </button>

            <button
              type="button"
              class="private-filter"
              :class="{ active: createdFilter === 'private' }"
              @click="createdFilter = 'private'"
            >
              <EyeOff :size="14" />
              私密
              <span>
                {{
                  myCharacters.filter(
                    (character) => character.visibility === 'private',
                  ).length
                }}
              </span>
            </button>
          </div>
        </Transition>
      </section>

      <p v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </p>

      <section v-if="loading" class="empty-state">
        <Sparkles :size="36" class="loading-icon" />
        <h2>正在读取你的角色…</h2>
      </section>

      <section
        v-else-if="displayedCharacters.length"
        class="character-grid"
      >
        <article
          v-for="character in displayedCharacters"
          :key="character.id"
          class="character-card"
          :class="character.color"
          @click="selectCharacter(character)"
        >
          <div class="card-background"></div>

          <img
            class="card-cover"
            :src="getCharacterImageUrl(character)"
            :alt="`${character.name} 的角色封面`"
            loading="lazy"
            decoding="async"
          />
          <div class="card-cover-shade"></div>

          <div class="card-top">
            <button
              v-if="activeTab === 'favorites'"
              type="button"
              class="card-icon-button favorite"
              title="取消收藏"
              @click.stop="removeFavorite(character.id)"
            >
              <Heart :size="19" fill="currentColor" />
            </button>

            <button
              v-else
              type="button"
              class="card-icon-button delete"
              title="删除角色"
              @click.stop="openDeleteModal(character)"
            >
              <Trash2 :size="18" />
            </button>
          </div>

          <div class="card-content">
            <h3>{{ character.name }}</h3>
          </div>
        </article>
      </section>

      <section v-else class="empty-state">
        <Heart v-if="activeTab === 'favorites'" :size="38" />
        <MessageCircleHeart v-else :size="38" />

        <h2>
          {{
            activeTab === 'favorites'
              ? '还没有收藏角色'
              : '还没有创建角色'
          }}
        </h2>

        <RouterLink
          :to="activeTab === 'favorites' ? '/characters' : '/create'"
          class="empty-action"
        >
          {{
            activeTab === 'favorites'
              ? '前往角色广场'
              : '创建我的角色'
          }}
        </RouterLink>
      </section>
    </main>
  </PageLayout>

  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="deleteTarget"
        class="modal-mask"
        @click.self="closeDeleteModal"
      >
        <section class="delete-modal">
          <button class="close-button" @click="closeDeleteModal">
            <X :size="20" />
          </button>

          <div class="delete-icon">
            <Trash2 :size="26" />
          </div>

          <p class="modal-eyebrow">DELETE CHARACTER</p>

          <h2>确认删除“{{ deleteTarget.name }}”吗？</h2>

          <p>
            删除后，该角色将从数据库永久移除，无法恢复。
          </p>

          <div class="modal-actions">
            <button
              type="button"
              :disabled="isDeleting"
              @click="closeDeleteModal"
            >
              暂不删除
            </button>

            <button
              type="button"
              class="danger-button"
              :disabled="isDeleting"
              @click="confirmDelete"
            >
              <Trash2 :size="16" />
              {{ isDeleting ? '正在删除…' : '确认删除' }}
            </button>
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.my-characters-page {
  width: min(1500px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  padding: 72px 7% 80px;
}

.tabs-row,
.tabs,
.character-grid,
.card-top,
.name-row,
.modal-actions {
  display: flex;
}

.tabs-area {
  margin-top: 112px;
  /* 创建页含二级筛选，收藏页没有；预留相同高度以固定分割线和卡片起始位置。 */
  min-height: 112px;
  box-sizing: border-box;
  padding-bottom: 17px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.09);
}

.tabs-row {
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.create-button {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  flex: none;
  padding: 13px 16px;
  border-radius: 13px;
  color: white;
  background: linear-gradient(135deg, #7768ff, #b86ee9);
  box-shadow: 0 10px 24px rgba(112, 95, 233, 0.25);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  transition: 0.2s ease;
}

.create-button:hover {
  box-shadow: 0 13px 28px rgba(133, 105, 255, 0.38);
  transform: translateY(-2px);
}

.tabs {
  gap: 10px;
  margin-top: 0;
  padding-bottom: 0;
  border-bottom: 0;
}

.tabs button {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 11px 14px;
  border: 1px solid transparent;
  border-radius: 11px;
  color: #99a4c1;
  cursor: pointer;
  background: transparent;
  font: inherit;
  font-size: 13px;
}

.tabs button.active {
  border-color: rgba(163, 144, 255, 0.38);
  color: #f7f5ff;
  background: linear-gradient(
    135deg,
    rgba(117, 100, 244, 0.35),
    rgba(179, 99, 224, 0.15)
  );
}

.tabs span {
  min-width: 19px;
  padding: 2px 6px;
  border-radius: 20px;
  color: #dcd6ff;
  background: rgba(255, 255, 255, 0.12);
  font-size: 10px;
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

.character-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-top: 28px;
}

.character-card {
  position: relative;
  min-height: 300px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 23px;
  background: rgba(255, 255, 255, 0.045);
  cursor: pointer;
  transition: 0.25s ease;
}

.character-card:hover {
  border-color: rgba(209, 201, 255, 0.32);
  box-shadow: 0 22px 50px rgba(0, 0, 0, 0.22);
  transform: translateY(-7px);
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

.card-cover {
  z-index: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-cover-shade {
  z-index: 1;
  background: linear-gradient(
    180deg,
    rgba(8, 11, 29, 0.08) 15%,
    rgba(9, 12, 32, 0.34) 48%,
    rgba(8, 10, 28, 0.97) 100%
  );
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
  z-index: 3;
  justify-content: space-between;
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

.card-icon-button {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  margin: -8px -8px 0 0;
  padding: 0;
  border: 0;
  border-radius: 50%;
  cursor: pointer;
}

.card-icon-button.favorite {
  color: #ff668f;
  background: rgba(255, 105, 143, 0.12);
}

.card-icon-button.delete {
  color: #c3c9e2;
  background: rgba(255, 255, 255, 0.07);
}

.card-icon-button.delete:hover {
  color: #ff9fb8;
  background: rgba(255, 99, 142, 0.15);
}

.card-content {
  position: absolute;
  z-index: 3;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18px;
  background: linear-gradient(
    transparent,
    rgba(13, 17, 40, 0.94) 24%
  );
}

.card-content h3 {
  margin: 0;
  color: #f3f3ff;
  font-size: 22px;
  line-height: 1.2;
}

.name-row {
  justify-content: space-between;
  align-items: end;
}

.name-row h3 {
  margin-bottom: 3px;
  color: #f3f3ff;
  font-size: 22px;
}

.name-row p {
  margin-bottom: 0;
  color: #9da7c6;
  font-size: 12px;
}

.character-message {
  min-height: 42px;
  margin: 15px 0 13px;
  color: #c6cce3;
  font-size: 13px;
  line-height: 1.6;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-list span {
  padding: 5px 8px;
  border-radius: 7px;
  color: #aeb7d3;
  background: rgba(255, 255, 255, 0.07);
  font-size: 10px;
}

.visibility-badge {
  display: inline-flex;
  gap: 5px;
  align-items: center;
  margin-top: 11px;
  padding: 5px 8px;
  border-radius: 7px;
  font-size: 10px;
}

.visibility-badge.public {
  color: #75ddc5;
  background: rgba(67, 199, 168, 0.12);
}

.visibility-badge.private {
  color: #c6b4ff;
  background: rgba(151, 121, 255, 0.14);
}

.empty-state {
  display: grid;
  min-height: 390px;
  margin-top: 28px;
  place-content: center;
  justify-items: center;
  border: 1px dashed rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  color: #98a3c3;
  text-align: center;
}

.empty-state h2 {
  margin: 16px 0 8px;
  color: #e9e9f8;
}

.empty-action {
  padding: 11px 15px;
  border-radius: 11px;
  color: white;
  background: linear-gradient(135deg, #7768ff, #b86ee9);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

.loading-icon {
  animation: spin 0.9s linear infinite;
}

.modal-mask {
  position: fixed;
  z-index: 9999;
  inset: 0;
  display: grid;
  padding: 20px;
  place-items: center;
  background: rgba(3, 6, 20, 0.76);
  backdrop-filter: blur(9px);
}

.delete-modal {
  position: relative;
  width: min(100%, 405px);
  padding: 34px;
  border: 1px solid rgba(255, 169, 193, 0.22);
  border-radius: 25px;
  text-align: center;
  background: linear-gradient(145deg, #282049, #12172d);
  box-shadow: 0 28px 75px rgba(0, 0, 0, 0.5);
}

.close-button {
  position: absolute;
  top: 14px;
  right: 15px;
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 0;
  border-radius: 10px;
  color: #adb5d2;
  cursor: pointer;
  background: transparent;
}

.delete-icon {
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  margin: 0 auto 18px;
  border-radius: 18px;
  color: #ffb3c7;
  background: rgba(238, 95, 140, 0.15);
}

.modal-eyebrow {
  margin: 0 0 8px;
  color: #e99bb4;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.7px;
}

.delete-modal h2 {
  margin-bottom: 12px;
  color: #f5f3ff;
  font-size: 22px;
}

.delete-modal > p:not(.modal-eyebrow) {
  color: #aeb7d0;
  font-size: 13px;
  line-height: 1.7;
}

.modal-actions {
  gap: 10px;
  margin-top: 22px;
}

.modal-actions button {
  flex: 1;
  min-height: 43px;
  border: 1px solid rgba(217, 211, 245, 0.15);
  border-radius: 12px;
  color: #ccd2e6;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.06);
  font: inherit;
}

.modal-actions .danger-button {
  display: flex;
  justify-content: center;
  gap: 7px;
  align-items: center;
  border: 0;
  color: white;
  background: linear-gradient(135deg, #d85d87, #ee7fa9);
}

.created-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  align-items: center;
  margin-top: 15px;
  padding-left: 3px;
}

.filter-label {
  margin-right: 3px;
  color: #7985a5;
  font-size: 11px;
}

.created-filters button {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  padding: 8px 11px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 9px;
  color: #aeb8d2;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.035);
  font: inherit;
  font-size: 12px;
  transition: 0.2s ease;
}

.created-filters button:hover {
  border-color: rgba(177, 157, 255, 0.35);
  color: #f1efff;
  background: rgba(122, 102, 238, 0.1);
}

.created-filters button.active {
  border-color: rgba(168, 144, 255, 0.6);
  color: #f4f1ff;
  background: rgba(125, 104, 245, 0.22);
  box-shadow: 0 6px 16px rgba(108, 89, 234, 0.15);
}

.created-filters .public-filter.active {
  border-color: rgba(82, 214, 183, 0.42);
  color: #78ddc6;
  background: rgba(63, 199, 168, 0.13);
}

.created-filters .private-filter.active {
  border-color: rgba(170, 139, 255, 0.48);
  color: #cfbaff;
  background: rgba(144, 110, 246, 0.16);
}

.created-filters button span {
  display: grid;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  place-items: center;
  border-radius: 20px;
  color: inherit;
  background: rgba(255, 255, 255, 0.1);
  font-size: 10px;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.filter-slide-enter-active,
.filter-slide-leave-active {
  transition: 0.2s ease;
}

.filter-slide-enter-from,
.filter-slide-leave-to {
  opacity: 0;
  transform: translateY(-7px);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1300px) {
  .character-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 980px) {
  .character-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 780px) {
  .my-characters-page {
    padding: 46px 20px 85px;
  }

  .tabs-area {
    margin-top: 36px;
  }

  .tabs-row {
    align-items: flex-start;
    flex-direction: column-reverse;
  }

  .create-button {
    align-self: flex-end;
  }

  .character-grid {
    grid-template-columns: 1fr;
  }
}
</style>
