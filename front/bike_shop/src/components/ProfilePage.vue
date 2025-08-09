<!-- 我的页面组件 - 美化版 -->
<template>
  <div class="profile-page">
    <div class="profile-header">
      <h1 class="profile-title">我的页面</h1>
      <button @click="loginOut" class="logout-btn">
        <i class="fas fa-sign-out-alt"></i> 退出登录
      </button>
    </div>
    
    <div class="profile-content">
      <!-- 左侧用户信息和统计 -->
      <div class="profile-left-column">
        <!-- 用户信息卡片 -->
        <div class="user-profile-card">
          <div class="user-avatar" v-if="user">
            {{ user.username.charAt(0).toUpperCase() }}
          </div>
          <div class="user-avatar skeleton" v-else></div>
          
          <div class="user-info-content">
            <div v-if="user">
              <h2 class="user-name">{{ user.username }}</h2>
              <div class="user-email">{{ user.email || '未设置邮箱' }}</div>
              <div class="user-role">管理员</div>
            </div>
            <div v-else class="user-loading">
              <div class="skeleton-line"></div>
              <div class="skeleton-line"></div>
              <div class="skeleton-line"></div>
            </div>
          </div>
        </div>
        
        <!-- 数据统计卡片 -->
        <div class="stats-card">
          <h3 class="card-title">数据统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ visitCount }}</div>
              <div class="stat-label">拜访次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ shopCount }}</div>
              <div class="stat-label">商店数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ daysSinceJoin }}</div>
              <div class="stat-label">活跃天数</div>
            </div>
          </div>
        </div>
        
        <!-- 最近活动 -->
        <div class="activity-card">
          <h3 class="card-title">最近活动</h3>
          <div class="activity-timeline">
            <div class="activity-item" v-for="(activity, index) in recentActivities" :key="index">
              <div class="activity-icon" :class="activity.type"></div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
            <div class="empty-activity" v-if="recentActivities.length === 0">
              暂无活动记录
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧数据导入区域 -->
      <div class="profile-right-column">
        <div class="import-card">
          <h3 class="card-title">数据导入</h3>
          
          <!-- 数据文件上传 -->
          <div class="import-section">
            <div class="import-section-header">
              <h4 class="import-title">
                <i class="fas fa-file-excel"></i> Excel数据导入
              </h4>
            </div>
            <div class="import-content">
              <div class="upload-area" :class="{ 'has-file': excelFile }">
            <label class="file-label">
              <input type="file" accept=".xlsx,.xls,.csv" @change="handleFileChange" class="excel-input" :disabled="isUploading" />
              <div class="upload-icon">
                <i class="fas fa-file-excel"></i>
              </div>
              <div class="upload-text">
                <span v-if="!excelFile">点击选择Excel文件</span>
                <span v-else class="file-name"><i class="fas fa-file-excel"></i> {{ excelFile.name }}</span>
              </div>
            </label>
          </div>
          <button @click="uploadExcel" :disabled="!excelFile || isUploading" class="upload-btn">
            <i class="fas fa-cloud-upload-alt"></i> {{ isUploading ? '上传中...' : '上传数据' }}
              </button>
              <transition name="fade">
                <div v-if="uploadMsg" class="upload-msg success-msg">{{ uploadMsg }}</div>
              </transition>
            </div>
          </div>
          
          <!-- 图片上传 -->
          <div class="import-section">
            <div class="import-section-header">
              <h4 class="import-title">
                <i class="fas fa-images"></i> 图片/压缩包上传
              </h4>
            </div>
            <div class="import-content">
              <div class="upload-area" :class="{ 'has-file': imageFiles.length > 0 }">
                <label class="file-label">
                  <input type="file" accept="image/*,.zip,.rar" @change="handleImageChange" class="excel-input" :multiple="true" :disabled="isUploading" />
                  <div class="upload-icon">
                    <i class="fas fa-images"></i>
                  </div>
                  <div class="upload-text">
                    <span v-if="imageFiles.length === 0">点击选择图片或压缩包</span>
                    <span v-else class="file-name">
                      <i class="fas fa-file-archive" v-if="imageFiles.some(f => f.name.endsWith('.zip') || f.name.endsWith('.rar'))"></i>
                      <i class="fas fa-images" v-else></i>
                      已选择 {{ imageFiles.length }} 个文件
                    </span>
                  </div>
                </label>
              </div>
              <button @click="uploadImage" :disabled="!imageFiles.length || isUploading" class="upload-btn">
                <i class="fas fa-cloud-upload-alt"></i> {{ isUploading ? '上传中...' : '上传图片' }}
              </button>
              <transition name="fade">
                <div v-if="uploadImgMsg" class="upload-msg img-msg">{{ uploadImgMsg }}</div>
              </transition>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错误提示对话框 -->
    <div v-if="showErrorDialog" class="error-dialog-mask">
      <div class="error-dialog">
        <div class="error-dialog-title">上传失败</div>
        <div class="error-dialog-msg">{{ errorDialogMsg }}</div>
        <button class="error-dialog-btn" @click="showErrorDialog = false">确定</button>
      </div>
    </div>
    
    <!-- 成功提示对话框 -->
    <div v-if="showSuccessDialog" class="success-dialog-mask">
      <div class="success-dialog">
        <div class="success-dialog-title">上传成功</div>
        <div class="success-dialog-msg">{{ successDialogMsg }}</div>
        <button class="success-dialog-btn" @click="showSuccessDialog = false">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
