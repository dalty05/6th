<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="profile-avatar">
        <i class="fas fa-user-circle"></i>
      </div>
      <div class="profile-title">
        <h1>My Profile</h1>
        <p>Manage your account settings and preferences</p>
      </div>
    </div>

    <div class="profile-grid">
      <!-- Personal Information Card -->
      <div class="profile-card">
        <div class="card-header">
          <i class="fas fa-user"></i>
          <h3>Personal Information</h3>
        </div>
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" v-model="profile.full_name" required>
          </div>
          <div class="form-group">
            <label>Email Address</label>
            <input type="email" v-model="profile.email" disabled class="disabled">
            <small>Email cannot be changed</small>
          </div>
          <div class="form-group">
            <label>Role</label>
            <input type="text" :value="getRoleLabel(profile.role)" disabled class="disabled">
          </div>
          <button type="submit" class="btn-save" :disabled="savingProfile">
            {{ savingProfile ? 'Saving...' : 'Save Changes' }}
          </button>
        </form>
      </div>

      <!-- Change Password Card -->
      <div class="profile-card">
        <div class="card-header">
          <i class="fas fa-lock"></i>
          <h3>Change Password</h3>
        </div>
        <form @submit.prevent="changePassword" class="profile-form">
          <div class="form-group">
            <label>Current Password</label>
            <input type="password" v-model="passwordForm.current_password" required>
          </div>
          <div class="form-group">
            <label>New Password</label>
            <input type="password" v-model="passwordForm.new_password" required>
            <small>Minimum 8 characters, at least one uppercase, one lowercase, and one number</small>
          </div>
          <div class="form-group">
            <label>Confirm New Password</label>
            <input type="password" v-model="passwordForm.confirm_password" required>
          </div>
          <button type="submit" class="btn-save" :disabled="savingPassword">
            {{ savingPassword ? 'Changing...' : 'Change Password' }}
          </button>
        </form>
      </div>

      <!-- Account Information Card -->
      <div class="profile-card">
        <div class="card-header">
          <i class="fas fa-info-circle"></i>
          <h3>Account Information</h3>
        </div>
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">Account Created:</span>
            <span class="info-value">{{ formatDate(profile.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Last Login:</span>
            <span class="info-value">{{ formatDate(profile.last_login) || 'Never' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Last Login IP:</span>
            <span class="info-value">{{ profile.last_login_ip || 'Unknown' }}</span>
          </div>
          <div class="info-item" v-if="profile.referral_code">
            <span class="info-label">Referral Code:</span>
            <span class="info-value code">{{ profile.referral_code }}</span>
          </div>
          <div class="info-item" v-if="profile.total_clicks !== undefined">
            <span class="info-label">Total Referral Clicks:</span>
            <span class="info-value">{{ profile.total_clicks || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Toast -->
    <div v-if="notification.show" :class="['notification', notification.type]" @click="notification.show = false">
      <i :class="notification.icon"></i>
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import authService from '@/services/auth'

const profile = ref({
  full_name: '',
  email: '',
  role: '',
  created_at: null,
  last_login: null,
  last_login_ip: null,
  referral_code: null,
  total_clicks: 0,
  total_conversions: 0
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const savingProfile = ref(false)
const savingPassword = ref(false)

const notification = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'fas fa-check-circle'
})

const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type,
    icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'
  }
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

const getRoleLabel = (role) => {
  const roles = {
    super_admin: 'Super Administrator',
    admin: 'Administrator',
    partner: 'Marketing Partner'
  }
  return roles[role] || role
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const loadProfile = async () => {
  try {
    // Use existing endpoint: /api/admin/profile
    const response = await api.get('/admin/profile')
    profile.value = response.data
  } catch (error) {
    console.error('Error loading profile:', error)
    showNotification('Failed to load profile', 'error')
  }
}

const updateProfile = async () => {
  savingProfile.value = true
  try {
    // Use existing endpoint: /api/admin/profile (PUT)
    await api.put('/admin/profile', { full_name: profile.value.full_name })
    showNotification('Profile updated successfully')
    
    // Update local user data
    const user = authService.getUser()
    if (user) {
      user.full_name = profile.value.full_name
      localStorage.setItem('user', JSON.stringify(user))
    }
  } catch (error) {
    showNotification(error.response?.data?.error || 'Failed to update profile', 'error')
  } finally {
    savingProfile.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    showNotification('New passwords do not match', 'error')
    return
  }
  
  if (passwordForm.value.new_password.length < 8) {
    showNotification('Password must be at least 8 characters', 'error')
    return
  }
  
  savingPassword.value = true
  try {
    // Use existing endpoint: /api/admin/change-password (PUT)
    await api.put('/admin/change-password', {
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password
    })
    showNotification('Password changed successfully')
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error) {
    showNotification(error.response?.data?.error || 'Failed to change password', 'error')
  } finally {
    savingPassword.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  padding: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  border-radius: 20px;
  color: white;
}

.profile-avatar i {
  font-size: 4rem;
}

.profile-title h1 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
}

.profile-title p {
  margin: 0;
  opacity: 0.9;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.profile-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.card-header i {
  font-size: 1.25rem;
  color: #f59e0b;
}

.card-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e3a8a;
}

.profile-form .form-group {
  margin-bottom: 1rem;
}

.profile-form label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: #374151;
}

.profile-form input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
}

.profile-form input.disabled {
  background: #f8fafc;
  color: #6b7280;
  cursor: not-allowed;
}

.profile-form small {
  font-size: 0.7rem;
  color: #9ca3af;
  display: block;
  margin-top: 0.25rem;
}

.btn-save {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  width: 100%;
  transition: all 0.2s;
}

.btn-save:hover {
  background: #f59e0b;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-label {
  font-size: 0.8rem;
  color: #6b7280;
}

.info-value {
  font-size: 0.85rem;
  font-weight: 500;
  color: #374151;
}

.info-value.code {
  font-family: monospace;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

/* Notification */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  cursor: pointer;
}

.notification.success {
  background: #10b981;
  color: white;
}

.notification.error {
  background: #ef4444;
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>