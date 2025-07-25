<template>
  <div class="edit-page">
    <h2>修改页面
      <button
        class="edit-shop-btn"
        :disabled="!selectedShop"
        :class="{active: selectedShop}"
        @click="onEditShopClick"
      >编辑商店</button>
    </h2>
    <table class="visited-table">
      <thead>
        <tr>
          <th>商店名</th>
          <th>国家</th>
          <th>城市</th>
          <th>地址</th>
          <th>电话</th>
          <th>邮箱</th>
          <th>标签</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="shop in pagedVisitedShops" :key="shop.id" :class="{selected: selectedShop && selectedShop.id === shop.id}" @click="selectShop(shop)">
          <td>{{ shop.name }}</td>
          <td>{{ shop.country }}</td>
          <td>{{ shop.city }}</td>
          <td>{{ shop.address }}</td>
          <td>{{ shop.phone }}</td>
          <td>{{ shop.email }}</td>
          <td>{{ shop.tags }}</td>
        </tr>
        <tr v-if="pagedVisitedShops.length === 0">
          <td colspan="7">暂无拜访过的商店</td>
        </tr>
      </tbody>
    </table>
    <!-- 分页控件 -->
    <div class="edit-pagination" style="margin-top:16px;display:flex;align-items:center;gap:16px;justify-content:center;">
      <span>每页</span>
      <select v-model.number="pageSize" @change="onPageSizeChange">
        <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
      </select>
      <span>条</span>
      <button :disabled="page===1" @click="gotoPage(page-1)">上一页</button>
      <span>第</span>
      <input v-model.number="page" style="width:48px;text-align:center;border-radius:6px;border:1.5px solid #b3d6ff;padding:4px 0;" @keyup.enter="gotoPage(page)" />
      <span>/ {{ Math.max(1, Math.ceil(total / pageSize)) }} 页</span>
      <button :disabled="page===Math.max(1, Math.ceil(total / pageSize))" @click="gotoPage(page+1)">下一页</button>
      <span style="margin-left:16px;">共 {{ total }} 条</span>
    </div>
    <!-- 编辑弹窗 -->
    <div v-if="showEditDialog" class="edit-dialog-mask">
      <div class="edit-dialog">
        <div class="edit-dialog-title">编辑商店信息</div>
        <div class="edit-dialog-content">
          <div class="form-row">
            <label>商店名：</label>
            <input v-model="editForm.name" class="beautify-input" />
            <label style="margin-left:18px;">经度：</label>
            <input v-model="editForm.lon" type="number" step="any" :disabled="!editLatLng" class="latlng-input beautify-input" />
          </div>
          <div class="form-row">
            <label>国家：</label>
            <input v-model="editForm.country" class="beautify-input" />
            <label style="margin-left:18px;">纬度：</label>
            <input v-model="editForm.lat" type="number" step="any" :disabled="!editLatLng" class="latlng-input beautify-input" />
          </div>
          <div class="form-row"><label>城市：</label><input v-model="editForm.city" class="beautify-input" /></div>
          <div class="form-row"><label>地址：</label><input v-model="editForm.address" class="beautify-input" /></div>
          <div class="form-row"><label>电话：</label><input v-model="editForm.phone" class="beautify-input" /></div>
          <div class="form-row"><label>邮箱：</label><input v-model="editForm.email" class="beautify-input" /></div>
          <div class="form-row"><label>评级：</label>
            <div class="level-radio-group">
              <label v-for="lv in ['A','B','C','D']" :key="lv" class="level-radio">
                <input type="radio" v-model="editForm.level" :value="lv" />
                <span>{{ lv }}</span>
              </label>
            </div>
          </div>
          <div class="form-row"><label>标签：</label><input v-model="editForm.tags" class="beautify-input" /></div>
          <div class="form-row"><label>图片：</label>
            <label class="file-label">
              <input type="file" accept="image/*" @change="onFileChange" class="file-input" />
              <span class="file-btn">选择图片文件</span>
            </label>
            <span v-if="fileName" class="file-name">已选：{{ fileName }}</span>
          </div>
          <div class="form-row latlng-checkbox-row">
            <label style="margin-left:auto;"><input type="checkbox" v-model="editLatLng" /> 允许修改经纬度</label>
          </div>
        </div>
        <div class="edit-dialog-actions">
          <button class="edit-dialog-btn confirm" @click="updateShop">保存</button>
          <button class="edit-dialog-btn cancel" @click="showEditDialog = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const visitedShops = ref([])
