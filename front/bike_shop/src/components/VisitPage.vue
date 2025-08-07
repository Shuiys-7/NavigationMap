<template>
  <div class="visit-page-card">
    <div class="visit-toolbar">
      <div class="visit-toolbar-title">拜访记录</div>
      <div class="toolbar-btns">
        <button class="add-visit-btn" @click="showDialog = true">添加拜访</button>
        <button
          class="delete-visit-btn"
          :disabled="!selectedVisit"
          :class="{active: selectedVisit}"
          @click="onDeleteClick"
        >删除拜访</button>
      </div>
    </div>
    <div class="visit-table-wrapper">
      <table class="visit-table">
        <thead>
          <tr>
            <th>拜访ID</th>
            <th>拜访对象</th>
            <th>时间</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
        <tr v-for="item in visitList" :key="item.id" :class="{selected: selectedVisit && selectedVisit.id === item.id}" @click="selectVisit(item)">
          <td>{{ item.id }}</td>
          <td>{{ item.shop__name }}</td>
          <td>{{ formatDateTime(item.visit_time) }}</td>
          <td>{{ item.notes }}</td>
        </tr>
          <tr v-if="visitList.length === 0">
            <td colspan="4">暂无拜访记录</td>
          </tr>
        </tbody>
      </table>
      <!-- 分页控件 -->
      <div class="visit-pagination" style="margin-top:16px;display:flex;align-items:center;gap:16px;justify-content:center;">
        <span>每页</span>
        <select v-model.number="pageSize" @change="onPageSizeChange">
          <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
        </select>
        <span>条</span>
        <button :disabled="page===1" @click="gotoPage(page-1)">上一页</button>
        <span>第</span>
        <input v-model.number="page" class="page-input" @keyup.enter="gotoPage(page)" />
        <span>/ {{ Math.max(1, Math.ceil(total / pageSize)) }} 页</span>
        <button :disabled="page===Math.max(1, Math.ceil(total / pageSize))" @click="gotoPage(page+1)">下一页</button>
        <span style="margin-left:16px;">共 {{ total }} 条</span>
      </div>
    </div>
    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteDialog" class="delete-dialog-mask">
      <div class="delete-dialog">
        <div class="delete-dialog-title">确认删除</div>
        <div class="delete-dialog-msg">确定要删除该拜访记录吗？</div>
        <div class="delete-dialog-actions">
          <button class="delete-dialog-btn confirm" @click="confirmDelete">确认</button>
          <button class="delete-dialog-btn cancel" @click="showDeleteDialog = false">取消</button>
        </div>
      </div>
    </div>
    <!-- 添加拜访弹窗 -->
    <div v-if="showDialog" class="detail-dialog-mask" @mousedown.self="closeDropdown">
      <div class="detail-dialog">
        <button class="detail-dialog-close" @click="closeDialog">×</button>
        <div class="detail-dialog-title">新建拜访</div>
        <div class="detail-dialog-flex">
          <div class="detail-dialog-content">
            <div class="detail-row">
              <span class="detail-label">用户名：</span>
              <span class="detail-value"><input :value="user?.username || ''" disabled class="dialog-input disabled" /></span>
            </div>
            <div class="detail-row">
              <span class="detail-label">拜访商店：</span>
              <span class="detail-value shop-input-wrap">
                <input v-model="shopInput" @input="onShopInput" @focus="shopDropdownVisible = true" placeholder="输入商店名搜索" autocomplete="off" class="dialog-input" />
                <ul v-if="shopDropdownVisible && filteredShops.length" class="dropdown-list">
                  <li v-for="shop in filteredShops" :key="shop.id" @click="selectShop(shop)">{{ shop.name }}</li>
                </ul>
              </span>
            </div>
