<!-- 需要先安装 ECharts：npm install echarts -->
<template>
  <div class="dashboard-stats-grid">
    <div class="dashboard-stat-card">
      <div class="stat-title">全部商店</div>
      <div class="stat-value">{{ stats.totalShops }}</div>
    </div>
    <div class="dashboard-stat-card">
      <div class="stat-title">用户数量</div>
      <div class="stat-value">{{ stats.totalUsers }}</div>
    </div>
    <div class="dashboard-stat-card">
      <div class="stat-title">我的拜访</div>
      <div class="stat-value">{{ stats.myVisits }}</div>
    </div>
    <div class="dashboard-stat-card">
      <div class="stat-title">所有人拜访</div>
      <div class="stat-value">{{ stats.totalVisits }}</div>
    </div>
    <div class="dashboard-stat-card">
      <div class="stat-title">已拜访商店</div>
      <div class="stat-value">{{ stats.visitedShops }}</div>
    </div>
    <div class="dashboard-stat-card">
      <div class="stat-title">未拜访商店</div>
      <div class="stat-value">{{ stats.unvisitedShops }}</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'

const stats = ref({
  totalShops: 0,
  totalUsers: 0,
  myVisits: 0,
  totalVisits: 0,
  visitedShops: 0,
  unvisitedShops: 0
})

async function fetchStats() {
  const token = localStorage.getItem('token')
  // 全部商店
  const shopRes = await axios.get('/api/data-list', { params: { page: 1, page_size: 1 }, headers: { Authorization: `Token ${token}` } })
  stats.value.totalShops = shopRes.data.total || 0
  // 已拜访商店
  const visitedRes = await axios.get('/api/data-list', { params: { page: 1, page_size: 1, visited: 1 }, headers: { Authorization: `Token ${token}` } })
  stats.value.visitedShops = visitedRes.data.total || 0
  // 未拜访商店
  const unvisitedRes = await axios.get('/api/data-list', { params: { page: 1, page_size: 1, visited: 0 }, headers: { Authorization: `Token ${token}` } })
  stats.value.unvisitedShops = unvisitedRes.data.total || 0
  // 用户数量
  const userRes = await axios.get('/api/all-user', { headers: { Authorization: `Token ${token}` } })
  stats.value.totalUsers = userRes.data.total_users || 0
  // 我的拜访
  const myVisitRes = await axios.get('/api/visit-shop-list', { params: { page: 1, page_size: 1 }, headers: { Authorization: `Token ${token}` } })
  stats.value.myVisits = myVisitRes.data.total || 0
  // 所有人拜访
  const allVisitRes = await axios.get('/api/all-visit', { headers: { Authorization: `Token ${token}` } })
  stats.value.totalVisits = allVisitRes.data.total_visits || 0
}

onMounted(async () => {
  await fetchStats()
})
</script>

<style scoped>
.dashboard-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px 32px;
  width: 100%;
  margin-bottom: 24px;
  margin-top: 8px;
}
.dashboard-stat-card {
  background: linear-gradient(90deg, #e0eaff 0%, #f7faff 100%);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(88,166,255,0.08);
  padding: 24px 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.stat-title {
  font-size: 1.08rem;
  color: #1765d8;
  margin-bottom: 8px;
  font-weight: 600;
}
.stat-value {
  font-size: 2.1rem;
  font-weight: 700;
  color: #1677ff;
}
.bi-dashboard {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 24px;
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
  box-sizing: border-box;
  flex: 1;
  display: flex;
}
</style>
