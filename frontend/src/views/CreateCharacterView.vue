<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  ArrowRight,
  ChevronRight,
  Check,
  Eye,
  EyeOff,
  Heart,
  ImagePlus,
  Mars,
  MessageCircleHeart,
  Plus,
  Sparkles,
  Trash2,
  Venus,
  WandSparkles,
  X,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'

// Keep requests on the current host so Vite/ngrok can proxy /api to FastAPI.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const router = useRouter()

const currentStep = ref(1)
const isSubmitting = ref(false)
const submitError = ref('')

const form = ref({
  name: '',
  avatar: '',
  color: 'purple',
  gender: 'female',
  background_image: '',
  description: '',
  relationship: '知心朋友',
  opening: '',
  visibility: 'private',
})

const memoryCards = ref([
  {
    id: `memory_${Date.now()}`,
    key: '',
    content: '',
  },
])
const activeMemoryCardIndex = ref(0)
const activeMemoryCard = computed(
  () => memoryCards.value[activeMemoryCardIndex.value],
)

function addMemoryCard() {
  memoryCards.value.push({
    id: `memory_${Date.now()}_${memoryCards.value.length}`,
    key: '',
    content: '',
  })
  activeMemoryCardIndex.value = memoryCards.value.length - 1
}

function nextMemoryCard() {
  if (memoryCards.value.length < 2) return
  activeMemoryCardIndex.value =
    (activeMemoryCardIndex.value + 1) % memoryCards.value.length
}

function removeActiveMemoryCard() {
  if (memoryCards.value.length === 1) {
    memoryCards.value[0].key = ''
    memoryCards.value[0].content = ''
    return
  }
  memoryCards.value.splice(activeMemoryCardIndex.value, 1)
  if (activeMemoryCardIndex.value >= memoryCards.value.length) {
    activeMemoryCardIndex.value = 0
  }
}

function getValidMemoryCards() {
  return memoryCards.value
    .map((card) => ({
      id: card.id,
      key: card.key.trim(),
      content: card.content.trim(),
    }))
    .filter((card) => card.key && card.content)
}

const steps = [
  { number: 1, title: '形象设计' },
  { number: 2, title: '角色简介' },
  { number: 3, title: '核心记忆' },
  { number: 4, title: '初始问候' },
]

const backgroundInput = ref(null)
const backgroundFile = ref(null)
const backgroundPreview = ref('')
const greetingInput = ref(null)
const greetingFile = ref(null)
const greetingPreview = ref('')

const relationshipOptions = [
  '知心朋友',
  '恋人陪伴',
  '学习搭子',
  '情绪树洞',
  '睡前聊天对象',
]

const showPersonalityModal = ref(false)
const selectedPersonalityTags = ref([])
const personalityTags = [
  '温柔', '治愈', '耐心', '共情', '安静', '可靠', '真诚', '理性',
  '活泼', '元气', '幽默', '细腻', '浪漫', '傲娇', '清醒', '松弛',
  '毒舌', '神秘', '成熟', '黏人', '专一', '高冷', '会倾听', '会鼓励',
  '夜猫子', '学习搭子', '情绪树洞', '睡前陪伴',
]

function togglePersonalityTag(tag) {
  const index = selectedPersonalityTags.value.indexOf(tag)
  if (index >= 0) {
    selectedPersonalityTags.value.splice(index, 1)
  } else if (selectedPersonalityTags.value.length < 8) {
    selectedPersonalityTags.value.push(tag)
  }
}

const previewName = computed(() => {
  return form.value.name.trim() || '未命名角色'
})

const previewAvatar = computed(() => previewName.value.slice(0, 1))

function selectBackground() {
  backgroundInput.value?.click()
}

function handleBackgroundChange(event) {
  const file = event.target.files?.[0]
  if (!file) return

  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    submitError.value = '请上传 JPG、PNG 或 WEBP 格式的图片。'
    event.target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    submitError.value = '背景图片不能超过 5MB。'
    event.target.value = ''
    return
  }

  if (backgroundPreview.value) URL.revokeObjectURL(backgroundPreview.value)
  backgroundFile.value = file
  backgroundPreview.value = URL.createObjectURL(file)
  submitError.value = ''
}

function removeBackground() {
  if (backgroundPreview.value) URL.revokeObjectURL(backgroundPreview.value)
  backgroundFile.value = null
  backgroundPreview.value = ''
  form.value.background_image = ''
  if (backgroundInput.value) backgroundInput.value.value = ''
}

function selectGreetingImage() {
  greetingInput.value?.click()
}

function handleGreetingChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    submitError.value = '请上传 JPG、PNG 或 WEBP 格式的问候图片。'
    event.target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    submitError.value = '问候图片不能超过 5MB。'
    event.target.value = ''
    return
  }
  if (greetingPreview.value) URL.revokeObjectURL(greetingPreview.value)
  greetingFile.value = file
  greetingPreview.value = URL.createObjectURL(file)
  submitError.value = ''
}

function removeGreetingImage() {
  if (greetingPreview.value) URL.revokeObjectURL(greetingPreview.value)
  greetingFile.value = null
  greetingPreview.value = ''
  if (greetingInput.value) greetingInput.value.value = ''
}

async function uploadBackground(token) {
  if (!backgroundFile.value) return ''
  const body = new FormData()
  body.append('file', backgroundFile.value)
  const response = await fetch(`${API_BASE_URL}/api/uploads/character-background`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body,
  })
  const result = await response.json()
  if (!response.ok) throw new Error(result.detail || '背景图片上传失败，请稍后重试。')
  return result.data.image_url
}

