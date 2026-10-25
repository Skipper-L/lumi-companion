<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  ChevronLeft,
  Heart,
  Image,
  Mic,
  MoreHorizontal,
  SendHorizontal,
  SmilePlus,
  Sparkles,
  Trash2,
  Volume2,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'

// Keep requests on the current host so Vite/ngrok can proxy /api to FastAPI.
const API_BASE_URL = ''

const router = useRouter()
const route = useRoute()

const inputText = ref('')
const isTyping = ref(false)
const messageList = ref(null)
const inputBox = ref(null)
const voiceMode = ref(false)

const showClearModal = ref(false)
const isDeleting = ref(false)
const deleteError = ref('')

const showRelationshipDetail = ref(false)
const showCharacterDetail = ref(false)
const editableMemoryCards = ref([])
const isSavingMemoryCards = ref(false)
const memoryCardError = ref('')
const memoryCardSuccess = ref('')

const selectedCharacter = ref({
  id: 'zhixia',
  name: '知夏',
  subtitle: '温柔倾听者',
  avatar: '知',
  status: '正在陪伴你',
  color: 'purple',
})

const messages = ref([])

const isConversationChat = computed(() => {
  return route.path.startsWith('/conversations/chat/')
})

const isCharacterSquareChat = computed(() => {
  return route.query.from === 'characters'
})

const showBackButton = computed(() => {
  return isConversationChat.value || isCharacterSquareChat.value
})

const chatSourceText = computed(() => {
  if (isConversationChat.value) {
    return '会话记录'
  }

  if (isCharacterSquareChat.value) {
    return '角色广场'
  }

  return ''
})

const backButtonText = computed(() => {
  if (isConversationChat.value) {
    return '返回会话记录'
  }

  return '返回角色广场'
})

const relationshipText = computed(() =>
  messages.value.length > 8
    ? '默契正在慢慢升温'
    : '正在慢慢了解你',
)

const characterDescription = computed(() => {
  return (
    selectedCharacter.value.description ||
    selectedCharacter.value.message ||
    selectedCharacter.value.opening ||
    `${selectedCharacter.value.name}正在等待和你慢慢认识彼此。`
  )
})

const characterAvatarImage = computed(() =>
  selectedCharacter.value.background_image || '',
)

const currentUserId = computed(() => {
  try {
    return Number(JSON.parse(localStorage.getItem('lumi_current_user') || '{}').id) || 0
  } catch {
    return 0
  }
})

const canEditMemoryCards = computed(() =>
  String(selectedCharacter.value.id || '').startsWith('custom_') &&
  Number(selectedCharacter.value.user_id) === currentUserId.value,
)

const chatBackgroundStyle = computed(() => {
  const image = selectedCharacter.value.background_image
  if (!image) return {}

  return {
    '--character-chat-background': `url("${image}")`,
  }
})

function getAuthHeaders() {
  const token = localStorage.getItem('lumi_access_token')

  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

function getOpeningMessage() {
  return {
    id: `opening-${Date.now()}`,
    role: 'assistant',
    time: '现在',
    content:
      selectedCharacter.value.opening ||
      selectedCharacter.value.message ||
      `你好，我是${selectedCharacter.value.name}。今天想让我怎么陪着你？`,
    image: selectedCharacter.value.greeting_image || '',
  }
}

function makeMemoryCard(card = {}) {
  return {
    id: card.id || `memory-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    key: card.key || '',
    content: card.content || '',
  }
}

function openCharacterDetail() {
  memoryCardError.value = ''
  memoryCardSuccess.value = ''
  const cards = selectedCharacter.value.memory_cards || []
  editableMemoryCards.value = cards.length
    ? cards.map((card) => makeMemoryCard(card))
    : [makeMemoryCard()]
  showCharacterDetail.value = true
}

function closeCharacterDetail() {
  if (isSavingMemoryCards.value) return
  showCharacterDetail.value = false
}

function addMemoryCard() {
  if (editableMemoryCards.value.length >= 20) return
  editableMemoryCards.value.push(makeMemoryCard())
}

function removeMemoryCard(index) {
  if (editableMemoryCards.value.length <= 1) return
  editableMemoryCards.value.splice(index, 1)
}

async function saveMemoryCards() {
  if (!canEditMemoryCards.value || isSavingMemoryCards.value) return

  const cards = editableMemoryCards.value
    .map((card) => ({
      ...card,
      key: card.key.trim(),
      content: card.content.trim(),
    }))
    .filter((card) => card.key || card.content)

  if (!cards.length || cards.some((card) => !card.key || !card.content)) {
    memoryCardError.value = '请完整填写每一张保留的记忆卡。'
    return
  }

  memoryCardError.value = ''
  memoryCardSuccess.value = ''
  isSavingMemoryCards.value = true

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/custom-characters/${encodeURIComponent(selectedCharacter.value.id)}/memory-cards`,
      {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({ memory_cards: cards }),
      },
    )
    const result = await response.json()
    if (!response.ok || !result.success) {
      throw new Error(result.detail || '保存记忆卡失败，请稍后重试。')
    }

    selectedCharacter.value = {
      ...selectedCharacter.value,
      ...result.data,
    }
    editableMemoryCards.value = result.data.memory_cards.map((card) => makeMemoryCard(card))
    localStorage.setItem('selected_character', JSON.stringify(selectedCharacter.value))
    memoryCardSuccess.value = '记忆卡已保存，下一次回复会使用新设定。'
  } catch (error) {
    memoryCardError.value = error.message || '保存记忆卡失败，请稍后重试。'
  } finally {
    isSavingMemoryCards.value = false
  }
}

