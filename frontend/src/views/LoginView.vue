<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Eye,
  EyeOff,
  Heart,
  LockKeyhole,
  Mail,
  UserRound,
} from 'lucide-vue-next'
import lumiLoginLogo from '../assets/lumi-login-logo.png'

// Keep requests on the current host so Vite/ngrok can proxy /api to FastAPI.
const API_BASE_URL = ''

const router = useRouter()
const route = useRoute()

const activeTab = ref('login')
const isSubmitting = ref(false)
const showPassword = ref(false)
const message = ref('')
const messageType = ref('')

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const isLogin = computed(() => activeTab.value === 'login')

function switchTab(tab) {
  activeTab.value = tab
  message.value = ''
  messageType.value = ''
  form.value.password = ''
  form.value.confirmPassword = ''
}

function showMessage(text, type = 'error') {
  message.value = text
  messageType.value = type
}

function getRedirectPath() {
  const redirect = route.query.redirect

  if (typeof redirect === 'string' && redirect.startsWith('/')) {
    return redirect
  }

  return '/chat'
}

async function submitForm() {
  if (isSubmitting.value) {
    return
  }

  const username = form.value.username.trim()
  const email = form.value.email.trim()
  const password = form.value.password

  if (!username || !password) {
    showMessage('请输入用户名和密码。')
    return
  }

  if (!isLogin.value) {
    if (!email) {
      showMessage('请输入邮箱地址。')
      return
    }

    if (password !== form.value.confirmPassword) {
      showMessage('两次输入的密码不一致。')
      return
    }
  }

  isSubmitting.value = true
  message.value = ''

  try {
    const endpoint = isLogin.value
      ? '/api/auth/login'
      : '/api/auth/register'

    const requestData = isLogin.value
      ? {
          username,
          password,
        }
      : {
          username,
          email,
          password,
        }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    })

    const result = await response.json()

    if (!response.ok || !result.success) {
      throw new Error(result.detail || '操作失败，请稍后再试。')
    }

    // 注册成功：引导用户使用刚注册的账号登录
    if (!isLogin.value) {
      showMessage('注册成功，现在可以登录了。', 'success')
      activeTab.value = 'login'
      form.value.password = ''
      form.value.confirmPassword = ''
      return
    }

    // 登录成功：保存 Token 和当前用户资料
    localStorage.setItem(
      'lumi_access_token',
      result.data.access_token,
    )

    localStorage.setItem(
      'lumi_current_user',
      JSON.stringify(result.data.user),
    )

    showMessage('登录成功，正在进入你的陪伴空间…', 'success')

    setTimeout(() => {
      router.replace(getRedirectPath())
    }, 500)
  } catch (error) {
    showMessage(
      error.message || '无法连接后端，请确认 FastAPI 正在运行。',
    )
  } finally {
    isSubmitting.value = false
  }
}

</script>

<template>
  <main class="auth-page">
    <div class="background-light light-one"></div>
    <div class="background-light light-two"></div>
    <div class="background-light light-three"></div>

    <section class="auth-card">
      <div class="welcome">
        <img :src="lumiLoginLogo" alt="Lumi" />
        <h1>Lumi</h1>
      </div>

      <div class="auth-tabs">
        <button
          :class="{ active: activeTab === 'login' }"
          @click="switchTab('login')"
        >
          登录
        </button>

        <button
          :class="{ active: activeTab === 'register' }"
          @click="switchTab('register')"
        >
          注册
        </button>
      </div>

      <form @submit.prevent="submitForm">
        <label class="form-item">
          <span>用户名</span>

          <div class="input-wrap">
            <UserRound :size="18" />

            <input
              v-model="form.username"
              :disabled="isSubmitting"
              autocomplete="username"
              maxlength="20"
              placeholder="输入你的用户名"
              type="text"
            />
          </div>
        </label>

        <label v-if="!isLogin" class="form-item">
          <span>邮箱</span>

          <div class="input-wrap">
            <Mail :size="18" />

            <input
              v-model="form.email"
              :disabled="isSubmitting"
              autocomplete="email"
              placeholder="name@example.com"
              type="email"
            />
          </div>
        </label>

        <label class="form-item">
          <span>密码</span>

          <div class="input-wrap">
            <LockKeyhole :size="18" />

            <input
              v-model="form.password"
              :disabled="isSubmitting"
              :type="showPassword ? 'text' : 'password'"
              :autocomplete="isLogin ? 'current-password' : 'new-password'"
              placeholder="至少 8 位密码"
            />

            <button
              class="eye-button"
              type="button"
              @click="showPassword = !showPassword"
            >
              <EyeOff v-if="showPassword" :size="18" />
              <Eye v-else :size="18" />
            </button>
          </div>
        </label>

        <label v-if="!isLogin" class="form-item">
          <span>确认密码</span>

          <div class="input-wrap">
            <LockKeyhole :size="18" />

            <input
              v-model="form.confirmPassword"
              :disabled="isSubmitting"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              placeholder="再次输入密码"
            />
          </div>
        </label>

        <p
          v-if="message"
          class="message"
          :class="messageType"
        >
          {{ message }}
        </p>

        <button
          class="submit-button"
          :disabled="isSubmitting"
          type="submit"
        >
          <Heart :size="18" />

          {{
            isSubmitting
              ? '请稍候…'
              : isLogin
                ? '登录并继续陪伴'
                : '创建我的陪伴空间'
          }}
        </button>
      </form>

      <p class="switch-text">
        {{
          isLogin
            ? '还没有 Lumi 账号？'
            : '已经拥有 Lumi 账号？'
        }}

        <button
          @click="switchTab(isLogin ? 'register' : 'login')"
        >
          {{ isLogin ? '立即注册' : '去登录' }}
        </button>
      </p>

    </section>
  </main>
