<template>
  <div class="navigation-map-page">
    <div class="search-panel">
      <div class="search-inputs">
        <input v-model="inputLat" placeholder="纬度" type="number" step="any" />
        <input v-model="inputLon" placeholder="经度" type="number" step="any" />
        <button @click="gotoLatLng">定位</button>
      </div>
      <div class="search-address">
        <input v-model="searchAddress" placeholder="搜索地址" />
        <button @click="searchLocation">搜索</button>
      </div>
    </div>

    <div class="map-container" ref="mapContainer"></div>

    <div class="performance-panel" v-if="showPerformance">
      <div class="performance-item">
        <span>标记数量: {{ visibleMarkersCount }}</span>
      </div>
      <div class="performance-item">
        <span>聚合数量: {{ clusterCount }}</span>
      </div>
      <div class="performance-item">
        <span>渲染模式: Canvas</span>
      </div>
    </div>

    <div class="route-panel" :class="{ 'route-panel-open': showRoutePanel }">
      <div class="route-panel-header">
        <h3>路径规划</h3>
        <button @click="toggleRoutePanel" class="toggle-btn">
          {{ showRoutePanel ? '×' : '🗺️' }}
        </button>
      </div>
      <div class="route-panel-content" v-if="showRoutePanel">
        <div class="route-inputs">
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

        <div class="route-actions">
          <button @click="clearRoutePoints" :disabled="routePoints.length === 0" class="clear-btn">清空路径</button>
          <button @click="calculateRoute" :disabled="routePoints.length < 2" class="calculate-btn">计算路径</button>
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

    <div class="point-panel" :class="{ 'point-panel-open': showPointPanel }">
      <div class="point-panel-header">
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

    <div class="zoom-hint" v-if="showZoomHint">
      <p>🔍 放大以显示坐标点</p>
    </div>

    <div class="performance-toggle">
      <button @click="togglePerformance" class="perf-btn">
        {{ showPerformance ? '隐藏' : '显示' }}性能监控
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const mapContainer = ref(null)
const inputLat = ref('')
const inputLon = ref('')
const searchAddress = ref('')
const newAddress = ref('')
const routePoints = ref([])
const routeInfo = ref(null)
const mapPoints = ref([])
const showRoutePanel = ref(false)
const showPointPanel = ref(false)
const selectedPoint = ref({})
const showZoomHint = ref(true)
const showPerformance = ref(false)
const visibleMarkersCount = ref(0)
const clusterCount = ref(0)

let map = null
let markerClusterGroup = null
let routePolyline = null