const selectedShop = ref(null)
const editForm = ref({})
const showEditDialog = ref(false)
const file = ref(null)
const fileName = ref('')
const editLatLng = ref(false)
// 分页相关
const page = ref(1)
const pageSize = ref(10)
const pageSizes = [5, 10, 20, 50, 100]
const total = ref(0)
const pagedVisitedShops = ref([])

function updatePagedVisitedShops() {
  total.value = visitedShops.value.length
  const start = (page.value - 1) * pageSize.value
  pagedVisitedShops.value = visitedShops.value.slice(start, start + pageSize.value)
}

async function fetchVisitedShops() {
  const token = localStorage.getItem('token')
  const res = await axios.get('/api/user-visited-shops', { headers: { Authorization: `Token ${token}` } })
  visitedShops.value = res.data
  updatePagedVisitedShops()
}
function gotoPage(n) {
  if (n < 1) n = 1
  const totalPages = Math.max(1, Math.ceil(total.value / pageSize.value))
  if (n > totalPages) n = totalPages
  page.value = n
  updatePagedVisitedShops()
}
function onPageSizeChange() {
  page.value = 1
  updatePagedVisitedShops()
}
function selectShop(shop) {
  selectedShop.value = shop
  editForm.value = { ...shop }
}
function onEditShopClick() {
  if (!selectedShop.value) return
  editForm.value = { ...selectedShop.value }
  file.value = null
  fileName.value = ''
  editLatLng.value = false
  showEditDialog.value = true
}
function onFileChange(e) {
  const f = e.target.files[0]
  if (f) {
    file.value = f
    fileName.value = f.name
  }
}
async function updateShop() {
  const token = localStorage.getItem('token')
  const formData = new FormData()
  formData.append('shop_id', selectedShop.value.id)
  for (const k of ['name','country','city','address','phone','email','tags']) {
    formData.append(k, editForm.value[k] || '')
  }
  if (file.value) formData.append('image', file.value)
  if (editLatLng.value) {
    formData.append('lat', editForm.value.lat)
    formData.append('lon', editForm.value.lon)
  }
  await axios.post('/api/update-shop', formData, { headers: { Authorization: `Token ${token}` } })
  await fetchVisitedShops()
  showEditDialog.value = false
  // 保持选中行高亮
  const updated = visitedShops.value.find(s => s.id === selectedShop.value.id)
  if (updated) selectShop(updated)
}
onMounted(() => {
  fetchVisitedShops()
})
</script>

