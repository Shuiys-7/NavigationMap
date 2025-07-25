<!-- 我的页面组件 -->
<template>
  <div class="profile-page">
    <div class="user-info-card flex1">
      <div class="user-info-content">
        <h2>当前用户信息</h2>
        <button @click="loginOut" class="logout-btn">登出</button>
        <div v-if="user">
          <div class="user-row"><span class="user-label">用户名：</span><span>{{ user.username }}</span></div>
          <div class="user-row"><span class="user-label">邮箱：</span><span>{{ user.email }}</span></div>
        </div>
        <div v-else class="user-loading">正在加载用户信息...</div>
      </div>
    </div>

<!--    <div class="visit-list-card flex2">-->
<!--      <h2>拜访列表</h2>-->
<!--      <table class="visit-table">-->
<!--        <thead>-->
<!--          <tr>-->
<!--            <th>拜访ID</th>-->
<!--            <th>拜访对象</th>-->
<!--            <th>时间</th>-->
<!--            <th>备注</th>-->
<!--          </tr>-->
<!--        </thead>-->
<!--        <tbody>-->
<!--          <tr v-for="item in visitList" :key="item.id">-->
<!--            <td>{{ item.id }}</td>-->
<!--            <td>{{ item.target }}</td>-->
<!--            <td>{{ item.time }}</td>-->
<!--            <td>{{ item.note }}</td>-->
<!--          </tr>-->
<!--          <tr v-if="visitList.length === 0">-->
<!--            <td colspan="4">暂无拜访记录</td>-->
<!--          </tr>-->
<!--        </tbody>-->
<!--      </table>-->
<!--    </div>-->

    <div class="import-card flex1">
      <h2>数据导入</h2>
      <div class="import-row import-row-parallel">
        <div class="import-block">
          <label class="file-label">
            <input type="file" accept=".xlsx,.xls,.csv" @change="handleFileChange" class="excel-input" />
            <span class="file-btn">选择数据文件</span>
          </label>
          <div class="upload-row">
            <button @click="uploadExcel" :disabled="!excelFile" class="upload-btn">上传数据</button>
            <span v-if="excelFile" class="file-name file-name-inline">{{ excelFile.name }}</span>
          </div>
          <transition name="fade">
            <div v-if="uploadMsg" class="upload-msg success-msg">{{ uploadMsg }}</div>
          </transition>
        </div>
        <div class="import-block import-block-img">
          <label class="file-label">
            <input type="file" accept="image/*,.zip,.rar" @change="handleImageChange" class="excel-input" :multiple="true" />
            <span class="file-btn">选择图片/压缩包</span>
          </label>
          <div class="img-upload-row">
            <button @click="uploadImage" :disabled="!imageFiles.length" class="upload-btn">上传图片</button>
            <span v-if="imageFiles.length" class="file-name">已选{{ imageFiles.length }}项</span>
          </div>
          <transition name="fade">
            <div v-if="uploadImgMsg" class="upload-msg img-msg">{{ uploadImgMsg }}</div>
          </transition>
        </div>
      </div>
    </div>
    <div v-if="showErrorDialog" class="error-dialog-mask">
      <div class="error-dialog">
        <div class="error-dialog-title">上传失败</div>
        <div class="error-dialog-msg">{{ errorDialogMsg }}</div>
        <button class="error-dialog-btn" @click="showErrorDialog = false">关闭</button>
      </div>
    </div>
    <div v-if="showSuccessDialog" class="error-dialog-mask">
      <div class="error-dialog">
        <div class="error-dialog-title" style="color:#3fb950">上传成功</div>
        <div class="error-dialog-msg">{{ successDialogMsg }}</div>
        <button class="error-dialog-btn" @click="showSuccessDialog = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
// 如果项目已用Element Plus，解开下行注释
// import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
const router = useRouter()

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