// 如果项目已用Element Plus，解开下行注释
// import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
const router = useRouter()

// 用户和上传相关状态
const user = ref(null)
const visitList = ref([])
const excelFile = ref(null)
const imageFiles = ref([])
const uploadMsg = ref('')
const uploadImgMsg = ref('')
const showErrorDialog = ref(false)
const errorDialogMsg = ref('')
const showSuccessDialog = ref(false)
const successDialogMsg = ref('')
const isUploading = ref(false)

// 统计数据
const visitCount = ref(0)
const shopCount = ref(0)
const daysSinceJoin = ref(0)

// 最近活动记录
const recentActivities = ref([])

// 计算用户注册天数
function calculateDaysSinceJoin(joinDate) {
  if (!joinDate) return 0
  const now = new Date()
  const join = new Date(joinDate)
  const diffTime = Math.abs(now - join)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

// 获取当前用户信息和所有统计数据
onMounted(async () => {
  try {
    // 首先获取用户数据
    await fetchUserData()
    
    // 并行获取其他统计数据以提高加载速度
    await Promise.all([
      fetchVisitData(),
      fetchShopCount(),
      generateRecentActivities()
    ])
    
    console.log('所有数据加载完成')
  } catch (error) {
    console.error('数据加载过程中发生错误:', error)
  }
})

// 获取用户数据
async function fetchUserData() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/user-data', {
      headers: { Authorization: `Token ${token}` }
    })
    user.value = res.data
    
    // 直接从数据库获取用户创建时间来计算活跃天数
    if (res.data && res.data.date_joined) {
      console.log('使用数据库中的用户创建时间计算活跃天数')
      daysSinceJoin.value = calculateDaysSinceJoin(res.data.date_joined)
    } else {
      // 如果API没有返回date_joined字段，使用备用方法
      console.log('API未返回用户创建时间，使用备用方法')
      await calculateDaysSinceFirstActivity(token)
    }
  } catch (e) {
    console.error('获取用户数据失败:', e)
    user.value = null
    daysSinceJoin.value = 0
  }
}

// 根据第一次活动记录计算活跃天数
async function calculateDaysSinceFirstActivity(token) {
  try {
    // 尝试获取最早的拜访记录
    const firstVisitRes = await axios.get('/api/visit-shop-list', {
      params: { page: 1, page_size: 1, sort: 'oldest' },
      headers: { Authorization: `Token ${token}` }
    })
    
    if (firstVisitRes.data.data && firstVisitRes.data.data.length > 0) {
      console.log('使用最早的拜访记录计算活跃天数')
      daysSinceJoin.value = calculateDaysSinceJoin(firstVisitRes.data.data[0].visit_time)
    } else {
      // 如果没有拜访记录，尝试获取最早的活动记录
      const activitiesRes = await axios.get('/api/user-recent-activities', {
        params: { limit: 100, sort: 'oldest' },
        headers: { Authorization: `Token ${token}` }
      })
      
      if (activitiesRes.data && activitiesRes.data.length > 0) {
        console.log('使用最早的活动记录计算活跃天数')
        daysSinceJoin.value = calculateDaysSinceJoin(activitiesRes.data[0].time)
      } else {
        // 如果没有任何记录，使用当前日期（今天注册）
        console.log('没有任何记录，使用1天作为活跃天数')
        daysSinceJoin.value = 1
      }
    }
  } catch (e) {
    console.error('计算活跃天数失败:', e)
    // 如果所有尝试都失败，使用1天作为默认值
    daysSinceJoin.value = 1
  }
}