function getAssistantMessageSegments(content) {
  const blocks = String(content || '')
    .replace(/\r\n/g, '\n')
    .split(/\n{1,}/)
    .map((block) => block.trim())
    .filter(Boolean)

  return blocks.map((block) => {
    const markedNarration = block.match(/^【(?:描写|场景|动作)】\s*(.*)$/)
    if (markedNarration) {
      return { type: 'narration', text: markedNarration[1] }
    }

    // 兼容规则上线前已保存的括号式动作描写。
    if (/^[（(].*[）)]$/.test(block)) {
      return {
        type: 'narration',
        text: block.replace(/^[（(]\s*|\s*[）)]$/g, ''),
      }
    }

    return { type: 'dialogue', text: block }
  })
}

async function refreshSelectedCharacter() {
  if (!selectedCharacter.value.id) return

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/character/${encodeURIComponent(selectedCharacter.value.id)}`,
      { headers: getAuthHeaders() },
    )

    if (response.status === 401) {
      goToLogin()
      return
    }

    const result = await response.json()
    if (!response.ok || !result.success) {
      throw new Error(result.detail || '读取角色资料失败')
    }

    // 保留页面展示所需的兼容字段，同时以数据库的最新开场语、图片和封面为准。
    selectedCharacter.value = {
      ...selectedCharacter.value,
      ...result.data,
      avatar:
        result.data.avatar || result.data.name?.trim()?.charAt(0) || selectedCharacter.value.avatar,
    }
    localStorage.setItem('selected_character', JSON.stringify(selectedCharacter.value))
  } catch (error) {
    // 网络暂时不可用时仍可使用本地缓存进入聊天，不阻断已有会话。
    console.warn('读取最新角色资料失败，将使用本地缓存：', error)
  }
}

function formatMessageTime(dateText) {
  const date = new Date(dateText)

  if (Number.isNaN(date.getTime())) {
    return ''
  }

  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function getTime() {
  return new Date().toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function goToLogin() {
  localStorage.removeItem('lumi_access_token')
  localStorage.removeItem('lumi_current_user')

  router.replace({
    path: '/login',
    query: {
      redirect: route.fullPath,
    },
  })
}

function backToPreviousPage() {
  if (isConversationChat.value) {
    router.push('/conversations')
    return
  }

  router.push('/characters')
}

async function loadMessagesFromDatabase() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/history/${selectedCharacter.value.id}`,
      {
        headers: getAuthHeaders(),
      },
    )

    if (response.status === 401) {
      goToLogin()
      return false
    }

    const result = await response.json()

    if (!response.ok || !result.success) {
      throw new Error(result.detail || '读取聊天记录失败')
    }

    if (result.data.length > 0) {
      const historyMessages = result.data.map((item) => ({
        id: `database-${item.id}`,
        role: item.role,
        content: item.content,
        time: formatMessageTime(item.created_at),
      }))

      // 初始问候是角色设定的一部分。旧版本没有把它写入消息表，
      // 因此再次进入聊天时需要补回，保证历史记录完整且问候图片不丢失。
      const openingMessage = getOpeningMessage()
      const hasOpening = historyMessages.some(
        (item) => item.role === 'assistant' && item.content === openingMessage.content,
      )
      messages.value = hasOpening
        ? historyMessages
        : [openingMessage, ...historyMessages]

      return true
    }

    return false
  } catch (error) {
    console.error('读取聊天记录失败：', error)
    return false
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messageList.value) {
      messageList.value.scrollTop = messageList.value.scrollHeight
    }
  })
}

function focusInput() {
  nextTick(() => inputBox.value?.focus())
}

function openClearModal() {
  deleteError.value = ''
  showClearModal.value = true
}

function closeClearModal() {
  if (isDeleting.value) return

  deleteError.value = ''
  showClearModal.value = false
}

onMounted(async () => {
  const savedCharacter = localStorage.getItem('selected_character')

  if (savedCharacter) {
    try {
      selectedCharacter.value = JSON.parse(savedCharacter)
    } catch (error) {
      console.error('读取角色信息失败：', error)
    }
  }

  await refreshSelectedCharacter()

  const hasHistory = await loadMessagesFromDatabase()

  if (!hasHistory && messages.value.length === 0) {
    messages.value = [getOpeningMessage()]
  }

  await nextTick()
  scrollToBottom()
  focusInput()
})

