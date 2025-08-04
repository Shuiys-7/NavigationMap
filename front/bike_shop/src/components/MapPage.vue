<!-- 展示页面组件 - 3D地球展示 -->
<template>
  <div class="showcase-page">
    <div class="cesium-map" ref="cesiumContainer"></div>
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
</style>
