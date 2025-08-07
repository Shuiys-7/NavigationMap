<!-- 展示页面组件 - 3D地球展示 -->
<template>
  <div class="showcase-page">
    <!-- 筛选面板 -->
    <div class="filter-panel" :class="{ collapsed: isFilterPanelCollapsed }">
      <div class="filter-panel-header">
        <h3>筛选面板</h3>
        <button @click="toggleFilterPanel" class="collapse-btn">
          {{ isFilterPanelCollapsed ? '展开' : '收缩' }}
        </button>
      </div>
      <div class="filter-panel-content" v-show="!isFilterPanelCollapsed">
        <div class="filter-group">
          <label>国家：</label>
          <select v-model="filters.country" @change="applyFilters">
            <option value="">全部国家</option>
            <option v-for="country in uniqueCountries" :key="country" :value="country">{{ country }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>城市：</label>
          <select v-model="filters.city" @change="applyFilters">
            <option value="">全部城市</option>
            <option v-for="city in filteredCities" :key="city" :value="city">{{ city }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>标签：</label>
          <select v-model="filters.tag" @change="applyFilters">
            <option value="">全部标签</option>
            <option v-for="tag in uniqueTags" :key="tag" :value="tag">{{ tag }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>拜访状态：</label>
          <select v-model="filters.visited" @change="applyFilters">
            <option value="">全部</option>
            <option value="已拜访">已拜访</option>
            <option value="未拜访">未拜访</option>
          </select>
        </div>
        <div class="filter-group">
          <label>评级：</label>
          <select v-model="filters.level" @change="applyFilters">
            <option value="">全部评级</option>
            <option v-for="level in uniqueLevels" :key="level" :value="level">{{ level }}</option>
          </select>
        </div>
        <button @click="clearFilters" class="clear-filters-btn">清除筛选</button>

        <!-- 新建店铺按钮 -->
        <div class="add-shop-section">
          <button @click="toggleAddShopMode" class="add-shop-btn" :class="{ active: addShopMode }">
            {{ addShopMode ? '取消新建' : '新建店铺' }}
          </button>
          <div v-if="addShopMode" class="add-shop-hint">
            点击地图上的位置来添加新店铺
          </div>
        </div>

        <!-- 路径规划按钮 -->
        <div class="navigation-section">
          <button @click="toggleNavigation" class="nav-toggle-btn">
            {{ showNavigation ? '隐藏导航' : '路径规划' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 导航面板 -->
    <div class="navigation-panel" v-if="showNavigation">
      <div class="nav-header">
        <h3>路径规划</h3>
        <button @click="toggleNavigation" class="close-nav-btn">×</button>
      </div>
      <div class="nav-content">
        <div class="nav-inputs">
          <input v-model="newAddress" placeholder="输入地址或点击地图添加" />
          <button @click="addRoutePoint">添加路径点</button>
        </div>
        <div class="route-points-list">
          <h4>路径点列表</h4>
          <div v-for="(point, index) in routePoints" :key="index" class="route-point-item">
            <span class="point-number">{{ index + 1 }}</span>
            <span class="point-address">{{ point.address || `${point.lat}, ${point.lon}` }}</span>
            <div class="point-actions">
              <button @click="movePoint(index, 'up')" :disabled="index === 0" class="move-btn">↑</button>
              <button @click="movePoint(index, 'down')" :disabled="index === routePoints.length - 1" class="move-btn">↓</button>
              <button @click="removeRoutePoint(index)" class="remove-btn">×</button>
            </div>
          </div>
        </div>
        <div class="nav-actions">
          <button @click="clearRoutePoints" :disabled="routePoints.length === 0" class="clear-btn">清空路径</button>
          <button @click="calculateRoute" :disabled="routePoints.length < 2" class="calculate-btn">计算路径</button>
          <button @click="getCurrentLocation" class="gps-btn">GPS定位</button>
          <button @click="clearRouteDrawing" :disabled="!routeEntity" class="clear-drawing-btn">清除路径线</button>
        </div>
        <div class="route-info" v-if="routeInfo">
          <div class="route-details">
            <p><strong>总距离：</strong>{{ routeInfo.distance }}</p>
            <p><strong>总时间：</strong>{{ routeInfo.duration }}</p>
            <p><strong>路径点：</strong>{{ routePoints.length }} 个</p>
          </div>
          <button @click="openGoogleMaps" class="google-btn">在Google Maps中打开</button>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div class="point-panel" :class="{ 'point-panel-open': showPointPanel }">
      <div class="point-panel-header" v-if="showPointPanel && selectedPoint.name">
        <h3>坐标点信息</h3>
        <button @click="closePointPanel" class="close-btn">×</button>
      </div>
      <div class="point-panel-content" v-if="showPointPanel && selectedPoint.name">
        <div class="point-details">
          <h4>{{ selectedPoint.name }}</h4>
          <p><strong>坐标：</strong>{{ selectedPoint.lat }}, {{ selectedPoint.lon }}</p>
          <p><strong>地址：</strong>{{ selectedPoint.address }}</p>
          <p><strong>国家：</strong>{{ selectedPoint.country }}</p>
          <p><strong>城市：</strong>{{ selectedPoint.city }}</p>
          <p><strong>评级：</strong>{{ selectedPoint.level }}</p>
          <p><strong>标签：</strong>{{ selectedPoint.tags }}</p>
          <p><strong>状态：</strong>{{ selectedPoint.visited }}</p>
        </div>
        <div v-if="selectedPoint.image" class="point-image">
          <img :src="selectedPoint.image" :alt="selectedPoint.name" />
        </div>
        <div class="point-actions">
          <button @click="addToRoute(selectedPoint)" class="add-btn">添加到路径</button>
        </div>
      </div>
    </div>

    <!-- 新建店铺弹窗 -->
    <div class="add-shop-modal" v-if="showAddShopModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>新建店铺</h3>
          <button @click="closeAddShopModal" class="close-modal-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>店铺名称：</label>
            <input v-model="newShop.name" placeholder="请输入店铺名称" />
          </div>
          <div class="form-group">
            <label>国家：</label>
            <input v-model="newShop.country" placeholder="请输入国家" />
          </div>
          <div class="form-group">
            <label>城市：</label>
            <input v-model="newShop.city" placeholder="请输入城市" />
          </div>
          <div class="form-group">
            <label>地址：</label>
            <input v-model="newShop.address" placeholder="请输入详细地址" />
          </div>
          <div class="form-group">
            <label>电话：</label>
            <input v-model="newShop.phone" placeholder="请输入电话号码" />
          </div>
          <div class="form-group">
            <label>邮箱：</label>
            <input v-model="newShop.email" placeholder="请输入邮箱地址" />
          </div>
          <div class="form-group">
            <label>标签：</label>
            <div class="tags-input">
              <div class="selected-tags">
                <span v-for="(tag, index) in newShop.tags" :key="index" class="tag">
                  {{ tag }}
                  <button @click="removeTag(index)" class="remove-tag">×</button>
                </span>
              </div>
              <div class="tag-input-group">
                <input v-model="newTag" placeholder="输入标签" @keyup.enter="addTag" />
                <button @click="addTag" class="add-tag-btn">添加</button>
              </div>
            </div>
          </div>
          <div class="coordinates-info">
            <p><strong>坐标：</strong>{{ newShop.lat }}, {{ newShop.lon }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddShopModal" class="cancel-btn">取消</button>
          <button @click="saveNewShop" class="save-btn">保存店铺</button>
        </div>
      </div>
    </div>



    <div class="cesium-map" ref="cesiumContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import * as Cesium from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import axios from 'axios'

const cesiumContainer = ref(null)
let viewer = null
let autoRotate = true
let rotateHandler = null
let allGeoData = ref([])
let filteredGeoData = ref([])

// 筛选相关
const filters = ref({
  country: '',
  city: '',
  tag: '',
  visited: '',
  level: ''
})

// 筛选面板收缩相关
const isFilterPanelCollapsed = ref(false)

// 新建店铺相关
const addShopMode = ref(false)
const showAddShopModal = ref(false)
const newShop = ref({
  name: '',
  country: '',
  city: '',
  address: '',
  phone: '',
  email: '',
  tags: [],
  lat: 0,
  lon: 0
})
const newTag = ref('')

// 导航相关
const showNavigation = ref(false)
const newAddress = ref('')
const routePoints = ref([])
const routeInfo = ref(null)
const routeEntity = ref(null) // 用于存储路径实体

// 详情弹窗相关
const showPointPanel = ref(false)
const selectedPoint = ref({})

// 计算属性
const uniqueCountries = computed(() => {
  const countries = [...new Set(allGeoData.value.map(item => item.country).filter(Boolean))]
  return countries.sort()
})

const filteredCities = computed(() => {
  let cities = allGeoData.value
  if (filters.value.country) {
    cities = cities.filter(item => item.country === filters.value.country)
  }
  const cityList = [...new Set(cities.map(item => item.city).filter(Boolean))]
  return cityList.sort()
})

const uniqueTags = computed(() => {
  const allTags = []
  allGeoData.value.forEach(item => {
    if (item.tags) {
      const tags = item.tags.split(',').map(tag => tag.trim()).filter(Boolean)
      allTags.push(...tags)
    }
  })
  return [...new Set(allTags)].sort()
})

const uniqueLevels = computed(() => {
  const levels = [...new Set(allGeoData.value.map(item => item.level).filter(Boolean))]
  return levels.sort()
})

async function fetchGeoData() {
  const token = localStorage.getItem('token')
  const res = await axios.get('/api/data-list', {
    params: { page: 1, page_size: 10000 },
    headers: { Authorization: `Token ${token}` }
  })
  return (res.data.data || []).map(item => ({
    name: item.name,
    lon: item.lon,
    lat: item.lat,
    address: item.address,
    country: item.country,
    city: item.city,
    image: item.image
      ? (item.image.startsWith('/media/shop_images/')
          ? item.image
          : item.image.startsWith('/media/images/')
            ? item.image.replace('/media/images/', '/media/shop_images/')
            : '/media/shop_images/' + item.image.replace(/^.*[\\/]/, ''))
      : '',
    tags: item.tags || '',
    visited: item.visited ? '已拜访' : '未拜访',
    level: item.level || ''
  }))
}

function applyFilters() {
  let filtered = allGeoData.value

  if (filters.value.country) {
    filtered = filtered.filter(item => item.country === filters.value.country)
  }
  if (filters.value.city) {
    filtered = filtered.filter(item => item.city === filters.value.city)
  }
  if (filters.value.tag) {
    filtered = filtered.filter(item => item.tags && item.tags.includes(filters.value.tag))
  }
  if (filters.value.visited) {
    filtered = filtered.filter(item => item.visited === filters.value.visited)
  }
  if (filters.value.level) {
    filtered = filtered.filter(item => item.level === filters.value.level)
  }

  filteredGeoData.value = filtered
  updateMapEntities()
}

function clearFilters() {
  filters.value = {
    country: '',
    city: '',
    tag: '',
    visited: '',
    level: ''
  }
  filteredGeoData.value = allGeoData.value
  updateMapEntities()
}

function updateMapEntities() {
  if (!viewer) return

  // 保存当前的路径实体
  const currentRouteEntity = routeEntity.value
  const currentRouteEntities = []

  // 保存所有路径相关的实体（起点、终点标记等）
  viewer.entities.values.forEach(entity => {
    if (entity.label && (entity.label.text === '起点' || entity.label.text === '终点')) {
      currentRouteEntities.push(entity)
    }
  })

  // 清除现有实体
  viewer.entities.removeAll()

  // 添加筛选后的实体
  filteredGeoData.value.forEach(item => {
    if (item.lon && item.lat) {
      const entity = viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(item.lon, item.lat),
        point: {
          pixelSize: 12,
          color: Cesium.Color.RED.withAlpha(0.85),
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2
        },
        label: {
          text: item.name,
          font: '14px sans-serif',
          fillColor: Cesium.Color.AQUA,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          outlineWidth: 2,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          pixelOffset: new Cesium.Cartesian2(0, -18),
          showBackground: true,
          show: false
        },
        description: `
          <div style='display:flex;align-items:flex-start;gap:18px;min-width:340px;'>
            <div style='flex:1;min-width:180px;font-size:15px;line-height:1.7;padding:8px 0 2px 0;'>
              <div style='font-size:18px;font-weight:700;color:#1677ff;margin-bottom:6px;'>${item.name}</div>
              <div><b>国家：</b><span style='color:#1765d8;'>${item.country || ''}</span></div>
              <div><b>城市：</b><span style='color:#1765d8;'>${item.city || ''}</span></div>
              <div><b>地址：</b>${item.address || ''}</div>
              <div><b>评级：</b>${item.level || ''}</div>
              <div><b>标签：</b>${item.tags || ''}</div>
              <div><b>是否拜访：</b>${item.visited}</div>
              <div><b>经度：</b>${item.lon}</div>
              <div><b>纬度：</b>${item.lat}</div>
            </div>
            ${item.image ? `<div style='flex:none;'><a href='${item.image}' target='_blank' style='display:inline-block;'><img src='${item.image}' style='max-width:180px;max-height:120px;border-radius:8px;box-shadow:0 2px 8px #1677ff22;cursor:zoom-in;' /></a></div>` : ''}
          </div>
        `
      })

      // 添加点击事件
      entity.click = () => {
        showPointDetails(item)
      }
    }
  })

  // 恢复路径实体
  if (currentRouteEntity) {
    routeEntity.value = viewer.entities.add(currentRouteEntity.polyline)
  }

  // 恢复路径相关的实体
  currentRouteEntities.forEach(entity => {
    viewer.entities.add(entity)
  })
}

// 筛选面板收缩相关函数
function toggleFilterPanel() {
  isFilterPanelCollapsed.value = !isFilterPanelCollapsed.value
}

// 新建店铺相关函数
function toggleAddShopMode() {
  addShopMode.value = !addShopMode.value
  if (!addShopMode.value) {
    showAddShopModal.value = false
  }
}

function handleMapClick(event) {
  if (!addShopMode.value) return

  const pickedPosition = viewer.camera.pickEllipsoid(event.position, viewer.scene.globe.ellipsoid)
  if (pickedPosition) {
    const cartographic = Cesium.Cartographic.fromCartesian(pickedPosition)
    const lon = Cesium.Math.toDegrees(cartographic.longitude)
    const lat = Cesium.Math.toDegrees(cartographic.latitude)

    // 检查是否已有标记点
    const existingEntity = viewer.entities.values.find(entity => {
      if (entity.position) {
        const entityPos = entity.position.getValue(Cesium.JulianDate.now())
        const entityCartographic = Cesium.Cartographic.fromCartesian(entityPos)
        const entityLon = Cesium.Math.toDegrees(entityCartographic.longitude)
        const entityLat = Cesium.Math.toDegrees(entityCartographic.latitude)
        return Math.abs(entityLon - lon) < 0.001 && Math.abs(entityLat - lat) < 0.001
      }
      return false
    })

    if (existingEntity) {
      alert('该位置已有店铺，请选择其他位置')
      return
    }

    newShop.value.lat = lat
    newShop.value.lon = lon
    showAddShopModal.value = true
  }
}

function closeAddShopModal() {
  showAddShopModal.value = false
  newShop.value = {
    name: '',
    country: '',
    city: '',
    address: '',
    phone: '',
    email: '',
    tags: [],
    lat: 0,
    lon: 0
  }
  newTag.value = ''
}

function addTag() {
  if (newTag.value.trim() && !newShop.value.tags.includes(newTag.value.trim())) {
    newShop.value.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

function removeTag(index) {
  newShop.value.tags.splice(index, 1)
}

async function saveNewShop() {
  if (!newShop.value.name.trim()) {
    alert('请输入店铺名称')
    return
  }

  try {
    const token = localStorage.getItem('token')
    const shopData = {
      name: newShop.value.name,
      country: newShop.value.country,
      city: newShop.value.city,
      address: newShop.value.address,
      phone: newShop.value.phone,
      email: newShop.value.email,
      tags: newShop.value.tags.join(','),
      lat: newShop.value.lat,
      lon: newShop.value.lon,
      visited: false,
      level: ''
    }

    const response = await axios.post('/api/shop/create/', shopData, {
      headers: { Authorization: `Token ${token}` }
    })

    if (response.data.success) {
      // 重新加载数据
      allGeoData.value = await fetchGeoData()
      filteredGeoData.value = allGeoData.value
      updateMapEntities()
      closeAddShopModal()
      addShopMode.value = false
      alert('店铺创建成功！')
    } else {
      alert('创建失败：' + response.data.message)
    }
  } catch (error) {
    console.error('创建店铺失败:', error)
    alert('创建店铺失败')
  }
}

// 导航相关函数
function toggleNavigation() {
  showNavigation.value = !showNavigation.value
}

async function addRoutePoint() {
  if (!newAddress.value.trim()) return

  try {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(newAddress.value)}`)
    const data = await response.json()

    if (data.length > 0) {
      const location = data[0]
      const point = {
        lat: parseFloat(location.lat),
        lon: parseFloat(location.lon),
        address: newAddress.value
      }
      routePoints.value.push(point)
      newAddress.value = ''
    } else {
      alert('未找到该地址')
    }
  } catch (error) {
    console.error('添加路径点失败:', error)
    alert('添加路径点失败')
  }
}

function removeRoutePoint(index) {
  routePoints.value.splice(index, 1)
}

function movePoint(index, direction) {
  if (direction === 'up' && index > 0) {
    const temp = routePoints.value[index]
    routePoints.value[index] = routePoints.value[index - 1]
    routePoints.value[index - 1] = temp
  } else if (direction === 'down' && index < routePoints.value.length - 1) {
    const temp = routePoints.value[index]
    routePoints.value[index] = routePoints.value[index + 1]
    routePoints.value[index + 1] = temp
  }
}

function clearRoutePoints() {
  routePoints.value = []
  routeInfo.value = null

  // 清除路径绘制
  if (routeEntity.value) {
    viewer.entities.remove(routeEntity.value)
    routeEntity.value = null
  }

  // 清除所有路径相关的实体（起点、终点标记等）
  viewer.entities.values.forEach(entity => {
    if (entity.label && (entity.label.text === '起点' || entity.label.text === '终点')) {
      viewer.entities.remove(entity)
    }
  })
}

async function calculateRoute() {
  if (routePoints.value.length < 2) return

  try {
    const coords = routePoints.value.map(point => `${point.lon},${point.lat}`).join(';')

    const routeResponse = await fetch(
      `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`
    )
    const routeData = await routeResponse.json()

    if (routeData.code === 'Ok' && routeData.routes.length > 0) {
      const route = routeData.routes[0]
      routeInfo.value = {
        distance: (route.distance / 1000).toFixed(1) + ' km',
        duration: Math.round(route.duration / 60) + ' 分钟'
      }

      // 绘制路径到地图上
      drawRouteOnMap(route.geometry.coordinates)
    } else {
      alert('路径计算失败')
    }
  } catch (error) {
    console.error('计算路径失败:', error)
    alert('计算路径失败')
  }
}

function openGoogleMaps() {
  if (routeInfo.value && routePoints.value.length >= 2) {
    const origin = `${routePoints.value[0].lat},${routePoints.value[0].lon}`
    const destination = `${routePoints.value[routePoints.value.length - 1].lat},${routePoints.value[routePoints.value.length - 1].lon}`
    const waypoints = routePoints.value.slice(1, -1).map(point => `${point.lat},${point.lon}`).join('|')

    let url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}`
    if (waypoints) {
      url += `&waypoints=${encodeURIComponent(waypoints)}`
    }
    window.open(url, '_blank')
  }
}

function getCurrentLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lon = position.coords.longitude

        // 获取地址信息
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
          .then(response => response.json())
          .then(data => {
            const address = data.display_name || `当前位置 (${lat.toFixed(6)}, ${lon.toFixed(6)})`
            const routePoint = {
              lat: lat,
              lon: lon,
              address: address
            }
            routePoints.value.unshift(routePoint) // 添加到开头作为起点
          })
          .catch(() => {
            const routePoint = {
              lat: lat,
              lon: lon,
              address: `当前位置 (${lat.toFixed(6)}, ${lon.toFixed(6)})`
            }
            routePoints.value.unshift(routePoint)
          })
      },
      (error) => {
        console.error('获取位置失败:', error)
        alert('无法获取当前位置，请检查GPS权限')
      }
    )
  } else {
    alert('您的浏览器不支持地理定位')
  }
}

// 详情弹窗相关函数
function showPointDetails(point) {
  selectedPoint.value = point
  showPointPanel.value = true
}

function closePointPanel() {
  showPointPanel.value = false
  selectedPoint.value = {}
}

function addToRoute(point) {
  const routePoint = {
    lat: point.lat,
    lon: point.lon,
    address: point.address || `${point.lat}, ${point.lon}`
  }
  routePoints.value.push(routePoint)
  closePointPanel()
}

// 绘制路径到地图上
function drawRouteOnMap(coordinates) {
  if (!viewer) return

  // 清除之前的路径
  if (routeEntity.value) {
    viewer.entities.remove(routeEntity.value)
    routeEntity.value = null
  }

  // 将GeoJSON坐标转换为Cesium坐标
  const positions = coordinates.map(coord =>
    Cesium.Cartesian3.fromDegrees(coord[0], coord[1])
  )

  // 创建路径实体
  routeEntity.value = viewer.entities.add({
    polyline: {
      positions: positions,
      width: 6,
      material: new Cesium.PolylineGlowMaterialProperty({
        glowColor: Cesium.Color.CYAN,
        color: Cesium.Color.CYAN,
        taperLength: 0.3
      }),
      clampToGround: true
    }
  })

  // 添加起点和终点标记
  if (positions.length > 0) {
    // 起点标记
    viewer.entities.add({
      position: positions[0],
      point: {
        pixelSize: 12,
        color: Cesium.Color.GREEN,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2
      },
      label: {
        text: '起点',
        font: '14px sans-serif',
        fillColor: Cesium.Color.WHITE,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        showBackground: true,
        backgroundColor: Cesium.Color.GREEN.withAlpha(0.8)
      }
    })

    // 终点标记
    viewer.entities.add({
      position: positions[positions.length - 1],
      point: {
        pixelSize: 12,
        color: Cesium.Color.RED,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2
      },
      label: {
        text: '终点',
        font: '14px sans-serif',
        fillColor: Cesium.Color.WHITE,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        showBackground: true,
        backgroundColor: Cesium.Color.RED.withAlpha(0.8)
      }
    })
  }

  // 调整相机视角以显示整个路径
  viewer.zoomTo(routeEntity.value)
}

// 清除路径绘制
function clearRouteDrawing() {
  if (!viewer || !routeEntity.value) return

  // 清除路径实体
  viewer.entities.remove(routeEntity.value)
  routeEntity.value = null

  // 清除所有路径相关的实体（起点、终点标记等）
  viewer.entities.values.forEach(entity => {
    if (entity.label && (entity.label.text === '起点' || entity.label.text === '终点')) {
      viewer.entities.remove(entity)
    }
  })
}

function createClusterIcon(count) {
  const size = 48
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')
  ctx.beginPath()
  ctx.arc(size/2, size/2, size/2-2, 0, 2*Math.PI)
  ctx.fillStyle = count > 100 ? '#f39c12' : (count > 10 ? '#e67e22' : '#e74c3c')
  ctx.globalAlpha = 0.8
  ctx.fill()
  ctx.globalAlpha = 1
  ctx.font = 'bold 20px sans-serif'
  ctx.fillStyle = '#fff'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(count, size/2, size/2)
  return canvas.toDataURL()
}

onMounted(async () => {
  window.CESIUM_BASE_URL = '/cesium/'
  viewer = new Cesium.Viewer(cesiumContainer.value, {
    timeline: false,
    animation: false,
    baseLayerPicker: true,
    geocoder: false,
    homeButton: true,
    sceneModePicker: true,
    navigationHelpButton: true,
    infoBox: true,
    selectionIndicator: true,
    shouldAnimate: true
  })

  // 地球赤道居中且更大
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(0, 20, 18000000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-90),
      roll: 0
    }
  })

  // 启用点聚合
  viewer.clustering = new Cesium.EntityCluster({
    enabled: true,
    pixelRange: 60,
    minimumClusterSize: 2
  })
  viewer.entities.cluster = viewer.clustering

  // 自定义聚合样式
  viewer.clustering.clusterEvent.addEventListener((clusteredEntities, cluster) => {
    cluster.label.show = true
    cluster.label.text = clusteredEntities.length.toString()
    cluster.label.font = 'bold 20px sans-serif'
    cluster.label.fillColor = Cesium.Color.WHITE
    cluster.billboard.show = true
    cluster.billboard.id = cluster.label.id
    cluster.billboard.image = createClusterIcon(clusteredEntities.length)
  })

  // 加载数据
  allGeoData.value = await fetchGeoData()
  filteredGeoData.value = allGeoData.value
  updateMapEntities()

  // 监听缩放级别，控制label显示
  // viewer.scene.camera.moveEnd.addEventListener(() => {
  //   const height = viewer.scene.camera.positionCartographic.height
  //   viewer.entities.values.forEach(entity => {
  //     if (entity.label) {
  //       entity.label.show = height < 2000000
  //     }
  //   })
  // })

  // 监听地图点击事件
  viewer.screenSpaceEventHandler.setInputAction((event) => {
    const pickedObject = viewer.scene.pick(event.position)
    if (pickedObject && pickedObject.id && pickedObject.id.click) {
      // 点击了实体
      pickedObject.id.click()
    } else {
      // 点击了地图空白区域
      handleMapClick(event)
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)

  // 自动旋转定时器
  rotateHandler = setInterval(() => {
    if (autoRotate && viewer) {
      const height = viewer.scene.camera.positionCartographic.height
      if (height > 6000000) {
        viewer.scene.camera.rotate(Cesium.Cartesian3.UNIT_Z, Cesium.Math.toRadians(0.1))
      }
    }
  }, 30)

  // 鼠标悬停/移出事件
  cesiumContainer.value.addEventListener('mouseenter', () => { autoRotate = false })
  cesiumContainer.value.addEventListener('mouseleave', () => { autoRotate = true })
})