// 获取拜访数据
async function fetchVisitData() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/visit-shop-list', {
      params: { page: 1, page_size: 1 },
      headers: { Authorization: `Token ${token}` }
    })
    visitList.value = res.data.results || []
    visitCount.value = res.data.total || 0
  } catch (e) {
    console.error('获取拜访数据失败:', e)
    visitList.value = []
    visitCount.value = 0
  }
}

// 获取商店数量
async function fetchShopCount() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/data-list', {
      params: { page: 1, page_size: 1 },
      headers: { Authorization: `Token ${token}` }
    })
    shopCount.value = res.data.total || 0
  } catch (e) {
    console.error('获取商店数量失败:', e)
    shopCount.value = 0
  }
}



// 获取最近活动记录 - 从API获取真实数据
async function generateRecentActivities() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/user-recent-activities', {
      params: { limit: 5 },
      headers: { Authorization: `Token ${token}` }
    })
    
    // 处理API返回的活动数据
    if (res.data && Array.isArray(res.data)) {
      const activities = res.data.map(activity => ({
        type: activity.type || 'visit', // 默认为拜访类型
        title: activity.title || '进行了一次活动',
        time: formatDate(new Date(activity.time))
      }))
      
      recentActivities.value = activities
    } else {
      console.warn('API返回的活动数据格式不正确:', res.data)
      recentActivities.value = []
      
      // 尝试从拜访记录生成活动数据
      await generateActivitiesFromVisits()
    }
  } catch (e) {
    console.error('获取活动记录失败:', e)
    recentActivities.value = []
    
    // 尝试从拜访记录生成活动数据
    await generateActivitiesFromVisits()
  }
}

// 从拜访记录生成活动数据
async function generateActivitiesFromVisits() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/visit-shop-list', {
      params: { page: 1, page_size: 5 },
      headers: { Authorization: `Token ${token}` }
    })
    
    if (res.data && res.data.data && Array.isArray(res.data.data)) {
      const activities = res.data.data.map(visit => ({
        type: 'visit',
        title: `拜访了商店 ${visit.shop__name || '未知商店'}`,
        time: formatDate(new Date(visit.visit_time))
      }))
      
      recentActivities.value = activities
    }
  } catch (e) {
    console.error('从拜访记录生成活动数据失败:', e)
  }
}

// 格式化日期
function formatDate(date) {
  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)
  
  if (diffDay > 0) {
    return `${diffDay}天前`
  } else if (diffHour > 0) {
    return `${diffHour}小时前`
  } else if (diffMin > 0) {
    return `${diffMin}分钟前`
  } else {
    return '刚刚'
  }
}

async function loginOut() {
  try {
    const token = localStorage.getItem('token')
    await axios.post('/api/logout', {}, {
      headers: { Authorization: `Token ${token}` }
    })
  } catch (e) {
    console.error('登出失败:', e)
  } finally {
    localStorage.removeItem('token')
    router.push('/login')  // 使用路由跳转而非直接更改 location
  }
}

function handleFileChange(e) {
  excelFile.value = e.target.files[0]
}

async function uploadExcel() {
  if (!excelFile.value || isUploading.value) return
  
  isUploading.value = true
  const formData = new FormData()
  formData.append('file', excelFile.value)
  
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('/api/import-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Token ${token}`
      }
    })
    uploadMsg.value = '数据上传成功！'
    successDialogMsg.value = '数据上传成功！'
    showSuccessDialog.value = true
    
    // 更新活动记录
    await addActivity('upload', '上传了Excel数据文件')
    
    // 更新商店数量
    await fetchShopCount() // 重新获取商店数量，因为Excel导入可能增加了商店
    
    // 刷新活动记录
    await generateRecentActivities()
  } catch (e) {
    // 如果有Element Plus:
    // ElMessage.error('数据上传失败！')
    errorDialogMsg.value = '数据上传失败！'
    showErrorDialog.value = true
    uploadMsg.value = ''
  } finally {
    isUploading.value = false
  }
}

