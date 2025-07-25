<!-- 地图页面组件 -->
<template>
  <div class="map-page">
    <div class="latlng-search">
      <input v-model="inputLat" placeholder="纬度" type="number" step="any" />
      <input v-model="inputLon" placeholder="经度" type="number" step="any" />
      <button @click="gotoLatLng">定位</button>
    </div>
    <div class="route-sidebar">
      <h3>路径点列表</h3>
      <ul>
        <li v-for="(pt, idx) in routePoints" :key="idx">
          {{ pt.name || (pt.lat + ',' + pt.lon) }}
          <button @click="removePoint(idx)">删除</button>
        </li>
      </ul>
      <button class="plan-btn" style="background:#888;margin-bottom:8px;" :disabled="routePoints.length===0" @click="clearRoutePoints">一键清空</button>
      <button class="plan-btn" :disabled="routePoints.length < 2" @click="planRoute">路径规划</button>
    </div>
<!--    <div class="plan-btn-top">-->
<!--      <button class="plan-btn" :disabled="routePoints.length < 2" @click="planRoute">路径规划</button>-->
<!--    </div>-->
    <div class="cesium-map" ref="cesiumContainer"></div>
    <!-- Google Maps 弹窗 -->
    <div v-if="showGoogleLink" class="google-link-mask">
      <div class="google-link-dialog">
        <div class="google-link-title">Google Maps 导航链接</div>
        <div class="google-link-content">
          <a :href="googleMapsUrl" target="_blank" style="color:#1677ff;font-size:1.1rem;word-break:break-all;">点击打开谷歌地图导航</a>
        </div>
        <div class="google-link-actions">
          <button @click="showGoogleLink=false" class="google-link-btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as Cesium from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import axios from 'axios'

const cesiumContainer = ref(null)
let viewer = null
let autoRotate = true
let rotateHandler = null
const inputLat = ref('')
const inputLon = ref('')

// 路径规划相关
const routePoints = ref([])
const plannedRoute = ref(null)
const carEntity = ref(null)
const isAnimating = ref(false)
let animationHandler = null
const showGoogleLink = ref(false)
const googleMapsUrl = ref('')

function addRoutePoint(lon, lat, name) {
  routePoints.value.push({ lon, lat, name })
}
function removePoint(idx) {
  routePoints.value.splice(idx, 1)
}

function clearRoutePoints() {
  routePoints.value = []
}

// 计算两点间距离（经纬度欧氏距离，适合小范围）
function calcDistance(a, b) {
  const dx = a.lon - b.lon
  const dy = a.lat - b.lat
  return Math.sqrt(dx * dx + dy * dy)
}
// 暴力TSP（点数≤8）
function tspBruteForce(points) {
  const n = points.length
  if (n <= 2) return points.map((_, i) => i)
  let minOrder = null
  let minDist = Infinity
  function permute(arr, l) {
    if (l === n) {
      let dist = 0
      for (let i = 1; i < n; ++i) dist += calcDistance(points[arr[i-1]], points[arr[i]])
      if (dist < minDist) {
        minDist = dist
        minOrder = arr.slice()
      }
      return
    }
    for (let i = l; i < n; ++i) {
      const newArr = arr.slice()
      ;[newArr[l], newArr[i]] = [newArr[i], newArr[l]]
      permute(newArr, l+1)
    }
  }
  permute([...Array(n).keys()], 0)
  return minOrder || points.map((_, i) => i)
}
// 贪心TSP（点数>8）
function tspGreedy(points) {
  const n = points.length
  const visited = Array(n).fill(false)
  const order = [0]
  visited[0] = true
  for (let step = 1; step < n; ++step) {
    let last = order[order.length-1]
    let minDist = Infinity, next = -1
    for (let i = 0; i < n; ++i) {
      if (!visited[i]) {
        let d = calcDistance(points[last], points[i])
        if (d < minDist) {
          minDist = d
          next = i
        }
      }
    }
    order.push(next)
    visited[next] = true
  }
  return order
}

