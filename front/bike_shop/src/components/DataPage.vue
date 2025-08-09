<template>
  <div class="data-page">
    <div class="data-search-bar">
      <input v-model="search" class="search-input" placeholder="搜索..." @keyup.enter="onSearch" />
      <select v-model="filterCountry" class="filter-select">
        <option value="">全部国家</option>
        <option v-for="c in countryList" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filterCity" class="filter-select">
        <option value="">全部城市</option>
        <option v-for="c in cityList" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filterLevel" class="filter-select">
        <option value="">全部评级</option>
        <option value="A">A</option>
        <option value="B">B</option>
        <option value="C">C</option>
        <option value="D">D</option>
      </select>
      <select v-model="filterVisited" class="filter-select">
        <option value="">全部拜访</option>
        <option value="1">已拜访</option>
        <option value="0">未拜访</option>
      </select>
      <select v-model="filterTag" class="filter-select">
        <option value="">全部标签</option>
        <option v-for="tag in tagList" :key="tag.id" :value="tag.name">{{ tag.name }}</option>
      </select>
      <button class="search-btn" @click="onSearch">搜索</button>
      <button 
        class="delete-btn" 
        :disabled="!selectedRow" 
        :class="{active: selectedRow}" 
        @click="onDeleteClick"
      >删除数据</button>
    </div>

    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
        <tr>
          <th v-for="col in showColumns" :key="col">{{ columnLabels[col] || col }}</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="row in pagedData" :key="row.id" @click="selectRow(row)" class="data-row-clickable" :class="{selected: selectedRow && selectedRow.id === row.id}">
          <td v-for="col in showColumns" :key="col">
            <template v-if="col === 'image'">
              <img v-if="row.image" :src="getImageUrl(row.image)" class="data-img" @click.stop="openImgPreview(getImageUrl(row.image))" style="cursor:zoom-in;" />
            </template>
            <template v-else-if="col === 'visited'">
              <span v-if="String(row[col]) === 'true'" class="visited-tag visited-true">已拜访</span>
              <span v-else class="visited-tag visited-false">未拜访</span>
            </template>
            <template v-else-if="col === 'tags'">
              <div class="data-tags">
                <span v-for="(tag, index) in (row[col] && typeof row[col] === 'string' ? row[col].split(',').filter(t => t.trim()) : [])" 
                      :key="index"
                      class="data-tag">
                  <i class="fas fa-tag tag-icon-small"></i>
                  {{ tag }}
                </span>
                <span v-if="!row[col] || typeof row[col] !== 'string' || row[col].split(',').filter(tag => tag && tag.trim()).length === 0" class="no-tags">
                  无标签
                </span>
              </div>
            </template>
            <template v-else>
              {{ row[col] }}
            </template>
          </td>
        </tr>
        <tr v-if="pagedData.length === 0">
          <td :colspan="showColumns.length" style="text-align:center;color:#aaa;font-size:1.1rem;padding:24px 0;">
            <span>暂无数据，试试更换搜索条件或导入数据。</span>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showImgPreview" class="img-preview-mask" @click.self="closeImgPreview">
      <img :src="previewImg" class="img-preview-big" :style="{transform: `scale(${imgScale})`}" @wheel="onImgWheel" />
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetailDialog" class="detail-dialog-mask">
      <div class="detail-dialog">
        <button class="detail-dialog-close" @click="showDetailDialog = false">×</button>
        <div class="detail-dialog-title">数据详情</div>
        <div class="detail-dialog-flex">
          <div class="detail-dialog-content">
            <div v-for="col in columns" :key="col" v-if="col !== 'image'" class="detail-row">
              <span class="detail-label">{{ columnLabels[col] || col }}：</span>
              <span class="detail-value">
                <template v-if="col === 'visited'">
                  <span v-if="String(detailRow[col]) === 'true'" class="visited-tag visited-true">已拜访</span>
                  <span v-else class="visited-tag visited-false">未拜访</span>
                </template>
                <template v-else-if="col === 'website' && detailRow[col]">
                  <a :href="detailRow[col]" target="_blank" rel="noopener" class="website-link">
                        {{ detailRow[col] }}
                  </a>
                </template>
                <template v-else-if="col === 'tags'">
                  <div class="data-tags">
                    <span v-for="(tag, index) in (detailRow[col] && typeof detailRow[col] === 'string' ? detailRow[col].split(',').filter(t => t.trim()) : [])" 
                          :key="index"
                          class="data-tag">
                      <i class="fas fa-tag tag-icon-small"></i>
                      {{ tag }}
                    </span>
                    <span v-if="!detailRow[col] || typeof detailRow[col] !== 'string' || detailRow[col].split(',').filter(tag => tag && tag.trim()).length === 0" class="no-tags">
                      无标签
                    </span>
                  </div>
                </template>
                <template v-else>
                  {{ detailRow[col] }}
                </template>
              </span>
            </div>
          </div>
          <div class="detail-img-box" v-if="detailRow.image">
            <img :src="getImageUrl(detailRow.image)" class="detail-img-big" />
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteDialog" class="delete-dialog-mask">
      <div class="delete-dialog">
        <div class="delete-dialog-title">确认删除</div>
        <div class="delete-dialog-msg">确定要删除该数据吗？此操作不可恢复。</div>
        <div class="delete-dialog-actions">
          <button class="delete-dialog-btn confirm" @click="confirmDelete">确认</button>
          <button class="delete-dialog-btn cancel" @click="showDeleteDialog = false">取消</button>
        </div>
      </div>
    </div>

    <div class="data-pagination">
      <span>每页</span>
      <select v-model.number="pageSize" @change="onPageSizeChange">
        <option :value="5">5</option>
        <option :value="10">10</option>
        <option :value="20">20</option>
        <option :value="50">50</option>
        <option :value="100">100</option>
      </select>
      <span>条</span>
      <button class="page-btn" :disabled="page===1" @click="gotoPage(page-1)">上一页</button>
      <span>第</span>
      <input v-model.number="inputPage" class="page-input" @keyup.enter="gotoPage(inputPage)" />
      <span>/ {{ totalPages }} 页</span>
      <button class="page-btn" :disabled="page===totalPages" @click="gotoPage(page+1)">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