async function uploadGreetingImage(token) {
  if (!greetingFile.value) return ''
  const body = new FormData()
  body.append('file', greetingFile.value)
  const response = await fetch(`${API_BASE_URL}/api/uploads/greeting-image`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body,
  })
  const result = await response.json()
  if (!response.ok) throw new Error(result.detail || '问候图片上传失败，请稍后重试。')
  return result.data.image_url
}

onBeforeUnmount(() => {
  if (backgroundPreview.value) URL.revokeObjectURL(backgroundPreview.value)
  if (greetingPreview.value) URL.revokeObjectURL(greetingPreview.value)
})

function nextStep() {
  submitError.value = ''

  if (currentStep.value === 1) {
    if (!form.value.name.trim()) {
      submitError.value = '请先填写角色名称'
      return
    }

    if (!['male', 'female'].includes(form.value.gender)) {
      submitError.value = '请选择角色性别，再进入下一步。'
      return
    }
  }

  if (currentStep.value === 2 && !form.value.description.trim()) {
    submitError.value = '请先填写角色简介'
    return
  }

  if (currentStep.value === 3 && !getValidMemoryCards().length) {
    submitError.value = '请至少完成一张记忆卡：填写关键词和对应内容。'
    return
  }

  if (currentStep.value < 4) {
    currentStep.value += 1
  }
}

function previousStep() {
  if (currentStep.value > 1) {
    currentStep.value -= 1
  }
}

function goToStep(step) {
  if (step <= currentStep.value) {
    currentStep.value = step
  }
}

async function completeCreation() {
  if (!form.value.name.trim()) {
    submitError.value = '先给你的角色取一个名字吧。'
    currentStep.value = 1
    return
  }

  if (!form.value.description.trim()) {
    submitError.value = '请先写下这位角色的简介。'
    currentStep.value = 2
    return
  }

  const validMemoryCards = getValidMemoryCards()
  if (!validMemoryCards.length) {
    submitError.value = '请至少完成一张记忆卡，再创建角色。'
    currentStep.value = 3
    return
  }

  const token = localStorage.getItem('lumi_access_token')

  if (!token) {
    router.push({
      path: '/login',
      query: {
        redirect: '/create',
      },
    })
    return
  }

  isSubmitting.value = true
  submitError.value = ''

  try {
    form.value.background_image = await uploadBackground(token)
    const greetingImage = await uploadGreetingImage(token)
    const response = await fetch(
      `${API_BASE_URL}/api/custom-characters`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: form.value.name.trim(),
          avatar: previewAvatar.value,
          color: form.value.color,
          atmosphere: form.value.atmosphere,
          gender: form.value.gender,
          background_image: form.value.background_image,
          relationship: form.value.relationship,
          description: form.value.description.trim(),
          opening: form.value.opening.trim(),
          greeting_image: greetingImage,
          memory_cards: validMemoryCards,
          personality_tags: selectedPersonalityTags.value,
          visibility: form.value.visibility,
        }),
      },
    )

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.detail || '创建角色失败，请稍后重试。')
    }

    const character = result.data

    // 让 ChatView 能马上读取刚创建好的角色
    localStorage.setItem(
      'selected_character',
      JSON.stringify(character),
    )

    router.push({
      path: '/my-characters',
      query: {
        tab: 'created',
      },
    })
  } catch (error) {
    submitError.value = error.message || '网络连接失败，请确认后端正在运行。'
  } finally {
    isSubmitting.value = false
  }
}
</script>
<template>
  <PageLayout>
    <main class="create-page">
      <header class="page-header">
        <div>
          <p class="eyebrow">
            <WandSparkles :size="15" />
            CREATE YOUR COMPANION
          </p>

         

         
        </div>

        <RouterLink class="back-link" to="/characters">
          <ArrowLeft :size="17" />
          返回角色广场
        </RouterLink>
      </header>

      <section class="creator-layout">
        <aside class="steps-panel">
          <button
            v-for="step in steps"
            :key="step.number"
            class="step-item"
            :class="{
              active: currentStep === step.number,
              done: currentStep > step.number,
            }"
            type="button"
            @click="goToStep(step.number)"
          >
            <span class="step-number">
              <Check v-if="currentStep > step.number" :size="16" />
              <template v-else>{{ step.number }}</template>
            </span>

            <span>
              <strong>{{ step.title }}</strong>
              <small>{{ step.subtitle }}</small>
            </span>
          </button>

          <div class="steps-tip">
            <Sparkles :size="17" />
            <p>不用一次设定得完美，之后也可以随时修改角色设定。</p>
          </div>
        </aside>

        <section class="form-panel">
          <!-- 第一步 -->
          <template v-if="currentStep === 1">
            <p class="step-label">STEP 01</p>
            
            

            <label class="field">
              <span>角色名称 <em>*</em></span>
              <input
                v-model="form.name"
                maxlength="12"
                placeholder="例如：知夏、临舟、小夜"
              />
            </label>

            <div class="field">
              <span>角色性别 <em>*</em></span>
              <div class="gender-options">
                <button
                  class="gender-option male"
                  :class="{ selected: form.gender === 'male' }"
                  type="button"
                  @click="form.gender = 'male'"
                >
                  <Mars :size="20" />
                  男
                </button>
                <button
                  class="gender-option female"
                  :class="{ selected: form.gender === 'female' }"
                  type="button"
                  @click="form.gender = 'female'"
                >
                  <Venus :size="20" />
                  女
                </button>
              </div>
            </div>

            <div class="field">
              <span>角色背景图 <small class="optional">JPG / PNG / WEBP，最大 5MB</small></span>
              <input
                ref="backgroundInput"
                class="file-input"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                @change="handleBackgroundChange"
              />
              <div v-if="backgroundPreview" class="upload-preview">
                <img :src="backgroundPreview" alt="角色背景预览" />
                <button type="button" class="remove-image" @click="removeBackground">
                  <X :size="16" /> 移除图片
                </button>
              </div>
              <button v-else type="button" class="upload-area" @click="selectBackground">
                <ImagePlus :size="26" />
                <strong>上传背景图片</strong>
              </button>
            </div>
          </template>

          <!-- 第二步 -->
          <template v-if="currentStep === 2">
            <p class="step-label">STEP 02</p>
            
           

            <label class="field">
              <span>角色简介 <em>*</em></span>
              <textarea
                v-model="form.description"
                maxlength="500"
                rows="8"
                placeholder="例如：TA 是一位温柔、耐心的倾听者，喜欢在深夜陪人梳理心事。不催促、不评判，总会用舒缓的方式回应你的情绪。"
              ></textarea>
              <small>{{ form.description.length }}/500</small>
            </label>
          </template>

          <!-- 第三步 -->
          <template v-if="currentStep === 3">
            <p class="step-label">STEP 03</p>
          
            

            <section class="personality-section">
              <div class="personality-heading">
                <div>
                  <span>个性标签</span>
                 
                </div>
                <button type="button" class="more-tags-button" @click="showPersonalityModal = true">
                  更多
                </button>
              </div>
              <div class="selected-tags">
                <button
                  v-for="tag in selectedPersonalityTags"
                  :key="tag"
                  type="button"
                  class="selected-tag"
                  @click="togglePersonalityTag(tag)"
                >
                  {{ tag }} <X :size="13" />
                </button>
                <span v-if="!selectedPersonalityTags.length" class="selected-tags-placeholder">
                  暂未选择，点击“更多”选择个性标签
                </span>
              </div>
            </section>

            <section class="memory-section">
              <div class="memory-section-heading">
                <div>
                  <span>核心记忆 <em>*</em></span>
              
                </div>
                <span class="memory-count">{{ activeMemoryCardIndex + 1 }} / {{ memoryCards.length }}</span>
              </div>

              <div class="memory-deck" :class="{ 'has-next-card': memoryCards.length > 1 }">
                <div v-if="memoryCards.length > 1" class="memory-card-back memory-card-back-two"></div>
                <div v-if="memoryCards.length > 1" class="memory-card-back memory-card-back-one"></div>

                <Transition name="memory-card" mode="out-in">
                  <article :key="activeMemoryCard.id" class="memory-card-front">
                    <div class="memory-card-toolbar">
                      <span>记忆卡 {{ activeMemoryCardIndex + 1 }}</span>
                      <button type="button" class="memory-remove" @click="removeActiveMemoryCard">
                        <Trash2 :size="15" />
                        删除
                      </button>
                    </div>

                    <label class="memory-field">
                      <span>记忆关键词</span>
                      <input
                        v-model="activeMemoryCard.key"
                        maxlength="40"
                        placeholder="例如：性格、外貌、成长经历、相处模式"
                      />
                    </label>

                    <label class="memory-field">
                      <span>对应内容</span>
                      <textarea
                        v-model="activeMemoryCard.content"
                        maxlength="1500"
                        rows="6"
                        placeholder="描述这项设定的具体内容。AI 会把它作为角色长期稳定的人物设定。"
                      ></textarea>
                      <small>{{ activeMemoryCard.content.length }}/1500</small>
                    </label>
                  </article>
                </Transition>

                <div class="memory-actions">
                  <button type="button" class="add-memory-button" @click="addMemoryCard">
                    <Plus :size="17" />
                    新增记忆卡
                  </button>
                  <button
                    v-if="memoryCards.length > 1"
                    type="button"
                    class="next-memory-button"
                    @click="nextMemoryCard"
                  >
                    下一张记忆
                    <ChevronRight :size="17" />
                  </button>
                </div>
              </div>
            </section>
          </template>

          <!-- 第四步 -->
         <!-- 第四步 -->
