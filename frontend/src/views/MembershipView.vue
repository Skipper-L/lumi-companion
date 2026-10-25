<script setup>
import { computed, ref } from 'vue'
import {
  Check,
  Crown,
  Diamond,
  ShieldCheck,
  Sparkles,
  X,
} from 'lucide-vue-next'
import PageLayout from '../components/PageLayout.vue'
import wechatPayQr from '../assets/images/wechat-pay.jpg'

const billingCycle = ref('yearly')
const showConfirmModal = ref(false)
const showQrModal = ref(false)
const selectedPlanId = ref('plus')

const plans = {
  free: {
    id: 'free',
    name: 'Lumi Free',
    icon: Sparkles,
    subtitle: '轻松开始一段陪伴',
    monthlyPrice: 0,
    yearlyPrice: 0,
    features: [
      '基础角色聊天',
      '保留最近 20 条消息',
      '每日 10 次对话',
    ],
  },
  plus: {
    id: 'plus',
    name: 'Lumi Plus',
    icon: Crown,
    subtitle: '让陪伴更贴近你的生活',
    monthlyPrice: 29,
    yearlyPrice: 19,
    saveText: '全年节省 ¥120',
    features: [
      '无限文字对话',
      '长期记忆与回忆空间',
      '语音陪伴 120 分钟/月',
      '全部高级角色与主题',
    ],
  },
  ultra: {
    id: 'ultra',
    name: 'Lumi Ultra',
    icon: Diamond,
    subtitle: '解锁完整的专属陪伴体验',
    monthlyPrice: 59,
    yearlyPrice: 39,
    saveText: '全年节省 ¥240',
    features: [
      'Plus 的全部权益',
      '语音陪伴不限时',
      '专属角色创建与训练',
      '优先体验新功能',
    ],
  },
}

const selectedPlan = computed(() => plans[selectedPlanId.value])

const currentPrice = computed(() => {
  if (billingCycle.value === 'yearly') {
    return selectedPlan.value.yearlyPrice
  }

  return selectedPlan.value.monthlyPrice
})

const billingDescription = computed(() => {
  if (billingCycle.value === 'yearly') {
    return '按年订阅，可随时取消'
  }

  return '按月订阅，可随时取消'
})

function getPlanPrice(plan) {
  if (billingCycle.value === 'yearly') {
    return plan.yearlyPrice
  }

  return plan.monthlyPrice
}

function openConfirm(planId) {
  selectedPlanId.value = planId
  showConfirmModal.value = true
}

function closeAllModal() {
  showConfirmModal.value = false
  showQrModal.value = false
}

function goToPayment() {
  showConfirmModal.value = false
  showQrModal.value = true
}
</script>

