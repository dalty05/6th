// frontend/src/main.js

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import axios from 'axios'

import '@fortawesome/fontawesome-free/css/all.min.css'

import Vue3Toastify from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'

import { initReferralTracking } from './utils/simple-tracking'
import permissionService from './services/permissionService'
import authService from './services/auth'

import AOS from 'aos'
import 'aos/dist/aos.css'

axios.defaults.withCredentials = true



// Handle 401 responses
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      permissionService.clear()
      
      if (router.currentRoute.value.path !== '/admin/login') {
        router.push('/admin/login')
      }
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)

app.use(router)
app.use(Vue3Toastify, {
  autoClose: 3000,
  position: 'top-right',
  theme: 'light'
})

AOS.init({
  duration: 800,
  once: true,
  offset: 100
})

initReferralTracking()

// ✅ Check auth status with backend
const user = JSON.parse(localStorage.getItem('user') || 'null')

if (user) {
  // ✅ Verify session with backend
  authService.checkAuth().then((valid) => {
    if (!valid) {
      console.log('ℹ️ Session expired, redirecting to login')
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      if (router.currentRoute.value.path.startsWith('/admin') || router.currentRoute.value.path.startsWith('/partner')) {
        router.replace('/admin/login')
      }
    } else {
      console.log('✅ Session verified, permissions loaded')
    }
  }).catch(() => {
    console.log('ℹ️ Session expired, redirecting to login')
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    if (router.currentRoute.value.path.startsWith('/admin') || router.currentRoute.value.path.startsWith('/partner')) {
      router.replace('/admin/login')
    }
  })
} else {
  console.log('ℹ️ No active session')
  if (window.location.pathname.startsWith('/admin') || window.location.pathname.startsWith('/partner')) {
    router.replace('/admin/login')
  }
}

app.mount('#app')

export { permissionService, authService }