onBeforeUnmount(() => {
  if (viewer) {
    viewer.destroy()
    viewer = null
  }
  if (rotateHandler) {
    clearInterval(rotateHandler)
    rotateHandler = null
  }
})
</script>

<style scoped>
p {
  color: #333;
}
label {
  color: #333;
}

.showcase-page {
  width: 100%;
  height: 100%;
  min-height: 600px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.10);
  padding: 0;
  display: flex;
  flex-direction: column;
  position: relative;
}

.cesium-map {
  width: 100%;
  height: 100%;
  min-height: 480px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(88,166,255,0.08);
  background: #222c36;
  margin: 0 auto;
}

/* 筛选面板 */
.filter-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  max-width: 400px;
  transition: all 0.3s ease;
}

.filter-panel.collapsed {
  max-width: 200px;
  padding: 12px;
}

.filter-panel.collapsed .filter-panel-content {
  display: none;
}

.filter-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.filter-panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.collapse-btn {
  padding: 6px 12px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s ease;
}

.collapse-btn:hover {
  background: #4096ff;
}

.filter-panel-content {
  transition: opacity 0.3s ease;
  padding: 0 0 0 0;
}

.filter-panel:not(.collapsed) {
  padding: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  min-width: 60px;
}

.filter-group select {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.clear-filters-btn {
  width: 100%;
  padding: 8px;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 8px;
}

.clear-filters-btn:hover {
  background: #ff7875;
}

/* 新建店铺面板 */
.add-shop-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.add-shop-btn {
  padding: 12px 20px;
  background: #52c41a;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.add-shop-btn.active {
  background: #ff4d4f;
}

.add-shop-btn:hover {
  opacity: 0.9;
}

.add-shop-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(0,0,0,0.8);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
}

