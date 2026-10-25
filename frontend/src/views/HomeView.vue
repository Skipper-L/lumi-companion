<script setup>
import { computed, ref } from 'vue'
import {
  ArrowUpRight,
  Heart,
  MessageCircleHeart,
  MoonStar,
  Sparkles,
  Stars,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'

const mouse = ref({ x: 50, y: 50 })

const lightPosition = computed(() => ({
  background: `radial-gradient(
    circle at ${mouse.value.x}% ${mouse.value.y}%,
    rgba(155, 125, 255, 0.19),
    transparent 28%
  )`,
}))

function handleMouseMove(event) {
  const rect = event.currentTarget.getBoundingClientRect()

  mouse.value = {
    x: ((event.clientX - rect.left) / rect.width) * 100,
    y: ((event.clientY - rect.top) / rect.height) * 100,
  }
}

const moods = [
  { icon: Heart, label: '想被倾听', color: 'pink' },
  { icon: MoonStar, label: '睡前聊聊', color: 'purple' },
  { icon: Sparkles, label: '治愈一下', color: 'green' },
]
</script>

<template>
  <PageLayout>
    <div class="home-page" @mousemove="handleMouseMove">
      <div class="mouse-light" :style="lightPosition"></div>

      <section class="hero">
        <div class="hero-copy">
          <div class="welcome-tag">
            <Stars :size="15" />
            <span>YOUR QUIET CORNER</span>
          </div>

          <p class="greeting"></p>

          <h1>
            
             <span>  Lumi </span>
            
          </h1>
       
        <p>   </p> 
        
          <p class="hero-description">
              世界很吵，好在 Lumi 愿意安静陪着你。
          </p>

          <div class="hero-actions">
            <RouterLink class="primary-button" to="/characters">
              <MessageCircleHeart :size="19" />
              开始一段对话
              <ArrowUpRight :size="18" />
            </RouterLink>

            <RouterLink class="secondary-button" to="/create">
              创建我的角色
            </RouterLink>
          </div>

          <div class="mood-row">
            <p>此刻，你更想……</p>

            <div class="mood-options">
              <RouterLink
                v-for="mood in moods"
                :key="mood.label"
                to="/characters"
                class="mood-option"
                :class="mood.color"
              >
                <component :is="mood.icon" :size="16" />
                {{ mood.label }}
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="hero-visual">
          <div class="orb orb-one"></div>
          <div class="orb orb-two"></div>
          <div class="orb orb-three"></div>

          <div class="star star-one">✦</div>
          <div class="star star-two">✧</div>
          <div class="star star-three">✦</div>

          <div class="character-glow"></div>

          <article class="character-card">
            <div class="card-top">
              <span class="online-dot"></span>
              <span>正在陪伴你</span>
              <button type="button" aria-label="收藏角色">♡</button>
            </div>

            <div class="character-info">
              <div>
                <p></p>
                <h2>Lumi</h2>
              </div>

              <span class="mood-badge">温柔 · 倾听</span>
            </div>

            <div class="character-message">
              <span class="message-mark"></span>
              <p>今天过得怎么样？<br />我一直都在。</p>
            </div>
          </article>

          <div class="floating-card memory-card">
            <span class="floating-icon">✦</span>
            <div>
              <small>共同回忆</small>
              <strong>第 12 次夜聊</strong>
            </div>
          </div>

          <div class="floating-card warmth-card">
            <span class="floating-icon">♡</span>
            <div>
              <small>关系温度</small>
              <strong>正在慢慢升温</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="bottom-note">
        <span></span>
        <p>不必时时坚强。你可以在这里，做你自己。</p>
      </section>
    </div>
  </PageLayout>
</template>

<style scoped>
.home-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  isolation: isolate;
  background:
    radial-gradient(circle at 78% 45%, rgba(85, 211, 193, 0.09), transparent 19%),
    radial-gradient(circle at 52% 18%, rgba(133, 103, 255, 0.12), transparent 23%);
}

.mouse-light {
  position: absolute;
  z-index: -1;
  inset: 0;
  pointer-events: none;
  transition: background 0.18s ease-out;
}

.hero {
  display: grid;
  grid-template-columns: minmax(360px, 0.95fr) minmax(420px, 1.05fr);
  gap: 30px;
  align-items: center;
  width: min(1240px, 100%);
  min-height: calc(100vh - 82px);
  margin: 0 auto;
  padding: 70px 7% 45px;
}