<template v-if="currentStep === 4">
  <p class="step-label">STEP 04</p>
  

  

  <label class="field">
    <span>初始问候 <span class="optional">可选</span></span>

    <textarea
      v-model="form.opening"
      maxlength="500"
      rows="6"
      placeholder="例如：晚上好呀，我是知夏。今天想从哪里开始聊起呢？"
    ></textarea>

    <small>{{ form.opening.length }}/500</small>
  </label>

  <div class="field">
    <span>问候语图片 <span class="optional">可选</span></span>
    <input
      ref="greetingInput"
      class="hidden-file-input"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      @change="handleGreetingChange"
    />
    <div v-if="greetingPreview" class="greeting-image-preview">
      <img :src="greetingPreview" alt="问候语图片预览" />
      <button type="button" @click="removeGreetingImage">
        <X :size="16" /> 移除图片
      </button>
    </div>
    <button v-else type="button" class="greeting-upload" @click="selectGreetingImage">
      <ImagePlus :size="18" /> 添加问候语图片
    </button>
    <small>进入聊天时会展示在初始问候语下方，支持 JPG、PNG、WEBP，最大 5MB。</small>
  </div>

  <div class="field">
    <span>角色可见范围</span>

    <div class="visibility-grid">
      <button
        type="button"
        class="visibility-option"
        :class="{ selected: form.visibility === 'private' }"
        @click="form.visibility = 'private'"
      >
        <span class="visibility-icon private">
          <EyeOff :size="19" />
        </span>

        <span>
          <strong>仅自己可见</strong>
          <small>角色只会出现在“我的创建”中。</small>
        </span>

        <Check
          v-if="form.visibility === 'private'"
          class="selected-check"
          :size="18"
        />
      </button>

      <button
        type="button"
        class="visibility-option"
        :class="{ selected: form.visibility === 'public' }"
        @click="form.visibility = 'public'"
      >
        <span class="visibility-icon public">
          <Eye :size="19" />
        </span>

        <span>
          <strong>公开到角色广场</strong>
          <small>其他用户可以在角色广场看见并选择 TA。</small>
        </span>

        <Check
          v-if="form.visibility === 'public'"
          class="selected-check"
          :size="18"
        />
      </button>
    </div>
  </div>

 