/* 导航面板 */
.navigation-panel {
  position: absolute;
  left: 20px;
  top: 65%;
  transform: translateY(-50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  max-width: 400px;
  min-width: 300px;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: #1677ff;
  color: white;
  border-radius: 8px 8px 0 0;
}

.nav-header h3 {
  margin: 0;
  font-size: 16px;
}

.close-nav-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-nav-btn:hover {
  background: rgba(255,255,255,0.2);
}

.nav-content {
  padding: 16px;
}

.nav-inputs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.nav-inputs input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.nav-inputs button {
  padding: 8px 16px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.route-points-list {
  margin-bottom: 12px;
}

.route-points-list h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.route-point-item {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 4px;
  font-size: 12px;
}

.point-number {
  background: #1677ff;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  margin-right: 8px;
}

.point-address {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.point-actions {
  display: flex;
  gap: 2px;
}

.move-btn, .remove-btn {
  padding: 2px 4px;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  font-size: 10px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.move-btn {
  background: #52c41a;
  color: white;
}

.move-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.remove-btn {
  background: #f5222d;
  color: white;
}

.nav-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.clear-btn, .calculate-btn, .gps-btn, .clear-drawing-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  min-width: 80px;
}

.clear-btn {
  background: #ff4d4f;
  color: white;
}

.calculate-btn {
  background: #52c41a;
  color: white;
}

.gps-btn {
  background: #722ed1;
  color: white;
}

.clear-drawing-btn {
  background: #fa8c16;
  color: white;
}

.clear-btn:disabled, .calculate-btn:disabled, .clear-drawing-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.route-info {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  margin-top: 12px;
}

.route-details p {
  margin: 4px 0;
  font-size: 14px;
}

.google-btn {
  margin-top: 8px;
  padding: 6px 12px;
  background: #34a853;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  width: 100%;
}

/* 筛选面板内的按钮区域 */
.add-shop-section, .navigation-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.add-shop-section {
  margin-bottom: 12px;
}

.nav-toggle-btn {
  width: 100%;
  padding: 8px 16px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.nav-toggle-btn:hover {
  background: #0958d9;
}

/* 详情弹窗 */
.point-panel {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  max-width: 350px;
  min-width: 300px;
  max-height: 80vh;
  overflow: hidden;
}

.point-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: #34a853;
  color: white;
  border-radius: 8px 8px 0 0;
}

.point-panel-header h3 {
  margin: 0;
  font-size: 16px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-btn:hover {
  background: rgba(255,255,255,0.2);
}

.point-panel-content {
  padding: 16px;
  overflow-y: auto;
  max-height: calc(80vh - 60px);
}

.point-details h4 {
  margin: 0 0 12px 0;
  color: #1677ff;
  font-size: 18px;
}

.point-details p {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

.point-image {
  margin: 16px 0;
  text-align: center;
}

.point-image img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.point-actions {
  margin-top: 16px;
  text-align: center;
}

.add-btn {
  padding: 8px 16px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.add-btn:hover {
  background: #0958d9;
}

/* 新建店铺弹窗 */
.add-shop-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e9ecef;
  background: #52c41a;
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-modal-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-modal-btn:hover {
  background: rgba(255,255,255,0.2);
}

.modal-body {
  padding: 16px;
  overflow-y: auto;
  max-height: 60vh;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.tags-input {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.tag {
  background: #1677ff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-input-group {
  display: flex;
  gap: 8px;
}

.tag-input-group input {
  flex: 1;
  margin: 0;
}

.add-tag-btn {
  padding: 8px 12px;
  background: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.coordinates-info {
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  margin-top: 12px;
}

.coordinates-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e9ecef;
}

.cancel-btn, .save-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn {
  background: #f5f5f5;
  color: #333;
}

.save-btn {
  background: #52c41a;
  color: white;
}

.cancel-btn:hover {
  background: #e8e8e8;
}

.save-btn:hover {
  background: #73d13d;
}

@media (max-width: 768px) {
  .filter-panel {
    max-width: 90vw;
    left: 10px;
    right: 10px;
  }

  .navigation-panel {
    max-width: 90vw;
    left: 10px;
    right: 10px;
  }

  .point-panel {
    max-width: 90vw;
    background: #ffffff;
    right: 10px;
    left: 10px;
  }

  .modal-content {
    width: 95%;
  }
}
</style>