// 添加活动记录函数
async function addActivity(type, title) {
  const now = new Date()
  const newActivity = {
    type,
    title,
    time: formatDate(now)
  }
  
  // 将新活动添加到活动列表的开头
  recentActivities.value.unshift(newActivity)
  
  // 保持活动列表最多显示5条记录
  if (recentActivities.value.length > 5) {
    recentActivities.value = recentActivities.value.slice(0, 5)
  }
  
  // 尝试将活动记录保存到服务器
  try {
    const token = localStorage.getItem('token')
    // 检查是否存在保存活动记录的API
    await axios.post('/api/save-activity', {
      type,
      title,
      time: now.toISOString()
    }, {
      headers: { Authorization: `Token ${token}` }
    })
    console.log('活动记录已保存到服务器')
  } catch (e) {
    // 如果API不存在或请求失败，只在前端显示
    console.warn('保存活动记录到服务器失败:', e)
    // 由于后端API可能只从Visit表获取活动，这里只在前端添加
    // 上传Excel和图片的活动记录会在前端显示，但可能不会保存到数据库
  }
}

function handleImageChange(e) {
  const files = Array.from(e.target.files)
  // 只允许zip/rar或图片，且图片最多10张
  const imgFiles = files.filter(f => f.type.startsWith('image/'))
  const zipFiles = files.filter(f => f.name.endsWith('.zip') || f.name.endsWith('.rar'))
  if (zipFiles.length > 0) {
    imageFiles.value = [zipFiles[0]] // 只允许一个压缩包
  } else if (imgFiles.length > 0) {
    imageFiles.value = imgFiles.slice(0, 10) // 最多10张图片
  } else {
    imageFiles.value = []
  }
}

async function uploadImage() {
  if (!imageFiles.value.length || isUploading.value) return
  
  isUploading.value = true
  const formData = new FormData()
  imageFiles.value.forEach((file, idx) => {
    formData.append('images', file)
  })
  
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('/api/import-images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Token ${token}`
      }
    })
    uploadImgMsg.value = '' // 上传成功后不再显示底部提示
    
    // 更新活动记录
    const isZip = imageFiles.value.some(file => 
      file.name.endsWith('.zip') || file.name.endsWith('.rar')
    )
    
    if (isZip) {
      await addActivity('upload', '上传了压缩包文件')
    } else {
      await addActivity('image', `上传了${imageFiles.value.length}张商店图片`)
    }
    
    successDialogMsg.value = '图片上传成功！'
    showSuccessDialog.value = true
    
    // 刷新活动记录
    await generateRecentActivities()
  } catch (e) {
    // 如果有Element Plus:
    // ElMessage.error('图片上传失败！')
    errorDialogMsg.value = '图片上传失败！'
    showErrorDialog.value = true
    uploadImgMsg.value = ''
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
  box-sizing: border-box;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  gap: 24px;
  padding: 24px 4vw 24px 4vw;
  background: #f5f7fa;
  overflow: auto;
  color: #333;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* 页面头部样式 */
.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.profile-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  flex: 1;
}

/* 内容区域布局 */
.profile-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
}

/* 左侧列样式 */
.profile-left-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 用户信息卡片样式 */
.user-profile-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.user-avatar.skeleton {
  background-color: #e0e0e0;
  animation: pulse 1.5s infinite;
}

.user-info-content {
  flex: 1;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.user-email {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.user-role {
  font-size: 14px;
  color: #3498db;
  font-weight: 500;
}

.skeleton-line {
  height: 14px;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin-bottom: 8px;
  animation: pulse 1.5s infinite;
}

/* 数据统计卡片样式 */
.stats-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #3498db;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
}

/* 活动记录卡片样式 */
.activity-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: white;
}

.activity-icon.visit {
  background-color: #3498db;
}

.activity-icon.upload {
  background-color: #2ecc71;
}

.activity-icon.image {
  background-color: #9b59b6;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: #7f8c8d;
}

