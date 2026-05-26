


import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import axios from 'axios'

axios.defaults.withCredentials = true



// Add auth token to all requests
axios.interceptors.request.use(config => {
  // You can add token if needed
  return config
})

// Handle 401 responses
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Clear user data and redirect to login
      localStorage.removeItem('user')
      if (router.currentRoute.value.path !== '/admin/login') {
        router.push('/admin/login')
      }
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.use(router)
app.mount('#app')