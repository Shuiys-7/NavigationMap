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
      <div v-if="loading" class="loading-indicator">
        <i class="fas fa-spinner fa-spin"></i> 加载中...
      </div>
      <div class="table-container">
        <table class="visit-table">
        <thead>
          <tr>
            <th>拜访ID</th>
            <th>拜访对象</th>
            <th>时间</th>
            <th>商店备注</th>
            <th>标签</th>
          </tr>
        </thead>
        <tbody>
        <tr v-for="item in visitList" :key="item.id" :class="{selected: selectedVisit && selectedVisit.id === item.id}" @click="selectVisit(item)">
          <td>{{ item.id }}</td>
          <td>
            <div class="shop-name-cell">
              <i class="fas fa-store shop-icon"></i>
              {{ item.shop__name }}
            </div>
          </td>
          <td>
            <div class="time-cell">
              <i class="fas fa-clock time-icon"></i>
              {{ formatDateTime(item.visit_time) }}
            </div>
          </td>

          <td>
            <div class="notes-cell" :title="item.shop_note">
              {{ item.shop_note || '无商店备注' }}
            </div>
          </td>
          <td>
            <div class="visit-tags">
              <!-- 调试信息已移除 -->

              <!-- 标签处理逻辑 -->
              <span v-for="(tag, index) in (item.tags && typeof item.tags === 'string' ? item.tags.split(',').filter(t => t.trim()) : [])"
                    :key="index"
                    class="visit-tag"
                    style="display: inline-block !important; margin-right: 5px; margin-bottom: 5px;">
                <i class="fas fa-tag tag-icon-small"></i>
                {{ tag }}
              </span>
              <span v-if="!item.tags || typeof item.tags !== 'string' || item.tags.split(',').filter(tag => tag && tag.trim()).length === 0" class="no-tags">
                无标签
              </span>
              <!-- 测试标签已移除 -->
            </div>
          </td>
        </tr>
          <tr v-if="visitList.length === 0 && !loading">
            <td colspan="5" class="no-data-cell">
              <i class="fas fa-info-circle"></i> 暂无拜访记录
            </td>
          </tr>
        </tbody>
      </table>
      </div>
      <!-- 分页控件 -->

    </div>
    <div class="visit-pagination">
      <div class="pagination-left">
        <span>共 {{ total }} 条记录</span>
      </div>
      <div class="pagination-center">
        <button
          class="pagination-btn"
          :disabled="page===1 || loading"
          @click="gotoPage(page-1)"
          :class="{disabled: page===1 || loading}"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        <span class="page-info">
            <span>第</span>
            <input
              v-model.number="page"
              class="page-input"
              @keyup.enter="gotoPage(page)"
              :disabled="loading"
            />
            <span>/ {{ Math.max(1, Math.ceil(total / pageSize)) }} 页</span>
          </span>
        <button
          class="pagination-btn"
          :disabled="page===Math.max(1, Math.ceil(total / pageSize)) || loading"
          @click="gotoPage(page+1)"
          :class="{disabled: page===Math.max(1, Math.ceil(total / pageSize)) || loading}"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
      <div class="pagination-right">
        <span>每页</span>
        <select
          v-model.number="pageSize"
          @change="onPageSizeChange"
          :disabled="loading"
          class="page-size-select"
        >
          <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
        </select>
        <span>条</span>
      </div>
    </div>
    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteDialog" class="delete-dialog-mask">
      <div class="delete-dialog">
        <div class="delete-dialog-title">确认删除</div>
        <div class="delete-dialog-msg">确定要删除该拜访记录吗？</div>
        <div class="delete-dialog-actions">
          <button class="delete-dialog-btn confirm" @click="confirmDelete" :disabled="loading">
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <span v-else>确认</span>
          </button>
          <button class="delete-dialog-btn cancel" @click="showDeleteDialog = false" :disabled="loading">取消</button>
        </div>
      </div>
    </div>
    <!-- 添加拜访弹窗 -->
    <div v-if="showDialog" class="visit-dialog-mask" @mousedown.self="closeDropdown">
      <div class="visit-dialog">
        <div class="dialog-header">
          <div class="dialog-title">
            <i class="fas fa-plus-circle"></i> 新建拜访
          </div>
          <button class="dialog-close" @click="closeDialog">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="dialog-body">
          <div class="dialog-grid">
            <!-- 左侧 -->
            <div class="dialog-column">
              <div class="form-item">
                <label><i class="fas fa-user"></i> 用户名</label>
                <div class="user-info">
                  <div class="user-avatar">{{ user?.username?.charAt(0).toUpperCase() || '?' }}</div>
                  <input :value="user?.username || ''" disabled class="input disabled" />
                </div>
              </div>

              <div class="form-item">
                <label><i class="fas fa-store"></i> 拜访商店</label>
                <div class="shop-search">
                  <input
                    v-model="shopInput"
                    @input="onShopInput"
                    @focus="shopDropdownVisible = true"
                    placeholder="输入商店名搜索..."
                    class="input"
                  />
                  <i class="fas fa-search search-icon"></i>
                </div>
                <div class="dropdown" v-if="shopDropdownVisible && filteredShops.length">
                  <ul>
                    <li
                      v-for="shop in filteredShops"
                      :key="shop.id"
                      @click="selectShop(shop)"
                    >
                      <i class="fas fa-store shop-icon"></i>
                      <div class="shop-info">
                        <div class="shop-name">{{ shop.name }}</div>
                        <div v-if="shop.address" class="shop-address">{{ shop.address }}</div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>


            </div>

            <!-- 右侧 -->
            <div class="dialog-column">
              <div class="form-item">
                <label><i class="fas fa-tags"></i> 标签选择</label>
                <div class="tags-select">
                  <label
                    v-for="tag in allTags"
                    :key="tag.id"
                    class="tag-option"
                    :class="{ selected: selectedTags.includes(tag.id) }"
                  >
                    <input type="checkbox" :value="tag.id" v-model="selectedTags" />
                    <span class="tag-name">{{ tag.name }}</span>
                  </label>
                </div>
              </div>

              <div class="form-item">
                <label><i class="fas fa-plus-circle"></i> 自定义标签</label>
                <div class="custom-tag">
                  <input
                    v-model="customTag"
                    placeholder="创建新标签..."
                    @keyup.enter="addCustomTag"
                    class="input"
                  />
                  <button @click="addCustomTag" class="btn add-tag-btn" :disabled="!customTag.trim() || loading">
                    <i class="fas fa-plus"></i>
                    {{ loading ? '添加中...' : '添加' }}
                  </button>
                </div>
              </div>

              <div class="form-item">
                <label><i class="fas fa-check-circle"></i> 已选标签</label>
                <div class="selected-tags">
                  <span v-if="selectedTags.length === 0" class="no-tags">
                    <i class="fas fa-info-circle"></i> 暂无已选标签
                  </span>
                  <span v-for="(tagId, index) in selectedTags" :key="index" class="tag">
                    <span class="tag-text">{{ allTags.find(t => t.id === tagId)?.name || '未知标签' }}</span>
                    <button @click="removeTag(index)" class="remove-tag" title="移除标签">
                      <i class="fas fa-times"></i>
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="dialog-footer">
          <button class="btn cancel" @click="closeDialog">
            <i class="fas fa-times"></i> 取消
          </button>
          <button class="btn primary" @click="submitVisit">
            <i class="fas fa-check"></i> 提交拜访
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
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
// 文件上传相关变量已移除
const showDialog = ref(false)
const dialogMsg = ref('')
const selectedVisit = ref(null)
const showDeleteDialog = ref(false)
const loading = ref(false) // 加载状态
const isMobile = ref(false) // 移动设备检测