async function planRoute() {
  if (routePoints.value.length < 2) return
  // 1. 计算TSP最优顺序
  let order
  if (routePoints.value.length <= 8) {
    order = tspBruteForce(routePoints.value)
  } else {
    order = tspGreedy(routePoints.value)
  }
  if (!Array.isArray(order) || order.length !== routePoints.value.length) {
    order = routePoints.value.map((_, i) => i)
  }
  const sortedPoints = order.map(idx => routePoints.value[idx])
  // 2. 构造OSRM /route请求
  const coords = sortedPoints.map(pt => `${pt.lon},${pt.lat}`).join(';')
  const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`
  const res = await fetch(url)
  const data = await res.json()
  if (data.code !== 'Ok' || !data.routes || data.routes.length === 0) {
    alert('路径规划失败：' + (data.message || '请检查点的选择或稍后重试'))
    return
  }
  plannedRoute.value = data.routes[0].geometry.coordinates
  routePoints.value = sortedPoints
  drawRouteOnMap(plannedRoute.value)
  animateCar(plannedRoute.value)

  // 生成Google Maps多点导航URL并弹窗（不自动跳转）
  if (sortedPoints.length >= 2) {
    const origin = `${sortedPoints[0].lat},${sortedPoints[0].lon}`
    const destination = `${sortedPoints[sortedPoints.length-1].lat},${sortedPoints[sortedPoints.length-1].lon}`
    const waypoints = sortedPoints.slice(1, -1).map(pt => `${pt.lat},${pt.lon}`).join('|')
    let gUrl = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}`
    if (waypoints) {
      gUrl += `&waypoints=${encodeURIComponent(waypoints)}`
    }
    googleMapsUrl.value = gUrl
    showGoogleLink.value = true
  }
}

function drawRouteOnMap(coords) {
  if (!viewer) return
  // 清除旧路径
  const old = viewer.entities.getById('osrm-route')
  if (old) viewer.entities.remove(old)
  // 绘制新路径
  const positions = coords.map(([lon, lat]) => Cesium.Cartesian3.fromDegrees(lon, lat))
  viewer.entities.add({
    id: 'osrm-route',
    polyline: {
      positions,
      width: 6,
      material: Cesium.Color.BLUE.withAlpha(0.7),
      clampToGround: true
    }
  })
}

function animateCar(coords) {
  if (!viewer) return
  if (carEntity.value) {
    viewer.entities.remove(carEntity.value)
    carEntity.value = null
  }
  const positions = coords.map(([lon, lat]) => Cesium.Cartesian3.fromDegrees(lon, lat))
  let idx = 0
  carEntity.value = viewer.entities.add({
    position: positions[0],
    billboard: {
      image: '/car.png', // 你需要准备一张小车图片
      width: 38,
      height: 38
    }
  })
  isAnimating.value = true
  if (animationHandler) clearInterval(animationHandler)
  animationHandler = setInterval(() => {
    idx++
    if (idx >= positions.length) {
      clearInterval(animationHandler)
      isAnimating.value = false
      return
    }
    carEntity.value.position = positions[idx]
  }, 40)
}

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

