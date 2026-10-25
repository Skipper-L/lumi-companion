<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Crown,
  House,
  LogOut,
  MessageCircleHeart,
  PlusCircle,
  Sparkles,
  UserRound,
  UsersRound,
  X,
} from 'lucide-vue-next'
import lumiMoonIcon from '../assets/lumi-default-cover.png'

const router = useRouter()
const route = useRoute()

const showLogoutModal = ref(false)

const currentUser = ref({
  username: '用户',
  email: '',
})

const navItems = [
  { label: '首页', path: '/', icon: House },
  { label: '角色广场', path: '/characters', icon: Sparkles },
  { label: '会话记录', path: '/conversations', icon: MessageCircleHeart },
  { label: '创建角色', path: '/create', icon: PlusCircle },
  { label: '我的空间', path: '/profile', icon: UserRound },
  { label: '会员中心', path: '/membership', icon: Crown },
  { label: '我的角色', path: '/my-characters', icon: UsersRound },
]

const userAvatarText = computed(() => {
  return currentUser.value.username?.slice(0, 1) || '你'
})

function loadCurrentUser() {
  const savedUser = localStorage.getItem('lumi_current_user')

  if (!savedUser) return

  try {
    currentUser.value = JSON.parse(savedUser)
  } catch (error) {
    console.error('读取登录用户信息失败：', error)
  }
}

function openLogoutModal() {
  showLogoutModal.value = true
}

function closeLogoutModal() {
  showLogoutModal.value = false
}

function confirmLogout() {
  localStorage.removeItem('lumi_access_token')
  localStorage.removeItem('lumi_current_user')

  showLogoutModal.value = false
  router.replace('/login')
}

onMounted(() => {
  loadCurrentUser()
})
</script>

<template>
  <aside class="navigation">
    <RouterLink class="brand" to="/">
      <span class="brand-icon">
        <img :src="lumiMoonIcon" alt="Lumi" />
      </span>
      <span>Lumi</span>
    </RouterLink>

    <p class="nav-title">探索</p>

    <nav>
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
       :class="{
  active:
    (item.path === '/conversations' &&
      route.path.startsWith('/conversations')) ||
    (item.path === '/characters' &&
      route.path === '/chat' &&
      route.query.from === 'characters'),
}"
      >
        <component :is="item.icon" :size="19" />
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="user-card">
      <div class="user-info">
        <div class="user-avatar">
          {{ userAvatarText }}
        </div>

        <div class="user-text">
          <strong>{{ currentUser.username }}</strong>
          <span>我的陪伴空间</span>
        </div>
      </div>

      <button
        class="logout-button"
        type="button"
        title="退出登录"
        @click="openLogoutModal"
      >
        <LogOut :size="17" />
      </button>
    </div>
  </aside>

  <Teleport to="body">
    <Transition name="logout-modal">
      <div
        v-if="showLogoutModal"
        class="logout-mask"
        @click.self="closeLogoutModal"
      >
        <section class="logout-modal">
          <button
            class="close-button"
            type="button"
            title="关闭"
            @click="closeLogoutModal"
          >
            <X :size="21" />
          </button>

          <div class="logout-icon">
            <LogOut :size="27" />
          </div>

          <p class="eyebrow">ACCOUNT MANAGEMENT</p>
          <h2>确定要退出登录吗？</h2>

          <p class="logout-description">
            退出后需要重新输入账号和密码才能继续使用 Lumi。
            你的聊天记录会安全保留在数据库中。
          </p>

          <div class="current-account">
            <span>{{ userAvatarText }}</span>

            <div>
              <strong>{{ currentUser.username }}</strong>
              <p>{{ currentUser.email || '当前登录账号' }}</p>
            </div>
          </div>

          <div class="logout-actions">
            <button type="button" @click="closeLogoutModal">
              暂不退出
            </button>

            <button
              class="confirm-logout"
              type="button"
              @click="confirmLogout"
            >
              <LogOut :size="17" />
              确认退出
            </button>
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.navigation {
  position: fixed;
  z-index: 10;
  display: flex;
  flex-direction: column;
  width: 250px;
  height: 100vh;
  padding: 28px 16px 18px;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(11, 16, 32, 0.72);
  backdrop-filter: blur(22px);
}

.brand {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 0 10px;
  color: #f5f5ff;
  font-size: 23px;
  font-weight: 800;
  letter-spacing: 0.6px;
  text-decoration: none;
}

.brand-icon {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
}

.brand-icon img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: drop-shadow(0 5px 12px rgba(165, 119, 255, 0.38));
}

.nav-title {
  margin: 42px 10px 12px;
  color: #7882a9;
  font-size: 12px;
  letter-spacing: 1.5px;
}

nav {
  display: grid;
  gap: 6px;
}