</template>

          <p v-if="submitError" class="submit-error">
            {{ submitError }}
          </p>

          <footer class="form-footer">
            <button
              v-if="currentStep > 1"
              class="previous-button"
              type="button"
              @click="previousStep"
            >
              <ArrowLeft :size="17" />
              上一步
            </button>

            <span v-else></span>

            <button
              v-if="currentStep < 4"
              class="next-button"
              type="button"
              @click="nextStep"
            >
              下一步
              <ArrowRight :size="17" />
            </button>

           <button
  v-else
  class="next-button complete-button"
  type="button"
  :disabled="isSubmitting"
  @click="completeCreation"
>
  <Sparkles v-if="isSubmitting" :size="18" class="loading-icon" />
  <MessageCircleHeart v-else :size="18" />

  {{ isSubmitting ? '正在创建角色…' : '完成并保存角色' }}
</button>
          </footer>
        </section>

        <aside class="preview-panel">
          <p class="preview-title">实时预览</p>

          <div class="preview-card" :class="form.color">
            <img
              v-if="backgroundPreview"
              class="preview-background"
              :src="backgroundPreview"
              alt=""
            />
            <div v-if="backgroundPreview" class="preview-shade"></div>
            <div class="preview-glow"></div>

            <div class="preview-status">
              <i></i>
              正在等待你的消息
            </div>

            <div class="preview-avatar-wrap">
              <div class="preview-avatar">
                {{ previewAvatar }}
              </div>
              <span class="avatar-orbit"></span>
              <span class="star star-one">✦</span>
              <span class="star star-two">✧</span>
            </div>

            <div class="preview-info">
              <p class="preview-gender" :class="form.gender">
                <Mars v-if="form.gender === 'male'" :size="15" />
                <Venus v-else :size="15" />
                {{ form.gender === 'male' ? '男' : '女' }}
              </p>
              <h3>{{ previewName }}</h3>
            </div>

            <div class="preview-message">
              <span>“</span>
              <p>{{ form.description || '写下角色简介后，这里会显示 TA 的独特故事。' }}</p>
            </div>

          </div>

          <p class="preview-tip">
            右侧卡片会随着你的设定即时变化。
          </p>
        </aside>
      </section>
    </main>

    <Transition name="tag-modal">
      <div v-if="showPersonalityModal" class="tag-modal-mask" @click.self="showPersonalityModal = false">
        <section class="tag-modal" role="dialog" aria-modal="true" aria-label="选择个性标签">
          <header>
            <div>
              <p>PERSONALITY TAGS</p>
              <h3>选择 TA 的个性标签</h3>
            </div>
            <button type="button" class="tag-modal-close" @click="showPersonalityModal = false">
              <X :size="19" />
            </button>
          </header>
          <p class="tag-modal-tip">已选 {{ selectedPersonalityTags.length }}/8。再次点击标签可取消选择。</p>
          <div class="tag-modal-grid">
            <button
              v-for="tag in personalityTags"
              :key="tag"
              type="button"
              :class="{ selected: selectedPersonalityTags.includes(tag) }"
              @click="togglePersonalityTag(tag)"
            >
              <Check v-if="selectedPersonalityTags.includes(tag)" :size="14" />
              {{ tag }}
            </button>
          </div>
          <footer>
            <button type="button" @click="showPersonalityModal = false">完成选择</button>
          </footer>
        </section>
      </div>
    </Transition>
  </PageLayout>
</template>

<style scoped>
.create-page {
  width: min(1380px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  padding: 66px 6% 80px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 25px;
  align-items: end;
  margin-bottom: 45px;
}

.eyebrow {
  display: flex;
  gap: 7px;
  align-items: center;
  margin: 0 0 12px;
  color: #a499ff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.8px;
}

.page-header h1 {
  margin: 0 0 12px;
  color: #f3f2ff;
  font-size: clamp(31px, 4vw, 48px);
  letter-spacing: -1.5px;
}

.page-header > div > p:last-child {
  margin: 0;
  color: #a5afcd;
  font-size: 15px;
}

.back-link {
  display: flex;
  gap: 7px;
  align-items: center;
  padding: 10px 12px;
  color: #aeb7d2;
  border-radius: 10px;
  text-decoration: none;
  transition: 0.2s ease;
}

.back-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}

.creator-layout {
  display: grid;
  grid-template-columns: 220px minmax(400px, 1fr) 285px;
  gap: 22px;
  align-items: start;
}

.steps-panel,
.form-panel,
.preview-panel {
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.035);
}

.steps-panel {
  padding: 14px;
}

