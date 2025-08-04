<!-- 主页布局组件，包含侧边栏和内容区 -->
<template>
  <div class="home-layout">
    <Sidebar @navigate="onNavigate" :active="activeMenu" />
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Sidebar from './Sidebar.vue'

const router = useRouter()
const route = useRoute()
const activeMenu = ref('dashboard')

watch(
  () => route.path,
  (val) => {
    if (val.includes('dashboard')) activeMenu.value = 'dashboard'
    else if (val.includes('showcase')) activeMenu.value = 'showcase'
    else if (val.includes('navigation')) activeMenu.value = 'navigation'
    else if (val.includes('data')) activeMenu.value = 'data'
    else if (val.includes('visit')) activeMenu.value = 'visit'
    else if (val.includes('edit')) activeMenu.value = 'edit'
    else if (val.includes('profile')) activeMenu.value = 'profile'
  },
  { immediate: true }
)

function onNavigate(menu) {
  router.push(`/home/${menu}`)
}
</script>

<style scoped>
.home-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
}
.main-content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  background: #fff;
  padding: 0;
  overflow: auto;
  display: flex;
  flex-direction: column;
}
</style> 