// 移动端检测
const isMobile = ref(false)

// 检测设备是否为移动端
function checkMobile() {
  isMobile.value = window.innerWidth <= 768
}

const search = ref('')
const filterType = ref('')
const filterStatus = ref('')
const dataList = ref([])
const columns = ref([])
const page = ref(1)
const pageSize = ref(10)
const inputPage = ref(1)
const total = ref(0)
const previewImg = ref('')
const showImgPreview = ref(false)
const imgScale = ref(1)
const filterCountry = ref('')
const filterCity = ref('')
const filterLevel = ref('')
const filterVisited = ref('')
const filterTag = ref('')
const countryList = ref([])
const cityList = ref([])
const tagList = ref([])
const allCityMap = ref({}) // 国家-城市映射
const allCitiesRaw = ref([]) // 数据库所有城市
const showDetailDialog = ref(false)
const detailRow = ref({})
const selectedRow = ref(null)
const showDeleteDialog = ref(false)

function openImgPreview(url) {
  previewImg.value = url
  showImgPreview.value = true
  imgScale.value = 1
}
function closeImgPreview() {
  showImgPreview.value = false
}
function onImgWheel(e) {
  e.preventDefault()
  let delta = e.deltaY < 0 ? 0.1 : -0.1
  let next = imgScale.value + delta
  if (next < 0.2) next = 0.2
  if (next > 5) next = 5
  imgScale.value = next
}

function showDetail(row) {
  detailRow.value = row
  showDetailDialog.value = true
}

function selectRow(row) {
  if (selectedRow.value && selectedRow.value.id === row.id) {
    // 如果点击的是已选中的行，则显示详情
    showDetail(row)
  } else {
    // 否则选中该行
    selectedRow.value = row
  }
}

function onDeleteClick() {
  if (!selectedRow.value) return
  showDeleteDialog.value = true
}

async function confirmDelete() {
  if (!selectedRow.value) return
  
  try {
    const token = localStorage.getItem('token')
    await axios.post('/api/delete-shop', {
      shop_id: selectedRow.value.id
    }, {
      headers: { Authorization: `Token ${token}` }
    })
    
    // 删除成功后刷新数据
    fetchData()
    showDeleteDialog.value = false
    selectedRow.value = null
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败，请稍后重试')
    showDeleteDialog.value = false
  }
}

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const pagedData = computed(() => dataList.value)
const baseColumns = ['id', 'name', 'country', 'city', 'address', 'level', 'tags', 'image', 'visited']
const showColumns = computed(() => baseColumns)