<!--            <div class="detail-row upload-row">-->
<!--              <span class="detail-label">上传照片：</span>-->
<!--                  <span class="detail-value">-->
<!--                  <label class="file-label">-->
<!--                   <input type="file" accept="image/*" @change="onFileChange" class="dialog-input-file" />-->
<!--                     选择文件-->
<!--                    </label>-->
<!--                <span v-if="fileName" class="file-name" style="display:block;margin-top:6px;">已选：{{ fileName }}</span>-->
<!--                 </span>-->
<!--            </div>-->
            <div class="detail-row">
              <span class="detail-label">备注：</span>
              <span class="detail-value">
                <input v-model="noteInput" placeholder="请输入备注" class="dialog-input" />
              </span>
            </div>
          </div>
        </div>
        <div class="form-actions">
          <button class="detail-dialog-btn" @click="submitVisit" :disabled="!selectedShop || !file">提交</button>
          <button class="detail-dialog-btn" @click="closeDialog">取消</button>
        </div>
        <div v-if="dialogMsg" class="dialog-msg">{{ dialogMsg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

function formatDateTime(val) {
  if (!val) return ''
  // 兼容 ISO 字符串和 Date 对象
  const d = typeof val === 'string' ? new Date(val) : val
  if (isNaN(d.getTime())) return ''
  const pad = n => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const user = ref(null)
const visitList = ref([])
const shopList = ref([])
const shopInput = ref('')
const filteredShops = ref([])
const selectedShop = ref(null)
const shopDropdownVisible = ref(false)
const file = ref(null)
const fileName = ref('')
const showDialog = ref(false)
const dialogMsg = ref('')
const noteInput = ref('') // 新增备注输入
const selectedVisit = ref(null)
const showDeleteDialog = ref(false)

// 分页相关
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const pageSizes = [5, 10, 20, 50, 100]

async function fetchVisitList() {
  const token = localStorage.getItem('token')
  try {
    const res = await axios.get('/api/visit-shop-list', {
      params: { page: page.value, page_size: pageSize.value },
      headers: { Authorization: `Token ${token}` }
    })
    visitList.value = Array.isArray(res.data.data) ? res.data.data : []
    total.value = res.data.total || 0
  } catch {
    visitList.value = []
    total.value = 0
  }
}

function gotoPage(n) {
  if (n < 1) n = 1
  const totalPages = Math.max(1, Math.ceil(total.value / pageSize.value))
  if (n > totalPages) n = totalPages
  page.value = n
  fetchVisitList()
}
function onPageSizeChange() {
  page.value = 1
  fetchVisitList()
}

// 获取用户、拜访、商店列表
onMounted(async () => {
  const token = localStorage.getItem('token')
  // 用户
  try {
    const res = await axios.get('/api/user-data', { headers: { Authorization: `Token ${token}` } })
    user.value = res.data
  } catch {}
  // 拜访
  try {
    const res = await axios.get('/api/visit-shop-list', { headers: { Authorization: `Token ${token}` } })
    visitList.value = Array.isArray(res.data.data) ? res.data.data : []
  } catch {}
  // 商店
  try {
    const res = await axios.get('/api/data-list', { params: { page: 1, page_size: 10000 }, headers: { Authorization: `Token ${token}` } })
    shopList.value = Array.isArray(res.data.data) ? res.data.data : []
  } catch {}
  fetchVisitList() // 初始化拜访列表
})

function onShopInput() {
  const kw = shopInput.value.trim().toLowerCase()
  if (!kw || kw.length < 1) {
    shopDropdownVisible.value = false
    filteredShops.value = []
    return
  }
  shopDropdownVisible.value = true
  filteredShops.value = shopList.value.filter(s => {
    if (!s.name) return false
    // 前缀匹配，忽略大小写
    return s.name.toLowerCase().startsWith(kw)
  })
}
function selectShop(shop) {
  selectedShop.value = shop
  shopInput.value = shop.name
  shopDropdownVisible.value = false
}
function onFileChange(e) {
  const f = e.target.files[0]
  if (f) {
    file.value = f
    fileName.value = f.name
  }
}
function closeDialog() {
  showDialog.value = false
  shopInput.value = ''
  selectedShop.value = null
  file.value = null
  fileName.value = ''
  dialogMsg.value = ''
  noteInput.value = '' // 清空备注
}
function closeDropdown() {
  shopDropdownVisible.value = false;
}
async function submitVisit() {
  if (!selectedShop.value || !file.value) return
  dialogMsg.value = '正在提交...'
  const token = localStorage.getItem('token')
  // 1. 上传图片，重命名为数据库图片名
  let uploadOk = false
  let newImgName = selectedShop.value.image ? selectedShop.value.image.split('/').pop() : file.value.name
  const renamedFile = new File([file.value], newImgName, { type: file.value.type })
  const formData = new FormData()
  formData.append('images', renamedFile)
  try {
    await axios.post('/api/import-images', formData, { headers: { 'Content-Type': 'multipart/form-data', Authorization: `Token ${token}` } })
    uploadOk = true
  } catch {
    dialogMsg.value = '图片上传失败'; return
  }
  // 2. 添加拜访记录
  try {
    await axios.post('/api/add-visit', {
      shop_id: selectedShop.value.id,
      shop_name: selectedShop.value.name,
      image: newImgName,
      notes: noteInput.value // 新增备注
    }, { headers: { Authorization: `Token ${token}` } })
    dialogMsg.value = '拜访添加成功！'
    setTimeout(() => { closeDialog(); window.location.reload() }, 1200)
  } catch {
    dialogMsg.value = '拜访记录添加失败'
  }
}

function selectVisit(item) {
  if (selectedVisit.value && selectedVisit.value.id === item.id) {
    selectedVisit.value = null
  } else {
    selectedVisit.value = item
  }
}

async function deleteVisit() {
  if (!selectedVisit.value) return
  // if (!confirm('确定要删除该拜访记录吗？')) return
  const token = localStorage.getItem('token')
  try {
    await axios.post('/api/delete-visit', { visit_id: selectedVisit.value.id }, { headers: { Authorization: `Token ${token}` } })
    selectedVisit.value = null
    fetchVisitList()
  } catch {
    alert('删除失败')
  }
}
function onDeleteClick() {
  if (!selectedVisit.value) return
  showDeleteDialog.value = true
}
async function confirmDelete() {
  showDeleteDialog.value = false
  await deleteVisit()
}
</script>

<style scoped>
.visit-page-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.10);
  padding: 36px 28px 28px 28px;
  font-size: 1.1rem;
  color: #222;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 18px;
  width: 100%;
  max-width: 100%;
  margin: 0;
  min-height: 100vh;
  height: 100vh;
  box-sizing: border-box;
}
.visit-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 0;
}
.toolbar-btns {
  display: flex;
  gap: 8px;
  margin-left: 0;
}
.visit-toolbar-title {
  font-size: 1.32rem;
  color: #1765d8;
  font-weight: 700;
  letter-spacing: 1px;
}
.add-visit-btn {
  padding: 10px 28px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1.08rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
  margin-left: 0 !important;
}
.add-visit-btn:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
}
.visit-table-wrapper {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  width: 100%;
  overflow-x: auto;
  min-height: 0;
}
.visit-table {
  width: 100%;
  max-width: 100%;
  height: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 0;
  overflow: visible;
  box-shadow: none;
  table-layout: auto;
  min-width: max-content;
  flex: 1 1 0;
}
.visit-table th, .visit-table td {
  padding: 14px 16px;
  text-align: center;
  font-size: 1.08rem;
  transition: background 0.2s;
  white-space: nowrap;
  height: 48px;
  line-height: 48px;
}
.visit-table th {
  background: linear-gradient(90deg, #eaf4ff 60%, #f7faff 100%);
  color: #1765d8;
  font-weight: 700;
  border-bottom: 2px solid #e0eaff;
  letter-spacing: 1px;
  white-space: nowrap;
  text-align: center;
}
.visit-table td {
  color: #222;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
  text-align: center;
}
.detail-dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.detail-dialog {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 12px 48px rgba(22,120,255,0.18);
  padding: 38px 44px 28px 44px;
  min-width: 420px;
  max-width: 96vw;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  animation: popIn 0.2s;
}
@keyframes popIn {
  from { transform: scale(0.95); opacity: 0.7; }
  to { transform: scale(1); opacity: 1; }
}
.detail-dialog-title {
  font-size: 1.32rem;
  color: #1765d8;
  font-weight: 800;
  margin-bottom: 18px;
  letter-spacing: 1px;
}
.detail-dialog-flex {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 100%;
  gap: 36px;
}
.detail-dialog-content {
  width: 0;
  flex: 1 1 0;
  margin-bottom: 18px;
  font-size: 1.16rem;
}
.detail-row {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  font-size: 1.08rem;
  gap: 10px;
}
.detail-row.upload-row {
  margin-top: 18px;
  margin-bottom: 18px;
}
.detail-label {
  color: #888;
  font-weight: 600;
  min-width: 90px;
  display: inline-block;
  font-size: 1.08rem;
}
.detail-value {
  color: #222;
  font-weight: 600;
  word-break: break-all;
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}
.shop-input-wrap {
  position: relative;
  display: inline-block;
  width: 100%;
}
.shop-input-wrap input[type="text"] {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  background: #f7faff;
  transition: border 0.2s;
}
.shop-input-wrap input[type="text"]:focus {
  border: 1.5px solid #1677ff;
  outline: none;
}
.dropdown-list {
  position: absolute;
  left: 0;
  top: 100%;
  background: #fff;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(88,166,255,0.13);
  margin-top: 2px;
  z-index: 100;
  min-width: 220px;
  max-width: 400px;
  max-height: 180px;
  overflow-y: auto;
  list-style: none;
  padding: 0;
}
.dropdown-list li {
  padding: 10px 18px;
  cursor: pointer;
  font-size: 1.08rem;
  transition: background 0.18s;
}
.dropdown-list li:hover {
  background: #eaf4ff;
}
.form-actions {
  display: flex;
  gap: 24px;
  margin-top: 8px;
}
.detail-dialog-btn {
  padding: 7px 28px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1.08rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.12);
  transition: background 0.2s, box-shadow 0.2s;
  align-self: center;
  margin-top: 8px;
}
.detail-dialog-btn:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
}
.detail-dialog-close {
  position: absolute;
  top: 18px;
  right: 22px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(90deg, #f7faff 60%, #eaf4ff 100%);
  border: 1.5px solid #b3d6ff;
  color: #1677ff;
  font-size: 1.8rem;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: background 0.2s, color 0.2s;
}
.detail-dialog-close:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
  color: #fff;
}
.dialog-msg {
  color: #e67e22;
  margin-top: 10px;
  font-size: 1.08rem;
  font-weight: 600;
}
.detail-value {
  color: #222;
  font-weight: 600;
  word-break: break-all;
  flex: 1;
  /* display: flex; */
  /* align-items: center; */
  display: block;
  position: relative;
}
.dialog-input {
  width: 100%;
  padding: 10px 16px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  background: #f7faff;
  transition: border 0.2s;
  margin-right: 8px;
}
.dialog-input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
}
.dialog-input.disabled {
  background: #f0f4fa;
  color: #aaa;
}
.dialog-input-file {
  display: none;
}
.file-label {
  display: inline-block;
  padding: 8px 22px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border-radius: 8px;
  font-size: 1.08rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
  margin-right: 12px;
}
.file-label:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
}
.file-name {
  color: #1765d8;
  font-size: 1.02rem;
  display: block;
  margin-top: 8px;
}
.selected {
  background: #eaf4ff !important;
}
.delete-visit-btn {
  padding: 10px 28px;
  border: none;
  border-radius: 8px;
  font-size: 1.08rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
  margin-left: 0;
  background: #ccc;
  color: #fff;
  cursor: not-allowed;
}
.delete-visit-btn.active {
  background: #e74c3c;
  color: #fff;
  cursor: pointer;
}
.delete-visit-btn:disabled {
  background: #ccc !important;
  color: #fff !important;
  cursor: not-allowed !important;
}
.delete-dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.delete-dialog {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  padding: 32px 36px 24px 36px;
  min-width: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.delete-dialog-title {
  font-size: 1.18rem;
  color: #e74c3c;
  font-weight: 700;
  margin-bottom: 12px;
}
.delete-dialog-msg {
  color: #333;
  font-size: 1rem;
  margin-bottom: 18px;
}
.delete-dialog-actions {
  display: flex;
  gap: 18px;
}
.delete-dialog-btn {
  padding: 7px 28px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.12);
  transition: background 0.2s, box-shadow 0.2s;
}
.delete-dialog-btn.confirm {
  background: #e74c3c;
  color: #fff;
}
.delete-dialog-btn.cancel {
  background: #ccc;
  color: #fff;
}
.visit-pagination {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: center;
  background: #f7faff;
  border-radius: 10px;
  padding: 12px 0;
  box-shadow: 0 2px 8px rgba(88,166,255,0.06);
}
.visit-pagination select, .visit-pagination input {
  border-radius: 8px;
  border: 1.5px solid #b3d6ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 7px 18px;
  margin: 0 2px;
  transition: background 0.2s, box-shadow 0.2s;
}
.visit-pagination select:focus, .visit-pagination input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 0 0 2px #b3d6ff44;
}
.visit-pagination button {
  border-radius: 8px;
  border: 1.5px solid #b3d6ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 7px 18px;
  margin: 0 2px;
  transition: background 0.2s, box-shadow 0.2s;
}
.visit-pagination button:disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
}
.visit-pagination button:not(:disabled):hover {
  background: #1677ff;
  color: #fff;
}
@media (max-width: 800px) {
  .visit-page-card {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(88,166,255,0.10);
    padding: 36px 28px 28px 28px;
    font-size: 1.1rem;
    color: #222;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 18px;
    width: 100%;
    max-width: 100%;
    margin: 0;
    height: 100dvh;
    box-sizing: border-box;
  }
  .visit-pagination {
    flex-wrap: wrap;
    gap: 10px;
    font-size: 0.95rem;
    justify-content: center;
    text-align: center;
  }
  .visit-pagination button,
  .visit-pagination input{
    font-size: 0.95rem;
    padding: 6px 10px;
  }
  .visit-pagination input[type="number"] {
    width: 60px;
  }
  .visit-pagination select{
    font-size: 0.95rem;
    padding: 6px 10px;
    width: 70px;
  }
  .page-input{
    width: 50px;
  }
}
</style>