async function fetchMapData() {
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

function gotoLatLng() {
  const lat = parseFloat(inputLat.value)
  const lon = parseFloat(inputLon.value)
  if (!isNaN(lat) && !isNaN(lon) && map) {
    map.setView([lat, lon], 13)
  }
}

async function searchLocation() {
  if (!searchAddress.value) return

  try {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchAddress.value)}`)
    const data = await response.json()

    if (data.length > 0) {
      const location = data[0]
      const lat = parseFloat(location.lat)
      const lon = parseFloat(location.lon)

      map.setView([lat, lon], 13)
      inputLat.value = lat.toString()
      inputLon.value = lon.toString()
    } else {
      alert('未找到该地址')
    }
  } catch (error) {
    console.error('搜索地址失败:', error)
    alert('搜索地址失败')
  }
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
  if (routePolyline) {
    map.removeLayer(routePolyline)
    routePolyline = null
  }
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

      if (routePolyline) {
        map.removeLayer(routePolyline)
      }

      const coordinates = route.geometry.coordinates.map(coord => [coord[1], coord[0]])
      routePolyline = L.polyline(coordinates, { color: 'blue', weight: 4 })
      routePolyline.addTo(map)

      const startPoint = routePoints.value[0]
      const endPoint = routePoints.value[routePoints.value.length - 1]

      const startMarker = L.marker([startPoint.lat, startPoint.lon], { icon: L.divIcon({ className: 'start-marker', html: '🚗' }) })
      const endMarker = L.marker([endPoint.lat, endPoint.lon], { icon: L.divIcon({ className: 'end-marker', html: '🏁' }) })
      startMarker.addTo(map)
      endMarker.addTo(map)

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

function addToRoute(point) {
  const routePoint = {
    lat: point.lat,
    lon: point.lon,
    address: point.address || `${point.lat}, ${point.lon}`
  }
  routePoints.value.push(routePoint)
}

function showPointDetails(point) {
  selectedPoint.value = point
  showPointPanel.value = true
}

function closePointPanel() {
  showPointPanel.value = false
  selectedPoint.value = {}
}

function toggleRoutePanel() {
  showRoutePanel.value = !showRoutePanel.value
}

function togglePerformance() {
  showPerformance.value = !showPerformance.value
}

function createCanvasMarker(point) {
  // 创建更大的Canvas
  const canvas = document.createElement('canvas')
  canvas.width = 32
  canvas.height = 32
  const ctx = canvas.getContext('2d')

  // 绘制外圈阴影（更大更明显）
  ctx.beginPath()
  ctx.arc(24, 24, 30, 0, 2 * Math.PI)
  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
  ctx.fill()

  // 绘制主圆（更大）
  ctx.beginPath()
  ctx.arc(24, 24, 24, 0, 2 * Math.PI)
  ctx.fillStyle = point.visited === '已拜访' ? '#52c41a' : '#ff4d4f'
  ctx.fill()

  // 绘制白色边框（更粗）
  ctx.strokeStyle = '#fff'
  ctx.lineWidth = 5
  ctx.stroke()

  // 绘制内圈
  ctx.beginPath()
  ctx.arc(32, 32, 16, 0, 2 * Math.PI)
  ctx.fillStyle = point.visited === '已拜访' ? '#73d13d' : '#ff7875'
  ctx.fill()

  // 绘制中心点
  ctx.beginPath()
  ctx.arc(32, 32, 6, 0, 2 * Math.PI)
  ctx.fillStyle = '#fff'
  ctx.fill()

  // 添加状态指示器（更大）
  if (point.visited === '已拜访') {
    // 已拜访：添加对勾
    ctx.beginPath()
    ctx.moveTo(24, 32)
    ctx.lineTo(30, 38)
    ctx.lineTo(40, 26)
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 4
    ctx.stroke()
  } else {
    // 未拜访：添加感叹号
    ctx.beginPath()
    ctx.moveTo(32, 20)
    ctx.lineTo(32, 36)
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 4
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(32, 44, 3, 0, 2 * Math.PI)
    ctx.fillStyle = '#fff'
    ctx.fill()
  }

  // 使用HTML字符串而不是Canvas
  const markerHtml = `
    <div style="
      width: 64px;
      height: 64px;
      background: ${point.visited === '已拜访' ? '#52c41a' : '#ff4d4f'};
      border: 5px solid #fff;
      border-radius: 50%;
      box-shadow: 0 4px 12px rgba(0,0,0,0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: white;
      font-weight: bold;
      position: relative;
    ">
      ${point.visited === '已拜访' ? '✓' : '!'}
    </div>
  `

  const icon = L.divIcon({
    html: markerHtml,
    className: 'custom-marker',
    iconSize: [64, 64],
    iconAnchor: [32, 32]
  })

  return L.marker([point.lat, point.lon], { icon })
}

function loadVisibleMarkers() {
  if (!map || !markerClusterGroup) return

  const zoom = map.getZoom()

  if (zoom < 8) {
    markerClusterGroup.clearLayers()
    visibleMarkersCount.value = 0
    clusterCount.value = 0
    return
  }

  const bounds = map.getBounds()

  markerClusterGroup.clearLayers()

  const visiblePoints = mapPoints.value.filter(point => {
    if (!point.lat || !point.lon) return false
    return bounds.contains([point.lat, point.lon])
  })

  visiblePoints.forEach(point => {
    const marker = createCanvasMarker(point)

    marker.bindPopup(`
      <div style="min-width: 200px;">
        <h4>${point.name}</h4>
        <p><strong>地址：</strong>${point.address || '无'}</p>
        <p><strong>状态：</strong>${point.visited}</p>
        <button onclick="window.showPointDetailsFromPopup('${point.name}')" style="margin-top: 8px; padding: 4px 8px; background: #1677ff; color: white; border: none; border-radius: 4px; cursor: pointer;">查看详情</button>
      </div>
    `)

    markerClusterGroup.addLayer(marker)
  })

  visibleMarkersCount.value = visiblePoints.length
  clusterCount.value = markerClusterGroup.getLayers().length
}

function updateZoomHint() {
  const zoom = map.getZoom()
  showZoomHint.value = zoom < 5
}

onMounted(async () => {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
  document.head.appendChild(link)

  const clusterLink = document.createElement('link')
  clusterLink.rel = 'stylesheet'
  clusterLink.href = 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css'
  document.head.appendChild(clusterLink)

  const script = document.createElement('script')
  script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
  script.onload = () => {
    const clusterScript = document.createElement('script')
    clusterScript.src = 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js'
    clusterScript.onload = async () => {
             map = L.map(mapContainer.value, {
         preferCanvas: true,
         renderer: L.canvas(),
         zoomAnimation: true,
         markerZoomAnimation: true,
         fadeAnimation: true
       }).setView([39.9042, 116.4074], 10)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map)

             markerClusterGroup = L.markerClusterGroup({
         chunkedLoading: true,
         maxClusterRadius: 60,
         spiderfyOnMaxZoom: false,
         showCoverageOnHover: false,
         zoomToBoundsOnClick: true,
         animate: false,
         animateAddingMarkers: false,
         disableClusteringAtZoom: 15,
         iconCreateFunction: function(cluster) {
           const count = cluster.getChildCount()
           let className = 'marker-cluster-'
           
           if (count > 100) {
             className += 'large'
           } else if (count > 10) {
             className += 'medium'
           } else {
             className += 'small'
           }
           
           return L.divIcon({
             html: `<div><span>${count}</span></div>`,
             className: className,
             iconSize: L.point(40, 40)
           })
         }
       })

      map.addLayer(markerClusterGroup)

      const data = await fetchMapData()
      mapPoints.value = data

      loadVisibleMarkers()

             let loadTimeout = null
       const debouncedLoadMarkers = () => {
         if (loadTimeout) clearTimeout(loadTimeout)
         loadTimeout = setTimeout(() => {
           loadVisibleMarkers()
         }, 200)
       }
       
              map.on('moveend', debouncedLoadMarkers)
       map.on('zoomend', () => {
         debouncedLoadMarkers()
         updateZoomHint()
       })
       map.on('viewreset', debouncedLoadMarkers)
       
       updateZoomHint()

      window.showPointDetailsFromPopup = function(pointName) {
        const point = data.find(p => p.name === pointName)
        if (point) {
          showPointDetails(point)
        }
      }

      map.on('click', function(e) {
        if (showRoutePanel.value) {
          const lat = e.latlng.lat
          const lon = e.latlng.lng

          fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
            .then(response => response.json())
            .then(data => {
              const address = data.display_name || `${lat.toFixed(6)}, ${lon.toFixed(6)}`
              const routePoint = {
                lat: lat,
                lon: lon,
                address: address
              }
              routePoints.value.push(routePoint)
            })
            .catch(() => {
              const routePoint = {
                lat: lat,
                lon: lon,
                address: `${lat.toFixed(6)}, ${lon.toFixed(6)}`
              }
              routePoints.value.push(routePoint)
            })
        }
      })
    }
    document.head.appendChild(clusterScript)
  }
  document.head.appendChild(script)
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
  }
  if (window.showPointDetailsFromPopup) {
    delete window.showPointDetailsFromPopup
  }
})
</script>

<style scoped>
.navigation-map-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.10);
  overflow: hidden;
  position: relative;
}

.search-panel {
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.search-inputs, .search-address {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-inputs input, .search-address input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  width: 120px;
}

.search-address input {
  width: 200px;
}

.search-panel button {
  padding: 8px 16px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.search-panel button:hover {
  background: #0958d9;
}

.map-container {
  flex: 1;
  min-height: 400px;
  position: relative;
}

.performance-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12px;
  border-radius: 8px;
  z-index: 1000;
  font-size: 12px;
}

.performance-item {
  margin: 4px 0;
}

.performance-toggle {
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.perf-btn {
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.perf-btn:hover {
  background: rgba(0, 0, 0, 0.9);
}

.route-panel {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  transition: all 0.3s ease;
  max-width: 300px;
  min-width: 250px;
}

.route-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: #1677ff;
  color: white;
  border-radius: 8px 8px 0 0;
}

.route-panel-header h3 {
  margin: 0;
  font-size: 16px;
}

.toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.toggle-btn:hover {
  background: rgba(255,255,255,0.2);
}

.route-panel-content {
  padding: 16px;
}

.route-inputs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.route-inputs input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.route-inputs button {
  padding: 8px 16px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.route-inputs button:disabled {
  background: #ccc;
  cursor: not-allowed;
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

.route-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.clear-btn, .calculate-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.clear-btn {
  background: #ff4d4f;
  color: white;
}

.clear-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.calculate-btn {
  background: #52c41a;
  color: white;
}

.calculate-btn:disabled {
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
}

.point-panel {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  transition: all 0.3s ease;
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
  background: #52c41a;
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

.zoom-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0,0,0,0.8);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  z-index: 500;
  font-size: 14px;
  text-align: center;
}

.custom-marker {
  background: transparent !important;
  border: none !important;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.6));
  transition: all 0.3s ease;
  z-index: 1000 !important;
}

.custom-marker:hover {
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.8));
  transform: scale(1.3);
}

/* 确保标记点始终可见 */
.leaflet-marker-icon {
  z-index: 1000 !important;
}

.leaflet-marker-shadow {
  display: none !important;
}

/* 强制显示自定义标记 */
.custom-marker div {
  z-index: 1000 !important;
  position: relative !important;
}

.start-marker {
  background: #52c41a;
  border-radius: 50%;
  width: 20px !important;
  height: 20px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.end-marker {
  background: #f5222d;
  border-radius: 50%;
  width: 20px !important;
  height: 20px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.marker-cluster-small {
  background-color: rgba(181, 226, 140, 0.6);
}

.marker-cluster-small div {
  background-color: rgba(110, 204, 57, 0.6);
}

.marker-cluster-medium {
  background-color: rgba(241, 211, 87, 0.6);
}

.marker-cluster-medium div {
  background-color: rgba(240, 194, 12, 0.6);
}

.marker-cluster-large {
  background-color: rgba(253, 156, 115, 0.6);
}

.marker-cluster-large div {
  background-color: rgba(241, 128, 23, 0.6);
}

.marker-cluster-small div,
.marker-cluster-medium div,
.marker-cluster-large div {
  color: white;
  font-weight: bold;
  text-align: center;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .route-panel, .point-panel {
    max-width: 90vw;
    min-width: 250px;
  }

  .search-panel {
    flex-direction: column;
    gap: 8px;
  }

  .search-inputs, .search-address {
    width: 100%;
  }

  .search-inputs input, .search-address input {
    flex: 1;
  }

  .performance-panel {
    top: 10px;
    right: 10px;
    font-size: 10px;
  }

  .performance-toggle {
    bottom: 10px;
    right: 10px;
  }
}
</style>
