import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/main.css'

import HomeView from './views/HomeView.vue'
import CharacterView from './views/CharacterView.vue'
import ChatView from './views/ChatView.vue'
import ConversationView from './views/ConversationView.vue'
import CreateCharacterView from './views/CreateCharacterView.vue'
import MyCharactersView from './views/MyCharactersView.vue'
import ProfileView from './views/ProfileView.vue'
import MembershipView from './views/MembershipView.vue'
import LoginView from './views/LoginView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/characters',
    name: 'characters',
    component: CharacterView,
  },

  // 角色广场内选中角色时、会话记录点击角色时，进入聊天页
  {
    path: '/chat',
    name: 'chat',
    component: ChatView,
  },
  {
  path: '/conversations/chat/:characterId',
  name: 'conversation-chat',
  component: ChatView,
},

  // 左侧菜单的新“会话记录”页面
  {
    path: '/conversations',
    name: 'conversations',
    component: ConversationView,
  },
  {
    path: '/create',
    name: 'create',
    component: CreateCharacterView,
  },
  {
    path: '/my-characters',
    name: 'my-characters',
    component: MyCharactersView,
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
  },
  {
    path: '/membership',
    name: 'membership',
    component: MembershipView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('lumi_access_token')

  if (!token && to.name !== 'login') {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (token && to.name === 'login') {
    return {
      name: 'home',
    }
  }

  return true
})

createApp(App).use(router).mount('#app')