// 标签相关
const allTags = ref([])
const selectedTags = ref([])
const customTag = ref('')

// 分页相关
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const pageSizes = [5, 10, 20, 50, 100]

// 检测是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
}

// 监听窗口大小变化
onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile);
})

async function fetchVisitList() {
  const token = localStorage.getItem('token')
  if (!token) {
    console.error('未找到登录令牌，请先登录')
    return
  }

  loading.value = true // 开始加载

  try {
    const res = await axios.get('/api/visit-shop-list', {
      params: { page: page.value, page_size: pageSize.value },
      headers: { Authorization: `Token ${token}` }
    })
    console.log('拜访数据:', res.data) // 添加日志，帮助调试
    // 打印每条记录的标签信息，帮助调试
    if (Array.isArray(res.data.data)) {
      res.data.data.forEach(item => {
        console.log(`记录ID: ${item.id}, 标签: ${item.tags}`)
        // 确保标签是字符串类型
        if (item.tags && typeof item.tags !== 'string') {
          item.tags = String(item.tags)
          console.log(`转换后的标签: ${item.tags}`)
        }
      })
    } else if (Array.isArray(res.data)) {
      res.data.forEach(item => {
        console.log(`记录ID: ${item.id}, 标签: ${item.tags}`)
        // 确保标签是字符串类型
        if (item.tags && typeof item.tags !== 'string') {
          item.tags = String(item.tags)
          console.log(`转换后的标签: ${item.tags}`)
        }
      })
    }

    // 检查返回数据格式
    if (res.data && typeof res.data === 'object') {
      // 确保data字段是数组
      if (Array.isArray(res.data.data)) {
        // 处理每条记录的标签
        const processedData = res.data.data.map(item => {
          // 确保标签是字符串类型
          if (item.tags === null || item.tags === undefined) {
            item.tags = ''
          } else if (typeof item.tags !== 'string') {
            item.tags = String(item.tags)
          }
          return item
        })
        visitList.value = processedData
        total.value = res.data.total || 0
        console.log(`成功获取${visitList.value.length}条拜访记录，总计${total.value}条`)
      } else if (Array.isArray(res.data)) {
        // 兼容直接返回数组的情况
        // 处理每条记录的标签
        const processedData = res.data.map(item => {
          // 确保标签是字符串类型
          if (item.tags === null || item.tags === undefined) {
            item.tags = ''
          } else if (typeof item.tags !== 'string') {
            item.tags = String(item.tags)
          }
          return item
        })
        visitList.value = processedData
        total.value = res.data.length
        console.log(`成功获取${visitList.value.length}条拜访记录（直接数组）`)
      } else {
        console.error('返回数据格式不正确，data不是数组:', res.data)
        visitList.value = []
        total.value = 0
        dialogMsg.value = '获取拜访数据失败：数据格式不正确'
      }
    } else {
      console.error('返回数据格式不正确:', res.data)
      visitList.value = []
      total.value = 0
      dialogMsg.value = '获取拜访数据失败：返回数据格式不正确'
    }
  } catch (error) {
    console.error('获取拜访列表失败:', error) // 添加错误日志
    visitList.value = []
    total.value = 0
    dialogMsg.value = `获取拜访数据失败：${error.message || '未知错误'}`
  } finally {
    loading.value = false // 结束加载
  }
}