.hero-copy {
  position: relative;
  z-index: 2;
}

.welcome-tag {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 9px 12px;
  color: #c8c0ff;
  border: 1px solid rgba(176, 160, 255, 0.23);
  border-radius: 99px;
  background: rgba(134, 114, 255, 0.09);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.greeting {
  margin: 31px 0 10px;
  color: #b8c0e2;
  font-size: 17px;
}

h1 {
  margin: 0;
  color: #f6f4ff;
  font-size: clamp(48px, 5.2vw, 78px);
  font-weight: 750;
  letter-spacing: -3px;
  line-height: 1.13;
}

h1 span {
  color: #d7ccff;
  text-shadow: 0 0 35px rgba(182, 157, 255, 0.2);
}

.hero-description {
  max-width: 505px;
  margin: 25px 0 0;
  color: #aab4d2;
  font-size: 16px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  gap: 13px;
  align-items: center;
  margin-top: 34px;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  gap: 10px;
  align-items: center;
  justify-content: center;
  min-height: 49px;
  padding: 0 19px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.primary-button {
  color: #fff;
  background: linear-gradient(135deg, #7668ff, #bd70ed);
  box-shadow: 0 14px 30px rgba(117, 100, 255, 0.27);
}

.primary-button:hover {
  box-shadow: 0 18px 38px rgba(117, 100, 255, 0.43);
  transform: translateY(-3px);
}

.secondary-button {
  color: #d6daef;
  border: 1px solid rgba(255, 255, 255, 0.13);
  background: rgba(255, 255, 255, 0.045);
}

.secondary-button:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.09);
  transform: translateY(-3px);
}

.mood-row {
  margin-top: 50px;
}

.mood-row > p {
  margin: 0 0 13px;
  color: #7883a7;
  font-size: 13px;
}

.mood-options {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.mood-option {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  padding: 10px 12px;
  color: #bbc2dd;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.035);
  font-size: 13px;
  text-decoration: none;
  transition: 0.2s ease;
}

.mood-option:hover {
  color: #fff;
  transform: translateY(-2px);
}

.mood-option.pink:hover {
  border-color: rgba(255, 145, 175, 0.45);
  background: rgba(255, 145, 175, 0.12);
}

.mood-option.purple:hover {
  border-color: rgba(160, 135, 255, 0.45);
  background: rgba(160, 135, 255, 0.12);
}

.mood-option.green:hover {
  border-color: rgba(82, 212, 190, 0.45);
  background: rgba(82, 212, 190, 0.12);
}

.hero-visual {
  position: relative;
  min-height: 620px;
}

.character-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(162, 120, 255, 0.3), transparent 66%);
  filter: blur(8px);
  transform: translate(-50%, -49%);
  animation: breathe 4s ease-in-out infinite;
}

.character-card {
  position: absolute;
  top: 50%;
  left: 50%;
  width: min(330px, 80%);
  padding: 17px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(12, 8, 35, 0.05) 0%, rgba(15, 10, 41, 0.1) 53%, rgba(10, 7, 31, 0.3) 100%),
    linear-gradient(145deg, rgba(197, 156, 255, 0.08), rgba(28, 21, 74, 0.01)),
    url('../assets/lumi-moon-spirit.png') center / cover;
  box-shadow: 0 35px 80px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(22px);
  transform: translate(-50%, -50%) rotate(4deg);
  animation: cardFloat 5s ease-in-out infinite;
}

.card-top {
  display: flex;
  gap: 7px;
  align-items: center;
  color: #d7d9f7;
  font-size: 11px;
}

.online-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #57dfbf;
  box-shadow: 0 0 10px #57dfbf;
}

.card-top button {
  margin-left: auto;
  padding: 0;
  color: #e9e6ff;
  background: transparent;
  cursor: pointer;
  font-size: 21px;
}

.character-info {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin: 282px 3px 13px;
}

.character-info p {
  margin: 0 0 4px;
  color: #abb1d3;
  font-size: 11px;
}

.character-info h2 {
  margin: 0;
  color: #fff;
  font-size: 24px;
}

.mood-badge {
  padding: 6px 8px;
  color: #f4c5e4;
  border: 1px solid rgba(255, 177, 217, 0.18);
  border-radius: 8px;
  background: rgba(255, 152, 204, 0.1);
  font-size: 10px;
}

.character-message {
  display: flex;
  gap: 7px;
  padding: 12px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.1);
}