<template>
  <PageLayout>
    <main class="membership-page">
      <div class="purple-light purple-light-left"></div>
      <div class="purple-light purple-light-right"></div>

      <section class="membership-hero">
        <div class="membership-badge">
          <Sparkles :size="17" />
          <span>LUMI MEMBERSHIP</span>
        </div>

        <h1>把陪伴，留得更久一点。</h1>
        <p>解锁更懂你的记忆、更沉浸的语音，以及只属于你的温柔空间。</p>

        <div class="billing-switch">
          <button
            :class="{ active: billingCycle === 'monthly' }"
            @click="billingCycle = 'monthly'"
          >
            月付
          </button>

          <button
            :class="{ active: billingCycle === 'yearly' }"
            @click="billingCycle = 'yearly'"
          >
            年付
            <span>省 34%</span>
          </button>
        </div>
      </section>

      <section class="plans-grid">
        <!-- 免费版 -->
        <article class="plan-card free-card">
          <div class="plan-icon">
            <Sparkles :size="28" />
          </div>

          <h2>Lumi Free</h2>
          <p class="plan-subtitle">轻松开始一段陪伴</p>

          <div class="price-block">
            <strong>¥0</strong>
            <span>永久免费</span>
          </div>

          <div class="line"></div>

          <ul class="feature-list">
            <li v-for="feature in plans.free.features" :key="feature">
              <Check :size="18" />
              <span>{{ feature }}</span>
            </li>
          </ul>

          <div class="line bottom-line"></div>

          <button class="current-button" disabled>
            当前免费版
          </button>
        </article>

        <!-- Plus -->
        <article class="plan-card plus-card">
          <div class="popular-tag">最受欢迎</div>

          <div class="plan-icon">
            <Crown :size="28" />
          </div>

          <h2>Lumi Plus</h2>
          <p class="plan-subtitle">让陪伴更贴近你的生活</p>

          <div class="price-block">
            <strong>¥{{ getPlanPrice(plans.plus) }}</strong>
            <span>/ 月</span>
          </div>

          <p class="save-text">
            按年订阅，{{ billingCycle === 'yearly' ? '全年节省 ¥120' : '更划算' }}
          </p>

          <div class="line"></div>

          <ul class="feature-list">
            <li v-for="feature in plans.plus.features" :key="feature">
              <Check :size="18" />
              <span>{{ feature }}</span>
            </li>
          </ul>

          <div class="line bottom-line"></div>

          <button class="plus-button" @click="openConfirm('plus')">
            选择 Lumi Plus
          </button>
        </article>

        <!-- Ultra -->
        <article class="plan-card ultra-card">
          <div class="plan-icon">
            <Diamond :size="27" />
          </div>

          <h2>Lumi Ultra</h2>
          <p class="plan-subtitle">解锁完整的专属陪伴体验</p>

          <div class="price-block">
            <strong>¥{{ getPlanPrice(plans.ultra) }}</strong>
            <span>/ 月</span>
          </div>

          <p class="save-text">
            按年订阅，{{ billingCycle === 'yearly' ? '全年节省 ¥240' : '更划算' }}
          </p>

          <div class="line"></div>

          <ul class="feature-list">
            <li v-for="feature in plans.ultra.features" :key="feature">
              <Check :size="18" />
              <span>{{ feature }}</span>
            </li>
          </ul>

          <div class="line bottom-line"></div>

          <button class="ultra-button" @click="openConfirm('ultra')">
            选择 Lumi Ultra
          </button>
        </article>
      </section>
    </main>

    <!-- 第一步：确认支付 -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showConfirmModal"
          class="modal-mask"
          @click.self="closeAllModal"
        >
          <section class="confirm-modal">
            <button class="close-button" @click="closeAllModal">
              <X :size="26" />
            </button>

            <div class="modal-icon">
              <component :is="selectedPlan.icon" :size="31" />
            </div>

            <p class="modal-small-title">即将解锁</p>
            <h2>{{ selectedPlan.name }}</h2>

            <div class="modal-price">
              <strong>¥{{ currentPrice }}</strong>
              <span>/ 月</span>
            </div>

            <p class="modal-description">
              {{ billingDescription }}
            </p>

            <button class="go-pay-button" @click="goToPayment">
              确认并前往支付
            </button>

            <p class="demo-tip">
              演示界面：支付功能将在后端阶段接入。
            </p>
          </section>
        </div>
      </Transition>
    </Teleport>

    <!-- 第二步：展示微信收款码 -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showQrModal"
          class="modal-mask"
          @click.self="closeAllModal"
        >
          <section class="qr-modal">
            <button class="close-button" @click="closeAllModal">
              <X :size="26" />
            </button>

            <div class="modal-icon">
              <component :is="selectedPlan.icon" :size="31" />
            </div>

            <p class="modal-small-title">微信扫码支付</p>
            <h2>{{ selectedPlan.name }}</h2>

            <div class="modal-price">
              <strong>¥{{ currentPrice }}</strong>
              <span>/ 月</span>
            </div>

            <p class="modal-description">
              {{ billingDescription }}
            </p>

            <div class="qr-image-box">
              <img :src="wechatPayQr" alt="微信支付收款二维码" />
            </div>

            <div class="wechat-text">
              <span>✓</span>
              请使用微信扫一扫完成支付
            </div>

            <p class="qr-notice">
              请核对支付金额后再付款。<br />
              目前仅展示收款码，正式开通会员需要后端验证支付结果。
            </p>

            <button class="cancel-pay-button" @click="closeAllModal">
              暂不支付
            </button>
          </section>
        </div>
      </Transition>
    </Teleport>
  </PageLayout>
