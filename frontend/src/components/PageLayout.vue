<template>
  <div class="app-shell">
    <AppNavigation />

    <main class="page-content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import AppNavigation from './AppNavigation.vue'
</script>

<style scoped>
.page-content {
  min-height: 100vh;
  margin-left: 250px;
}

@media (max-width: 800px) {
  .page-content {
    margin-left: 0;
    padding-bottom: 64px;
  }
}
</style>