function gotoLatLng() {
  const lat = parseFloat(inputLat.value)
  const lon = parseFloat(inputLon.value)
  if (!isNaN(lat) && !isNaN(lon) && viewer) {
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(lon, lat, 200), // 更近的高度
      orientation: {
        heading: Cesium.Math.toRadians(0),
        pitch: Cesium.Math.toRadians(-90), // 俯视
        roll: 0
      },
      duration: 1.2 // 动画更快
    })
  }
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
    destination: Cesium.Cartesian3.fromDegrees(0, 20, 18000000), // 纬度20度上空，距离调小地球更大
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

  // 加载数据点
  const geoData = await fetchGeoData()
  geoData.forEach(item => {
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
      // 点击点添加到路径点列表
      entity.point._id = item.name
      entity._lon = item.lon
      entity._lat = item.lat
      entity._name = item.name
      entity._isRouteSelectable = true
    }
  })

  // 监听缩放级别，控制label显示
  viewer.scene.camera.moveEnd.addEventListener(() => {
    const height = viewer.scene.camera.positionCartographic.height
    viewer.entities.values.forEach(entity => {
      if (entity.label) {
        entity.label.show = height < 2000000 // 你可以根据实际调整这个阈值
      }
    })
  })

  // 自动旋转定时器
  rotateHandler = setInterval(() => {
    if (autoRotate && viewer) {
      const height = viewer.scene.camera.positionCartographic.height
      if (height > 6000000) { // 只有缩小时才自动旋转
        viewer.scene.camera.rotate(Cesium.Cartesian3.UNIT_Z, Cesium.Math.toRadians(0.1))
      }
    }
  }, 30)

  // 鼠标悬停/移出事件
  cesiumContainer.value.addEventListener('mouseenter', () => { autoRotate = false })
  cesiumContainer.value.addEventListener('mouseleave', () => { autoRotate = true })

  // 监听地图点击事件
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  handler.setInputAction(function(click) {
    const picked = viewer.scene.pick(click.position)
    if (picked && picked.id && picked.id._isRouteSelectable) {
      addRoutePoint(picked.id._lon, picked.id._lat, picked.id._name)
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
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
  if (animationHandler) {
    clearInterval(animationHandler)
    animationHandler = null
  }
})
</script>

<style scoped>
.map-page {
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
.latlng-search {
  position: absolute;
  top: 24px;
  left: 36px;
  z-index: 100;
  background: rgba(255,255,255,0.97);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(88,166,255,0.13);
  padding: 12px 38px;
  display: flex;
  gap: 10px;
  align-items: center;
  min-width: 420px;
  max-width: 600px;
}
.latlng-search input {
  width: 150px;
  padding: 7px 10px;
  border: 1.5px solid #b3d6ff;
  border-radius: 6px;
  font-size: 1rem;
}
.latlng-search button {
  padding: 7px 18px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
}
.latlng-search button:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
}
.route-sidebar {
  position: absolute;
  left: 24px;
  top: 120px;
  z-index: 200;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(88,166,255,0.13);
  padding: 18px 24px 18px 24px;
  min-width: 220px;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.route-sidebar h3 {
  margin: 0 0 8px 0;
  font-size: 1.12rem;
  color: #1765d8;
  font-weight: 700;
}
.route-sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0 0 12px 0;
}
.route-sidebar li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 1.05rem;
  border-bottom: 1px solid #e0eaff;
}
.route-sidebar button {
  padding: 4px 12px;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.98rem;
  font-weight: 600;
  cursor: pointer;
  margin-left: 8px;
  transition: background 0.2s;
}
.route-sidebar button:hover {
  background: #c0392b;
}
.plan-btn-top {
  position: absolute;
  right: 36px;
  top: 24px;
  z-index: 200;
}
.plan-btn {
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
.plan-btn:disabled {
  background: #b3d6ff;
  cursor: not-allowed;
}
.plan-btn:not(:disabled):hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
}
.google-link-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.google-link-dialog {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(88,166,255,0.18);
  padding: 32px 38px 24px 38px;
  min-width: 320px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.google-link-title {
  font-size: 1.18rem;
  font-weight: 700;
  color: #1765d8;
  margin-bottom: 18px;
}
.google-link-content {
  margin-bottom: 18px;
  text-align: center;
}
.google-link-btn {
  padding: 7px 28px;
  background: linear-gradient(90deg, #58a6ff, #1677ff);
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(88,166,255,0.10);
  transition: background 0.2s, box-shadow 0.2s;
}
.google-link-btn:hover {
  background: linear-gradient(90deg, #1677ff, #58a6ff);
}
</style>
