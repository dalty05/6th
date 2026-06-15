<template>
  <div class="system-settings">
    <div class="settings-header">
      <h1>System Settings</h1>
      <p>Configure application behavior and preferences</p>
    </div>

    <div class="settings-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id" 
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id; loadGroupSettings(tab.id)">
        <i :class="tab.icon"></i> {{ tab.name }}
      </button>
    </div>

    <div class="settings-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading settings...</p>
      </div>

      <form v-else @submit.prevent="saveSettings" class="settings-form">
        <!-- General Settings -->
        <div v-if="activeTab === 'general'" class="settings-group">
          <h3>General Settings</h3>
          <div class="form-group">
            <label>Site Name</label>
            <input type="text" v-model="settings.site_name">
            <small>Website name displayed in browser tabs and headers</small>
          </div>
          <div class="form-group">
            <label>Site Logo URL</label>
            <input type="text" v-model="settings.site_logo">
            <small>Path to logo image</small>
          </div>
          <div class="form-group">
            <label>Contact Email</label>
            <input type="email" v-model="settings.contact_email">
            <small>Default email for contact forms</small>
          </div>
          <div class="form-group">
            <label>Contact Phone</label>
            <input type="text" v-model="settings.contact_phone">
          </div>
          <div class="form-group">
            <label>Company Address</label>
            <textarea v-model="settings.company_address" rows="2"></textarea>
          </div>
        </div>

        <!-- Email Settings -->
        <div v-if="activeTab === 'email'" class="settings-group">
          <h3>Email Configuration</h3>
          <div class="form-group">
            <label>SMTP Server</label>
            <input type="text" v-model="settings.smtp_server">
          </div>
          <div class="form-group">
            <label>SMTP Port</label>
            <input type="number" v-model="settings.smtp_port">
          </div>
          <div class="form-group">
            <label>SMTP Username</label>
            <input type="text" v-model="settings.smtp_username">
          </div>
          <div class="form-group">
            <label>SMTP Password</label>
            <input type="password" v-model="settings.smtp_password" placeholder="Leave blank to keep current">
            <small>Enter new password to update</small>
          </div>
          <div class="form-group">
            <label>Email From Name</label>
            <input type="text" v-model="settings.email_from_name">
          </div>
          <button type="button" class="btn-test" @click="testEmail" :disabled="testingEmail">
            {{ testingEmail ? 'Sending...' : 'Test Email Configuration' }}
          </button>
        </div>

        <!-- Security Settings -->
        <div v-if="activeTab === 'security'" class="settings-group">
          <h3>Security Settings</h3>
          <div class="form-group">
            <label>Session Timeout (minutes)</label>
            <input type="number" v-model="settings.session_timeout">
            <small>Time before automatic logout</small>
          </div>
          <div class="form-group">
            <label>Max Login Attempts</label>
            <input type="number" v-model="settings.max_login_attempts">
          </div>
          <div class="form-group">
            <label>Minimum Password Length</label>
            <input type="number" v-model="settings.password_min_length">
          </div>
          <div class="form-group">
            <label>OTP Expiry (minutes)</label>
            <input type="number" v-model="settings.otp_expiry_minutes">
          </div>
        </div>

        <!-- Referral Settings -->
        <div v-if="activeTab === 'referral'" class="settings-group">
          <h3>Referral Settings</h3>
          <div class="form-group">
            <label>Default Destination URL</label>
            <input type="url" v-model="settings.referral_default_destination">
            <small>Where users are redirected when no destination is specified</small>
          </div>
          <div class="form-group">
            <label>Conversion Tracking Days</label>
            <input type="number" v-model="settings.referral_conversion_days">
            <small>Number of days to track conversions after click</small>
          </div>
        </div>

        <!-- Blog Settings -->
        <div v-if="activeTab === 'blog'" class="settings-group">
          <h3>Blog Settings</h3>
          <div class="form-group">
            <label>Posts Per Page</label>
            <input type="number" v-model="settings.blog_posts_per_page">
          </div>
          <div class="form-group">
            <label>Default Image URL</label>
            <input type="text" v-model="settings.blog_default_image">
          </div>
        </div>

        <!-- Product Settings -->
        <div v-if="activeTab === 'product'" class="settings-group">
          <h3>Product Settings</h3>
          <div class="form-group">
            <label>Products Per Page</label>
            <input type="number" v-model="settings.products_per_page">
          </div>
          <div class="form-group">
            <label>Featured Products Count</label>
            <input type="number" v-model="settings.featured_products_count">
          </div>
        </div>

        <!-- Job Settings -->
        <div v-if="activeTab === 'job'" class="settings-group">
          <h3>Job Settings</h3>
          <div class="form-group">
            <label>Jobs Per Page</label>
            <input type="number" v-model="settings.jobs_per_page">
          </div>
          <div class="form-group">
            <label>Application Deadline (days)</label>
            <input type="number" v-model="settings.application_deadline_days">
            <small>Default deadline from posting date</small>
          </div>
        </div>

        <!-- Outlet Settings -->
        <div v-if="activeTab === 'outlet'" class="settings-group">
          <h3>Outlet Settings</h3>
          <div class="form-group">
            <label>Outlets Per Page</label>
            <input type="number" v-model="settings.outlets_per_page">
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-save" :disabled="saving">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            {{ saving ? 'Saving...' : 'Save All Settings' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Notification -->
    <div v-if="notification.show" :class="['notification', notification.type]" @click="notification.show = false">
      <i :class="notification.icon"></i>
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/services/api'

