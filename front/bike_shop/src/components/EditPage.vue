<template>
  <div class="edit-page">
    <div class="edit-header">
      <h2>修改页面</h2>
      <button
        class="edit-shop-btn"
        :disabled="!selectedShop"
        :class="{active: selectedShop}"
        @click="onEditShopClick"
      >编辑商店</button>
    </div>
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
          <td>
            <div class="edit-tags">
              <span v-for="(tag, index) in getTagsArray(shop.tags)" 
                    :key="index"
                    class="edit-tag">
                <i class="fas fa-tag tag-icon-small"></i>
                {{ tag }}
              </span>
              <span v-if="getTagsArray(shop.tags).length === 0" class="no-tags">
                无标签
              </span>
            </div>
          </td>
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
      <input v-model.number="page" class="page-input" @keyup.enter="gotoPage(page)" />
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
          <div class="form-row tag-edit-row">
            <label>标签：</label>
            <div class="tag-edit-container">
              <div class="current-tags">
                <div v-for="(tag, index) in currentTags" :key="index" class="edit-tag editable">
                  <i class="fas fa-tag tag-icon-small"></i>
                  <span>{{ tag }}</span>
                  <i class="fas fa-times remove-tag-icon" @click.stop="removeTag(index)"></i>
                </div>
                <span v-if="currentTags.length === 0" class="no-tags">无标签</span>
              </div>
              <div class="tag-input-container">
                <div class="tag-input-wrapper">
                  <input 
                    ref="tagInputRef"
                    v-model="newTag" 
                    class="tag-input beautify-input" 
                    placeholder="输入或选择标签" 
                    @keyup.enter="addTag"
                    @keyup.delete="handleBackspace"
                    @input="filterTags"
                    @focus="showTagDropdown = true; filterTags()"
                  />
                  <div 
                    v-if="showTagDropdown && filteredTags.length > 0" 
                    ref="tagDropdownRef"
                    class="tag-dropdown"
                  >
                    <div 
                      v-for="tag in filteredTags" 
                      :key="tag.id" 
                      class="tag-dropdown-item"
                      @click="selectTag(tag)"
                    >
                      <i class="fas fa-tag tag-icon-small"></i> {{ tag.name }}
                    </div>
                  </div>
                </div>
                <button class="add-tag-btn" @click="addTag" :disabled="!newTag.trim()">
                  <i class="fas fa-plus"></i> 添加
                </button>
              </div>
            </div>
          </div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const visitedShops = ref([])
const selectedShop = ref(null)
const editForm = ref({})
const showEditDialog = ref(false)
const file = ref(null)
const fileName = ref('')
const editLatLng = ref(false)
// 标签相关
const currentTags = ref([])
const newTag = ref('')
const allTags = ref([])  // 存储所有可用的标签
const showTagDropdown = ref(false)  // 控制标签下拉列表的显示
const filteredTags = ref([])  // 根据输入过滤的标签列表
const tagInputRef = ref(null)  // 标签输入框的引用
const tagDropdownRef = ref(null)  // 标签下拉框的引用
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
  
  // 初始化标签 - 使用getTagsArray函数处理不同格式的标签数据
  currentTags.value = getTagsArray(selectedShop.value.tags)
  newTag.value = ''
  
  // 初始化标签下拉列表
  filterTags()
  
  showEditDialog.value = true
}
function onFileChange(e) {
  const f = e.target.files[0]
  if (f) {
    file.value = f
    fileName.value = f.name
  }
}
// 标签相关函数
function getTagsArray(tags) {
  // 处理不同格式的标签数据
  if (!tags) return []
  if (typeof tags === 'string') {
    return tags.split(',').filter(t => t.trim()).map(t => t.trim())
  }
  if (Array.isArray(tags)) {
    return tags.filter(t => t && (typeof t === 'string' ? t.trim() : t))
  }
  return []
}