function gotoPage(n) {
  if (loading.value) return // 如果正在加载，不执行操作

  if (n < 1) n = 1
  const totalPages = Math.max(1, Math.ceil(total.value / pageSize.value))
  if (n > totalPages) n = totalPages

  if (page.value === n) return // 如果页码没变，不执行操作

  page.value = n
  fetchVisitList()
}

function onPageSizeChange() {
  if (loading.value) return // 如果正在加载，不执行操作

  page.value = 1
  fetchVisitList()
}

// 获取商店列表
async function fetchShopList() {
  const token = localStorage.getItem('token')
  if (!token) {
    console.error('获取商店列表失败：未找到认证令牌')
    return
  }

  // 不设置全局loading，因为这是初始化操作，不应阻止用户其他交互
  try {
    const res = await axios.get('/api/data-list', {
      params: { page: 1, page_size: 10000 }, // 获取所有商店
      headers: { Authorization: `Token ${token}` }
    })

    if (res.data && Array.isArray(res.data.data)) {
      shopList.value = res.data.data
      // console.log(`成功获取${shopList.value.length}条商店记录`)
    } else {
      console.error('商店数据格式不正确:', res.data)
      shopList.value = []
    }
  } catch (error) {
    console.error('获取商店列表失败:', error)
    shopList.value = []
  }
}

// 获取标签列表
async function fetchTags() {
  const token = localStorage.getItem('token')
  if (!token) {
    console.error('获取标签失败：未找到认证令牌')
    return
  }

  // 不设置全局loading，因为这是初始化操作，不应阻止用户其他交互
  try {
    const res = await axios.get('/api/tag_list', { headers: { Authorization: `Token ${token}` } })
    if (res.data && res.data.tags) {
      allTags.value = res.data.tags || []
      console.log(`成功获取${allTags.value.length}个标签`)
    } else {
      console.error('获取标签失败：返回数据格式不正确', res.data)
    }
  } catch (error) {
    console.error('获取标签失败', error)
    // 不显示错误消息，因为这不是用户直接操作
  }
}