// 获取当前用户信息和拜访列表
onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/user-data', {
      headers: { Authorization: `Token ${token}` }
    })
    user.value = res.data
  } catch (e) {
    user.value = null
  }
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/visit-list', {
      headers: { Authorization: `Token ${token}` }
    })
    visitList.value = res.data
  } catch (e) {
    visitList.value = []
  }
})

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
  if (!excelFile.value) return
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
  } catch (e) {
    // 如果有Element Plus:
    // ElMessage.error('数据上传失败！')
    errorDialogMsg.value = '数据上传失败！'
    showErrorDialog.value = true
    uploadMsg.value = ''
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
  if (!imageFiles.value.length) return
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
    successDialogMsg.value = '图片上传成功！'
    showSuccessDialog.value = true
  } catch (e) {
    // 如果有Element Plus:
    // ElMessage.error('图片上传失败！')
    errorDialogMsg.value = '图片上传失败！'
    showErrorDialog.value = true
    uploadImgMsg.value = ''
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
}
.user-info-card, .visit-list-card, .import-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.08);
  padding: 24px 32px;
  min-height: 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  border: none;
}
.user-info-card {
  flex-direction: column;
  align-items: flex-start;
  gap: 0;
}
.user-info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.user-info-card h2 {
  margin: 0 0 14px 0;
  font-size: 1.32rem;
  color: #1765d8;
  font-weight: 700;
  letter-spacing: 1px;
}
.user-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.08rem;
  margin-bottom: 4px;
}
.user-label {
  color: #888;
  font-weight: 500;
}
.user-loading {
  color: #aaa;
  font-size: 1rem;
}
.visit-list-card {
  flex-direction: column;
}
.visit-list-card h2, .import-card h2 {
  margin-top: 0;
  margin-bottom: 4px;
  font-size: 1.32rem;
  color: #1765d8;
  font-weight: 700;
  letter-spacing: 1px;
}
.visit-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}
.visit-table th, .visit-table td {
  border: 1px solid #f0f0f0;
  padding: 8px 12px;
  text-align: center;
  color: #333;
}
.visit-table th {
  background: #f7faff;
  color: #1765d8;
  font-weight: 600;
  font-size: 1.05rem;
}
.import-card {
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
  background: #fff;
  border: none;
}
.import-row {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  width: 100%;
  margin-bottom: 0;
}
.import-row-parallel {
  flex-direction: row;
  justify-content: flex-start;
}
.import-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  min-width: 220px;
  flex: 1;
  background: none;
}
.import-block-img {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  min-width: 220px;
  background: none;
}
.img-upload-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.file-label {
  position: relative;
  display: inline-block;
}
.excel-input {
  display: none;
}
.file-btn {
  display: inline-block;
  padding: 7px 18px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
  border: none;
}
.file-btn:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
  box-shadow: 0 4px 16px rgba(88,166,255,0.18);
}
.upload-btn {
  flex: none;
  padding: 7px 22px;
  font-size: 1rem;
  border-radius: 6px;
  border: none;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.12);
  transition: background 0.2s, box-shadow 0.2s;
}
.upload-btn:disabled {
  background: #b3d6ff;
  cursor: not-allowed;
}
.upload-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
  box-shadow: 0 4px 16px rgba(88,166,255,0.18);
}
.file-name {
  color: #1677ff;
  font-size: 0.98rem;
  margin-left: 6px;
  font-style: italic;
}
.upload-msg {
  margin-top: 8px;
  font-size: 1rem;
  padding: 8px 18px;
  border-radius: 6px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(88,166,255,0.08);
  display: inline-block;
}
.success-msg {
  background: rgba(63, 185, 80, 0.13);
  color: #3fb950;
  border: 1px solid #3fb95044;
}
.img-msg {
  background: rgba(88, 166, 255, 0.13);
  color: #1677ff;
  border: 1px solid #1677ff44;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.flex1 {
  flex: 1 1 0;
  min-height: 0;
}
.flex2 {
  flex: 2 1 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.error-dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.error-dialog {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  padding: 32px 36px 24px 36px;
  min-width: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.error-dialog-title {
  font-size: 1.18rem;
  color: #e74c3c;
  font-weight: 700;
  margin-bottom: 12px;
}
.error-dialog-msg {
  color: #333;
  font-size: 1rem;
  margin-bottom: 18px;
}
.error-dialog-btn {
  padding: 7px 28px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.12);
  transition: background 0.2s, box-shadow 0.2s;
}
.error-dialog-btn:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
}
.upload-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.file-name-inline {
  color: #1677ff;
  font-size: 0.98rem;
  margin-left: 12px;
  font-style: italic;
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  padding: 8px 24px;
  background: linear-gradient(90deg, #ff4d4f, #ff7875);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.2);
  transition: background 0.25s, box-shadow 0.25s;
  margin-bottom: 16px;
}

.logout-btn:hover {
  background: linear-gradient(90deg, #ff7875, #ff4d4f);
  box-shadow: 0 4px 16px rgba(255, 77, 79, 0.3);
}

</style>
