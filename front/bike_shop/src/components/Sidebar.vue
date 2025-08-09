<!-- 侧边栏组件，包含首页、展示、地图、数据、拜访、修改、我的菜单 -->
<template>
  <div class="sidebar">
    <div
      v-for="item in menus"
      :key="item.key"
      :class="['sidebar-item', { active: active === item.key }]"
      @click="$emit('navigate', item.key)"
    >
      <span>{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
const props = defineProps({
  active: String
})
const menus = [
  { key: 'dashboard', label: '首页' },
  { key: 'showcase', label: '地图' },
  // { key: 'navigation', label: '地图' },
  { key: 'data', label: '数据' },
  { key: 'visit', label: '拜访' },
  { key: 'edit', label: '修改' },
  { key: 'profile', label: '我的' }
]
</script>

<style scoped>
.sidebar {
  width: 180px;
  background: #222c36;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding-top: 40px;
  box-shadow: 2px 0 8px rgba(0,0,0,0.04);
}
.sidebar-item {
  padding: 18px 32px;
  cursor: pointer;
  font-size: 18px;
  transition: background 0.2s;
}
.sidebar-item.active, .sidebar-item:hover {
  background: #1677ff;
  color: #fff;
}
</style>