.step-item {
  display: flex;
  gap: 11px;
  width: 100%;
  padding: 13px 8px;
  color: #7e88a8;
  border-radius: 13px;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.step-item.active {
  color: #f0efff;
  background: linear-gradient(90deg, rgba(118, 104, 255, 0.2), transparent);
}

.step-item.done {
  color: #bfb9f6;
}

.step-number {
  display: grid;
  flex: 0 0 auto;
  width: 27px;
  height: 27px;
  place-items: center;
  color: #a5afcb;
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 9px;
  font-size: 12px;
}

.active .step-number,
.done .step-number {
  color: #fff;
  border-color: transparent;
  background: linear-gradient(135deg, #796bff, #b976ec);
}

.step-item strong,
.step-item small {
  display: block;
}

.step-item strong {
  margin: 1px 0 3px;
  font-size: 13px;
}

.step-item small {
  color: #737e9d;
  font-size: 10px;
}

.steps-tip {
  display: flex;
  gap: 8px;
  margin: 23px 4px 5px;
  padding-top: 17px;
  color: #9c94e3;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.steps-tip p {
  margin: 0;
  color: #7f89aa;
  font-size: 11px;
  line-height: 1.6;
}

.form-panel {
  min-height: 570px;
  padding: 33px;
}

.step-label {
  margin: 0 0 8px;
  color: #978aff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.form-panel h2 {
  margin: 0;
  color: #f0f0ff;
  font-size: 27px;
}

.step-description {
  max-width: 610px;
  margin: 10px 0 27px;
  color: #98a3c0;
  font-size: 13px;
  line-height: 1.7;
}

.field {
  display: block;
  margin-top: 22px;
}

.field > span {
  display: block;
  margin-bottom: 9px;
  color: #dfe1f1;
  font-size: 13px;
  font-weight: 700;
}

.field em {
  color: #ff93b6;
  font-style: normal;
}

.field input,
.field textarea {
  width: 100%;
  padding: 12px 13px;
  color: #eaebfb;
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 12px;
  outline: none;
  background: rgba(7, 11, 27, 0.45);
  font: inherit;
  font-size: 13px;
  transition: 0.2s ease;
}

.field textarea {
  line-height: 1.6;
  resize: vertical;
}

.field input:focus,
.field textarea:focus {
  border-color: rgba(158, 140, 255, 0.5);
  box-shadow: 0 0 0 4px rgba(129, 110, 255, 0.09);
}

.field small {
  display: block;
  margin-top: 5px;
  color: #717c9b;
  font-size: 10px;
  text-align: right;
}

.avatar-options,
.color-options,
.atmosphere-grid,
.choice-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.avatar-option {
  display: grid;
  width: 43px;
  height: 43px;
  place-items: center;
  color: #d9d7f5;
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  font-size: 17px;
  font-weight: 800;
}

.avatar-option.selected {
  color: white;
  border-color: #a791ff;
  background: linear-gradient(135deg, #7b6cff, #ad70dc);
  box-shadow: 0 7px 17px rgba(113, 95, 232, 0.25);
}

.color-option,
.choice-option,
.atmosphere-option {
  color: #aeb7d2;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.035);
  cursor: pointer;
  transition: 0.2s ease;
}

.color-option {
  display: flex;
  gap: 7px;
  align-items: center;
  padding: 8px 10px;
  font-size: 11px;
}

.color-option i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.color-option.purple i {
  background: #9b81ff;
}

.color-option.pink i {
  background: #ed8ebd;
}

.color-option.blue i {
  background: #75b9ec;
}

.color-option.green i {
  background: #6bd2b7;
}

.color-option.orange i {
  background: #efa85e;
}

.color-option.selected,
.choice-option.selected,
.atmosphere-option.selected {
  color: #f2f1ff;
  border-color: rgba(160, 143, 255, 0.57);
  background: rgba(124, 105, 246, 0.16);
}

.atmosphere-option {
  display: flex;
  gap: 7px;
  align-items: center;
  padding: 10px 12px;
  font-size: 12px;
}

.choice-option {
  padding: 10px 13px;
  font-size: 12px;
}

.notice-card {
  display: flex;
  gap: 11px;
  margin-top: 23px;
  padding: 15px;
  color: #bdadff;
  border: 1px solid rgba(171, 151, 255, 0.19);
  border-radius: 14px;
  background: rgba(130, 110, 245, 0.09);
}

.notice-card strong {
  display: block;
  color: #e5e1ff;
  font-size: 12px;
}

.notice-card p {
  margin: 5px 0 0;
  color: #a9b1cc;
  font-size: 11px;
  line-height: 1.5;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 36px;
}

.previous-button,
.next-button {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  min-height: 42px;
  padding: 0 15px;
  border-radius: 11px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.previous-button {
  color: #b4bdd7;
  background: transparent;
}

.previous-button:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}

.next-button {
  color: white;
  background: linear-gradient(135deg, #7768ff, #b46dea);
  box-shadow: 0 9px 20px rgba(111, 94, 237, 0.23);
}

.next-button:hover {
  transform: translateY(-2px);
}

.complete-button {
  background: linear-gradient(135deg, #8e69eb, #ec79b3);
}

.preview-panel {
  position: sticky;
  top: 24px;
  padding: 17px;
}

.preview-title {
  margin: 0 0 14px;
  color: #a9b2ce;
  font-size: 12px;
  font-weight: 700;
}

.preview-card {
  position: relative;
  min-height: 405px;
  padding: 15px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 19px;
  background: linear-gradient(150deg, rgba(105, 87, 176, 0.56), rgba(22, 25, 62, 0.9));
}

.gender-options {
  display: flex;
  gap: 12px;
}

.gender-option {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  min-width: 110px;
  padding: 11px 18px;
  color: #aeb8d5;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.045);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  transition: 0.2s ease;
}

.gender-option:hover { transform: translateY(-1px); }
.gender-option.male { color: #70d7ff; }
.gender-option.female { color: #ff9db9; }
.gender-option.male.selected {
  color: #e7fbff;
  border-color: rgba(93, 207, 255, 0.76);
  background: linear-gradient(135deg, rgba(40, 154, 217, 0.48), rgba(38, 96, 177, 0.24));
  box-shadow: 0 8px 20px rgba(47, 161, 231, 0.17);
}
.gender-option.female.selected {
  color: #fff0f5;
  border-color: rgba(255, 130, 171, 0.76);
  background: linear-gradient(135deg, rgba(220, 83, 139, 0.48), rgba(151, 67, 160, 0.24));
  box-shadow: 0 8px 20px rgba(233, 93, 153, 0.17);
}

.optional {
  float: right;
  color: #75809e;
  font-size: 10px;
  font-weight: 400;
}
.file-input { display: none; }
.upload-area {
  display: grid;
  width: 100%;
  min-height: 142px;
  place-content: center;
  gap: 8px;
  color: #a996ff;
  border: 1px dashed rgba(160, 141, 255, 0.48);
  border-radius: 14px;
  background: rgba(113, 90, 212, 0.06);
  cursor: pointer;
  font: inherit;
  transition: 0.2s ease;
}
.upload-area:hover { border-color: #b09aff; background: rgba(128, 102, 233, 0.12); }
.upload-area strong { color: #ded9ff; font-size: 13px; }
.upload-area small { color: #8290b4; font-size: 11px; }
.upload-preview { position: relative; overflow: hidden; height: 182px; border: 1px solid rgba(255, 255, 255, 0.13); border-radius: 14px; }
.upload-preview img { display: block; width: 100%; height: 100%; object-fit: cover; }

.hidden-file-input { display: none; }
.greeting-upload {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 10px 13px;
  border: 1px dashed rgba(177, 156, 255, 0.45);
  border-radius: 10px;
  color: #dcd6ff;
  cursor: pointer;
  background: rgba(120, 99, 235, 0.1);
  font: inherit;
  font-size: 12px;
}
.greeting-image-preview {
  position: relative;
  overflow: hidden;
  width: min(100%, 280px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
}
.greeting-image-preview img { display: block; width: 100%; max-height: 220px; object-fit: cover; }
.greeting-image-preview button {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: inline-flex;
  gap: 5px;
  align-items: center;
  padding: 6px 8px;
  border: 0;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  background: rgba(10, 12, 28, 0.75);
  font-size: 11px;
}
.remove-image { position: absolute; right: 10px; bottom: 10px; display: inline-flex; gap: 5px; align-items: center; padding: 7px 10px; color: #fff; border: 0; border-radius: 8px; background: rgba(10, 13, 32, 0.76); cursor: pointer; font: inherit; font-size: 11px; }
.preview-background, .preview-shade { position: absolute; inset: 0; width: 100%; height: 100%; }
.preview-background { object-fit: cover; }
.preview-shade { background: linear-gradient(180deg, rgba(8, 11, 30, 0.05) 25%, rgba(9, 12, 34, 0.94) 88%); }
.preview-gender { display: inline-flex; gap: 4px; align-items: center; justify-content: center; margin: 0 0 4px !important; }
.preview-gender.male { color: #6fe0ff !important; }
.preview-gender.female { color: #ff9cbd !important; }

.preview-card.pink {
  background: linear-gradient(150deg, rgba(179, 87, 139, 0.48), rgba(53, 25, 54, 0.9));
}

.preview-card.blue {
  background: linear-gradient(150deg, rgba(70, 124, 181, 0.5), rgba(18, 32, 63, 0.9));
}

.preview-card.green {
  background: linear-gradient(150deg, rgba(56, 144, 122, 0.48), rgba(15, 47, 51, 0.9));
}

.preview-card.orange {
  background: linear-gradient(150deg, rgba(190, 116, 60, 0.48), rgba(61, 36, 31, 0.9));
}

.preview-glow {
  position: absolute;
  top: 36px;
  left: 50%;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(217, 184, 255, 0.38), transparent 67%);
  transform: translateX(-50%);
  animation: breathe 3.5s ease-in-out infinite;
}

.preview-status {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 6px;
  align-items: center;
  color: #d3d7eb;
  font-size: 10px;
}

.preview-status i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #55dfbd;
  box-shadow: 0 0 7px #55dfbd;
}

.preview-avatar-wrap {
  position: relative;
  z-index: 2;
  display: grid;
  width: 130px;
  height: 150px;
  place-items: center;
  margin: 11px auto 0;
}

.preview-avatar {
  display: grid;
  width: 101px;
  height: 101px;
  place-items: center;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.26);
  border-radius: 38px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.29), rgba(255, 255, 255, 0.06));
  box-shadow: 0 13px 27px rgba(0, 0, 0, 0.22);
  font-size: 40px;
  font-weight: 800;
  backdrop-filter: blur(10px);
  animation: float 4s ease-in-out infinite;
}

.avatar-orbit {
  position: absolute;
  inset: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 45px;
  transform: rotate(18deg);
}

.star {
  position: absolute;
  color: #f0e8ff;
  text-shadow: 0 0 11px #e1cfff;
  animation: twinkle 2.7s ease-in-out infinite;
}

.star-one {
  top: 11px;
  right: 9px;
}

.star-two {
  bottom: 17px;
  left: 6px;
  animation-delay: -1.2s;
}

.preview-info {
  position: relative;
  z-index: 2;
  text-align: center;
}

.preview-info p {
  margin: 0 0 4px;
  color: #c6c3e5;
  font-size: 10px;
}

.preview-info h3 {
  margin: 0;
  color: white;
  font-size: 24px;
}

.preview-info span {
  color: #b9c0d8;
  font-size: 10px;
}

.preview-message {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 5px;
  margin-top: 16px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
}

.preview-message span {
  color: #e0d2ff;
  font-size: 21px;
  line-height: 1;
}

.preview-message p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  margin: 0;
  color: #e7e7f6;
  font-size: 11px;
  line-height: 1.55;
}

.preview-tip {
  margin: 13px 3px 0;
  color: #7f89a8;
  font-size: 10px;
  text-align: center;
}

@keyframes breathe {
  50% {
    opacity: 0.55;
    transform: translateX(-50%) scale(1.13);
  }
}

@keyframes float {
  50% {
    transform: translateY(-7px);
  }
}

@keyframes twinkle {
  50% {
    opacity: 0.4;
    transform: scale(0.7);
  }
}

@media (max-width: 1120px) {
  .creator-layout {
    grid-template-columns: 200px minmax(400px, 1fr);
  }

  .preview-panel {
    display: none;
  }
}

@media (max-width: 770px) {
  .create-page {
    padding: 43px 20px 85px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
    margin-bottom: 30px;
  }

  .creator-layout {
    grid-template-columns: 1fr;
  }

  .steps-panel {
    display: flex;
    overflow-x: auto;
    gap: 8px;
  }

  .step-item {
    flex: 0 0 auto;
    width: auto;
  }

  .step-item small,
  .steps-tip {
    display: none;
  }

  .form-panel {
    min-height: auto;
    padding: 24px 18px;
  }
}
.visibility-grid {
  display: grid;
  gap: 10px;
}

.visibility-option {
  position: relative;
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  color: #adb7d2;
  cursor: pointer;
  text-align: left;
  background: rgba(255, 255, 255, 0.035);
  transition: 0.22s ease;
}

.visibility-option:hover {
  border-color: rgba(173, 151, 255, 0.38);
  background: rgba(127, 107, 244, 0.1);
  transform: translateY(-1px);
}

.visibility-option.selected {
  border-color: rgba(166, 143, 255, 0.62);
  background: linear-gradient(
    135deg,
    rgba(119, 101, 247, 0.2),
    rgba(199, 101, 208, 0.08)
  );
  box-shadow: 0 8px 22px rgba(113, 91, 235, 0.13);
}

.visibility-icon {
  display: grid;
  width: 39px;
  height: 39px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 12px;
}

.visibility-icon.private {
  color: #b9abff;
  background: rgba(137, 112, 255, 0.17);
}

.visibility-icon.public {
  color: #78dec7;
  background: rgba(70, 203, 172, 0.14);
}

.visibility-option > span:nth-child(2) {
  display: grid;
  gap: 4px;
}

.visibility-option strong {
  color: #e9e8f8;
  font-size: 13px;
}

.visibility-option small {
  color: #8994b1;
  font-size: 11px;
  line-height: 1.45;
}

.selected-check {
  margin-left: auto;
  color: #cbbaff;
}

.submit-error {
  margin: 18px 0 0;
  padding: 11px 13px;
  border: 1px solid rgba(255, 116, 150, 0.22);
  border-radius: 11px;
  color: #ffb1c5;
  background: rgba(238, 88, 130, 0.1);
  font-size: 12px;
}

.memory-section {
  margin-top: 25px;
}

.personality-section { margin-top: 20px; }
.personality-heading { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
.personality-heading > div > span { color: #e3e3f5; font-size: 13px; font-weight: 700; }
.personality-heading p { margin: 6px 0 0; color: #8490b1; font-size: 11px; }
.more-tags-button { padding: 7px 13px; border: 1px solid rgba(167, 143, 255, 0.48); border-radius: 9px; color: #ddd7ff; cursor: pointer; background: rgba(117, 93, 225, 0.14); font: inherit; font-size: 11px; font-weight: 700; transition: .2s ease; }
.more-tags-button:hover { background: rgba(132, 103, 242, .27); transform: translateY(-1px); }
.selected-tags { display: flex; flex-wrap: wrap; gap: 8px; min-height: 42px; margin-top: 12px; padding: 9px; border: 1px solid rgba(255,255,255,.09); border-radius: 12px; background: rgba(255,255,255,.025); }
.selected-tag { display: inline-flex; align-items: center; gap: 5px; padding: 6px 9px; border: 1px solid rgba(171, 148, 255, .34); border-radius: 999px; color: #e4dfff; cursor: pointer; background: rgba(119, 93, 229, .15); font: inherit; font-size: 11px; }
.selected-tags-placeholder { align-self: center; color: #76819f; font-size: 11px; }

.tag-modal-mask { position: fixed; z-index: 1000; inset: 0; display: grid; place-items: center; padding: 20px; background: rgba(4, 7, 23, .7); backdrop-filter: blur(10px); }
.tag-modal { width: min(560px, 100%); padding: 25px; border: 1px solid rgba(188, 166, 255, .32); border-radius: 20px; color: #eceaff; background: linear-gradient(145deg, #202247, #10152e); box-shadow: 0 28px 65px rgba(0,0,0,.48), 0 0 45px rgba(112, 88, 224, .16); }
.tag-modal header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
.tag-modal header p { margin: 0 0 5px; color: #a891ff; font-size: 10px; font-weight: 700; letter-spacing: 1.4px; }
.tag-modal h3 { margin: 0; font-size: 20px; }
.tag-modal-close { display: grid; width: 34px; height: 34px; place-items: center; border: 0; border-radius: 10px; color: #bfc5e0; cursor: pointer; background: rgba(255,255,255,.06); }
.tag-modal-tip { margin: 13px 0 18px; color: #98a2c0; font-size: 12px; }
.tag-modal-grid { display: flex; flex-wrap: wrap; gap: 9px; max-height: 310px; overflow-y: auto; padding-right: 3px; }
.tag-modal-grid button { display: inline-flex; gap: 5px; align-items: center; padding: 9px 11px; border: 1px solid rgba(255,255,255,.1); border-radius: 10px; color: #aeb8d3; cursor: pointer; background: rgba(255,255,255,.035); font: inherit; font-size: 12px; transition: .2s ease; }
.tag-modal-grid button:hover { border-color: rgba(172, 146, 255,.45); color: #e9e5ff; }
.tag-modal-grid button.selected { border-color: rgba(170, 142, 255,.65); color: #f6f3ff; background: linear-gradient(135deg, rgba(115,89,229,.48), rgba(192,92,201,.24)); box-shadow: 0 6px 14px rgba(93,70,200,.18); }
.tag-modal footer { display: flex; justify-content: flex-end; margin-top: 22px; }
.tag-modal footer button { padding: 10px 19px; border: 0; border-radius: 10px; color: white; cursor: pointer; background: linear-gradient(135deg, #7961ec, #bd61cf); font: inherit; font-size: 12px; font-weight: 700; }
.tag-modal-enter-active, .tag-modal-leave-active { transition: opacity .24s ease; }
.tag-modal-enter-active .tag-modal, .tag-modal-leave-active .tag-modal { transition: transform .24s cubic-bezier(.2,.75,.25,1), opacity .24s ease; }
.tag-modal-enter-from, .tag-modal-leave-to { opacity: 0; }
.tag-modal-enter-from .tag-modal, .tag-modal-leave-to .tag-modal { opacity: 0; transform: translateY(12px) scale(.97); }

.memory-section-heading {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 13px;
}

.memory-section-heading > div > span {
  color: #e5e4f6;
  font-size: 13px;
  font-weight: 700;
}

.memory-section-heading p {
  margin: 7px 0 0;
  color: #8792b2;
  font-size: 11px;
  line-height: 1.55;
}

.memory-count {
  flex: none;
  padding: 5px 9px;
  border: 1px solid rgba(167, 145, 255, 0.25);
  border-radius: 999px;
  color: #c7baff;
  background: rgba(116, 91, 222, 0.1);
  font-size: 10px;
}

.memory-deck {
  position: relative;
  min-height: 333px;
  padding: 0 20px 30px 0;
}

.memory-card-front,
.memory-card-back {
  border: 1px solid rgba(181, 162, 255, 0.2);
  border-radius: 17px;
  background: linear-gradient(145deg, rgba(35, 37, 74, 0.96), rgba(17, 21, 50, 0.96));
}

.memory-card-front {
  position: relative;
  z-index: 3;
  min-height: 303px;
  padding: 17px;
  box-shadow: 0 16px 34px rgba(5, 8, 30, 0.28), inset 0 1px rgba(255, 255, 255, 0.04);
}

.memory-card-back {
  position: absolute;
  inset: 12px 0 18px 14px;
  z-index: 1;
  opacity: 0.62;
  pointer-events: none;
}

.memory-card-back-one {
  z-index: 2;
  transform: rotate(1.5deg) translate(8px, 8px);
  background: linear-gradient(145deg, rgba(91, 71, 172, 0.68), rgba(23, 29, 67, 0.92));
}

.memory-card-back-two {
  transform: rotate(3deg) translate(15px, 15px);
  background: linear-gradient(145deg, rgba(169, 74, 171, 0.28), rgba(23, 29, 67, 0.9));
}

.memory-card-toolbar,
.memory-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.memory-card-toolbar {
  margin-bottom: 14px;
  color: #cabeff;
  font-size: 11px;
  font-weight: 700;
}

.memory-remove,
.add-memory-button,
.next-memory-button {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  border: 0;
  cursor: pointer;
  font: inherit;
  transition: transform 0.24s ease, box-shadow 0.24s ease, background 0.24s ease;
}

.memory-remove {
  padding: 5px 7px;
  border-radius: 8px;
  color: #bdc4df;
  background: transparent;
  font-size: 10px;
}

.memory-remove:hover { color: #ffb1ca; background: rgba(255, 105, 151, 0.1); }

.memory-field { display: block; margin-top: 12px; }
.memory-field > span { display: block; margin-bottom: 7px; color: #cbd2e9; font-size: 11px; font-weight: 700; }
.memory-field input,
.memory-field textarea {
  box-sizing: border-box;
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  outline: none;
  color: #e8eaff;
  background: rgba(8, 11, 30, 0.53);
  font: inherit;
  font-size: 12px;
}
.memory-field input { padding: 10px 11px; }
.memory-field textarea { padding: 10px 11px; line-height: 1.6; resize: vertical; }
.memory-field input:focus,
.memory-field textarea:focus { border-color: rgba(168, 143, 255, 0.55); box-shadow: 0 0 0 3px rgba(125, 101, 237, 0.1); }
.memory-field small { display: block; margin-top: 4px; color: #71809e; font-size: 10px; text-align: right; }

.memory-actions {
  position: absolute;
  z-index: 4;
  right: 0;
  bottom: 0;
  left: 0;
}

.add-memory-button,
.next-memory-button {
  padding: 9px 11px;
  border-radius: 10px;
  color: #e9e5ff;
  background: rgba(119, 94, 229, 0.15);
  box-shadow: 0 7px 15px rgba(28, 20, 78, 0.18);
  font-size: 11px;
  font-weight: 700;
}

.next-memory-button { color: #fff5fe; background: linear-gradient(135deg, #7c63e6, #b75bc8); }
.add-memory-button:hover,
.next-memory-button:hover { transform: translateY(-2px); box-shadow: 0 11px 21px rgba(99, 69, 213, 0.29); }

.memory-card-enter-active,
.memory-card-leave-active { transition: opacity 0.32s ease, transform 0.32s cubic-bezier(0.22, 0.72, 0.24, 1); }
.memory-card-enter-from { opacity: 0; transform: translateY(24px) rotate(-2deg) scale(0.96); }
.memory-card-leave-to { opacity: 0; transform: translateY(-15px) rotate(2deg) scale(1.02); }

.complete-button:disabled {
  cursor: wait;
  opacity: 0.7;
  transform: none;
}

.loading-icon {
  animation: loading-rotate 0.9s linear infinite;
}

@keyframes loading-rotate {
  to {
    transform: rotate(360deg);
  }
}
</style>
