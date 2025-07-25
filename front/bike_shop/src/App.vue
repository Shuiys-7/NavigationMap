<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <div v-if="['/login','/register'].includes(route.path)" class="auth-center-bg">
    <router-view />
  </div>
  <div v-else id="app-root">
    <router-view />
  </div>
</template>

<style>
html, body, #app, #app-root {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #0d1117;
  color: #c9d1d9;
}
.auth-center-bg {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d1117;
}
</style>