.empty-activity {
  text-align: center;
  padding: 16px;
  color: #7f8c8d;
  font-style: italic;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
/* 通用卡片样式 - 已被上面的样式替代 */
/* 右侧列样式 */
.profile-right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 导入卡片样式 */
.import-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.import-section {
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 24px;
}

.import-section:last-child {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.import-section-header {
  margin-bottom: 16px;
}

.import-title {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.import-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-area {
  border: 2px dashed #bdc3c7;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  background-color: rgba(236, 240, 241, 0.5);
}

.upload-area:hover {
  border-color: #3498db;
  background-color: rgba(236, 240, 241, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.upload-area.has-file {
  border-color: #2ecc71;
  background-color: rgba(46, 204, 113, 0.05);
}

.upload-icon {
  font-size: 40px;
  color: #7f8c8d;
  margin-bottom: 16px;
  transition: transform 0.3s ease, color 0.3s ease;
}

.upload-area:hover .upload-icon {
  color: #3498db;
  transform: scale(1.1);
}

.upload-text {
  font-size: 16px;
  color: #7f8c8d;
  transition: color 0.3s ease;
}

.upload-area:hover .upload-text {
  color: #34495e;
}

.file-name {
  color: #2ecc71;
  font-weight: 500;
}

.file-label {
  display: block;
  cursor: pointer;
  color: #3498db;
  font-weight: 500;
  transition: all 0.2s ease;
}

.file-label:hover {
  color: #2980b9;
}

.excel-input {
  display: none;
}

.upload-btn {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  box-shadow: 0 4px 10px rgba(52, 152, 219, 0.2);
}

.upload-btn i {
  margin-right: 8px;
  font-size: 16px;
}

.upload-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
}

.upload-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(52, 152, 219, 0.2);
}

.upload-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
.upload-msg {
  margin-top: 12px;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  display: inline-block;
  animation: fadeIn 0.3s ease;
}

.success-msg {
  background: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
  border: 1px solid rgba(46, 204, 113, 0.3);
}

.img-msg {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.3);
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
/* 文件名显示样式 */
.file-name {
  display: inline-flex;
  align-items: center;
  margin: 10px 0;
  padding: 8px 12px;
  background-color: rgba(52, 152, 219, 0.08);
  border: 1px solid rgba(52, 152, 219, 0.2);
  border-radius: 6px;
  color: #3498db;
  font-size: 14px;
  max-width: 100%;
  overflow: hidden;
  animation: fadeIn 0.3s ease;
}

.file-name i {
  margin-right: 8px;
  font-size: 16px;
}

.file-name span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 对话框样式 */
.error-dialog-mask, .success-dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.error-dialog, .success-dialog {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 25px 70px rgba(0,0,0,0.15);
  padding: 36px;
  min-width: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: slideUp 0.3s ease-out;
  transform: translateY(0);
  transition: transform 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(40px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.error-dialog {
  border-top: 6px solid #e74c3c;
}

.success-dialog {
  border-top: 6px solid #2ecc71;
}

.error-dialog-title, .success-dialog-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.error-dialog-title {
  color: #e74c3c;
}

.success-dialog-title {
  color: #2ecc71;
}

.error-dialog-title::before, .success-dialog-title::before {
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  font-size: 26px;
}

.error-dialog-title::before {
  content: '\f057'; /* times-circle */
}

.success-dialog-title::before {
  content: '\f058'; /* check-circle */
}

.error-dialog-msg, .success-dialog-msg {
  color: #2c3e50;
  font-size: 17px;
  margin-bottom: 28px;
  text-align: center;
  line-height: 1.6;
}

.error-dialog-btn, .success-dialog-btn {
  padding: 14px 36px;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 15px rgba(0,0,0,0.15);
  width: 80%;
}

.error-dialog-btn {
  background: #e74c3c;
}

.success-dialog-btn {
  background: #2ecc71;
}

.error-dialog-btn:hover, .success-dialog-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

.error-dialog-btn:hover {
  background: #c0392b;
}

.success-dialog-btn:hover {
  background: #27ae60;
}

.error-dialog-btn:active, .success-dialog-btn:active {
  transform: translateY(0);
  box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}
/* 响应式调整 */
@media (max-width: 576px) {
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .logout-btn {
    position: static;
    margin-top: 8px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .user-profile-card {
    flex-direction: column;
    text-align: center;
  }
  
  .user-avatar {
    margin: 0 auto 16px auto;
  }
}

/* 登出按钮样式 */
.logout-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 24px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.2);
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
}

.logout-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.logout-btn:hover {
  background: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(231, 76, 60, 0.3);
}

.logout-btn:hover::before {
  transform: translateX(100%);
}

.logout-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.2);
}

.logout-btn::after {
  content: '\2192'; /* 右箭头 */
  margin-left: 8px;
  transition: transform 0.3s ease;
}

.logout-btn:hover::after {
  transform: translateX(4px);
}

</style>
