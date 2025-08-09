<!-- 使用 ECharts 美化首页界面 -->
<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1 class="dashboard-title">商店拜访数据分析</h1>
    </div>
    
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
    </div>
    
    <div class="dashboard-charts-container">
      <div class="chart-card">
        <div class="chart-title">商店拜访情况</div>
        <div ref="visitPieChartRef" class="chart-container"></div>
      </div>
      
      <div class="chart-card">
        <div class="chart-title">拜访统计</div>
        <div class="visit-stats">
          <div class="visit-stat-item">
            <div class="visit-stat-label">已拜访商店</div>
            <div class="visit-stat-value visited">{{ stats.visitedShops }}</div>
          </div>
          <div class="visit-stat-item">
            <div class="visit-stat-label">未拜访商店</div>
            <div class="visit-stat-value unvisited">{{ stats.unvisitedShops }}</div>
          </div>
          <div class="visit-stat-item">
            <div class="visit-stat-label">拜访完成率</div>
            <div class="visit-stat-value completion-rate">{{ visitCompletionRate }}%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const visitPieChartRef = ref(null)
let visitPieChart = null
const isMobile = ref(false)

const stats = ref({
  totalShops: 0,
  totalUsers: 0,
  myVisits: 0,
  totalVisits: 0,
  visitedShops: 0,
  unvisitedShops: 0
})

// 计算拜访完成率
const visitCompletionRate = computed(() => {
  if (stats.value.totalShops === 0) return 0
  return Math.round((stats.value.visitedShops / stats.value.totalShops) * 100)
})

// 检测是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

async function fetchStats() {
  const token = localStorage.getItem('token')
  try {
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
    
    // 数据加载完成后初始化图表
    initCharts()
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 初始化图表
function initCharts() {
  initVisitPieChart()
}

// 初始化拜访饼图
function initVisitPieChart() {
  if (!visitPieChartRef.value) return
  
  // 如果图表已经存在，先销毁
  if (visitPieChart) {
    visitPieChart.dispose()
  }
  
  // 初始化图表
  visitPieChart = echarts.init(visitPieChartRef.value)
  
  // 设置图表选项
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['已拜访商店', '未拜访商店']
    },
    series: [
      {
        name: '拜访情况',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: stats.value.visitedShops, name: '已拜访商店', itemStyle: { color: '#1677ff' } },
          { value: stats.value.unvisitedShops, name: '未拜访商店', itemStyle: { color: '#ff7875' } }
        ]
      }
    ]
  }
  
  // 使用配置项设置图表
  visitPieChart.setOption(option)
}

// 监听窗口大小变化，调整图表大小
function handleResize() {
  if (visitPieChart) {
    visitPieChart.resize()
  }
  checkMobile()
}

onMounted(async () => {
  checkMobile()
  await fetchStats()
  window.addEventListener('resize', handleResize)
})

// 组件卸载前清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (visitPieChart) {
    visitPieChart.dispose()
    visitPieChart = null
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100%;
  box-sizing: border-box;
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1765d8;
  margin: 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #e0eaff;
}

.dashboard-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  width: 100%;
  margin-bottom: 32px;
}

.dashboard-stat-card {
  background: linear-gradient(135deg, #e0eaff 0%, #f7faff 100%);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(88,166,255,0.1);
  padding: 24px 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid rgba(88,166,255,0.1);
}

.dashboard-stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(88,166,255,0.15);
}

.stat-title {
  font-size: 1.1rem;
  color: #1765d8;
  margin-bottom: 12px;
  font-weight: 600;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1677ff;
  text-shadow: 0 2px 4px rgba(22,119,255,0.1);
}

.dashboard-charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  padding: 24px;
  display: flex;
  flex-direction: column;
  border: 1px solid #eaedf2;
}

.chart-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1765d8;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0eaff;
}

.chart-container {
  flex: 1;
  min-height: 300px;
}

.visit-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  height: 100%;
  justify-content: center;
}

.visit-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #f8faff;
  border-radius: 12px;
  border-left: 4px solid #1677ff;
}

.visit-stat-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.visit-stat-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.visit-stat-value.visited {
  color: #1677ff;
}

.visit-stat-value.unvisited {
  color: #ff7875;
}

.visit-stat-value.completion-rate {
  color: #52c41a;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .dashboard-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-title {
    font-size: 1.6rem;
  }
  
  .stat-value {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .dashboard-title {
    font-size: 1.4rem;
    padding-bottom: 10px;
  }
  
  .dashboard-stats-grid {
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .dashboard-stat-card {
    padding: 16px 0;
  }
  
  .stat-title {
    font-size: 1rem;
    margin-bottom: 8px;
  }
  
  .stat-value {
    font-size: 1.8rem;
  }
  
  .dashboard-charts-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .chart-card {
    padding: 16px;
  }
  
  .chart-title {
    font-size: 1.2rem;
    margin-bottom: 16px;
    padding-bottom: 10px;
  }
  
  .chart-container {
    min-height: 250px;
  }
  
  .visit-stats {
    padding: 10px;
    gap: 16px;
  }
  
  .visit-stat-item {
    padding: 12px 16px;
  }
  
  .visit-stat-label {
    font-size: 1rem;
  }
  
  .visit-stat-value {
    font-size: 1.3rem;
  }
}

@media (max-width: 480px) {
  .dashboard-container {
    padding: 12px;
  }
  
  .dashboard-title {
    font-size: 1.3rem;
  }
  
  .dashboard-stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .dashboard-stat-card {
    padding: 14px 0;
  }
  
  .stat-title {
    font-size: 0.95rem;
  }
  
  .stat-value {
    font-size: 1.6rem;
  }
  
  .chart-card {
    padding: 12px;
  }
  
  .chart-title {
    font-size: 1.1rem;
    margin-bottom: 12px;
  }
  
  .chart-container {
    min-height: 200px;
  }
  
  .visit-stat-item {
    padding: 10px 12px;
  }
  
  .visit-stat-label {
    font-size: 0.9rem;
  }
  
  .visit-stat-value {
    font-size: 1.2rem;
  }
}
</style>
