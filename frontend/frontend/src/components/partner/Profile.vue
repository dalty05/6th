<template>
  <div class="partner-profile">
    <div class="page-header">
      <div>
        <h1>My Profile</h1>
        <p>Manage your account settings and preferences</p>
      </div>
    </div>

    <div class="profile-grid">
      <!-- Profile Information Card -->
      <div class="profile-card glass-card">
        <div class="card-header">
          <h3><i class="fas fa-user-circle"></i> Profile Information</h3>
        </div>
        
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input type="text" v-model="profileForm.full_name" class="form-input" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input type="email" v-model="profileForm.email" class="form-input" disabled>
            <div class="form-hint">Email cannot be changed</div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Referral Code</label>
            <div class="referral-code-display">
              <code>{{ user?.referral_code || 'Not available' }}</code>
              <button type="button" @click="copyReferralCode" class="btn btn-sm btn-outline">
                <i class="fas fa-copy"></i> Copy
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Account Status</label>
            <div class="status-badge" :class="user?.is_active ? 'status-active' : 'status-inactive'">
              <i :class="user?.is_active ? 'fas fa-check-circle' : 'fas fa-ban'"></i>
              {{ user?.is_active ? 'Active' : 'Inactive' }}
            </div>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="profileLoading">
              <i v-if="profileLoading" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ profileLoading ? 'Saving...' : 'Update Profile' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Change Password Card -->
      <div class="password-card glass-card">
        <div class="card-header">
          <h3><i class="fas fa-key"></i> Change Password</h3>
        </div>
        
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label class="form-label">Current Password</label>
            <input type="password" v-model="passwordForm.current_password" class="form-input" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">New Password</label>
            <input type="password" v-model="passwordForm.new_password" class="form-input" required>
            <div class="form-hint">
              Must be at least 8 characters with uppercase, lowercase, and number
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Confirm New Password</label>
            <input type="password" v-model="passwordForm.confirm_password" class="form-input" required>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="passwordLoading">
              <i v-if="passwordLoading" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-sync-alt"></i>
              {{ passwordLoading ? 'Changing...' : 'Change Password' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Stats Card -->
      <div class="stats-card glass-card">
        <div class="card-header">
          <h3><i class="fas fa-chart-line"></i> Your Performance</h3>
        </div>
        
        <div class="stats-list">
          <div class="stat-row">
            <span class="stat-label">Total Clicks Generated</span>
            <span class="stat-value">{{ userStats.totalClicks || 0 }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Unique Visitors</span>
            <span class="stat-value">{{ userStats.uniqueClicks || 0 }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Conversions</span>
            <span class="stat-value">{{ userStats.totalConversions || 0 }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Conversion Rate</span>
            <span class="stat-value">{{ userStats.conversionRate || 0 }}%</span>
          </div>
        </div>
        
        <div class="card-footer">
          <router-link to="/partner/analytics" class="btn btn-outline btn-block">
            View Full Analytics <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
      </div>

      <!-- Notification Preferences Card -->
      <div class="notifications-card glass-card">
        <div class="card-header">
          <h3><i class="fas fa-bell"></i> Notification Preferences</h3>
        </div>
        
        <div class="notification-options">
          <label class="toggle-switch">
            <input type="checkbox" v-model="notifications.email_notifications">
            <span class="toggle-slider"></span>
            <span class="toggle-label">Email Notifications</span>
          </label>
          <p class="option-hint">Receive email updates about your referral performance</p>
          
          <label class="toggle-switch">
            <input type="checkbox" v-model="notifications.daily_summary">
            <span class="toggle-slider"></span>
            <span class="toggle-label">Daily Summary</span>
          </label>
          <p class="option-hint">Get a daily summary of your referral activity</p>
          
          <label class="toggle-switch">
            <input type="checkbox" v-model="notifications.conversion_alerts">
            <span class="toggle-slider"></span>
            <span class="toggle-label">Conversion Alerts</span>
          </label>
          <p class="option-hint">Get notified when someone converts through your link</p>
        </div>
        
        <div class="form-actions">
          <button @click="savePreferences" class="btn btn-primary" :disabled="preferencesLoading">
            <i v-if="preferencesLoading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-save"></i>
            Save Preferences
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Toast handled by toastify -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import authService from '@/services/auth'
import api from '@/services/api'

const router = useRouter()
const user = ref(null)
const userStats = ref({
  totalClicks: 0,
  uniqueClicks: 0,
  totalConversions: 0,
  conversionRate: 0
})

const profileLoading = ref(false)
const passwordLoading = ref(false)
const preferencesLoading = ref(false)

const profileForm = ref({
  full_name: '',
  email: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const notifications = ref({
  email_notifications: true,
  daily_summary: false,
  conversion_alerts: true
})

const loadUserData = async () => {
  user.value = authService.getUser()
  if (!user.value) {
    router.push('/')
    return
  }
  
  profileForm.value = {
    full_name: user.value.full_name || '',
    email: user.value.email || ''
  }
  
  // Load user stats
  try {
    const response = await api.get('/referral/stats')
    userStats.value = {
      totalClicks: response.data.totalClicks || 0,
      uniqueClicks: response.data.uniqueClicks || 0,
      totalConversions: response.data.totalConversions || 0,
      conversionRate: response.data.conversionRate || 0
    }
  } catch (error) {
    console.error('Error loading user stats:', error)
  }
  
  // Load saved preferences from localStorage
  const savedPrefs = localStorage.getItem('partner_notifications')
  if (savedPrefs) {
    notifications.value = JSON.parse(savedPrefs)
  }
}

const updateProfile = async () => {
  profileLoading.value = true
  try {
    await authService.updateProfile(profileForm.value.full_name)
    toast.success('Profile updated successfully')
    // Refresh user data
    const updatedUser = await authService.getProfile()
    authService.setUser(updatedUser)
    user.value = updatedUser
  } catch (error) {
    console.error('Error updating profile:', error)
    toast.error(error.response?.data?.error || 'Failed to update profile')
  } finally {
    profileLoading.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    toast.error('New passwords do not match')
    return
  }
  
  if (passwordForm.value.new_password.length < 8) {
    toast.error('Password must be at least 8 characters')
    return
  }
  
  passwordLoading.value = true
  try {
    await authService.changePassword(
      passwordForm.value.current_password,
      passwordForm.value.new_password
    )
    toast.success('Password changed successfully')
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error) {
    console.error('Error changing password:', error)
    toast.error(error.response?.data?.error || 'Failed to change password')
  } finally {
    passwordLoading.value = false
  }
}

const savePreferences = async () => {
  preferencesLoading.value = true
  try {
    localStorage.setItem('partner_notifications', JSON.stringify(notifications.value))
    toast.success('Notification preferences saved')
  } catch (error) {
    console.error('Error saving preferences:', error)
    toast.error('Failed to save preferences')
  } finally {
    preferencesLoading.value = false
  }
}

const copyReferralCode = () => {
  if (user.value?.referral_code) {
    navigator.clipboard.writeText(user.value.referral_code)
    toast.success('Referral code copied to clipboard!')
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.partner-profile {
  min-height: 100vh;
  background: var(--gray-50);
  padding: var(--spacing-6);
}

.page-header {
  margin-bottom: var(--spacing-6);
}

.page-header h1 {
  color: var(--primary-blue);
  margin: 0 0 var(--spacing-1) 0;
}

.page-header p {
  color: var(--gray-500);
  margin: 0;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-6);
}

.profile-card, .password-card, .stats-card, .notifications-card {
  background: white;
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.profile-card, .password-card {
  grid-column: span 1;
}

.stats-card, .notifications-card {
  grid-column: span 1;
}

.card-header {
  padding: var(--spacing-5);
  border-bottom: 1px solid var(--gray-200);
}

.card-header h3 {
  color: var(--primary-blue);
  margin: 0;
  font-size: var(--text-lg);
}

.card-header h3 i {
  margin-right: var(--spacing-2);
  color: var(--accent-orange);
}

.profile-form, .password-form {
  padding: var(--spacing-5);
}

.referral-code-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.referral-code-display code {
  background: var(--gray-100);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-lg);
  font-family: monospace;
  font-size: var(--text-sm);
  color: var(--primary-blue);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  width: fit-content;
}

.status-active {
  background: var(--success-light);
  color: var(--success-dark);
}

.status-inactive {
  background: var(--error-light);
  color: var(--error-dark);
}

.form-actions {
  margin-top: var(--spacing-5);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--gray-200);
}

.stats-list {
  padding: var(--spacing-5);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-2) 0;
  border-bottom: 1px solid var(--gray-100);
}

.stat-label {
  color: var(--gray-600);
  font-size: var(--text-sm);
}

.stat-value {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--primary-blue);
}

.card-footer {
  padding: var(--spacing-4) var(--spacing-5);
  border-top: 1px solid var(--gray-200);
}

.btn-block {
  width: 100%;
  justify-content: center;
}

.notification-options {
  padding: var(--spacing-5);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.option-hint {
  font-size: var(--text-xs);
  color: var(--gray-400);
  margin-top: -8px;
  margin-bottom: var(--spacing-2);
}

@media (max-width: 1024px) {
  .profile-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .profile-card, .password-card, .stats-card, .notifications-card {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .partner-profile {
    padding: var(--spacing-4);
  }
  
  .referral-code-display {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>