.nav-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px 13px;
  border-radius: 12px;
  color: #aeb6d4;
  text-decoration: none;
  transition: 0.22s ease;
}

.nav-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.07);
}

.nav-item.router-link-exact-active,
.nav-item.active {
  color: white;
  background: linear-gradient(
    90deg,
    rgba(123, 106, 255, 0.26),
    rgba(123, 106, 255, 0.05)
  );
}

.user-card {
  display: flex;
  justify-content: space-between;
  gap: 9px;
  align-items: center;
  margin-top: auto;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.045);
  transition: 0.22s ease;
}

.user-card:hover {
  border-color: rgba(185, 164, 255, 0.3);
  background: rgba(115, 92, 189, 0.13);
}

.user-info {
  display: flex;
  min-width: 0;
  gap: 10px;
  align-items: center;
}

.user-avatar {
  display: grid;
  width: 34px;
  height: 34px;
  flex: none;
  place-items: center;
  border-radius: 50%;
  color: white;
  background: linear-gradient(135deg, #52d4be, #587bff);
  font-size: 14px;
  font-weight: 800;
}

.user-text {
  min-width: 0;
}

.user-text strong,
.user-text span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-text strong {
  color: #e9ebfb;
  font-size: 13px;
}

.user-text span {
  margin-top: 3px;
  color: #838dac;
  font-size: 11px;
}

.logout-button {
  display: grid;
  width: 33px;
  height: 33px;
  flex: none;
  place-items: center;
  border: 0;
  border-radius: 10px;
  color: #9da8c7;
  cursor: pointer;
  background: transparent;
  opacity: 0;
  transform: translateX(5px);
  transition: 0.22s ease;
}

.user-card:hover .logout-button {
  opacity: 1;
  transform: translateX(0);
}

.logout-button:hover {
  color: #ffc0d3;
  background: rgba(238, 94, 139, 0.16);
}

.logout-mask {
  position: fixed;
  z-index: 9999;
  inset: 0;
  display: grid;
  padding: 20px;
  place-items: center;
  background: rgba(3, 6, 20, 0.76);
  backdrop-filter: blur(10px);
}

.logout-modal {
  position: relative;
  width: min(100%, 410px);
  padding: 33px;
  border: 1px solid rgba(208, 187, 255, 0.27);
  border-radius: 26px;
  text-align: center;
  background: linear-gradient(145deg, #25204d, #11172f);
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
  color: #abb5d3;
  cursor: pointer;
  background: transparent;
}

.close-button:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.logout-icon {
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  margin: 0 auto 18px;
  border-radius: 18px;
  color: #ffc0d7;
  background: rgba(232, 96, 150, 0.16);
}

.eyebrow {
  margin: 0 0 8px;
  color: #c7abff;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.7px;
}

.logout-modal h2 {
  margin: 0;
  color: #f5f3ff;
  font-size: 24px;
}

.logout-description {
  margin: 14px 0 19px;
  color: #adb5d0;
  font-size: 13px;
  line-height: 1.75;
}

.current-account {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 12px;
  border-radius: 14px;
  text-align: left;
  background: rgba(255, 255, 255, 0.065);
}

.current-account > span {
  display: grid;
  width: 35px;
  height: 35px;
  flex: none;
  place-items: center;
  border-radius: 11px;
  color: white;
  background: linear-gradient(135deg, #52d4be, #587bff);
  font-weight: 800;
}

.current-account strong {
  display: block;
  color: #e9ebfb;
  font-size: 13px;
}

.current-account p {
  margin: 4px 0 0;
  color: #838dac;
  font-size: 11px;
}

.logout-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 22px;
}

.logout-actions button {
  display: flex;
  min-height: 43px;
  justify-content: center;
  gap: 7px;
  align-items: center;
  border: 1px solid rgba(217, 211, 245, 0.15);
  border-radius: 12px;
  color: #ccd2e6;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.06);
  font: inherit;
}

.logout-actions .confirm-logout {
  border: 0;
  color: white;
  background: linear-gradient(135deg, #cf5f88, #eb7ca9);
}

.logout-modal-enter-active,
.logout-modal-leave-active {
  transition: opacity 0.22s ease;
}

.logout-modal-enter-from,
.logout-modal-leave-to {
  opacity: 0;
}

@media (max-width: 800px) {
  .navigation {
    bottom: 0;
    flex-direction: row;
    width: 100%;
    height: 64px;
    padding: 7px 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    border-right: 0;
  }

  .brand,
  .nav-title,
  .user-card {
    display: none;
  }

  nav {
    display: flex;
    justify-content: space-around;
    width: 100%;
  }

  .nav-item {
    flex-direction: column;
    gap: 3px;
    padding: 5px 7px;
    font-size: 10px;
  }
}
</style>
