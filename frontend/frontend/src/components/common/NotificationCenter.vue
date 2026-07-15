<template>
  <div class="notification-center">
    <button class="notification-btn" @click="toggleDropdown" :class="{ active: isOpen }">
      <i class="fas fa-bell"></i>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
    </button>
    
    <div v-if="isOpen" class="notification-dropdown glass-card" @click.stop>
      <div class="dropdown-header">
        <h3>Notifications</h3>
        <div class="header-actions">
          <button v-if="unreadCount > 0" @click="markAllRead" class="btn-text">Mark all as read</button>
          <button @click="closeDropdown" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <div class="dropdown-content">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading notifications...</p>
        </div>
        
        <div v-else-if="notifications.length === 0" class="empty-state">
          <i class="fas fa-bell-slash"></i>
          <p>No notifications yet</p>
        </div>
        
        <div v-else class="notifications-list">
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ unread: !notification.read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon" :class="notification.type">
              <i :class="getIconClass(notification.type)"></i>
            </div>
            <div class="notification-content">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
            </div>
            <button @click.stop="deleteNotification(notification.id)" class="delete-notification">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>
      
      <div class="dropdown-footer" v-if="notifications.length > 0">
        <button @click="viewAllNotifications" class="btn-link">View All Notifications</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import notificationService from '@/services/notification'

const isOpen = ref(false)
const loading = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loadNotifications()
  }
}

const closeDropdown = () => {
  isOpen.value = false
}

const loadNotifications = async () => {
  loading.value = true
  try {
    const data = await notificationService.fetchNotifications(10)
    notifications.value = data
    unreadCount.value = notificationService.unreadCount.value
  } finally {
    loading.value = false
  }
}

const markAllRead = async () => {
  await notificationService.markAllAsRead()
  notifications.value.forEach(n => n.read = true)
  unreadCount.value = 0
}

const deleteNotification = async (id) => {
  await notificationService.deleteNotification(id)
  notifications.value = notifications.value.filter(n => n.id !== id)
  unreadCount.value = notifications.value.filter(n => !n.read).length
}

const handleNotificationClick = (notification) => {
  if (!notification.read) {
    notificationService.markAsRead(notification.id)
    notification.read = true
    unreadCount.value--
  }
  
  if (notification.link) {
    window.location.href = notification.link
  }
  closeDropdown()
}

const viewAllNotifications = () => {
  // Navigate to notifications page
  window.location.href = '/admin/notifications'
  closeDropdown()
}

const getIconClass = (type) => {
  switch(type) {
    case 'success': return 'fas fa-check-circle'
    case 'error': return 'fas fa-exclamation-circle'
    case 'warning': return 'fas fa-exclamation-triangle'
    default: return 'fas fa-info-circle'
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`
  return date.toLocaleDateString()
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  const dropdown = document.querySelector('.notification-center')
  if (dropdown && !dropdown.contains(event.target) && isOpen.value) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // Initial load of unread count
  unreadCount.value = notificationService.unreadCount.value
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.notification-center {
  position: relative;
}

.notification-btn {
  position: relative;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #333;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.notification-btn:hover {
  background: #f8fafc;
  color: #f59e0b;
}

.notification-btn.active {
  background: #fef3c7;
  color: #f59e0b;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #dc2626;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 5px;
  border-radius: 50%;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 380px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  margin-top: 8px;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.dropdown-header h3 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-text {
  background: none;
  border: none;
  font-size: 0.75rem;
  color: #f59e0b;
  cursor: pointer;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
}

.dropdown-content {
  max-height: 400px;
  overflow-y: auto;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 2px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 0.5rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state i {
  font-size: 2rem;
  color: #cbd5e1;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #666;
  font-size: 0.85rem;
}

.notifications-list {
  display: flex;
  flex-direction: column;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.3s;
  position: relative;
}

.notification-item:hover {
  background: #f8fafc;
}

.notification-item.unread {
  background: #fef3c7;
}

.notification-item.unread:hover {
  background: #fde68a;
}

.notification-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.success {
  background: #d1fae5;
  color: #10b981;
}

.notification-icon.error {
  background: #fee2e2;
  color: #dc2626;
}

.notification-icon.warning {
  background: #fef3c7;
  color: #f59e0b;
}

.notification-icon.info {
  background: #e0e7ff;
  color: #3b82f6;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 0.25rem;
  font-size: 0.85rem;
}

.notification-message {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.notification-time {
  font-size: 0.65rem;
  color: #999;
}

.delete-notification {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0.25rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.notification-item:hover .delete-notification {
  opacity: 1;
}

.delete-notification:hover {
  color: #dc2626;
}

.dropdown-footer {
  padding: 0.75rem;
  text-align: center;
  border-top: 1px solid #e5e7eb;
}

.btn-link {
  background: none;
  border: none;
  color: #f59e0b;
  font-size: 0.8rem;
  cursor: pointer;
}

.glass-card {
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

@media (max-width: 480px) {
  .notification-dropdown {
    width: 320px;
    right: -60px;
  }
}
</style>