const activeTab = ref('general')
const loading = ref(false)
const saving = ref(false)
const testingEmail = ref(false)

const tabs = [
  { id: 'general', name: 'General', icon: 'fas fa-cog' },
  { id: 'email', name: 'Email', icon: 'fas fa-envelope' },
  { id: 'security', name: 'Security', icon: 'fas fa-shield-alt' },
  { id: 'referral', name: 'Referral', icon: 'fas fa-link' },
  { id: 'blog', name: 'Blog', icon: 'fas fa-newspaper' },
  { id: 'product', name: 'Products', icon: 'fas fa-box' },
  { id: 'job', name: 'Jobs', icon: 'fas fa-briefcase' },
  { id: 'outlet', name: 'Outlets', icon: 'fas fa-store' }
]

const settings = reactive({
  site_name: '',
  site_logo: '',
  contact_email: '',
  contact_phone: '',
  company_address: '',
  smtp_server: '',
  smtp_port: '',
  smtp_username: '',
  smtp_password: '',
  email_from_name: '',
  session_timeout: '',
  max_login_attempts: '',
  password_min_length: '',
  otp_expiry_minutes: '',
  referral_default_destination: '',
  referral_conversion_days: '',
  blog_posts_per_page: '',
  blog_default_image: '',
  products_per_page: '',
  featured_products_count: '',
  jobs_per_page: '',
  application_deadline_days: '',
  outlets_per_page: ''
})

const notification = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'fas fa-check-circle'
})

const showNotification = (message, type = 'success') => {
  notification.value = { show: true, message, type, icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle' }
  setTimeout(() => notification.value.show = false, 3000)
}

const loadGroupSettings = async (group) => {
  loading.value = true
  try {
    const response = await api.get(`/admin/settings/${group}`)
    const data = response.data
    for (const [key, value] of Object.entries(data)) {
      if (key in settings) {
        settings[key] = value || ''
      }
    }
  } catch (error) {
    console.error('Error loading settings:', error)
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const settingsToSave = {}
    for (const [key, value] of Object.entries(settings)) {
      if (value !== undefined && value !== '') {
        settingsToSave[key] = value
      }
    }
    
    await api.put('/admin/settings/bulk', {
      group: activeTab.value,
      settings: settingsToSave
    })
    showNotification('Settings saved successfully')
  } catch (error) {
    showNotification('Failed to save settings', 'error')
  } finally {
    saving.value = false
  }
}

const testEmail = async () => {
  testingEmail.value = true
  try {
    await api.post('/admin/settings/test-email')
    showNotification('Test email sent successfully')
  } catch (error) {
    showNotification('Failed to send test email', 'error')
  } finally {
    testingEmail.value = false
  }
}

onMounted(() => {
  loadGroupSettings('general')
})
</script>

<style scoped>
.system-settings {
  padding: 1.5rem;
  max-width: 900px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: 1.5rem;
}

.settings-header h1 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 0.25rem;
}

.settings-header p {
  color: #6b7280;
  margin: 0;
}

.settings-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.settings-tabs button {
  padding: 0.6rem 1.2rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.settings-tabs button:hover {
  color: #1e3a8a;
}

.settings-tabs button.active {
  color: #1e3a8a;
  border-bottom: 2px solid #f59e0b;
}

.settings-group {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}

.settings-group h3 {
  margin: 0 0 1rem;
  color: #1e3a8a;
  font-size: 1rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 0.8rem;
  color: #374151;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
}

.form-group small {
  font-size: 0.7rem;
  color: #9ca3af;
  display: block;
  margin-top: 0.25rem;
}

.btn-test {
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

.btn-test:hover {
  background: #d1d5db;
}

.form-actions {
  margin-top: 1.5rem;
  text-align: right;
}

.btn-save {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-save:hover {
  background: #f59e0b;
}

.loading-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #1e3a8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

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

.notification.success { background: #10b981; color: white; }
.notification.error { background: #ef4444; color: white; }

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
</style>