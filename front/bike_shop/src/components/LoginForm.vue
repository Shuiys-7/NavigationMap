<template>
  <div class="auth-form">
    <h2>用户登录</h2>
    <form @submit.prevent="handleLogin">
      <div class="input-group">
        <input v-model="username" placeholder="用户名" required />
      </div>
      <div class="input-group">
        <input v-model="password" type="password" placeholder="密码" required />
      </div>
      <button type="submit">登 录</button>
    </form>
    
    <div v-if="error" class="form-message error">{{ error }}</div>

    <div class="switch-form">
      <span>还没有账户？</span>
      <a @click="goRegister">立即注册</a>
    </div>

    <teleport to="body">
      <div v-if="showSuccessModal" class="toast-success">
        <div class="toast-content">
          <span class="toast-icon">✔</span>
          <span class="toast-title">登录成功</span>
          <button class="toast-close" @click="showSuccessModal = false">×</button>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const showSuccessModal = ref(false)

const goRegister = () => {
  console.log('跳转到注册页')
  router.push('/register')
}

const handleLogin = async () => {
  error.value = ''
  showSuccessModal.value = false
  try {
    const res = await axios.post('/api/login', {
      username: username.value,
      password: password.value
    })
    if (res.data.status === 'success') {
      showSuccessModal.value = true
      localStorage.setItem('token', res.data.token)
      setTimeout(() => {
        showSuccessModal.value = false
        router.push('/home/dashboard')
      }, 2000)
    } else {
      error.value = '登录失败'
    }
  } catch (e) {
    error.value = '用户名或密码错误'
  }
}
</script>

<style scoped>
@import '../assets/auth_form.css';

.toast-success {
  position: fixed;
  top: 32px;
  right: 32px;
  z-index: 2000;
  animation: toastIn 0.4s;
}

@keyframes toastIn {
  from { opacity: 0; transform: translateY(-30px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.toast-content {
  display: flex;
  align-items: center;
  background: rgba(20, 40, 70, 0.98);
  border-radius: 14px;
  box-shadow: 0 4px 24px 0 rgba(0, 191, 255, 0.18);
  border: 1.5px solid #58a6ff44;
  padding: 18px 32px 18px 22px;
  min-width: 160px;
  position: relative;
}

.toast-icon {
  font-size: 1.6rem;
  color: #3fb950;
  margin-right: 12px;
  text-shadow: 0 0 8px #3fb95088;
}

.toast-title {
  font-size: 1.08rem;
  font-weight: 600;
  color: #58a6ff;
  letter-spacing: 1px;
}

.toast-close {
  position: absolute;
  top: 6px;
  right: 10px;
  background: none;
  border: none;
  color: #58a6ff;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  transition: color 0.2s;
}
.toast-close:hover {
  color: #3fb950;
}
</style>