// 添加自定义标签
async function addCustomTag() {
  const tag = customTag.value.trim()
  if (!tag || loading.value) return

  // 检查是否已存在相同标签
  if (allTags.value.some(t => t.name.toLowerCase() === tag.toLowerCase())) {
    dialogMsg.value = '标签已存在'
    return
  }

  loading.value = true // 开始加载
  dialogMsg.value = '添加标签中...'

  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('/api/tag_add', { name: tag }, {
      headers: {
        Authorization: `Token ${token}`
      }
    })

    const newTag = res.data.tag  // 取正确的标签对象
    allTags.value.push(newTag)   // 添加到所有标签列表
    selectedTags.value.push(newTag.id)  // 添加到选中标签数组
    customTag.value = ''  // 清空输入框
    dialogMsg.value = '标签添加成功'
    setTimeout(() => {
      if (dialogMsg.value === '标签添加成功') dialogMsg.value = ''
    }, 2000)

  } catch (error) {
    console.error('添加标签失败', error)
    dialogMsg.value = '添加标签失败：' + (error.response?.data?.error || error.message || '未知错误')
  } finally {
    loading.value = false // 结束加载
  }
}

// 移除标签
function removeTag(index) {
  // 如果正在加载，不执行操作
  if (loading.value) return

  selectedTags.value.splice(index, 1);
}

// 获取用户、商店列表和标签
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    console.error('未找到登录令牌，请先登录')
    dialogMsg.value = '请先登录后再访问此页面'
    return
  }

  loading.value = true // 开始加载

  try {
    // 并行获取用户数据
    const getUserData = async () => {
      try {
        const res = await axios.get('/api/user-data', { headers: { Authorization: `Token ${token}` } })
        if (res.data) {
          user.value = res.data
          // console.log('用户数据:', user.value)
        } else {
          console.error('获取用户数据失败: 返回数据为空')
        }
      } catch (error) {
        console.error('获取用户数据失败:', error)
      }
    }

    // 并行获取所有数据
    await Promise.all([
      getUserData(),
      fetchShopList(),
      fetchTags(),
      fetchVisitList()
    ])
  } catch (error) {
    console.error('初始化数据失败:', error)
    dialogMsg.value = '加载数据失败，请刷新页面重试'
  } finally {
    loading.value = false // 结束加载
  }
})

function onShopInput() {
  // 如果正在加载，不执行操作
  if (loading.value) return

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
  // 如果正在加载，不执行操作
  if (loading.value) return

  selectedShop.value = shop
  shopInput.value = shop.name
  shopDropdownVisible.value = false
  
  // 如果店铺有标签，加载到已选标签中
  if (shop.tags && typeof shop.tags === 'string' && shop.tags.trim() !== '') {
    // 清空当前已选标签
    selectedTags.value = []
    
    // 将店铺标签字符串分割为数组
    const shopTagNames = shop.tags.split(',').map(tag => tag.trim()).filter(Boolean)
    
    // 将标签名称转换为标签ID并添加到已选标签中
    shopTagNames.forEach(tagName => {
      const tag = allTags.value.find(t => t.name.toLowerCase() === tagName.toLowerCase())
      if (tag) {
        selectedTags.value.push(tag.id)
      }
    })
    
    if (selectedTags.value.length > 0) {
      dialogMsg.value = '已加载店铺标签'
      setTimeout(() => {
        if (dialogMsg.value === '已加载店铺标签') dialogMsg.value = ''
      }, 2000)
    }
  }
}
// 文件变更函数已移除
function closeDialog() {
  // 如果正在加载，不执行操作
  if (loading.value) return

  // 重置所有状态
  showDialog.value = false
  shopInput.value = ''
  selectedShop.value = null
  dialogMsg.value = ''
  selectedTags.value = [] // 清空选中标签
  customTag.value = '' // 清空自定义标签输入
  shopDropdownVisible.value = false // 关闭下拉列表
  filteredShops.value = [] // 清空筛选结果
}
function closeDropdown() {
  // 如果正在加载，不执行操作
  if (loading.value) return

  shopDropdownVisible.value = false;
}
async function submitVisit() {
  if (!selectedShop.value) return
  if (loading.value) return // 如果正在加载，不执行操作

  loading.value = true // 开始加载
  dialogMsg.value = '正在提交...'
  const token = localStorage.getItem('token')

  try {
    // 使用默认图片或商店现有图片
    let newImgName = selectedShop.value.image ? selectedShop.value.image.split('/').pop() : 'default_shop.jpg'

    // 1. 更新商店标签（如果有选择标签）
    if (selectedTags.value.length > 0) {
      try {
        // 将标签ID转换为标签名称的逗号分隔字符串
        const tagNames = selectedTags.value.map(tagId => {
          const tag = allTags.value.find(t => t.id === tagId)
          return tag ? tag.name : ''
        }).filter(Boolean).join(',')

        // 更新商店信息，包括标签
        await axios.post('/api/update-shop', {
          shop_id: selectedShop.value.id,
          tags: tagNames
        }, { headers: { Authorization: `Token ${token}` } })
      } catch (error) {
        console.error('更新商店标签失败', error)
        // 继续执行，不中断流程
      }
    }

    // 2. 添加拜访记录
    await axios.post('/api/add-visit', {
      shop_id: selectedShop.value.id,
      shop_name: selectedShop.value.name,
      image: newImgName,
      tags: selectedTags.value // 添加标签IDs
    }, { headers: { Authorization: `Token ${token}` } })

    dialogMsg.value = '拜访添加成功！'

    // 成功后刷新数据，而不是重新加载页面
    setTimeout(async () => {
      await fetchVisitList() // 刷新拜访列表
      closeDialog() // 关闭弹窗
    }, 1200)
  } catch (error) {
    console.error('添加拜访记录失败', error)
    dialogMsg.value = '拜访记录添加失败：' + (error.response?.data?.error || error.message || '未知错误')
  } finally {
    loading.value = false // 结束加载
  }
}