function onPageSizeChange() {
  page.value = 1
  inputPage.value = 1
  fetchData()
}
function gotoPage(p) {
  let n = Number(p)
  if (!n || n < 1) n = 1
  if (n > totalPages.value) n = totalPages.value
  page.value = n
  inputPage.value = n
  fetchData()
}

function getImageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path + '?t=' + Date.now()
  let url = path
  if (url.startsWith('/media/images/')) {
    url = url.replace('/media/images/', '/media/shop_images/')
  } else if (url.startsWith('media/images/')) {
    url = url.replace('media/images/', 'media/shop_images/')
  } else if (url.startsWith('/media/')) {
  } else if (url.startsWith('media/')) {
    url = '/' + url
  } else {
    url = '/media/shop_images/' + url.split('/').pop()
  }
  return url + '?t=' + Date.now()
}

async function fetchTags() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/tag_list', {
      headers: {
        Authorization: `Token ${token}`
      }
    })
    tagList.value = res.data.tags || []
  } catch (e) {
    console.error('获取标签列表失败:', e)
    tagList.value = []
  }
}

async function fetchData() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/data-list', {
      params: {
        search: search.value,
        page: page.value,
        page_size: pageSize.value,
        country: filterCountry.value,
        city: filterCity.value,
        level: filterLevel.value,
        visited: filterVisited.value,
        tag: filterTag.value
      },
      headers: {
        Authorization: `Token ${token}`
      }
    })
    dataList.value = res.data.data || []
    columns.value = res.data.columns || []
    total.value = res.data.total || 0
    countryList.value = res.data.all_countries || []
    allCitiesRaw.value = res.data.all_cities || []
    // 构建国家-城市映射，基于数据库所有数据
    allCityMap.value = {}
    if (res.data.all_countries && res.data.all_cities && res.data.data) {
      for (const row of res.data.data) {
        if (row.country && row.city) {
          if (!allCityMap.value[row.country]) allCityMap.value[row.country] = new Set()
          allCityMap.value[row.country].add(row.city)
        }
      }
      for (const k in allCityMap.value) {
        allCityMap.value[k] = Array.from(allCityMap.value[k]).sort()
      }
    }
    // 城市下拉：始终显示数据库所有城市（去重），不依赖国家选择
    cityList.value = allCitiesRaw.value;
  } catch (e) {
    dataList.value = []
    columns.value = []
    total.value = 0
    countryList.value = []
    cityList.value = []
    allCityMap.value = {}
    allCitiesRaw.value = []
  }
}

function onSearch() {
  page.value = 1
  inputPage.value = 1
  fetchData()
}

function resetFilter() {
  search.value = ''
  filterCountry.value = ''
  filterCity.value = ''
  filterLevel.value = ''
  filterVisited.value = ''
  filterTag.value = ''
  page.value = 1
  inputPage.value = 1
  fetchData()
}

onMounted(() => {
  fetchData()
  fetchTags()
  window.addEventListener('keydown', handleEscClose)
  
  // 初始检测设备类型
  checkMobile()
  
  // 监听窗口大小变化
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscClose)
  window.removeEventListener('resize', checkMobile)
})
function handleEscClose(e) {
  if (showImgPreview.value && (e.key === 'Escape' || e.key === 'Esc')) {
    closeImgPreview()
  }
}
</script>

<script>
export default {
  data() {
    return {

      showColumns: ['id', 'name', 'country', 'city', 'lat', 'lon', 'address', 'phone', 'email', 'level', 'tags', 'image', 'visited','website'],
      columnLabels: {
        id: '编号',
        name: '店铺名称',
        country: '国家',
        city: '城市',
        lat: '经度',
        lon: '纬度',
        address: '地址',
        phone: '联系方式',
        email: '邮箱',
        level: '级别',
        tags: '标签',
        image: '首页图片',
        visited: '是否拜访',
        website: '网址',
      }
    }
  }
}
</script>

<style scoped>
.data-page {
  padding: 30px;
  background: #f8fafd;
  min-height: 100vh;
  font-size: 1.1rem;
  color: #222;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 18px;
}

/* 标签样式 */
.data-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  justify-content: flex-start;
  min-height: 24px;
  padding: 2px 0;
}

.data-tag {
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
}