async function sendMessage() {
  const text = inputText.value.trim()

  if (!text || isTyping.value) return

  messages.value.push({
    id: `user-${Date.now()}`,
    role: 'user',
    time: getTime(),
    content: text,
  })

  inputText.value = ''
  isTyping.value = true

  await nextTick()
  scrollToBottom()

  const startTime = Date.now()

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        character_id: selectedCharacter.value.id,
        messages: messages.value.map((message) => ({
          role: message.role,
          content: message.content,
        })),
      }),
    })

    if (response.status === 401) {
      goToLogin()
      return
    }

    const result = await response.json()

    if (!response.ok || !result.success) {
      throw new Error(result.detail || '后端回复异常')
    }

    const remainingTime = 1000 - (Date.now() - startTime)

    if (remainingTime > 0) {
      await new Promise((resolve) => {
        setTimeout(resolve, remainingTime)
      })
    }

    messages.value.push({
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      time: getTime(),
      content: result.data.content,
    })
  } catch (error) {
    console.error('发送消息失败：', error)

    messages.value.push({
      id: `assistant-error-${Date.now()}`,
      role: 'assistant',
      time: getTime(),
      content: error.message || '暂时无法连接陪伴服务，请确认 FastAPI 后端正在运行。',
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
    focusInput()
  }
}

async function confirmClearChat() {
  if (isDeleting.value) return

  isDeleting.value = true
  deleteError.value = ''

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/history/${selectedCharacter.value.id}`,
      {
        method: 'DELETE',
        headers: getAuthHeaders(),
      },
    )

    if (response.status === 401) {
      goToLogin()
      return
    }

    const result = await response.json()

    if (!response.ok || !result.success) {
      throw new Error(result.detail || '删除聊天记录失败')
    }

    messages.value = [getOpeningMessage()]
    showClearModal.value = false

    await nextTick()
    scrollToBottom()
    focusInput()
  } catch (error) {
    deleteError.value = error.message || '删除失败，请稍后重试。'
  } finally {
    isDeleting.value = false
  }
}
</script>

<template>
  <PageLayout>
    <main
      class="chat-page"
      :class="{ 'has-character-background': characterAvatarImage }"
      :style="chatBackgroundStyle"
    >
      <section class="chat-room">
        <header class="chat-header">
          <div class="header-left">
           <button
  v-if="showBackButton"
  class="back-button"
  type="button"
  :title="backButtonText"
  @click="backToPreviousPage"
>
  <ArrowLeft :size="18" />
  <span>{{ backButtonText }}</span>
</button>

            <div class="header-character">
              <button
                class="avatar character-detail-trigger"
                type="button"
                title="查看角色详情"
                @click="openCharacterDetail"
              >
                <img
                  v-if="characterAvatarImage"
                  :src="characterAvatarImage"
                  alt=""
                />
                <template v-else>{{ selectedCharacter.avatar }}</template>
              </button>

              <div>
                <h1>
                  {{ selectedCharacter.name }}
                  <small>AI 陪伴者</small>
                 <em v-if="chatSourceText">{{ chatSourceText }}</em>
                </h1>

                <p>
                  ●
                  {{
                    isTyping
                      ? '正在整理想对你说的话…'
                      : selectedCharacter.status
                  }}
                </p>
              </div>
            </div>
          </div>

          <div class="header-buttons">
            <button type="button" title="清空聊天" @click="openClearModal">
              <Trash2 :size="18" />
            </button>

            <button type="button" @click="voiceMode = !voiceMode">
              <Volume2 :size="19" />
            </button>

            <button type="button">
              <MoreHorizontal :size="20" />
            </button>
          </div>
        </header>

        <div ref="messageList" class="message-list">
          <span class="today">今天</span>

          <article
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="message.role"
          >
            <span
              v-if="message.role === 'assistant'"
              class="message-avatar"
            >
              <img
                v-if="characterAvatarImage"
                :src="characterAvatarImage"
                alt=""
              />
              <template v-else>{{ selectedCharacter.avatar }}</template>
            </span>

            <div>
              <div class="bubble">
                <template v-if="message.role === 'assistant'">
                  <p
                    v-for="(segment, index) in getAssistantMessageSegments(message.content)"
                    :key="`${message.id}-${index}`"
                    class="message-segment"
                    :class="segment.type"
                  >
                    {{ segment.text }}
                  </p>
                </template>
                <span v-else>{{ message.content }}</span>
              <img
                v-if="message.image"
                class="greeting-message-image"
                :src="message.image"
                alt="角色问候图片"
              />
              </div>
              <time>{{ message.time }}</time>
            </div>
          </article>

          <article v-if="isTyping" class="message assistant">
            <span class="message-avatar">
              <img
                v-if="characterAvatarImage"
                :src="characterAvatarImage"
                alt=""
              />
              <template v-else>{{ selectedCharacter.avatar }}</template>
            </span>

            <div class="typing">
              <i></i>
              <i></i>
              <i></i>
            </div>
          </article>
        </div>

        <div v-if="voiceMode" class="voice-panel">
          <span>{{ selectedCharacter.avatar }}</span>

          <div class="wave">
            <i v-for="item in 16" :key="item"></i>
          </div>

          <p>语音陪伴模式</p>

          <button type="button" @click="voiceMode = false">
            关闭
          </button>
        </div>

        <form class="composer" @submit.prevent="sendMessage">
          <button type="button">
            <SmilePlus :size="20" />
          </button>

          <button type="button">
            <Image :size="20" />
          </button>

          <textarea
            ref="inputBox"
            v-model="inputText"
            :disabled="isTyping"
            rows="1"
            placeholder="想说什么都可以告诉我…"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>

          <button type="button" @click="voiceMode = !voiceMode">
            <Mic :size="19" />
          </button>

          <button
            class="send"
            :disabled="!inputText.trim() || isTyping"
            type="submit"
          >
            <SendHorizontal :size="19" />
          </button>
        </form>
      </section>

      <aside class="relationship-panel">
        <button
          class="panel-close"
          type="button"
          @click="showRelationshipDetail = true"
        >
          <ChevronLeft :size="19" />
        </button>

        <div class="person">
          <div class="aura"></div>

          <div class="person-logo">
            <span>{{ selectedCharacter.avatar }}</span>
          </div>
        </div>

        <div class="profile">
          <p>正在和你聊天</p>
          <h2>{{ selectedCharacter.name }}</h2>
          <span>{{ selectedCharacter.subtitle }}</span>
        </div>

        <button
          class="relationship-button"
          type="button"
          @click="showRelationshipDetail = true"
        >
          <div>
            <span><Heart :size="16" />关系温度</span>
            <strong>28%</strong>
          </div>

          <section><i></i></section>

          <p>{{ relationshipText }}</p>
        </button>

        <section class="description-card" tabindex="0">
          <div class="description-title">
            <Sparkles :size="16" />
            <strong>角色简介</strong>
          </div>

          <p>{{ characterDescription }}</p>

          <span>悬停查看 TA 的故事</span>
        </section>
      </aside>
    </main>

    <div
      v-if="showClearModal"
      class="mask"
      @click.self="closeClearModal"
    >
      <section class="modal">
        <button
          class="close"
          :disabled="isDeleting"
          type="button"
          @click="closeClearModal"
        >
          ×
        </button>

        <span class="modal-icon">
          <Trash2 :size="24" />
        </span>

        <p class="eyebrow">MEMORY MANAGEMENT</p>
        <h2>清空这段回忆？</h2>

        <p class="description">
          你和「{{ selectedCharacter.name }}」的聊天记录将从数据库中删除。
          这个操作无法恢复。
        </p>

        <div class="modal-character">
          <b>{{ selectedCharacter.avatar }}</b>

          <span>
            <strong>{{ selectedCharacter.name }}</strong>
            <p>当前陪伴角色</p>
          </span>
        </div>

        <p v-if="deleteError" class="delete-error">
          {{ deleteError }}
        </p>

        <div class="modal-actions">
          <button
            type="button"
            :disabled="isDeleting"
            @click="closeClearModal"
          >
            再想想
          </button>

          <button
            class="danger"
            type="button"
            :disabled="isDeleting"
            @click="confirmClearChat"
          >
            <Trash2 :size="16" />
            {{ isDeleting ? '正在清空…' : '确认清空' }}
          </button>
        </div>
      </section>
    </div>

    <Transition name="character-detail">
      <div
        v-if="showCharacterDetail"
        class="character-detail-mask"
        @click.self="closeCharacterDetail"
      >
        <section class="character-detail-page">
        <header class="character-detail-header">
          <button type="button" @click="closeCharacterDetail">
            <ArrowLeft :size="18" />
            返回聊天
          </button>

          <p>角色详情</p>
        </header>

        <div class="character-detail-content">
          <aside class="character-detail-profile">
            <div class="detail-cover">
              <img
                v-if="characterAvatarImage"
                :src="characterAvatarImage"
                alt=""
              />
              <span v-else>{{ selectedCharacter.avatar }}</span>
            </div>

            <p class="detail-status">正在和你聊天</p>
            <h2>{{ selectedCharacter.name }}</h2>
            <span>{{ selectedCharacter.subtitle || selectedCharacter.relationship || '陪伴角色' }}</span>

            <div v-if="selectedCharacter.personality_tags?.length" class="detail-tags">
              <i v-for="tag in selectedCharacter.personality_tags" :key="tag">{{ tag }}</i>
            </div>

            <p class="detail-description">{{ characterDescription }}</p>
          </aside>

          <main class="memory-editor">
            <div class="memory-editor-heading">
              <div>
                <p>MEMORY CARDS</p>
                <h2>角色记忆卡</h2>
                <span>这些内容会作为角色的固定事实与长期设定使用。</span>
              </div>

              <button
                v-if="canEditMemoryCards"
                type="button"
                class="add-memory-card"
                :disabled="editableMemoryCards.length >= 20"
                @click="addMemoryCard"
              >
                + 新增记忆卡
              </button>
            </div>

            <p v-if="!canEditMemoryCards" class="memory-readonly">
              该角色不是你创建的角色，记忆卡仅供查看。
            </p>

            <div class="memory-card-list">
              <article
                v-for="(card, index) in editableMemoryCards"
                :key="card.id"
                class="memory-edit-card"
              >
                <div class="memory-card-title">
                  <strong>记忆卡 {{ index + 1 }}</strong>
                  <button
                    v-if="canEditMemoryCards && editableMemoryCards.length > 1"
                    type="button"
                    @click="removeMemoryCard(index)"
                  >
                    删除
                  </button>
                </div>

                <label>
                  <span>记忆关键词</span>
                  <input
                    v-model="card.key"
                    :readonly="!canEditMemoryCards"
                    maxlength="40"
                    placeholder="例如：性格、外貌、经历、相处模式"
                  />
                </label>

                <label>
                  <span>对应内容</span>
                  <textarea
                    v-model="card.content"
                    :readonly="!canEditMemoryCards"
                    maxlength="1500"
                    rows="7"
                    placeholder="写下角色不能违背的背景、经历或偏好。"
                  ></textarea>
                </label>
              </article>
            </div>

            <p v-if="memoryCardError" class="memory-editor-error">{{ memoryCardError }}</p>
            <p v-if="memoryCardSuccess" class="memory-editor-success">{{ memoryCardSuccess }}</p>

            <footer v-if="canEditMemoryCards" class="memory-editor-footer">
              <span>最多可保存 20 张记忆卡</span>
              <button type="button" :disabled="isSavingMemoryCards" @click="saveMemoryCards">
                {{ isSavingMemoryCards ? '正在保存…' : '保存记忆卡' }}
              </button>
            </footer>
          </main>
        </div>
        </section>
      </div>
    </Transition>

    <div
      v-if="showRelationshipDetail"
      class="detail-mask"
      @click.self="showRelationshipDetail = false"
    >
      <aside class="detail-panel">
        <button
          class="close"
          type="button"
          @click="showRelationshipDetail = false"
        >
          ×
        </button>

        <p class="eyebrow">YOUR CONNECTION</p>
        <h2>你和 {{ selectedCharacter.name }} 的关系</h2>

        <div class="temperature">
          <strong>28%</strong>
          <span>
            <b>刚刚开始熟悉</b>
            <p>每一次真诚对话，都会让 TA 更了解你。</p>
          </span>
        </div>

        <footer>
          <Sparkles :size="18" />
          关系温度不是分数，而是共同经历的温柔痕迹。
        </footer>
      </aside>
    </div>
  </PageLayout>
</template>

<style scoped>
.chat-page {
  position: relative;
  isolation: isolate;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 315px;
  min-height: 100vh;
}

.chat-page.has-character-background::before {
  position: absolute;
  z-index: -2;
  inset: 0;
  content: '';
  background-image: var(--character-chat-background);
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.chat-page.has-character-background::after {
  position: absolute;
  z-index: -1;
  inset: 0;
  content: '';
  background:
    linear-gradient(90deg, rgba(6, 10, 27, 0.74), rgba(8, 12, 30, 0.56)),
    rgba(6, 10, 27, 0.28);
  backdrop-filter: blur(1px);
}

.chat-room {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100vh;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.chat-header,
.header-left,
.header-character,
.header-buttons,
.composer,
.relationship-button > div,
.modal-actions {
  display: flex;
  align-items: center;
}

.chat-header {
  justify-content: space-between;
  padding: 16px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(12, 17, 37, 0.55);
}

.header-left,
.header-character {
  gap: 11px;
}

.back-button {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  padding: 8px 10px;
  border: 1px solid rgba(190, 177, 255, 0.2);
  border-radius: 10px;
  color: #b8c1db;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.045);
  font: inherit;
  font-size: 11px;
  transition: 0.2s ease;
}

.back-button:hover {
  border-color: rgba(187, 168, 255, 0.48);
  color: #f3f1ff;
  background: rgba(127, 106, 246, 0.16);
  transform: translateX(-2px);
}

.avatar,
.message-avatar {
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: white;
  background: linear-gradient(145deg, #b98edc, #7966cf);
  font-weight: 800;
  overflow: hidden;
}

.avatar img,
.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.greeting-message-image {
  display: block;
  width: min(100%, 420px);
  max-height: 460px;
  border: 0;
  border-radius: 10px;
  object-fit: cover;
}

.avatar {
  position: relative;
  width: 42px;
  height: 42px;
}

.character-detail-trigger {
  padding: 0;
  border: 1px solid transparent;
  cursor: pointer;
  transition: 0.22s ease;
}

.character-detail-trigger:hover {
  border-color: rgba(213, 197, 255, 0.8);
  box-shadow: 0 0 0 4px rgba(150, 117, 255, 0.14), 0 7px 18px rgba(8, 7, 30, 0.3);
  transform: translateY(-1px);
}

.avatar i {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 9px;
  height: 9px;
  border: 2px solid #10162d;
  border-radius: 50%;
  background: #53dfbd;
  z-index: 1;
}

.header-character h1 {
  margin: 0;
  color: #f1f2ff;
  font-size: 17px;
}

.header-character small,
.header-character em {
  display: inline-block;
  margin-left: 5px;
  padding: 3px 6px;
  border-radius: 5px;
  font-size: 9px;
  font-style: normal;
  vertical-align: middle;
}

.header-character small {
  color: #beb8ff;
  background: rgba(145, 123, 255, 0.14);
}

.header-character em {
  color: #7fe5c2;
  background: rgba(77, 212, 173, 0.12);
}

.header-character p {
  margin: 5px 0 0;
  color: #7ce4c0;
  font-size: 11px;
}

.header-buttons {
  gap: 7px;
}

.header-buttons button,
.composer button {
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 10px;
  color: #aeb8d5;
  cursor: pointer;
  background: transparent;
}

.header-buttons button {
  width: 36px;
  height: 36px;
}

.message-list {
  overflow-y: auto;
  padding: 26px 8%;
}

.today {
  display: block;
  width: max-content;
  margin: 0 auto 29px;
  padding: 5px 10px;
  border-radius: 8px;
  color: #747f9f;
  background: rgba(255, 255, 255, 0.04);
  font-size: 11px;
}

.message {
  display: flex;
  gap: 10px;
  max-width: 78%;
  margin-bottom: 20px;
}

.message.user {
  justify-content: flex-end;
  margin-left: auto;
}

.message-avatar {
  flex: 0 0 31px;
  width: 31px;
  height: 31px;
  box-sizing: border-box;
  font-size: 13px;
}

.bubble {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 12px 15px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px 16px 16px;
  color: #e7e9fb;
  background: rgba(255, 255, 255, 0.07);
  line-height: 1.7;
  white-space: pre-wrap;
}

.message-segment {
  margin: 0;
  white-space: pre-wrap;
}

.assistant .message-segment.narration {
  color: rgba(214, 220, 239, 0.56);
  font-size: 13px;
  line-height: 1.65;
}

.assistant .message-segment.dialogue {
  color: #f4f5ff;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.78;
}

.user .bubble {
  border: 0;
  border-radius: 16px 4px 16px 16px;
  background: linear-gradient(135deg, #7164ef, #a06ad6);
}

time {
  display: block;
  margin-top: 5px;
  color: #606b8a;
  font-size: 10px;
}

.user time {
  text-align: right;
}

.typing {
  display: flex;
  gap: 5px;
  align-items: center;
  height: 42px;
  padding: 0 16px;
  border-radius: 5px 15px 15px;
  background: rgba(255, 255, 255, 0.08);
}

.typing i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #bcb9ec;
  animation: typing 1s infinite;
}

.typing i:nth-child(2) {
  animation-delay: 0.18s;
}

.typing i:nth-child(3) {
  animation-delay: 0.36s;
}

.composer {
  gap: 8px;
  align-items: end;
  padding: 16px 8% 25px;
}

.composer textarea {
  flex: 1;
  min-height: 48px;
  padding: 13px 15px;
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 15px;
  outline: 0;
  color: #e7e9fa;
  background: rgba(255, 255, 255, 0.05);
  font: inherit;
  resize: none;
}

.send {
  width: 44px;
  height: 44px;
  border-radius: 14px !important;
  color: white !important;
  background: linear-gradient(135deg, #7668ff, #b36bea) !important;
}

.send:disabled {
  cursor: not-allowed;
  opacity: 0.43;
}

.relationship-panel {
  position: relative;
  padding: 28px 21px;
  background: rgba(14, 19, 42, 0.8);
}

.has-character-background .relationship-panel {
  background: rgba(10, 15, 35, 0.28);
  backdrop-filter: blur(9px);
}

.panel-close {
  position: absolute;
  top: 16px;
  left: -16px;
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: #aeb7d4;
  cursor: pointer;
  background: #171d3d;
}

.person {
  position: relative;
  display: grid;
  height: 205px;
  place-items: center;
}

.aura {
  position: absolute;
  width: 155px;
  height: 155px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(171, 128, 255, 0.48), transparent 68%);
  animation: breathe 3.5s infinite;
}

.person-logo {
  position: relative;
  z-index: 2;
  display: grid;
  width: 120px;
  height: 148px;
  place-items: center;
  border-radius: 60px 60px 32px;
  color: white;
  background: linear-gradient(145deg, #8c6bc2, #523b82);
  box-shadow: 0 17px 35px rgba(122, 84, 205, 0.3);
  font-size: 42px;
  font-weight: 800;
  animation: floating 4.5s infinite;
}

.profile {
  text-align: center;
}

.profile p {
  margin: 0;
  color: #8f99b9;
  font-size: 11px;
}

.profile h2 {
  margin: 5px 0;
  color: white;
}

.profile span {
  color: #a5adca;
  font-size: 12px;
}

.relationship-button {
  width: 100%;
  margin-top: 23px;
  padding: 15px;
  border: 1px solid rgba(174, 158, 255, 0.18);
  border-radius: 16px;
  color: inherit;
  cursor: pointer;
  background: rgba(136, 116, 255, 0.1);
  text-align: left;
}

.relationship-button > div {
  justify-content: space-between;
}

.relationship-button span {
  display: flex;
  gap: 6px;
  align-items: center;
  color: #dad7f5;
  font-size: 12px;
}

.relationship-button strong {
  color: #e0bdff;
}

.relationship-button section {
  height: 5px;
  margin-top: 12px;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.1);
}

.relationship-button section i {
  display: block;
  width: 28%;
  height: 100%;
  background: linear-gradient(90deg, #a78bff, #ff9bc7);
}

.relationship-button p {
  margin: 11px 0 0;
  color: #9fa9c7;
  font-size: 11px;
}

.description-card {
  margin-top: 25px;
  padding: 15px;
  overflow: hidden;
  border: 1px solid rgba(174, 159, 255, 0.16);
  border-radius: 16px;
  outline: 0;
  background: linear-gradient(
    145deg,
    rgba(127, 106, 246, 0.12),
    rgba(255, 255, 255, 0.035)
  );
  cursor: default;
  transition: 0.25s ease;
}

.description-card:hover,
.description-card:focus {
  border-color: rgba(189, 169, 255, 0.42);
  background: linear-gradient(
    145deg,
    rgba(132, 110, 252, 0.19),
    rgba(255, 255, 255, 0.06)
  );
  box-shadow: 0 13px 28px rgba(61, 47, 145, 0.2);
  transform: translateY(-3px);
}

.description-title {
  display: flex;
  gap: 7px;
  align-items: center;
  color: #ded9ff;
}

.description-title strong {
  font-size: 13px;
}

.description-card p {
  max-height: 208px;
  margin: 11px 0 8px;
  overflow-y: auto;
  padding-right: 4px;
  color: #b9c2dc;
  font-size: 12px;
  line-height: 1.75;
  white-space: pre-wrap;
}

.description-card > span {
  color: #968dde;
  font-size: 10px;
}

.voice-panel {
  position: fixed;
  z-index: 20;
  right: 340px;
  bottom: 92px;
  display: flex;
  gap: 13px;
  align-items: center;
  padding: 15px;
  border: 1px solid rgba(171, 158, 255, 0.24);
  border-radius: 17px;
  background: rgba(26, 25, 62, 0.95);
}

.wave {
  display: flex;
  gap: 3px;
}

.wave i {
  width: 3px;
  height: 16px;
  background: #bdadff;
  animation: wave 0.8s infinite alternate;
}

.voice-panel button {
  color: #d4cffb;
  background: rgba(255, 255, 255, 0.08);
}

.mask,
.detail-mask {
  position: fixed;
  z-index: 100;
  inset: 0;
  background: rgba(3, 6, 19, 0.72);
  backdrop-filter: blur(8px);
}

.mask {
  display: grid;
  padding: 20px;
  place-items: center;
}

.modal {
  position: relative;
  width: min(400px, 100%);
  padding: 31px;
  border: 1px solid rgba(226, 211, 255, 0.25);
  border-radius: 25px;
  background: linear-gradient(145deg, #25204d, #12182f);
  box-shadow: 0 28px 75px rgba(0, 0, 0, 0.5);
}

.close {
  position: absolute;
  top: 13px;
  right: 15px;
  width: 31px;
  height: 31px;
  border: 0;
  border-radius: 9px;
  color: #abb5d3;
  cursor: pointer;
  background: transparent;
  font-size: 25px;
}

.modal-icon {
  display: grid;
  width: 51px;
  height: 51px;
  place-items: center;
  margin: auto;
  border-radius: 17px;
  color: #ffafcb;
  background: rgba(255, 108, 166, 0.12);
}

.eyebrow {
  margin: 20px 0 8px;
  color: #b5a5ff;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.6px;
}

.modal .eyebrow,
.modal h2 {
  text-align: center;
}

.modal h2 {
  margin: 0;
  color: #f4f2ff;
}

.description {
  color: #adb6d1;
  font-size: 13px;
  line-height: 1.75;
  text-align: center;
}

.modal-character {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 11px 13px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.05);
}

.modal-character b {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 11px;
  color: white;
  background: #8068cf;
}

.modal-character strong {
  color: #e8e9fb;
  font-size: 12px;
}

.modal-character p {
  margin: 3px 0;
  color: #818ca9;
  font-size: 10px;
}

.delete-error {
  margin: 14px 0 0;
  color: #ff9dbf;
  font-size: 12px;
  text-align: center;
}

.modal-actions {
  gap: 10px;
  margin-top: 22px;
}

.modal-actions button {
  display: flex;
  flex: 1;
  gap: 7px;
  justify-content: center;
  align-items: center;
  min-height: 42px;
  border: 0;
  border-radius: 11px;
  color: #cad1e7;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.06);
}

.modal-actions .danger {
  color: white;
  background: linear-gradient(135deg, #db668d, #ef7cae);
}

.detail-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: min(430px, 100%);
  height: 100vh;
  padding: 42px 30px;
  border-left: 1px solid rgba(255, 255, 255, 0.13);
  background: #161834;
}

.detail-panel h2 {
  color: #f4f2ff;
  line-height: 1.35;
}

.temperature {
  display: flex;
  gap: 17px;
  align-items: center;
  margin: 30px 0;
  padding: 17px;
  border-radius: 19px;
  background: rgba(139, 112, 255, 0.1);
}

.temperature > strong {
  display: grid;
  width: 74px;
  height: 74px;
  place-items: center;
  border: 6px solid #a98cff;
  border-left-color: rgba(255, 255, 255, 0.16);
  border-radius: 50%;
  color: white;
}

.temperature b {
  color: #e7e8fa;
  font-size: 14px;
}

.temperature p {
  color: #9ea8c7;
  font-size: 12px;
  line-height: 1.6;
}

.detail-panel footer {
  display: flex;
  gap: 10px;
  margin-top: 31px;
  padding: 14px;
  border-radius: 14px;
  color: #bebfd8;
  background: rgba(163, 132, 255, 0.1);
  font-size: 11px;
  line-height: 1.65;
}

.character-detail-mask {
  position: fixed;
  z-index: 120;
  inset: 0;
  padding: 24px;
  overflow-y: auto;
  background: rgba(3, 6, 18, 0.75);
  backdrop-filter: blur(12px);
}

/* 详情页以轻微上浮、聚焦的方式出现，避免整页生硬地替换聊天界面。 */
.character-detail-enter-active,
.character-detail-leave-active {
  transition: opacity 280ms ease;
}

.character-detail-enter-from,
.character-detail-leave-to {
  opacity: 0;
}

.character-detail-enter-active .character-detail-page {
  animation: character-detail-page-in 480ms cubic-bezier(0.22, 1, 0.36, 1) both;
}

.character-detail-leave-active .character-detail-page {
  animation: character-detail-page-out 220ms cubic-bezier(0.4, 0, 1, 1) both;
}

.character-detail-enter-active .character-detail-profile,
.character-detail-enter-active .memory-editor {
  animation: character-detail-section-in 460ms cubic-bezier(0.22, 1, 0.36, 1) both;
}

.character-detail-enter-active .memory-editor {
  animation-delay: 70ms;
}

@keyframes character-detail-page-in {
  from {
    opacity: 0;
    transform: translateY(22px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes character-detail-page-out {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(12px) scale(0.99);
  }
}

@keyframes character-detail-section-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .character-detail-enter-active,
  .character-detail-leave-active {
    transition-duration: 1ms;
  }

  .character-detail-enter-active .character-detail-page,
  .character-detail-leave-active .character-detail-page,
  .character-detail-enter-active .character-detail-profile,
  .character-detail-enter-active .memory-editor {
    animation: none;
  }
}

.character-detail-page {
  width: min(1180px, 100%);
  min-height: calc(100vh - 48px);
  margin: 0 auto;
  overflow: hidden;
  border: 1px solid rgba(214, 201, 255, 0.18);
  border-radius: 26px;
  background: linear-gradient(135deg, rgba(26, 22, 61, 0.97), rgba(11, 15, 35, 0.98));
  box-shadow: 0 34px 100px rgba(0, 0, 0, 0.52);
  transform-origin: 50% 18%;
}

.character-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(9, 12, 31, 0.46);
}

.character-detail-header button {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 9px 12px;
  border: 1px solid rgba(190, 177, 255, 0.22);
  border-radius: 10px;
  color: #cdd3ec;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.045);
  font: inherit;
  font-size: 12px;
}

.character-detail-header p {
  margin: 0;
  color: #c8c0ff;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.5px;
}

.character-detail-content {
  display: grid;
  grid-template-columns: minmax(250px, 0.7fr) minmax(0, 1.3fr);
  min-height: calc(100vh - 113px);
}

.character-detail-profile {
  padding: 34px 29px;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(160deg, rgba(116, 92, 210, 0.14), rgba(9, 14, 33, 0.12));
}

.detail-cover {
  display: grid;
  width: min(210px, 100%);
  aspect-ratio: 1;
  place-items: center;
  margin: 0 auto 24px;
  overflow: hidden;
  border: 1px solid rgba(224, 217, 255, 0.18);
  border-radius: 28px;
  color: white;
  background: linear-gradient(145deg, #9b7be5, #49377f);
  font-size: 52px;
  font-weight: 800;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.24);
}

.detail-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-status {
  margin: 0 0 7px;
  color: #76e6ca;
  font-size: 12px;
}

.character-detail-profile h2 {
  margin: 0;
  color: #f5f3ff;
  font-size: 28px;
}

.character-detail-profile > span {
  display: block;
  margin-top: 7px;
  color: #abb6d7;
  font-size: 13px;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 22px;
}

.detail-tags i {
  padding: 6px 9px;
  border-radius: 9px;
  color: #d7ceff;
  background: rgba(152, 124, 255, 0.13);
  font-size: 11px;
  font-style: normal;
}

.detail-description {
  margin: 24px 0 0;
  color: #aeb8d4;
  font-size: 13px;
  line-height: 1.85;
  white-space: pre-wrap;
}

.memory-editor {
  padding: 34px clamp(22px, 4vw, 46px);
}

.memory-editor-heading {
  display: flex;
  gap: 20px;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 26px;
}

.memory-editor-heading p {
  margin: 0 0 7px;
  color: #ad98ff;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.4px;
}

.memory-editor-heading h2 {
  margin: 0;
  color: #f5f3ff;
  font-size: 24px;
}

.memory-editor-heading span {
  display: block;
  margin-top: 9px;
  color: #929dbd;
  font-size: 12px;
}

.add-memory-card,
.memory-editor-footer button {
  border: 0;
  border-radius: 11px;
  color: white;
  cursor: pointer;
  background: linear-gradient(135deg, #7668ff, #af69df);
  box-shadow: 0 10px 24px rgba(113, 94, 241, 0.22);
  font: inherit;
  font-size: 12px;
  font-weight: 700;
}

.add-memory-card {
  flex: none;
  padding: 10px 13px;
}

.add-memory-card:disabled,
.memory-editor-footer button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.memory-readonly,
.memory-editor-error,
.memory-editor-success {
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 12px;
}

.memory-readonly {
  margin: 0 0 17px;
  color: #adb8d3;
  background: rgba(255, 255, 255, 0.045);
}

.memory-card-list {
  display: grid;
  gap: 15px;
}

.memory-edit-card {
  padding: 17px;
  border: 1px solid rgba(165, 143, 255, 0.18);
  border-radius: 17px;
  background: linear-gradient(145deg, rgba(117, 91, 211, 0.11), rgba(255, 255, 255, 0.025));
}

.memory-card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  color: #e6e1ff;
  font-size: 13px;
}

.memory-card-title button {
  border: 0;
  color: #f3a0ba;
  cursor: pointer;
  background: transparent;
  font: inherit;
  font-size: 11px;
}

.memory-edit-card label {
  display: block;
  margin-top: 12px;
}

.memory-edit-card label:first-of-type {
  margin-top: 0;
}

.memory-edit-card label > span {
  display: block;
  margin-bottom: 7px;
  color: #aeb8d5;
  font-size: 11px;
}

.memory-edit-card input,
.memory-edit-card textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 10px 11px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  outline: 0;
  color: #eef0ff;
  background: rgba(5, 8, 25, 0.48);
  font: inherit;
  font-size: 13px;
  line-height: 1.65;
}

.memory-edit-card textarea {
  resize: vertical;
}

.memory-edit-card input:focus,
.memory-edit-card textarea:focus {
  border-color: rgba(182, 159, 255, 0.7);
  box-shadow: 0 0 0 3px rgba(137, 111, 246, 0.13);
}

.memory-edit-card input[readonly],
.memory-edit-card textarea[readonly] {
  cursor: default;
  color: #c7cee4;
  background: rgba(5, 8, 25, 0.28);
}

.memory-editor-error {
  margin: 15px 0 0;
  color: #ffacc4;
  background: rgba(255, 101, 148, 0.1);
}

.memory-editor-success {
  margin: 15px 0 0;
  color: #7ee8ce;
  background: rgba(78, 214, 181, 0.1);
}

.memory-editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  color: #8490b3;
  font-size: 11px;
}

.memory-editor-footer button {
  padding: 11px 16px;
}

@keyframes typing {
  50% {
    opacity: 0.35;
    transform: translateY(-4px);
  }
}

@keyframes breathe {
  50% {
    opacity: 0.55;
    transform: scale(1.12);
  }
}

@keyframes floating {
  50% {
    transform: translateY(-8px);
  }
}

@keyframes wave {
  to {
    height: 27px;
    background: #ffb8dd;
  }
}

@media (max-width: 820px) {
  .chat-page {
    display: block;
  }

  .chat-room {
    height: calc(100dvh - 64px);
    border: 0;
  }

  .relationship-panel {
    display: none;
  }

  .message-list {
    padding: 23px 18px;
  }

  .composer {
    padding: 12px 14px 16px;
  }

  .voice-panel {
    right: 16px;
    bottom: 88px;
  }
}

@media (max-width: 600px) {
  .chat-header {
    padding: 13px 15px;
  }

  .back-button {
    padding: 8px;
  }

  .back-button span {
    display: none;
  }

  .header-left {
    gap: 8px;
  }

  .header-character h1 {
    font-size: 14px;
  }

  .header-character small,
  .header-character em {
    display: none;
  }
}

@media (max-width: 780px) {
  .character-detail-mask {
    padding: 0;
  }

  .character-detail-page {
    min-height: 100vh;
    border: 0;
    border-radius: 0;
  }

  .character-detail-content {
    grid-template-columns: 1fr;
  }

  .character-detail-profile {
    padding: 25px 22px;
    border-right: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .detail-cover {
    width: 116px;
    margin: 0 0 17px;
  }

  .memory-editor {
    padding: 26px 20px;
  }

  .memory-editor-heading,
  .memory-editor-footer {
    align-items: start;
    flex-direction: column;
  }
}
</style>