function selectVisit(item) {
  if (loading.value) return // 如果正在加载，不执行操作

  if (selectedVisit.value && selectedVisit.value.id === item.id) {
    selectedVisit.value = null
  } else {
    selectedVisit.value = item
  }
}

async function deleteVisit() {
  if (!selectedVisit.value || loading.value) return

  loading.value = true // 开始加载
  dialogMsg.value = '正在删除...' // 显示删除中的消息

  const token = localStorage.getItem('token')
  try {
    await axios.post('/api/delete-visit', { visit_id: selectedVisit.value.id }, { headers: { Authorization: `Token ${token}` } })
    selectedVisit.value = null
    dialogMsg.value = '删除成功'
    setTimeout(() => {
      if (dialogMsg.value === '删除成功') dialogMsg.value = ''
    }, 2000)
    await fetchVisitList()
  } catch (error) {
    console.error('删除拜访记录失败:', error)
    dialogMsg.value = '删除失败，请重试'
  } finally {
    loading.value = false // 结束加载
  }
}

function onDeleteClick() {
  if (!selectedVisit.value || loading.value) return
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
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(88,166,255,0.15);
  padding: 30px;
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
  border: 1px solid #f0f5ff;
  transition: all 0.3s ease;
}

/* 弹窗布局样式 */
.dialog-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  width: 100%;
  margin-bottom: 20px;
}

.dialog-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: #f8fafd;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
  transition: all 0.3s ease;
}

.dialog-column:hover {
  box-shadow: 0 6px 20px rgba(22, 119, 255, 0.08);
  transform: translateY(-2px);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.2);
  flex-shrink: 0;
}


.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  color: #1677ff;
  z-index: 1;
}


.shop-icon {
  font-size: 1.2rem;
  color: #1677ff;
}


.shop-address {
  font-size: 0.85rem;
  color: #6b7280;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.15);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.25);
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  width: 18px;
  height: 18px;
  transition: all 0.2s ease;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
}

.remove-tag:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.remove-tag:hover {
  color: #e0f0ff;
  transform: scale(1.2);
}




/* 拜访表格标签样式 */
.visit-tags {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 5px !important;
  justify-content: flex-start !important;
  min-height: 30px !important;
  padding: 2px 0 !important;
}

.visit-tag {
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
  border: 1px solid rgba(255,255,255,0.2);
  visibility: visible;
  opacity: 1;
}


/* 响应式布局 */
@media (max-width: 768px) {
  .dialog-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .detail-dialog {
    width: 90%;
    padding: 20px;
  }

  .table-container {
    max-height: calc(100vh - 250px);
    min-height: 250px;
  }

  .visit-table th, .visit-table td {
    padding: 12px 14px;
    font-size: 0.95rem;
  }
}

@media (max-width: 480px) {
  .visit-table-wrapper {
    padding: 16px 12px;
  }

  .table-container {
    max-height: calc(100vh - 200px);
    min-height: 200px;
  }

  .visit-table th, .visit-table td {
    padding: 10px 12px;
    font-size: 0.85rem;
  }
}
.visit-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 0px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafd, #eaf4ff);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.08);
  border: 1px solid rgba(22, 119, 255, 0.1);
  flex-wrap: wrap;
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
  padding: 10px 20px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-left: 0 !important;
}

.add-visit-btn:hover {
  background: #0958d9;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.2);
}

