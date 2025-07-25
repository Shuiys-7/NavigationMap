<template>
  <div class="auth-form">
    <h2>创建账户</h2>
    <form @submit.prevent="handleRegister">
      <div class="input-group">
        <input v-model="username" placeholder="用户名" required />
      </div>
      <div class="input-group">
        <input v-model="password" type="password" placeholder="密码" required />
      </div>
      <div class="input-group">
        <input v-model="email" type="email" placeholder="邮箱" required />
      </div>
      <button type="submit">注 册</button>
    </form>

    <div v-if="error" class="form-message error">{{ error }}</div>
    <div v-if="success" class="form-message success">注册成功！请前往登录。</div>

    <div class="switch-form">
      <span>已有账户？</span>
      <a @click="goLogin">立即登录</a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const email = ref('')
const error = ref('')
const success = ref(false)

const goLogin = () => {
  router.push('/login')
}

const handleRegister = async () => {
  error.value = ''
  success.value = false
  try {
    const res = await axios.post('/api/register', {
      username: username.value,
      password: password.value,
      email: email.value
    })
    if (res.data.status === '注册成功') {
      success.value = true
      setTimeout(() => {
        goLogin()
      }, 2000)
    } else {
      error.value = res.data.error || '注册失败'
    }
  } catch (e) {
    error.value = '注册失败'
  }
}
</script>

<style scoped>
@import '../assets/auth_form.css';
</style>
