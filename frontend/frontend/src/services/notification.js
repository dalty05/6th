// src/services/notification.js
import { ref } from 'vue'
import { toast } from 'vue3-toastify'
import api from './api'

class NotificationService {
  constructor() {
    this.notifications = ref([])
    this.unreadCount = ref(0)
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.webSocketEnabled = false // Temporarily disable WebSocket until backend is ready
  }

  initWebSocket() {
    if (!this.webSocketEnabled) {
      return
    }
    
    const token = localStorage.getItem('token') || localStorage.getItem('user')
    const wsUrl = `ws://${window.location.hostname}:5000/ws/notifications?token=${token}`
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleNotification(data)
        } catch (e) {
        }
      }
      
      this.ws.onerror = (error) => {
        throw new Error(`WebSocket error: ${error.message}`)
      }
      
      this.ws.onclose = () => {

        this.reconnect()
      }
    } catch (error) {
      throw(error)
    }
  }

 
  reconnect() {
    if (!this.webSocketEnabled) return
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++
        this.initWebSocket()
      }, 3000 * this.reconnectAttempts)
    }
  }

  /**
   * Handle incoming notification
   */
  handleNotification(notification) {
    // Add to notifications list
    this.notifications.value.unshift({
      id: Date.now(),
      ...notification,
      read: false,
      timestamp: new Date().toISOString()
    })
    
    // Keep only last 50 notifications
    if (this.notifications.value.length > 50) {
      this.notifications.value = this.notifications.value.slice(0, 50)
    }
    
    // Update unread count
    this.updateUnreadCount()
    
    // Show toast notification
    this.showToast(notification)
  }

  /**
   * Show toast notification
   */
  showToast(notification) {
    const options = {
      autoClose: 5000,
      position: 'top-right',
      theme: 'light'
    }
    
    switch (notification.type) {
      case 'success':
        toast.success(notification.message, options)
        break
      case 'error':
        toast.error(notification.message, options)
        break
      case 'warning':
        toast.warning(notification.message, options)
        break
      default:
        toast.info(notification.message, options)
    }
  }

  /**
   * Fetch notifications from API with fallback data
   */
  async fetchNotifications(limit = 20) {
    try {
      const response = await api.get(`/notifications?limit=${limit}`)
      this.notifications.value = response.data
      this.updateUnreadCount()
      return response.data
    } catch (error) {
      return []
    }
  }

  async markAsRead(notificationId) {
    try {
      await api.put(`/notifications/${notificationId}/read`)
      const notification = this.notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.read = true
        this.updateUnreadCount()
      }
    } catch (error) {
    }
  }

  async markAllAsRead() {
    try {
      await api.put('/notifications/read-all')
      this.notifications.value.forEach(n => n.read = true)
      this.unreadCount.value = 0
    } catch (error) {
    }
  }

  async deleteNotification(notificationId) {
    try {
      await api.delete(`/notifications/${notificationId}`)
      this.notifications.value = this.notifications.value.filter(n => n.id !== notificationId)
      this.updateUnreadCount()
    } catch (error) {
    }
  }

  updateUnreadCount() {
    this.unreadCount.value = this.notifications.value.filter(n => !n.read).length
  }

  /**
   * Add a test notification (for development)
   */
  addTestNotification(message, type = 'info') {
    this.handleNotification({
      type: type,
      title: 'Test Notification',
      message: message,
      icon: 'fas fa-bell'
    })
  }

  /**
   * Close WebSocket connection
   */
  closeWebSocket() {
    if (this.ws) {
      this.ws.close()
    }
  }
}

export default new NotificationService()