async function addTag() {
  const tag = newTag.value.trim()
  if (!tag) return
  
  // 检查是否已存在该标签
  if (!currentTags.value.includes(tag)) {
    // 检查是否需要创建新标签
    let tagExists = allTags.value.some(t => t.name.toLowerCase() === tag.toLowerCase())
    
    if (!tagExists) {
      try {
        // 创建新标签
        const token = localStorage.getItem('token')
        const res = await axios.post('/api/tag_add', { name: tag }, { headers: { Authorization: `Token ${token}` } })
        if (res.data.status === 'success') {
          // 添加到所有标签列表
          allTags.value.push(res.data.tag)
          console.log('创建新标签成功:', res.data.tag)
        }
      } catch (error) {
        console.error('创建标签失败:', error)
      }
    }
    
    // 添加到当前标签列表
    currentTags.value.push(tag)
    // 更新editForm中的tags字段
    editForm.value.tags = currentTags.value.join(',')
  }
  
  newTag.value = ''
  showTagDropdown.value = false
}

function removeTag(index) {
  currentTags.value.splice(index, 1)
  // 更新editForm中的tags字段
  editForm.value.tags = currentTags.value.join(',')
}

function handleBackspace(e) {
  // 当输入框为空且按下退格键时，删除最后一个标签
  if (newTag.value === '' && currentTags.value.length > 0) {
    removeTag(currentTags.value.length - 1)
  }
}

async function updateShop() {
  const token = localStorage.getItem('token')
  const formData = new FormData()
  formData.append('shop_id', selectedShop.value.id)
  
  // 将当前标签数组转换为逗号分隔的字符串
  editForm.value.tags = currentTags.value.join(',')
  
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
// 获取所有标签
async function fetchAllTags() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/tag_list', { headers: { Authorization: `Token ${token}` } })
    allTags.value = res.data.tags || []
    console.log('获取到所有标签:', allTags.value)
  } catch (error) {
    console.error('获取标签失败:', error)
  }
}

// 根据输入过滤标签
function filterTags() {
  const input = newTag.value.toLowerCase().trim()
  if (!input) {
    filteredTags.value = allTags.value
  } else {
    filteredTags.value = allTags.value.filter(tag => 
      tag.name.toLowerCase().includes(input) && !currentTags.value.includes(tag.name)
    )
  }
}

// 选择标签
function selectTag(tag) {
  if (!currentTags.value.includes(tag.name)) {
    currentTags.value.push(tag.name)
    // 更新editForm中的tags字段
    editForm.value.tags = currentTags.value.join(',')
  }
  newTag.value = ''
  showTagDropdown.value = false
}

// 处理点击事件，判断是否点击在下拉框外部
function handleClickOutside(event) {
  // 如果下拉框不显示，不需要处理
  if (!showTagDropdown.value) return
  
  // 检查点击是否在标签输入框或下拉框内
  const isClickInside = (
    (tagInputRef.value && tagInputRef.value.contains(event.target)) ||
    (tagDropdownRef.value && tagDropdownRef.value.contains(event.target))
  )
  
  // 如果点击在外部，关闭下拉框
  if (!isClickInside) {
    showTagDropdown.value = false
  }
}

onMounted(() => {
  fetchVisitedShops()
  fetchAllTags()
  
  // 添加全局点击事件监听器
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // 移除全局点击事件监听器
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.edit-page {
  padding: 30px;
  background: #f8fafd;
  min-height: 100vh;
  font-size: 1.1rem;
  color: #222;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 18px;
  position: relative;
}

/* 标签样式 */
.edit-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  justify-content: flex-start;
  min-height: 24px;
  padding: 2px 0;
}

.edit-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  background: #1677ff;
  color: white;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
  margin-right: 5px;
  margin-bottom: 3px;
  border: 1px solid transparent;
  transition: all 0.3s ease;
}

.edit-tag.editable {
  padding-right: 4px;
  cursor: default;
  box-shadow: 0 2px 4px rgba(22, 119, 255, 0.15);
}

.edit-tag.editable:hover {
  background: #0958d9;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(22, 119, 255, 0.25);
}

.tag-icon-small {
  font-size: 10px;
  margin-right: 3px;
  color: white;
  display: inline-block;
}

