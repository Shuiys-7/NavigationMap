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
      <button class="search-btn" @click="onSearch">搜索</button>
    </div>

    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
        <tr>
          <th v-for="col in showColumns" :key="col">{{ columnLabels[col] || col }}</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="row in pagedData" :key="row.id" @click="showDetail(row)" class="data-row-clickable">
          <td v-for="col in showColumns" :key="col">
            <template v-if="col === 'image'">
              <img v-if="row.image" :src="getImageUrl(row.image)" class="data-img" @click.stop="openImgPreview(getImageUrl(row.image))" style="cursor:zoom-in;" />
            </template>
            <template v-else-if="col === 'visited'">
              <span v-if="String(row[col]) === 'true'" class="visited-tag visited-true">已拜访</span>
              <span v-else class="visited-tag visited-false">未拜访</span>
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
const countryList = ref([])
const cityList = ref([])
const allCityMap = ref({}) // 国家-城市映射
const allCitiesRaw = ref([]) // 数据库所有城市
const showDetailDialog = ref(false)
const detailRow = ref({})

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

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const pagedData = computed(() => dataList.value)
const baseColumns = ['id', 'name', 'country', 'city', 'address', 'level', 'image', 'visited']
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

async function fetchData() {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/data-list', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        search: search.value,
        country: filterCountry.value,
        city: filterCity.value,
        level: filterLevel.value,
        visited: filterVisited.value,
      },
      headers: { Authorization: `Token ${token}` }
    })
    dataList.value = res.data.data || []
    columns.value = res.data.columns || (dataList.value[0] ? Object.keys(dataList.value[0]) : [])
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