.add-visit-btn::before {
  content: '+';
  margin-right: 8px;
  font-size: 1.2rem;
  font-weight: bold;
}
.visit-table-wrapper {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  width: 100%;
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(22, 119, 255, 0.08);
  border: 1px solid rgba(22, 119, 255, 0.1);
}

.table-container {
  width: 100%;
  overflow: auto;
  max-height: calc(100vh - 300px);
  min-height: 300px;
  position: relative;
  border-radius: 12px;
  /* 添加滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #d0e0ff #f8fafd;
}

/* 自定义滚动条样式 */
.table-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f8fafd;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background-color: #d0e0ff;
  border-radius: 4px;
  border: 2px solid #f8fafd;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background-color: #1677ff;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
  color: #1677ff;
  font-size: 1rem;
}

.loading i {
  font-size: 1.5rem;
  margin-right: 10px;
  animation: spin 1s linear infinite;
}

.loading-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(255, 255, 255, 0.8);
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #333;
  z-index: 10;
}

.loading-indicator i {
  margin-right: 8px;
  color: #1890ff;
  font-size: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.shop-name-cell, .time-cell, .notes-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.shop-icon, .time-icon {
  color: #1677ff;
  font-size: 14px;
}

.notes-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.no-data-cell {
  text-align: center;
  padding: 40px 0;
  color: #8c8c8c;
  font-size: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.no-data-cell i {
  font-size: 3rem;
  margin-bottom: 16px;
  color: #d9d9d9;
}
.visit-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  border-radius: 12px;
  overflow: visible;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  table-layout: auto;
  min-width: max-content;
  transition: all 0.3s ease;
  margin: 0;
}
.visit-table th, .visit-table td {
  padding: 16px 20px;
  text-align: center;
  font-size: 1.08rem;
  transition: background 0.3s ease;
  white-space: nowrap; /* 不换行，始终一行显示 */
  height: 52px; /* 统一行高，可根据需要调整 */
  line-height: 1.5; /* 调整行高比例 */
  vertical-align: middle;
}
.visit-table th {
  background: linear-gradient(to bottom, #f0f7ff, #e6f0ff);
  color: #1677ff;
  font-weight: 600;
  border-bottom: 1px solid #d0e0ff;
  letter-spacing: 1.2px;
  white-space: nowrap;
  text-align: left;
  text-transform: uppercase;
  font-size: 0.95rem;
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 14px 16px;
  box-shadow: 0 2px 5px rgba(22, 119, 255, 0.1);
  /* 确保表头背景色完全不透明 */
  background-color: #f0f7ff;
}
.visit-table td {
  color: #2c3e50;
  border-bottom: 1px solid #eef2f7;
  vertical-align: middle;
  text-align: center;
  padding: 12px 16px;
}
.visit-table tr:last-child td {
  border-bottom: none;
}
.visit-table tbody tr:nth-child(odd) {
  background: #f8fafd;
}

.visit-table tbody tr:nth-child(even) {
  background: #ffffff;
}

.visit-table tbody tr:hover {
  background: #f5f9ff !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
  transition: all 0.3s ease;
}

.visit-table tr:nth-child(even) td {
  background: #fafcff;
}

.visit-table tbody tr.selected {
  background: #e0f0ff !important;
  border-left: 4px solid #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.15);
}

@keyframes popIn {
  from { transform: scale(0.95); opacity: 0.7; }
  to { transform: scale(1); opacity: 1; }
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

.dropdown-list li {
  padding: 10px 18px;
  cursor: pointer;
  font-size: 1.08rem;
  transition: background 0.18s;
}
.dropdown-list li:hover {
  background: #eaf4ff;
}



button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f0f0f0 !important;
  color: #999 !important;
  border-color: #ddd !important;
  box-shadow: none !important;
}

.selected {
  background: #eaf4ff !important;
}
.delete-visit-btn {
  padding: 10px 20px;
  background: #fff;
  color: #ff4d4f;
  border: 1.5px solid #ffccc7;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-left: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-visit-btn:hover:not(:disabled) {
  background: #fff1f0;
  color: #ff4d4f;
  border-color: #ff7875;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 77, 79, 0.1);
}

.delete-visit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
  background: #ccc !important;
  color: #fff !important;
}

.delete-visit-btn.active {
  background: #fff1f0;
  color: #ff4d4f;
  border-color: #ff7875;
  cursor: pointer;
}

.delete-visit-btn::before {
  content: '×';
  margin-right: 8px;
  font-size: 1.2rem;
  font-weight: bold;
}
.delete-dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.delete-dialog {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 400px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.delete-dialog-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.delete-dialog-title i {
  color: #ff4d4f;
  font-size: 1.4rem;
}

.delete-dialog-msg {
  color: #666;
  line-height: 1.5;
}

.delete-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

.delete-dialog-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-dialog-btn.cancel {
  background: #f0f0f0;
  color: #666;
  border: none;
}

.delete-dialog-btn.cancel:hover {
  background: #e0e0e0;
}

.delete-dialog-btn.confirm {
  background: #ff4d4f;
  color: white;
  border: none;
}

.delete-dialog-btn.confirm:hover {
  background: #cf1322;
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.2);
}
.visit-pagination {
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

.pagination-left,
.pagination-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-center {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 5px;
}

.page-size-select {
  border-radius: 8px;
  border: 1.5px solid #b3d6ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 7px 12px;
  transition: background 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.page-size-select:disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
}

.visit-pagination select:focus, .visit-pagination input:focus {
  border: 1.5px solid #1677ff;
  outline: none;
  box-shadow: 0 0 0 2px #b3d6ff44;
}

.pagination-btn {
  border-radius: 10px;
  border: 1px solid #d0e0ff;
  background: #fff;
  color: #1765d8;
  font-weight: 600;
  padding: 10px 16px;
  margin: 0 2px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-btn:disabled, .pagination-btn.disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
}

.pagination-btn:not(:disabled):not(.disabled):hover {
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
  color: #1765d8;
  font-weight: 600;
  transition: all 0.3s ease;
}

.page-input:focus {
  outline: none;
  border-color: #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
  transform: translateY(-1px);
}
@media (max-width: 800px) {
  .visit-page-card {
    padding: 15px;
    height: 100dvh;
    box-sizing: border-box;
  }
  .visit-table {
    font-size: 14px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch; /* 提升iOS滚动体验 */
  }
  .visit-table th, .visit-table td {
    padding: 8px 10px;
  }
  .visit-pagination {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
    font-size: 0.95rem;
    text-align: center;
  }
  .pagination-left,
  .pagination-center,
  .pagination-right {
    width: 100%;
    justify-content: center;
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
  .notes-cell {
    max-width: 120px;
  }
  .dialog-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .visit-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .toolbar-btns {
    width: 100%;
    justify-content: space-between;
  }

  .add-visit-btn, .delete-visit-btn {
    width: 48%;
    justify-content: center;
  }

  .visit-table-wrapper {
    width: 100%;
    max-height: 400px;
    overflow-y: auto;
    overflow-x: auto;
    padding: 16px;
    -webkit-overflow-scrolling: touch; /* 提升iOS滚动体验 */
  }

  .visit-table {
    min-width: 650px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch; /* 提升iOS滚动体验 */
  }

  .visit-dialog {
    width: 95%;
    padding: 16px;
  }

  .dialog-header {
    padding: 16px;
  }

  .dialog-title {
    font-size: 18px;
  }

  .dialog-body {
    padding: 16px;
    max-height: calc(90vh - 120px);
  }

  .form-item label {
    font-size: 14px;
  }

  .input, .textarea {
    padding: 10px 12px;
    font-size: 14px;
  }

  .tags-select,
  .selected-tags {
    max-height: 150px;
  }

  .tag-option {
    padding: 5px 10px;
    font-size: 13px;
  }

  .tag {
    padding: 5px 10px;
    font-size: 13px;
  }

  .btn {
    padding: 8px 16px;
    font-size: 14px;
  }

  .dialog-footer {
    padding: 16px;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .visit-toolbar-title {
    font-size: 18px;
  }

  .visit-pagination {
    font-size: 0.85rem;
  }

  .visit-pagination button,
  .visit-pagination input,
  .visit-pagination select {
    font-size: 0.85rem;
    padding: 5px 8px;
  }

  .dialog-title {
    font-size: 16px;
  }

  .dialog-close {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .form-item label {
    font-size: 13px;
  }

  .input, .textarea {
    padding: 8px 10px;
    font-size: 13px;
  }

  .tag-option {
    padding: 4px 8px;
    font-size: 12px;
  }

  .tag {
    padding: 4px 8px;
    font-size: 12px;
  }

  .btn {
    padding: 7px 14px;
    font-size: 13px;
  }

  .custom-tag {
    flex-direction: column;
    gap: 8px;
  }

  .add-tag-btn {
    width: 100%;
    justify-content: center;
  }

  .shop-name {
    font-size: 13px;
  }

  .shop-address {
    font-size: 12px;
  }

  .dropdown li {
    padding: 10px 12px;
  }
}

.visit-dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.visit-dialog {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 50%;
  max-width: 90%;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eaedf2;
  background: linear-gradient(to right, #f8faff, #f0f5ff);
}

.dialog-title {
  font-size: 20px;
  font-weight: 700;
  color: #1765d8;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-title i {
  font-size: 22px;
  color: #1677ff;
}

.dialog-close {
  background: transparent;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #666;
  font-size: 18px;
  transition: all 0.2s;
}

.dialog-close:hover {
  background: rgba(0,0,0,0.05);
  color: #ff4d4f;
  transform: rotate(90deg);
}

.dialog-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.dialog-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.form-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 22px;
}

.form-item label {
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}

.form-item label i {
  color: #1677ff;
  font-size: 16px;
}

.input, .textarea {
  border: 1.5px solid #d9e2f0;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 15px;
  width: 100%;
  transition: all 0.2s;
  background: #f8faff;
  color: #333;
}

.input:focus, .textarea:focus {
  border-color: #1677ff;
  box-shadow: 0 0 0 3px rgba(22, 119, 255, 0.1);
  outline: none;
  background: #fff;
}

.input.disabled {
  background: #f0f2f5;
  color: #666;
  cursor: not-allowed;
}

.textarea {
  min-height: 100px;
  resize: vertical;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  background: linear-gradient(135deg, #1677ff, #4096ff);
  color: #fff;
  width: 38px;
  height: 38px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 3px 8px rgba(22, 119, 255, 0.3);
}

.shop-search {
  position: relative;
}

.shop-search .input {
  padding-right: 40px;
}

.search-icon {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #1677ff;
  font-size: 16px;
}

.dropdown {
  position: absolute;
  width: 100%;
  max-height: 250px;
  overflow-y: auto;
  background: white;
  border-radius: 10px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  z-index: 10;
  margin-top: 5px;
  border: 1px solid #eaedf2;
}

.dropdown ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.dropdown li {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f2f5;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: background 0.2s;
}

.dropdown li:last-child {
  border-bottom: none;
}

.dropdown li:hover {
  background: #f0f7ff;
}

.shop-icon {
  color: #1677ff;
  font-size: 16px;
}

.shop-info {
  flex: 1;
}

.shop-name {
  font-weight: 600;
  color: #333;
}

.shop-address {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.tags-select {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  max-height: 180px;
  overflow-y: auto;
  background: #f8faff;
  border: 1.5px solid #d9e2f0;
  border-radius: 10px;
  padding: 12px;
}

.tag-option {
  border: 1.5px solid #d9e2f0;
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
  background: white;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  user-select: none;
}

.tag-option:hover {
  border-color: #1677ff;
  background: #f0f7ff;
}

.tag-option.selected {
  background: #1677ff;
  color: #fff;
  border-color: #1677ff;
  box-shadow: 0 3px 6px rgba(22, 119, 255, 0.2);
}

.tag-option input[type="checkbox"] {
  display: none;
}

.tag-name {
  font-size: 14px;
}

.custom-tag {
  display: flex;
  gap: 10px;
}

.add-tag-btn {
  background: #1677ff;
  color: white;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  border-radius: 10px;
  transition: all 0.2s;
}

.add-tag-btn:hover:not(:disabled) {
  background: #0958d9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(22, 119, 255, 0.2);
}

.add-tag-btn:disabled {
  background: #d9d9d9;
  color: #999;
  cursor: not-allowed;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
  background: #f8faff;
  border: 1.5px solid #d9e2f0;
  border-radius: 10px;
  padding: 12px;
}

.no-tags {
  color: #999;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #e6f4ff;
  color: #1677ff;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.tag-text {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-tag {
  background: transparent;
  border: none;
  color: #1677ff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 12px;
  transition: all 0.2s;
}

.remove-tag:hover {
  background: rgba(22, 119, 255, 0.1);
  color: #ff4d4f;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn.primary {
  background: linear-gradient(135deg, #1677ff, #4096ff);
  color: #fff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

.btn.primary:hover {
  background: linear-gradient(135deg, #0958d9, #1677ff);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.4);
}

.btn.cancel {
  background: #f0f2f5;
  color: #666;
}

.btn.cancel:hover {
  background: #e6e6e6;
  color: #333;
}

.dialog-footer {
     padding: 20px 24px;
     border-top: 1px solid #eaedf2;
     display: flex;
     justify-content: flex-end;
     gap: 16px;
     background: #f8faff;
   }


</style>