.remove-tag-icon {
  font-size: 10px;
  margin-left: 4px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.remove-tag-icon:hover {
  color: white;
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.2);
}

.no-tags {
  color: #999;
  font-style: italic;
  font-size: 12px;
}

/* 标签编辑相关样式 */
.tag-edit-row {
  flex-direction: column;
  align-items: flex-start;
}

.tag-edit-row label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.tag-edit-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.current-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 30px;
  padding: 8px;
  background: #f7faff;
  border-radius: 8px;
  border: 1px dashed #b3d6ff;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.tag-input-container {
  display: flex;
  gap: 10px;
  width: 100%;
}

.tag-input-wrapper {
  position: relative;
  flex: 1;
}

.tag-input {
  flex: 1;
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.tag-input:focus {
  border-color: #1677ff;
  box-shadow: 0 0 0 2px rgba(22, 119, 255, 0.2);
  outline: none;
}

.tag-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 10000;
  margin-top: 4px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.tag-dropdown::-webkit-scrollbar {
  width: 6px;
}

.tag-dropdown::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.tag-dropdown::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.tag-dropdown::-webkit-scrollbar-thumb:hover {
  background: #aaa;
}

.tag-dropdown-item {
  padding: 10px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f0f0f0;
}

.tag-dropdown-item:last-child {
  border-bottom: none;
}

.tag-dropdown-item:hover {
  background: #f0f7ff;
  padding-left: 16px;
}

.add-tag-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.15);
  position: relative;
  overflow: hidden;
}

.add-tag-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  transition: transform 0.6s;
  transform: skewX(-15deg);
}

.add-tag-btn:hover {
  background: linear-gradient(135deg, #0958d9, #003eb3);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(9, 88, 217, 0.3);
}

.add-tag-btn:hover::before {
  transform: skewX(-15deg) translateX(200%);
}

.add-tag-btn:disabled {
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0) !important;
  color: #999 !important;
  cursor: not-allowed !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
  transform: none !important;
}
.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.edit-shop-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
  color: #999;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: not-allowed;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.edit-shop-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  transition: transform 0.6s;
  transform: skewX(-15deg);
}

.edit-shop-btn.active {
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.2);
}

.edit-shop-btn.active:hover {
  background: linear-gradient(135deg, #0958d9, #003eb3);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(9, 88, 217, 0.3);
}

.edit-shop-btn.active:hover::before {
  transform: skewX(-15deg) translateX(200%);
}

.edit-shop-btn:disabled {
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0) !important;
  color: #999 !important;
  cursor: not-allowed !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}
.visited-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  table-layout: auto;
  min-width: max-content;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.visited-table th, .visited-table td {
  padding: 16px 20px;
  text-align: center;
  font-size: 1.08rem;
  transition: background 0.3s ease;
  white-space: nowrap;
  height: 52px;
  line-height: 52px;
}

.visited-table th {
  background: #f8fafd;
  color: #2c3e50;
  font-weight: 700;
  border-bottom: 2px solid #e0eaff;
  letter-spacing: 1.2px;
  white-space: nowrap;
  text-align: center;
  text-transform: uppercase;
  font-size: 0.95rem;
}

.visited-table td {
  color: #2c3e50;
  border-bottom: 1px solid #eef2f7;
  vertical-align: middle;
  text-align: center;
}

.visited-table tr:last-child td {
  border-bottom: none;
}

.visited-table tbody tr:nth-child(odd) {
  background: #f8fafd;
}

.visited-table tbody tr:nth-child(even) {
  background: #ffffff;
}

.visited-table tbody tr:hover {
  background: #f5f9ff !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
  transition: all 0.3s ease;
}

.visited-table tr.selected {
  background: #e0f0ff !important;
  border-left: 4px solid #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.15);
  transition: all 0.3s ease;
}
.edit-dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.edit-dialog {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(22,119,255,0.2);
  padding: 32px 36px;
  min-width: 380px;
  max-width: 90vw;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
}
.edit-dialog-title {
  font-size: 1.5rem;
  color: #1765d8;
  font-weight: 800;
  margin-bottom: 20px;
  letter-spacing: 1px;
  position: relative;
  padding-bottom: 12px;
}