onMounted(() => {
  fetchData()
  window.addEventListener('keydown', handleEscClose)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscClose)
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
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.10);
  padding: 36px 28px 28px 28px;
  min-height: 400px;
  font-size: 1.1rem;
  color: #222;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 18px;
}
.data-search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 0px;
}
.search-input {
  flex: 1;
  padding: 10px 16px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  background: #f7faff;
  transition: border 0.2s;
}
.search-input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
}
.search-btn {
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
}
.search-btn:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
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
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 0;
  overflow: visible;
  box-shadow: none;
  table-layout: auto;
  min-width: max-content;
}
.data-table th, .data-table td {
  padding: 14px 16px;
  text-align: center;
  font-size: 1.08rem;
  transition: background 0.2s;
  white-space: nowrap; /* 不换行，始终一行显示 */
  height: 48px; /* 统一行高，可根据需要调整 */
  line-height: 48px; /* 垂直居中 */
}
.data-table th {
  background: linear-gradient(90deg, #eaf4ff 60%, #f7faff 100%);
  color: #1765d8;
  font-weight: 700;
  border-bottom: 2px solid #e0eaff;
  letter-spacing: 1px;
  white-space: nowrap;
  text-align: center;
}
.data-table td {
  color: #222;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
  text-align: center;
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
  min-width: 70px;
  padding: 7px 22px;
  border-radius: 28px;
  font-size: 1.12rem;
  font-weight: 800;
  color: #fff;
  text-align: center;
  margin-left: 6px;
  box-shadow: 0 4px 16px rgba(88,166,255,0.13), 0 1.5px 8px rgba(0,0,0,0.08);
  letter-spacing: 1.5px;
  border: 2px solid rgba(255,255,255,0.18);
  transition: box-shadow 0.2s, border 0.2s;
  backdrop-filter: blur(1.5px);
}
.visited-true {
  background: linear-gradient(90deg, #1fd976 0%, #38f9d7 100%);
  box-shadow: 0 4px 16px rgba(31,217,118,0.18);
  border-color: #1fd97644;
  opacity: 0.97;
}
.visited-false {
  background: linear-gradient(90deg, rgba(255,88,88,0.95) 0%, rgba(240,152,25,0.85) 100%);
  box-shadow: 0 4px 16px rgba(255,88,88,0.18);
  border-color: #ff585844;
  opacity: 0.95;
}
.filter-select {
  padding: 8px 22px 8px 12px;
  border: 1.5px solid #b3d6ff;
  border-radius: 8px;
  font-size: 1.08rem;
  background: linear-gradient(90deg, #f7faff 60%, #eaf4ff 100%);
  color: #1765d8;
  font-weight: 500;
  transition: border 0.2s, box-shadow 0.2s;
  margin-right: 8px;
  box-shadow: 0 2px 8px rgba(88,166,255,0.06);
}
.filter-select:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 0 0 2px #b3d6ff44;
}
.data-pagination {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  font-size: 1.08rem;
  justify-content: center;
  background: #f7faff;
  border-radius: 10px;
  padding: 12px 0;
  box-shadow: 0 2px 8px rgba(88,166,255,0.06);
}
.page-btn, .page-input, select {
  border-radius: 8px;
  border: 1.5px solid #b3d6ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 7px 18px;
  margin: 0 2px;
  transition: background 0.2s, box-shadow 0.2s;
}
.page-btn:disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
}
.page-btn:not(:disabled):hover {
  background: #1677ff;
  color: #fff;
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
.data-img {
  max-width: 80px;
  max-height: 80px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  background: #f7faff;
}
.img-preview-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(22, 120, 255, 0.5) 0%, rgba(255,255,255,0.5) 100%);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.img-preview-big {
  max-width: 70vw;
  max-height: 70vh;
  border-radius: 12px;
  box-shadow: 0 4px 32px rgba(22,120,255,0.18);
  background: none;
}
.img-preview-close {
  position: absolute;
  top: 8px;
  right: 12px;
  background: none;
  border: none;
  font-size: 2rem;
  color: #1677ff;
  cursor: pointer;
  font-weight: bold;
  line-height: 1;
  transition: color 0.2s;
}
.img-preview-close:hover {
  color: #e74c3c;
}
.data-row-clickable {
  cursor: pointer;
  transition: background 0.18s;
}
.data-table tbody tr:nth-child(odd) {
  background: #f7faff;
}
.data-table tbody tr:nth-child(even) {
  background: #fdfdff;
}
.data-table tbody tr:hover, .data-row-clickable:hover {
  background: #e6f0ff !important;
  transition: background 0.2s;
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
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  padding: 32px 36px 24px 36px;
  min-width: 700px;
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
}
.detail-dialog-title {
  font-size: 1.22rem;
  color: #1765d8;
  font-weight: 700;
  margin-bottom: 18px;
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
.detail-img-box {
  flex: none;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  min-width: 220px;
  max-width: 320px;
}
.detail-img-big {
  max-width: 260px;
  max-height: 260px;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.13);
  background: #f7faff;
  margin-left: 8px;
}
.detail-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 1.08rem;
}
.detail-label {
  color: #888;
  font-weight: 500;
  min-width: 90px;
  display: inline-block;
}
.detail-value {
  color: #222;
  font-weight: 600;
  word-break: break-all;
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
@media (max-width: 768px) {
  .data-search-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  /* 设置每个组件的默认宽度 */
  .search-input,
  .filter-select,
  .search-btn{
    width: 110px;
    font-size: 0.9rem;
    padding: 6px 6px;
  }

  .data-pagination {
    flex-wrap: wrap;
    gap: 10px;
    font-size: 0.95rem;
    padding: 10px;
    justify-content: center;
    text-align: center;
  }
  .data-pagination button,
  .data-pagination input{
    font-size: 0.95rem;
    padding: 6px 10px;
  }
  .data-pagination input[type="number"] {
    width: 60px;
  }
  .data-pagination select{
    font-size: 0.95rem;
    padding: 6px 10px;
    width: 70px;
  }
  .page-input{
    width: 50px;
  }
}
</style>