</template>

<style scoped>
.auth-page {
  position: relative;
  display: grid;
  min-height: 100vh;
  overflow: hidden;
  padding: 30px 20px;
  place-items: center;
  color: #f7f5ff;
  background:
    radial-gradient(circle at 50% -12%, rgba(126, 89, 226, 0.22), transparent 37%),
    #080c20;
}

.background-light {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}

.light-one {
  top: 18%;
  left: -130px;
  width: 300px;
  height: 300px;
  background: rgba(112, 75, 220, 0.22);
}

.light-two {
  right: -90px;
  bottom: 8%;
  width: 280px;
  height: 280px;
  background: rgba(232, 95, 193, 0.16);
}

.light-three {
  top: 50%;
  left: 52%;
  width: 160px;
  height: 160px;
  background: rgba(85, 173, 232, 0.08);
}

.auth-card {
  position: relative;
  z-index: 1;
  width: min(100%, 448px);
  padding: 38px;
  border: 1px solid rgba(198, 185, 255, 0.22);
  border-radius: 29px;
  background:
    linear-gradient(145deg, rgba(43, 37, 91, 0.84), rgba(18, 23, 51, 0.93));
  box-shadow:
    0 30px 85px rgba(0, 0, 0, 0.38),
    inset 0 1px rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
}

.welcome {
  display: grid;
  gap: 11px;
  justify-items: center;
  width: 148px;
  margin: 2px auto 26px;
  place-items: center;
  text-align: center;
}

.welcome img {
  width: 122px;
  height: 122px;
  object-fit: cover;
  object-position: center;
  border-radius: 31px;
  box-shadow: 0 13px 31px rgba(6, 3, 26, 0.36);
}

.welcome h1 {
  margin: 0;
  color: #d8bdff;
  font-size: 27px;
  font-weight: 850;
  letter-spacing: 1.5px;
  line-height: 1;
  text-shadow:
    0 0 9px rgba(180, 126, 255, 0.75),
    0 0 22px rgba(125, 79, 235, 0.38);
}

.auth-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5px;
  padding: 5px;
  margin-bottom: 23px;
  border-radius: 14px;
  background: rgba(5, 8, 29, 0.38);
}

.auth-tabs button {
  padding: 11px;
  border: 0;
  border-radius: 10px;
  color: #a8a9c5;
  cursor: pointer;
  font: inherit;
  background: transparent;
  transition: 0.2s ease;
}

.auth-tabs button.active {
  color: white;
  font-weight: 700;
  background: linear-gradient(110deg, #7657ec, #a960d6);
  box-shadow: 0 6px 15px rgba(115, 78, 212, 0.31);
}

.form-item {
  display: block;
  margin-top: 16px;
}

.form-item > span {
  display: block;
  margin-bottom: 8px;
  color: #c6c5dc;
  font-size: 13px;
}

.input-wrap {
  display: flex;
  gap: 10px;
  align-items: center;
  height: 48px;
  padding: 0 13px;
  border: 1px solid rgba(179, 180, 219, 0.17);
  border-radius: 13px;
  color: #999ec0;
  background: rgba(8, 13, 36, 0.42);
  transition: 0.2s ease;
}

.input-wrap:focus-within {
  border-color: rgba(191, 157, 255, 0.69);
  box-shadow: 0 0 0 4px rgba(126, 87, 228, 0.11);
}

.input-wrap input {
  width: 100%;
  outline: none;
  border: 0;
  color: #f0effb;
  font: inherit;
  font-size: 14px;
  background: transparent;
}

.input-wrap input::placeholder {
  color: #6f779a;
}

.eye-button {
  display: grid;
  flex: none;
  width: 30px;
  height: 30px;
  place-items: center;
  border: 0;
  border-radius: 8px;
  color: #959bc0;
  cursor: pointer;
  background: transparent;
}

.eye-button:hover {
  color: #e3d5ff;
  background: rgba(255, 255, 255, 0.08);
}

.message {
  padding: 10px 12px;
  margin: 16px 0 0;
  border-radius: 10px;
  font-size: 12px;
  line-height: 1.5;
}

.message.error {
  color: #ffb7cd;
  background: rgba(227, 82, 126, 0.13);
}

.message.success {
  color: #a7ecc8;
  background: rgba(66, 192, 133, 0.13);
}

.submit-button {
  display: flex;
  width: 100%;
  justify-content: center;
  gap: 9px;
  align-items: center;
  padding: 15px;
  margin-top: 23px;
  border: 0;
  border-radius: 13px;
  color: white;
  cursor: pointer;
  font: inherit;
  font-size: 15px;
  font-weight: 800;
  background: linear-gradient(105deg, #7659f0, #c561d8);
  box-shadow: 0 13px 26px rgba(133, 75, 219, 0.35);
  transition: 0.25s ease;
}

.submit-button:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: translateY(-3px);
}

.submit-button:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.switch-text {
  margin: 21px 0 0;
  color: #9297b8;
  font-size: 13px;
  text-align: center;
}

.switch-text button {
  padding: 0;
  border: 0;
  color: #cfb3ff;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  background: transparent;
}

@media (max-width: 520px) {
  .auth-page {
    padding: 80px 16px 25px;
    place-items: start center;
  }

  .auth-card {
    padding: 27px 22px;
    border-radius: 23px;
  }

}
</style>