<style scoped>
.edit-page {
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.10);
  min-height: 300px;
  font-size: 1.2rem;
  color: #222;
  position: relative;
}
.edit-shop-btn {
  position: absolute;
  top: 32px;
  right: 40px;
  padding: 8px 28px;
  border: none;
  border-radius: 8px;
  font-size: 1.08rem;
  font-weight: 600;
  background: #ccc;
  color: #fff;
  cursor: not-allowed;
  transition: background 0.2s;
}
.edit-shop-btn.active {
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  cursor: pointer;
}
.edit-shop-btn:disabled {
  background: #ccc !important;
  color: #fff !important;
  cursor: not-allowed !important;
}
.visited-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 32px;
}
.visited-table th, .visited-table td {
  border: 1px solid #e0eaff;
  padding: 10px 14px;
  text-align: center;
  font-size: 1.08rem;
}
.visited-table th {
  background: #f7faff;
  color: #1765d8;
  font-weight: 700;
}
.visited-table tr.selected {
  background: #eaf4ff;
}
.edit-dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.edit-dialog {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 12px 48px rgba(22,120,255,0.18);
  padding: 38px 44px 28px 44px;
  min-width: 380px;
  max-width: 96vw;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  animation: popIn 0.2s;
}
@keyframes popIn {
  from { transform: scale(0.95); opacity: 0.7; }
  to { transform: scale(1); opacity: 1; }
}
.edit-dialog-title {
  font-size: 1.32rem;
  color: #1765d8;
  font-weight: 800;
  margin-bottom: 18px;
  letter-spacing: 1px;
}
.edit-dialog-content {
  width: 100%;
  margin-bottom: 18px;
  font-size: 1.16rem;
}
.edit-dialog-content .form-row {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  font-size: 1.08rem;
  gap: 10px;
}
.edit-dialog-content .form-row label {
  color: #888;
  font-weight: 600;
  min-width: 70px;
  display: inline-block;
  font-size: 1.08rem;
}
.edit-dialog-content .form-row input[type="text"],
.edit-dialog-content .form-row input[type="number"] {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  background: #f7faff;
  transition: border 0.2s;
}
.edit-dialog-content .form-row input[type="text"]:focus,
.edit-dialog-content .form-row input[type="number"]:focus {
  border: 1.5px solid #1677ff;
  outline: none;
}
.beautify-input {
  background: linear-gradient(90deg, #f7faff 60%, #eaf4ff 100%);
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  padding: 8px 12px;
  transition: border 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(88,166,255,0.06);
}
.beautify-input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 0 0 2px #b3d6ff44;
}
.latlng-input:disabled {
  background: #f0f4fa !important;
  color: #aaa !important;
  cursor: not-allowed !important;
}
.edit-dialog-actions {
  display: flex;
  gap: 18px;
  margin-top: 12px;
  justify-content: center;
}
.edit-dialog-btn {
  padding: 8px 32px;
  border: none;
  border-radius: 8px;
  font-size: 1.08rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
}
.edit-dialog-btn.confirm {
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
}
.edit-dialog-btn.cancel {
  background: #ccc;
  color: #fff;
}
.file-name {
  color: #1765d8;
  font-size: 1.02rem;
  margin-left: 6px;
}
.file-label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 12px;
}
.file-input {
  display: none;
}
.file-btn {
  display: inline-block;
  padding: 10px 28px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border-radius: 10px;
  font-size: 1.08rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
  margin-right: 12px;
  border: none;
  outline: none;
}
.file-btn:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
  box-shadow: 0 4px 16px rgba(88,166,255,0.18);
}
.latlng-checkbox-row {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 18px;
  margin-top: -10px;
}
.edit-pagination {
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
.edit-pagination select, .edit-pagination input {
  border-radius: 8px;
  border: 1.5px solid #b3d6ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 7px 18px;
  margin: 0 2px;
  transition: background 0.2s, box-shadow 0.2s;
}
.edit-pagination select:focus, .edit-pagination input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 0 0 2px #b3d6ff44;
}
.edit-pagination button {
  border-radius: 8px;
  border: 1.5px solid #b3d6ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 7px 18px;
  margin: 0 2px;
  transition: background 0.2s, box-shadow 0.2s;
}
.edit-pagination button:disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
}
.edit-pagination button:not(:disabled):hover {
  background: #1677ff;
  color: #fff;
}
.level-radio-group {
  display: flex;
  gap: 8px;
  align-items: center;
}
.level-radio {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 1.08rem;
  color: #1765d8;
  font-weight: 600;
}
.level-radio input[type="radio"] {
  accent-color: #1677ff;
  width: 18px;
  height: 18px;
  margin-right: 2px;
}
</style>