.tag-icon-small {
  font-size: 10px;
  margin-right: 3px;
  color: white;
  display: inline-block;
}

.no-tags {
  color: #999;
  font-style: italic;
  font-size: 12px;
}
.data-search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 0px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafd, #eaf4ff);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.08);
  border: 1px solid rgba(22, 119, 255, 0.1);
  flex-wrap: wrap;
  align-items: center;
}
.search-input {
  flex: 1;
  padding: 10px 16px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  background: #f7faff;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
  min-width: 200px;
}
.search-input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
  transform: translateY(-1px);
}
.search-btn {
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
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.search-btn::before {
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

.search-btn:hover::before {
  transform: skewX(-15deg) translateX(200%);
}

.search-btn:hover {
  background: linear-gradient(135deg, #0958d9, #003eb3);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(9, 88, 217, 0.3);
}

.delete-btn {
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

.delete-btn::before {
  content: '×';
  margin-right: 8px;
  font-size: 1.2rem;
  font-weight: bold;
}

.delete-btn.active {
  background: linear-gradient(135deg, #ff5858, #f09819);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(255, 88, 88, 0.2);
}

.delete-btn.active:hover {
  background: linear-gradient(135deg, #f09819, #ff5858);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 88, 88, 0.3);
}
/* .data-filter-bar {
  display: flex;
  gap: 24px;
  margin: 10px 0 8px 0;
  align-items: center;
} */
/* .filter-label {
  font-size: 1rem;
  color: #1765d8;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
} */
.data-table-wrapper {
  overflow-x: auto;
  margin-bottom: 30px;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(22, 119, 255, 0.08);
  border: 1px solid rgba(22, 119, 255, 0.1);
}
.data-table {
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
}

.data-table th, .data-table td {
  padding: 16px 20px;
  text-align: center;
  font-size: 1.08rem;
  transition: background 0.3s ease;
  white-space: nowrap; /* 不换行，始终一行显示 */
  height: 52px; /* 统一行高，可根据需要调整 */
  line-height: 52px; /* 垂直居中 */
}

.data-table th {
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

.data-table td {
  color: #2c3e50;
  border-bottom: 1px solid #eef2f7;
  vertical-align: middle;
  text-align: center;
}

.data-table tr:last-child td {
  border-bottom: none;
}
.data-table td img.data-img {
  display: block;
  margin: 0 auto;
  max-width: 60px;
  max-height: 60px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(88,166,255,0.13);
  background: #f7faff;
  cursor: zoom-in;
  transition: box-shadow 0.2s;
}
.data-table td img.data-img:hover {
  box-shadow: 0 4px 16px rgba(22,120,255,0.18);
}
.visited-tag {
  display: inline-block;
  min-width: 80px;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  margin-left: 6px;
}

.visited-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.visited-true {
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  color: #0050b3;
  border: 1px solid #91caff;
}

.visited-true:hover {
  background: linear-gradient(135deg, #bae7ff, #91caff);
  border: 1px solid #69c0ff;
}

.visited-false {
  background: linear-gradient(135deg, #fff2e8, #ffd8bf);
  color: #d4380d;
  border: 1px solid #ffbb96;
}

.visited-false:hover {
  background: linear-gradient(135deg, #ffd8bf, #ffbb96);
  border: 1px solid #ff9c6e;
}
.filter-select {
  padding: 12px 16px;
  border: 1px solid #d0e0ff;
  border-radius: 10px;
  font-size: 1rem;
  min-width: 180px;
  background-color: #fff;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%231677ff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 40px;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
  transform: translateY(-1px);
}

.filter-select:hover {
  border-color: #58a6ff;
  background-color: #f8fafd;
}
.data-pagination {
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

.page-btn, .page-input, select {
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

.page-btn:disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
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
  transform: translateY(-1px);
}
.data-img {
  max-width: 80px;
  max-height: 80px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.1);
  border: 2px solid #fff;
  background: #f7faff;
}

.data-img:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.2);
  border-color: #d0e0ff;
}
.img-preview-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
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

.img-preview-big {
  max-width: 70vw;
  max-height: 70vh;
  border-radius: 12px;
  box-shadow: 0 0 50px rgba(22, 119, 255, 0.3);
  background: none;
  animation: zoomIn 0.4s ease;
  transform-origin: center;
}

@keyframes zoomIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.img-preview-close {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  color: #fff;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(2px);
  border: 2px solid rgba(255,255,255,0.2);
}

.img-preview-close:hover {
  background: rgba(255,255,255,0.3);
  transform: rotate(90deg);
  box-shadow: 0 0 20px rgba(255,255,255,0.4);
}
.data-row-clickable {
  cursor: pointer;
  transition: all 0.3s ease;
}

.data-table tbody tr:nth-child(odd) {
  background: #f8fafd;
}

.data-table tbody tr:nth-child(even) {
  background: #ffffff;
}

.data-table tbody tr:hover, .data-row-clickable:hover {
  background: #f5f9ff !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
  transition: all 0.3s ease;
}

.data-table tbody tr.selected {
  background: #e0f0ff !important;
  border-left: 4px solid #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.15);
}

.delete-dialog-mask {
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

.delete-dialog {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(255,88,88,0.2);
  padding: 32px 36px;
  width: 450px;
  max-width: 90vw;
  animation: popIn 0.3s ease;
  overflow: hidden;
}

.delete-dialog-title {
  font-size: 1.5rem;
  color: #ff5858;
  font-weight: 800;
  margin-bottom: 20px;
  letter-spacing: 1px;
  position: relative;
  padding-bottom: 12px;
}

.delete-dialog-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #ff5858, #f09819);
  border-radius: 3px;
}

.delete-dialog-msg {
  font-size: 1.1rem;
  margin-bottom: 30px;
  color: #2c3e50;
  line-height: 1.6;
}

.delete-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.delete-dialog-btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 1.08rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.delete-dialog-btn.confirm {
  background: linear-gradient(90deg, #ff5858, #f09819);
  color: #fff;
  box-shadow: 0 4px 12px rgba(255,88,88,0.18);
}

.delete-dialog-btn.confirm:hover {
  background: linear-gradient(90deg, #f09819, #ff5858);
  box-shadow: 0 8px 20px rgba(255,88,88,0.3);
  transform: translateY(-2px);
}

.delete-dialog-btn.cancel {
  background: #f8fafd;
  color: #2c3e50;
  border: 1px solid #d0e0ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.05);
}

.delete-dialog-btn.cancel:hover {
  background: #f0f7ff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(22, 119, 255, 0.1);
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
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(22,120,255,0.2);
  padding: 40px 48px 32px 48px;
  min-width: 700px;
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  animation: popIn 0.3s ease;
  overflow: hidden;
}

@keyframes popIn {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
.detail-dialog-title {
  font-size: 1.5rem;
  color: #1765d8;
  font-weight: 800;
  margin-bottom: 24px;
  letter-spacing: 1px;
  position: relative;
  padding-bottom: 12px;
}

.detail-dialog-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  border-radius: 3px;
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
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  max-height: 70vh;
  padding-right: 16px;
  padding-bottom: 10px;
}

.detail-dialog-content::-webkit-scrollbar {
  width: 8px;
}

.detail-dialog-content::-webkit-scrollbar-track {
  background: #f5f9ff;
  border-radius: 10px;
}

.detail-dialog-content::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #58a6ff, #1677ff);
  border-radius: 10px;
  border: 2px solid #f5f9ff;
}

.detail-dialog-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #1677ff, #0056d6);
}
.detail-img-box {
  flex: none;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  min-width: 220px;
  max-width: 320px;
  padding: 16px;
  background: #f8fafd;
  border-radius: 16px;
  box-shadow: inset 0 2px 8px rgba(22, 119, 255, 0.08);
}
.detail-img-big {
  max-width: 260px;
  max-height: 260px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(22, 119, 255, 0.15);
  background: #f7faff;
  margin-left: 8px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.detail-img-big:hover {
  transform: scale(1.02);
  box-shadow: 0 12px 30px rgba(22, 119, 255, 0.25);
}
.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 12px;
  background: #f8fafd;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
}

.detail-row:hover {
  background: #f0f7ff;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.1);
}

.detail-label {
  min-width: 140px;
  font-weight: 700;
  color: #1765d8;
  padding-right: 16px;
  position: relative;
}

.detail-label::after {
  content: ':';
  position: absolute;
  right: 8px;
  color: #58a6ff;
}

.detail-value {
  flex: 1;
  color: #2c3e50;
  word-break: break-word;
  line-height: 1.5;
  font-size: 1.05rem;
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
  top: 20px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f7faff, #eaf4ff);
  border: 1.5px solid #b3d6ff;
  color: #1677ff;
  font-size: 1.8rem;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(88,166,255,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.3s ease;
}

.detail-dialog-close:hover {
  background: linear-gradient(135deg, #1677ff, #58a6ff);
  color: #fff;
  transform: rotate(90deg);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.25);
}
@media (max-width: 768px) {
  .data-page {
    padding: 15px;
    gap: 12px;
  }
  
  .data-search-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px;
    border-radius: 12px;
  }

  /* 搜索栏组件样式优化 */
  .search-input {
    width: 100%;
    font-size: 16px; /* 防止iOS缩放 */
    padding: 10px 12px;
    order: -1; /* 搜索框放在最前面 */
  }
  
  .filter-select {
    width: calc(50% - 4px);
    font-size: 16px; /* 防止iOS缩放 */
    padding: 10px 8px;
    min-width: unset;
    background-position: right 8px center;
    padding-right: 30px;
  }
  
  .search-btn,
  .delete-btn {
    width: calc(50% - 4px);
    font-size: 0.95rem;
    padding: 10px 8px;
    margin-top: 8px;
  }
  
  /* 表格容器样式优化 */
  .data-table-wrapper {
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 15px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch; /* 提升iOS滚动体验 */
  }
  
  /* 表格样式优化 */
  .data-table th, 
  .data-table td {
    padding: 10px 12px;
    font-size: 0.95rem;
    height: 40px;
    line-height: 1.3;
  }
  
  /* 图片预览样式优化 */
  .img-preview-big {
    max-width: 90vw;
    max-height: 80vh;
  }
  
  /* 详情弹窗样式优化 */
  .detail-dialog {
    min-width: unset;
    width: 90vw;
    padding: 20px;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .detail-dialog-flex {
    flex-direction: column;
    gap: 20px;
  }
  
  .detail-img-box {
    width: 100%;
    max-width: 100%;
    justify-content: center;
    padding: 12px;
  }
  
  .detail-img-big {
    max-width: 100%;
    margin-left: 0;
  }
  
  .detail-dialog-content {
    width: 100%;
    padding-right: 0;
    font-size: 1rem;
  }
  
  .detail-row {
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  
  .detail-label {
    min-width: 100px;
    font-size: 0.95rem;
  }
  
  .detail-value {
    font-size: 0.95rem;
  }
  
  /* 删除弹窗样式优化 */
  .delete-dialog {
    padding: 20px;
    width: 90vw;
  }
  
  .delete-dialog-title {
    font-size: 1.3rem;
    margin-bottom: 15px;
  }
  
  .delete-dialog-msg {
    font-size: 1rem;
    margin-bottom: 20px;
  }
  
  .delete-dialog-btn {
    padding: 10px 16px;
    font-size: 1rem;
  }
  
  /* 分页控件样式优化 */
  .data-pagination {
    flex-wrap: wrap;
    gap: 8px;
    font-size: 0.95rem;
    padding: 12px;
    justify-content: center;
    text-align: center;
  }
  
  .data-pagination button,
  .data-pagination input {
    font-size: 16px; /* 防止iOS缩放 */
    padding: 8px 12px;
  }
  
  .data-pagination input[type="number"] {
    width: 60px;
  }
  
  .data-pagination select {
    font-size: 16px; /* 防止iOS缩放 */
    padding: 8px 12px;
    width: 70px;
  }
  
  .page-input {
    width: 50px;
  }
  
  /* 标签样式优化 */
  .data-tag {
    padding: 2px 6px;
    font-size: 0.75rem;
  }
  
  /* 访问状态标签样式优化 */
  .visited-tag {
    min-width: 60px;
    padding: 4px 8px;
    font-size: 0.8rem;
  }
}

/* 小型手机屏幕适配 */
@media (max-width: 480px) {
  .data-page {
    padding: 10px;
  }
  
  .filter-select {
    width: 100%;
    margin-bottom: 4px;
  }
  
  .search-btn,
  .delete-btn {
    width: 100%;
  }
  
  .data-table th, 
  .data-table td {
    padding: 8px 10px;
    font-size: 0.9rem;
  }
  
  .detail-dialog-title {
    font-size: 1.2rem;
  }
  
  .detail-dialog-close {
    top: 10px;
    right: 10px;
    width: 36px;
    height: 36px;
    font-size: 1.5rem;
  }
}
</style>