</template>

<style scoped>
.membership-page {
  position: relative;
  min-height: 100%;
  overflow: hidden;
  padding: 70px 48px 86px;
  color: #f7f5ff;
  background: #080c21;
}

.purple-light {
  position: absolute;
  border-radius: 50%;
  filter: blur(82px);
  pointer-events: none;
}

.purple-light-left {
  top: 360px;
  left: -120px;
  width: 310px;
  height: 440px;
  background: rgba(97, 55, 192, 0.29);
}

.purple-light-right {
  top: -130px;
  right: 19%;
  width: 300px;
  height: 240px;
  background: rgba(104, 68, 200, 0.18);
}

.membership-hero {
  position: relative;
  z-index: 1;
  text-align: center;
}

.membership-badge {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 10px 19px;
  border: 1px solid rgba(193, 173, 255, 0.21);
  border-radius: 999px;
  color: #d2c3fa;
  font-size: 14px;
  letter-spacing: 0.9px;
  background: rgba(80, 61, 145, 0.2);
}

.membership-hero h1 {
  margin: 38px 0 17px;
  font-size: clamp(40px, 5vw, 66px);
  line-height: 1.12;
  letter-spacing: -3px;
}

.membership-hero > p {
  margin: 0;
  color: #989bbc;
  font-size: 17px;
}

.billing-switch {
  display: flex;
  width: fit-content;
  gap: 4px;
  margin: 42px auto 65px;
  padding: 6px;
  border: 1px solid rgba(177, 161, 236, 0.14);
  border-radius: 17px;
  background: rgba(29, 28, 66, 0.7);
}

.billing-switch button {
  padding: 12px 17px;
  border: 0;
  border-radius: 12px;
  color: #9a9aba;
  cursor: pointer;
  font: inherit;
  font-size: 15px;
  background: transparent;
  transition: 0.25s ease;
}

.billing-switch button.active {
  color: #38215f;
  font-weight: 800;
  background: linear-gradient(120deg, #eadbff, #f8d4fa);
  box-shadow: 0 5px 14px rgba(232, 196, 255, 0.16);
}

.billing-switch span {
  margin-left: 5px;
  color: #e26bb1;
  font-size: 13px;
}

.plans-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.plan-card {
  position: relative;
  display: flex;
  min-height: 620px;
  flex-direction: column;
  padding: 36px;
  border: 1px solid rgba(144, 149, 199, 0.18);
  border-radius: 31px;
  background: rgba(20, 26, 57, 0.84);
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.025);
}

.plan-card:hover {
  border-color: rgba(190, 163, 255, 0.3);
}

.plus-card {
  border-color: rgba(166, 131, 255, 0.82);
  background:
    linear-gradient(180deg, rgba(50, 41, 104, 0.25), transparent 35%),
    rgba(20, 26, 57, 0.96);
  box-shadow:
    0 24px 60px rgba(13, 9, 43, 0.35),
    inset 0 1px rgba(255, 255, 255, 0.08);
}