.message-mark {
  color: #d7c6ff;
  font-size: 25px;
  line-height: 1;
}

.character-message p {
  margin: 0;
  color: #e6e8ff;
  font-size: 12px;
  line-height: 1.6;
}

.floating-card {
  position: absolute;
  z-index: 2;
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 16px;
  background: rgba(26, 25, 61, 0.7);
  box-shadow: 0 16px 35px rgba(0, 0, 0, 0.17);
  backdrop-filter: blur(16px);
  animation: smallFloat 4s ease-in-out infinite;
}

.floating-card small,
.floating-card strong {
  display: block;
}

.floating-card small {
  margin-bottom: 3px;
  color: #98a2c3;
  font-size: 10px;
}

.floating-card strong {
  color: #f1f0ff;
  font-size: 12px;
}

.floating-icon {
  display: grid;
  width: 29px;
  height: 29px;
  place-items: center;
  color: #ffe0f5;
  border-radius: 9px;
  background: rgba(245, 137, 202, 0.17);
}

.memory-card {
  top: 16%;
  left: 2%;
}

.warmth-card {
  right: 0;
  bottom: 15%;
  animation-delay: -2s;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(1px);
  opacity: 0.8;
  animation: orbFloat 8s ease-in-out infinite;
}

.orb-one {
  top: 8%;
  right: 4%;
  width: 135px;
  height: 135px;
  background: radial-gradient(circle at 32% 28%, #e1b3ff, #7965d9 68%);
}

.orb-two {
  bottom: 7%;
  left: 8%;
  width: 84px;
  height: 84px;
  background: radial-gradient(circle at 35% 35%, #9ff1e3, #3b9ea1 74%);
  animation-delay: -3s;
}

.orb-three {
  top: 37%;
  left: 3%;
  width: 46px;
  height: 46px;
  background: linear-gradient(135deg, #ffbed6, #d574b9);
  animation-delay: -5s;
}

.star {
  position: absolute;
  color: #e9e0ff;
  text-shadow: 0 0 14px rgba(212, 190, 255, 0.8);
  animation: twinkle 3s ease-in-out infinite;
}

.star-one {
  top: 25%;
  right: 8%;
  font-size: 22px;
}

.star-two {
  bottom: 27%;
  left: 4%;
  font-size: 15px;
  animation-delay: -1s;
}

.star-three {
  top: 5%;
  left: 29%;
  font-size: 13px;
  animation-delay: -2s;
}

.bottom-note {
  display: flex;
  gap: 12px;
  align-items: center;
  width: min(1240px, 100%);
  margin: 0 auto;
  padding: 0 7% 30px;
  color: #7f89aa;
  font-size: 12px;
}

.bottom-note span {
  width: 28px;
  height: 1px;
  background: #786ee4;
}

.bottom-note p {
  margin: 0;
}

@keyframes breathe {
  50% {
    opacity: 0.63;
    transform: translate(-50%, -49%) scale(1.08);
  }
}

@keyframes cardFloat {
  50% {
    transform: translate(-50%, calc(-50% - 11px)) rotate(2deg);
  }
}

@keyframes smallFloat {
  50% {
    transform: translateY(-8px);
  }
}

@keyframes orbFloat {
  50% {
    transform: translateY(-16px) translateX(8px);
  }
}

@keyframes twinkle {
  50% {
    opacity: 0.35;
    transform: scale(0.75);
  }
}

@media (max-width: 1050px) {
  .hero {
    grid-template-columns: 1fr;
    padding-top: 65px;
  }

  .hero-copy {
    text-align: center;
  }

  .hero-description {
    margin-right: auto;
    margin-left: auto;
  }

  .hero-actions,
  .mood-options {
    justify-content: center;
  }

  .hero-visual {
    min-height: 540px;
  }

  .bottom-note {
    justify-content: center;
  }
}

@media (max-width: 560px) {
  .hero {
    padding: 55px 20px 20px;
  }

  h1 {
    font-size: 48px;
    letter-spacing: -2px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .primary-button,
  .secondary-button {
    width: 100%;
  }

  .hero-visual {
    min-height: 465px;
    transform: scale(0.9);
    transform-origin: top center;
  }

  .memory-card {
    left: -2%;
  }

  .warmth-card {
    right: -3%;
  }

  .bottom-note {
    padding: 0 20px 20px;
    text-align: center;
  }
}
</style>