.edit-dialog-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  border-radius: 3px;
}

.edit-dialog-content {
  width: 100%;
  margin-bottom: 18px;
  font-size: 1.16rem;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  max-height: 70vh;
  padding-right: 16px;
  padding-bottom: 10px;
}

.edit-dialog-content::-webkit-scrollbar {
  width: 8px;
}

.edit-dialog-content::-webkit-scrollbar-track {
  background: #f5f9ff;
  border-radius: 10px;
}

.edit-dialog-content::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #58a6ff, #1677ff);
  border-radius: 10px;
  border: 2px solid #f5f9ff;
}

.edit-dialog-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #1677ff, #0056d6);
}
.edit-dialog-content .form-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 12px;
  background: #f8fafd;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
  gap: 10px;
}

.edit-dialog-content .form-row:hover {
  background: #f0f7ff;
}

.edit-dialog-content .form-row label {
  color: #1765d8;
  font-weight: 700;
  min-width: 70px;
  display: inline-block;
  font-size: 1.08rem;
  padding-right: 16px;
  position: relative;
}

.edit-dialog-content .form-row label::after {
  content: ':';
  position: absolute;
  right: 8px;
  color: #58a6ff;
}

.edit-dialog-content .form-row input[type="text"],
.edit-dialog-content .form-row input[type="number"] {
  flex: 1;
  padding: 10px 16px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  background: #f7faff;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
}

.edit-dialog-content .form-row input[type="text"]:focus,
.edit-dialog-content .form-row input[type="number"]:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
}

.beautify-input {
  background: #f7faff;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  padding: 10px 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
}

.beautify-input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
}
.latlng-input:disabled {
  background: #f0f4fa !important;
  color: #aaa !important;
  cursor: not-allowed !important;
}
.edit-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eaedf2;
}

.edit-dialog-btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 1.08rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
}

.edit-dialog-btn.confirm {
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.18);
}

.edit-dialog-btn.confirm:hover {
  background: linear-gradient(90deg, #1677ff, #0056d6);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.25);
}

.edit-dialog-btn.cancel {
  background: #f0f2f5;
  color: #666;
}

.edit-dialog-btn.cancel:hover {
  background: #e6e6e6;
  color: #333;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
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
  padding: 10px 20px;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.2);
  margin-right: 12px;
  position: relative;
  overflow: hidden;
}

.file-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  transition: transform 0.6s;
  transform: skewX(-15deg);
}

.file-btn:hover::before {
  transform: skewX(-15deg) translateX(200%);
}

.file-btn:hover {
  background: linear-gradient(135deg, #0958d9, #003eb3);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(9, 88, 217, 0.3);
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
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 30px;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafd, #eaf4ff);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.08);
  border: 1px solid rgba(22, 119, 255, 0.1);
  font-size: 1.08rem;
}

.edit-pagination select, .edit-pagination input, .edit-pagination button {
  border-radius: 10px;
  border: 1px solid #d0e0ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 10px 16px;
  margin: 0 2px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
}

.edit-pagination select:focus, .edit-pagination input:focus {
  outline: none;
  border-color: #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
}

.edit-pagination button:disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
}

.edit-pagination button:not(:disabled):hover {
  background: #1677ff;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.1);
}

.page-input {
  width: 90px;
  padding: 8px 14px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.12rem;
  text-align: center;
  background: #f7faff;
}

.page-input:focus {
  outline: none;
  border-color: #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
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

@media (max-width: 800px) {
  .edit-pagination {
    flex-wrap: wrap;
    gap: 10px;
    font-size: 0.95rem;
    justify-content: center;
    text-align: center;
  }
  .edit-pagination button,
  .edit-pagination input{
    font-size: 0.95rem;
    padding: 6px 10px;
  }
  .edit-pagination input[type="number"] {
    width: 60px;
  }
  .edit-pagination select{
    font-size: 0.95rem;
    padding: 6px 10px;
    width: 70px;
  }
  .page-input{
    width: 50px;
  }
}
</style>