.popular-tag {
  position: absolute;
  top: -1px;
  right: 25px;
  padding: 9px 15px;
  border-radius: 0 0 12px 12px;
  color: #fff3ff;
  font-size: 13px;
  font-weight: 800;
  background: linear-gradient(100deg, #9470fb, #d76cce);
  box-shadow: 0 8px 18px rgba(167, 88, 220, 0.28);
}

.plan-icon {
  display: grid;
  width: 66px;
  height: 66px;
  place-items: center;
  border-radius: 19px;
  color: #d5c0ff;
  background: rgba(116, 85, 194, 0.27);
}

.plan-card h2 {
  margin: 31px 0 10px;
  font-size: 30px;
  letter-spacing: -1px;
}

.plan-subtitle {
  min-height: 41px;
  margin: 0;
  color: #9698b9;
  font-size: 16px;
}

.price-block {
  display: flex;
  align-items: baseline;
  gap: 9px;
  margin-top: 52px;
}

.price-block strong {
  font-size: 51px;
  letter-spacing: -2px;
}

.price-block span {
  color: #9698b9;
  font-size: 16px;
}

.save-text {
  min-height: 21px;
  margin: 9px 0 0;
  color: #7fcdaa;
  font-size: 14px;
  font-weight: 600;
}

.line {
  height: 1px;
  margin: 28px 0;
  background: rgba(153, 156, 194, 0.15);
}

.bottom-line {
  margin-top: auto;
  margin-bottom: 34px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 0;
  margin: 0;
  list-style: none;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 11px;
  color: #c2c2db;
  font-size: 16px;
}

.feature-list svg {
  flex: none;
  color: #aa8cff;
}

.current-button,
.ultra-button,
.plus-button {
  width: 100%;
  padding: 17px;
  border-radius: 15px;
  font: inherit;
  font-size: 18px;
  font-weight: 800;
}

.current-button {
  border: 1px solid rgba(182, 185, 215, 0.18);
  color: #dcdaeb;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.035);
}

.ultra-button {
  border: 1px solid rgba(181, 182, 226, 0.23);
  color: #f2effb;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.045);
  transition: 0.25s ease;
}

.ultra-button:hover {
  border-color: rgba(221, 202, 255, 0.55);
  background: rgba(136, 96, 224, 0.18);
  transform: translateY(-3px);
}

.plus-button {
  border: 0;
  color: white;
  cursor: pointer;
  background: linear-gradient(100deg, #7858f1, #cc61d6);
  box-shadow: 0 15px 26px rgba(119, 76, 224, 0.3);
  transition: 0.25s ease;
}

.plus-button:hover {
  box-shadow: 0 19px 34px rgba(178, 82, 218, 0.46);
  transform: translateY(-3px);
}

/* 弹窗通用样式 */
.modal-mask {
  position: fixed;
  z-index: 9999;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 22px;
  background: rgba(3, 5, 20, 0.77);
  backdrop-filter: blur(14px);
}

.confirm-modal,
.qr-modal {
  position: relative;
  width: min(100%, 510px);
  overflow: hidden;
  border: 1px solid rgba(190, 169, 245, 0.31);
  border-radius: 32px;
  text-align: center;
  color: #f8f5ff;
  background:
    radial-gradient(circle at 50% -12%, rgba(134, 90, 219, 0.27), transparent 43%),
    linear-gradient(145deg, #252252, #11142f);
  box-shadow: 0 32px 85px rgba(0, 0, 0, 0.58);
}

.confirm-modal {
  padding: 50px 52px 45px;
}

.qr-modal {
  padding: 38px 42px 32px;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 21px;
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border: 0;
  border-radius: 12px;
  color: #c9c4e0;
  cursor: pointer;
  background: transparent;
  transition: 0.2s ease;
}

.close-button:hover {
  color: white;
  background: rgba(255, 255, 255, 0.09);
}

.modal-icon {
  display: grid;
  width: 67px;
  height: 67px;
  place-items: center;
  margin: 0 auto 29px;
  border-radius: 21px;
  color: #dfc9ff;
  background: linear-gradient(135deg, #4f3b92, #372b6f);
}

.modal-small-title {
  margin: 0;
  color: #b7afd2;
  font-size: 16px;
}

.confirm-modal h2,
.qr-modal h2 {
  margin: 14px 0 25px;
  font-size: 39px;
  letter-spacing: -1.5px;
}

.modal-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 9px;
}

.modal-price strong {
  font-size: 51px;
  letter-spacing: -2px;
}

.modal-price span {
  color: #bab5d1;
  font-size: 18px;
  font-weight: 700;
}

.modal-description {
  margin: 12px 0 31px;
  color: #c1bdd2;
  font-size: 16px;
}

.go-pay-button {
  width: 100%;
  padding: 18px;
  border: 0;
  border-radius: 15px;
  color: white;
  cursor: pointer;
  font: inherit;
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(100deg, #7958f4, #c964d4);
  box-shadow: 0 14px 26px rgba(132, 74, 223, 0.38);
  transition: 0.25s ease;
}

.go-pay-button:hover {
  box-shadow: 0 18px 34px rgba(175, 81, 222, 0.5);
  transform: translateY(-3px);
}

.demo-tip {
  margin: 22px 0 0;
  color: #8986a3;
  font-size: 13px;
}

.qr-modal h2 {
  margin-bottom: 16px;
  font-size: 32px;
}

.qr-modal .modal-description {
  margin-bottom: 19px;
  font-size: 14px;
}

.qr-image-box {
  width: 228px;
  height: 228px;
  padding: 8px;
  margin: 0 auto 18px;
  border-radius: 17px;
  background: #ffffff;
  box-shadow: 0 15px 31px rgba(0, 0, 0, 0.26);
}

.qr-image-box img {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 10px;
  object-fit: cover;
}

.wechat-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  color: #e2deee;
  font-size: 14px;
}

.wechat-text span {
  display: grid;
  width: 20px;
  height: 20px;
  place-items: center;
  border-radius: 50%;
  color: white;
  font-size: 13px;
  font-weight: 900;
  background: #1fc675;
}

.qr-notice {
  margin: 14px 0 16px;
  color: #908da7;
  font-size: 11px;
  line-height: 1.75;
}

.cancel-pay-button {
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(199, 185, 248, 0.2);
  border-radius: 12px;
  color: #d5d0e6;
  cursor: pointer;
  font: inherit;
  background: rgba(255, 255, 255, 0.045);
  transition: 0.2s ease;
}

.cancel-pay-button:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-active .confirm-modal,
.modal-enter-active .qr-modal,
.modal-leave-active .confirm-modal,
.modal-leave-active .qr-modal {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .confirm-modal,
.modal-enter-from .qr-modal,
.modal-leave-to .confirm-modal,
.modal-leave-to .qr-modal {
  opacity: 0;
  transform: translateY(18px) scale(0.96);
}

@media (max-width: 1000px) {
  .plans-grid {
    grid-template-columns: 1fr;
    max-width: 620px;
  }

  .plan-card {
    min-height: auto;
  }

  .bottom-line {
    margin-top: 30px;
  }
}

@media (max-width: 600px) {
  .membership-page {
    padding: 48px 18px 60px;
  }

  .membership-hero h1 {
    letter-spacing: -2px;
  }

  .membership-hero > p {
    font-size: 14px;
    line-height: 1.7;
  }

  .plan-card {
    padding: 29px 24px;
  }

  .confirm-modal {
    padding: 44px 25px 32px;
  }

  .qr-modal {
    padding: 37px 24px 26px;
  }

  .confirm-modal h2 {
    font-size: 32px;
  }
}
/* 会员页面整体紧凑一点 */
.membership-page {
  padding-top: 36px;
  padding-bottom: 46px;
}

.membership-hero h1 {
  font-size: clamp(34px, 3.8vw, 50px);
}

.membership-hero > p {
  font-size: 14px;
}

.billing-switch {
  margin-top: 26px;
  margin-bottom: 36px;
  transform: scale(0.94);
}

.plans-grid {
  max-width: 1280px;
  gap: 20px;
}

.plan-card {
  min-height: 520px;
  padding: 27px;
  border-radius: 24px;
}

.plan-icon {
  width: 54px;
  height: 54px;
  border-radius: 16px;
}

.plan-card h2 {
  margin-top: 21px;
  margin-bottom: 6px;
  font-size: 25px;
}

.plan-subtitle {
  min-height: 31px;
  font-size: 13px;
}

.price-block {
  margin-top: 31px;
}

.price-block strong {
  font-size: 41px;
}

.line {
  margin-top: 18px;
  margin-bottom: 18px;
}

.feature-list {
  gap: 11px;
}

.feature-list li {
  font-size: 13px;
}

.bottom-line {
  margin-top: auto;
  margin-bottom: 19px;
}

.current-button,
.ultra-button,
.plus-button {
  padding: 13px;
  font-size: 15px;
}
</style>
