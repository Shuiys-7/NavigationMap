<!-- 主页布局组件，包含侧边栏和内容区 -->
<template>
  <div class="home-layout">
    <!-- 移动端 -->
    <div class="mobile-header">
      <button class="hamburger" @click="toggleSidebar">☰</button>
    </div>

    <!-- 侧边栏 + 遮罩层 -->
    <Sidebar
      v-if="isSidebarVisible || isDesktop"
      @navigate="onNavigate"
      :active="activeMenu"
      class="sidebar"
      :class="{ 'mobile-visible': isSidebarVisible && !isDesktop }"
    />
    <div
      v-if="isSidebarVisible && !isDesktop"
      class="overlay"
      @click="closeSidebar"
    ></div>

    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Sidebar from './Sidebar.vue'

const router = useRouter()
const route = useRoute()
const activeMenu = ref('dashboard')
const isSidebarVisible = ref(false)
const isDesktop = ref(window.innerWidth >= 768)

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
  if (!isDesktop.value) closeSidebar()
}

function toggleSidebar() {
  isSidebarVisible.value = !isSidebarVisible.value
}

function closeSidebar() {
  isSidebarVisible.value = false
}

function handleResize() {
  isDesktop.value = window.innerWidth >= 768
  if (isDesktop.value) {
    isSidebarVisible.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>


<style scoped>
.home-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
}
.sidebar {
  width: 240px;
  transition: transform 0.3s ease;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 10;
}

.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  height: 48px;
  width: 100%;
  background-color: #fff;
  display: none;
  align-items: center;
  padding: 0 12px;
  z-index: 20;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.hamburger {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
}
.main-content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  height: 100%;
  background: #fff;
  overflow: auto;
  display: flex;
  flex-direction: column;
}
/* 移动端样式 */
@media (max-width: 767px) {
  .mobile-header {
    display: flex;
  }
  .main-content {
    flex: 1;
    min-width: 0;
    min-height: 0;
    height: 100%;
    background: #fff;
    padding-top: 50px;
    overflow: auto;
    display: flex;
    flex-direction: column;
  }
  .sidebar {
    position: fixed;
    top: 48px;
    left: 0;
    height: calc(100% - 48px);
    z-index: 99999;
    background-color: #30363d;
    transform: translateX(-100%);
  }

  .sidebar.mobile-visible {
    transform: translateX(0);
  }
}
</style>
