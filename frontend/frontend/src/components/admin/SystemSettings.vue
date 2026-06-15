<template>
  <div class="system-settings">
    <div class="settings-header">
      <h2>System Settings</h2>
      <p>Configure your application preferences and system options</p>
    </div>

    <!-- Tabs -->
    <div class="settings-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
      >
        <i :class="tab.icon"></i>
        {{ tab.name }}
      </button>
    </div>

    <div class="settings-content">
      <!-- General Settings -->
      <div v-if="activeTab === 'general'" class="settings-pane">
        <div class="settings-section">
          <h3>General Settings</h3>
          <div class="settings-form">
            <div class="form-group">
              <label class="form-label">Site Name</label>
              <input type="text" v-model="general.site_name" class="form-input">
              <div class="form-hint">This appears in browser tabs and headers</div>
            </div>

            <div class="form-group">
              <label class="form-label">Site Description</label>
              <textarea v-model="general.site_description" class="form-textarea" rows="3"></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Contact Email</label>
              <input type="email" v-model="general.contact_email" class="form-input">
            </div>

            <div class="form-group">
              <label class="form-label">Contact Phone</label>
              <input type="text" v-model="general.contact_phone" class="form-input">
            </div>

            <div class="form-group">
              <label class="form-label">Address</label>
              <textarea v-model="general.address" class="form-textarea" rows="2"></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- Email Settings -->
      <div v-if="activeTab === 'email'" class="settings-pane">
        <div class="settings-section">
          <h3>Email Configuration</h3>
          <div class="settings-form">
            <div class="form-group">
              <label class="form-label">SMTP Server</label>
              <input type="text" v-model="email.smtp_server" class="form-input" placeholder="smtp.gmail.com">
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">SMTP Port</label>
                <input type="number" v-model="email.smtp_port" class="form-input" placeholder="587">
              </div>
              <div class="form-group">
                <label class="form-label">Encryption</label>
                <select v-model="email.encryption" class="form-select">
                  <option value="tls">TLS</option>
                  <option value="ssl">SSL</option>
                  <option value="none">None</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">SMTP Username</label>
              <input type="email" v-model="email.smtp_username" class="form-input">
            </div>

            <div class="form-group">
              <label class="form-label">SMTP Password</label>
              <input type="password" v-model="email.smtp_password" class="form-input">
              <div class="form-hint">Password is stored encrypted</div>
            </div>

            <div class="form-group">
              <label class="form-label">From Email</label>
              <input type="email" v-model="email.from_email" class="form-input">
            </div>

            <div class="form-group">
              <label class="form-label">From Name</label>
              <input type="text" v-model="email.from_name" class="form-input">
            </div>

            <button @click="testEmail" class="btn btn-outline">
              <i class="fas fa-paper-plane"></i> Send Test Email
            </button>
          </div>
        </div>
      </div>

      <!-- Security Settings -->
      <div v-if="activeTab === 'security'" class="settings-pane">
        <div class="settings-section">
          <h3>Security Settings</h3>
          <div class="settings-form">
            <div class="form-group">
              <label class="toggle-switch">
                <input type="checkbox" v-model="security.two_factor_auth">
                <span class="toggle-slider"></span>
                <span class="toggle-label">Require Two-Factor Authentication</span>
              </label>
            </div>

            <div class="form-group">
              <label class="toggle-switch">
                <input type="checkbox" v-model="security.email_verification">
                <span class="toggle-slider"></span>
                <span class="toggle-label">Require Email Verification</span>
              </label>
            </div>

            <div class="form-group">
              <label class="form-label">Session Timeout (minutes)</label>
              <input type="number" v-model="security.session_timeout" class="form-input" min="15" max="720">
              <div class="form-hint">Users will be logged out after inactivity</div>
            </div>

            <div class="form-group">
              <label class="form-label">Max Login Attempts</label>
              <input type="number" v-model="security.max_login_attempts" class="form-input" min="3" max="10">
            </div>
          </div>
        </div>
      </div>

      <!-- Backup & Maintenance -->
      <div v-if="activeTab === 'backup'" class="settings-pane">
        <div class="settings-section">
          <h3>Backup & Maintenance</h3>
          <div class="settings-form">
            <div class="form-group">
              <label class="toggle-switch">
                <input type="checkbox" v-model="backup.auto_backup">
                <span class="toggle-slider"></span>
                <span class="toggle-label">Automatic Backups</span>
              </label>
            </div>

            <div class="form-group" v-if="backup.auto_backup">
              <label class="form-label">Backup Frequency</label>
              <select v-model="backup.frequency" class="form-select">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div class="form-actions">
              <button @click="createBackup" class="btn btn-primary">
                <i class="fas fa-database"></i> Create Backup Now
              </button>
              <button @click="clearCache" class="btn btn-outline">
                <i class="fas fa-broom"></i> Clear Cache
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- API Settings -->
      <div v-if="activeTab === 'api'" class="settings-pane">
        <div class="settings-section">
          <h3>API Configuration</h3>
          <div class="settings-form">
            <div class="form-group">
              <label class="form-label">API Rate Limit (requests per minute)</label>
              <input type="number" v-model="api.rate_limit" class="form-input" min="10" max="1000">
            </div>

            <div class="form-group">
              <label class="toggle-switch">
                <input type="checkbox" v-model="api.enable_api">
                <span class="toggle-slider"></span>
                <span class="toggle-label">Enable API Access</span>
              </label>
            </div>

            <div class="form-group" v-if="api.enable_api">
              <button @click="regenerateApiKey" class="btn btn-outline">
                <i class="fas fa-key"></i> Regenerate API Key
              </button>
              <div class="form-hint">Current API Key: {{ api.api_key || 'Not generated' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="settings-actions">
      <button @click="saveSettings" class="btn btn-primary" :disabled="saving">
        <i v-if="saving" class="fas fa-spinner fa-spin"></i>
        <i v-else class="fas fa-save"></i>
        {{ saving ? 'Saving...' : 'Save All Settings' }}
      </button>
      <button @click="resetSettings" class="btn btn-secondary">
        <i class="fas fa-undo"></i> Reset to Default
      </button>
    </div>

    <!-- Notification -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      <i :class="notification.icon"></i>
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

const activeTab = ref('general')
const saving = ref(false)

const tabs = [
  { id: 'general', name: 'General', icon: 'fas fa-cog' },
  { id: 'email', name: 'Email', icon: 'fas fa-envelope' },
  { id: 'security', name: 'Security', icon: 'fas fa-shield-alt' },
  { id: 'backup', name: 'Backup', icon: 'fas fa-database' },
  { id: 'api', name: 'API', icon: 'fas fa-code' }
]

// Settings data
const general = ref({
  site_name: 'Mount Kenya Milk',
  site_description: 'Kenya\'s largest dairy co-operative',
  contact_email: 'info@merudairy.co.ke',
  contact_phone: '+254 710 901 376',
  address: 'Meru Town, Kenya'
})

const email = ref({
  smtp_server: 'smtp.gmail.com',
  smtp_port: 587,
  encryption: 'tls',
  smtp_username: '',
  smtp_password: '',
  from_email: 'noreply@merudairy.co.ke',
  from_name: 'Meru Dairy'
})

const security = ref({
  two_factor_auth: true,
  email_verification: true,
  session_timeout: 60,
  max_login_attempts: 5
})

const backup = ref({
  auto_backup: false,
  frequency: 'weekly'
})

const apiSettings = ref({
  rate_limit: 100,
  enable_api: false,
  api_key: ''
})

const notification = ref({
  show: false,
  type: 'success',
  icon: '',
  message: ''
})

const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    type,
    icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle',
    message
  }
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

const loadSettings = async () => {
  try {
    const response = await api.get('/admin/settings')
    const data = response.data
    general.value = data.general || general.value
    email.value = data.email || email.value
    security.value = data.security || security.value
    backup.value = data.backup || backup.value
    apiSettings.value = data.api || apiSettings.value
  } catch (error) {
    console.error('Error loading settings:', error)
    // Load from localStorage as fallback
    const saved = localStorage.getItem('system_settings')
    if (saved) {
      const data = JSON.parse(saved)
      general.value = data.general || general.value
      email.value = data.email || email.value
      security.value = data.security || security.value
      backup.value = data.backup || backup.value
      apiSettings.value = data.api || apiSettings.value
    }
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const settings = {
      general: general.value,
      email: email.value,
      security: security.value,
      backup: backup.value,
      api: apiSettings.value
    }
    
    await api.post('/admin/settings', settings)
    localStorage.setItem('system_settings', JSON.stringify(settings))
    showNotification('Settings saved successfully!')
    toast.success('Settings saved successfully')
  } catch (error) {
    console.error('Error saving settings:', error)
    showNotification('Failed to save settings', 'error')
    toast.error('Failed to save settings')
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  if (confirm('Reset all settings to default values?')) {
    general.value = {
      site_name: 'Mount Kenya Milk',
      site_description: 'Kenya\'s largest dairy co-operative',
      contact_email: 'info@merudairy.co.ke',
      contact_phone: '+254 710 901 376',
      address: 'Meru Town, Kenya'
    }
    email.value = {
      smtp_server: 'smtp.gmail.com',
      smtp_port: 587,
      encryption: 'tls',
      smtp_username: '',
      smtp_password: '',
      from_email: 'noreply@merudairy.co.ke',
      from_name: 'Meru Dairy'
    }
    security.value = {
      two_factor_auth: true,
      email_verification: true,
      session_timeout: 60,
      max_login_attempts: 5
    }
    backup.value = {
      auto_backup: false,
      frequency: 'weekly'
    }
    apiSettings.value = {
      rate_limit: 100,
      enable_api: false,
      api_key: ''
    }
    showNotification('Settings reset to default')
  }
}

const testEmail = async () => {
  try {
    await api.post('/admin/test-email', { to: email.value.smtp_username })
    showNotification('Test email sent successfully!')
    toast.success('Test email sent')
  } catch (error) {
    showNotification('Failed to send test email', 'error')
    toast.error('Failed to send test email')
  }
}

const createBackup = async () => {
  try {
    const response = await api.post('/admin/backup')
    showNotification('Backup created successfully!')
    toast.success('Backup created')
  } catch (error) {
    showNotification('Failed to create backup', 'error')
    toast.error('Failed to create backup')
  }
}

const clearCache = async () => {
  if (confirm('Clear system cache? This may temporarily slow down the site.')) {
    try {
      await api.post('/admin/clear-cache')
      showNotification('Cache cleared successfully')
      toast.success('Cache cleared')
    } catch (error) {
      showNotification('Failed to clear cache', 'error')
    }
  }
}

const regenerateApiKey = async () => {
  if (confirm('Regenerate API key? Old key will stop working.')) {
    try {
      const response = await api.post('/admin/regenerate-api-key')
      apiSettings.value.api_key = response.data.api_key
      showNotification('API key regenerated')
    } catch (error) {
      showNotification('Failed to regenerate API key', 'error')
    }
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.system-settings {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.settings-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.settings-header h2 {
  color: #1e3a8a;
  margin: 0 0 0.25rem 0;
}

.settings-header p {
  color: #666;
  margin: 0;
}

.settings-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  transition: all 0.3s;
  border-radius: 8px 8px 0 0;
}

.tab-btn i {
  margin-right: 0.5rem;
}

.tab-btn:hover {
  background: #f8fafc;
  color: #f59e0b;
}

.tab-btn.active {
  color: #f59e0b;
  border-bottom: 2px solid #f59e0b;
}

.settings-pane {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 1rem;
}

.settings-section {
  margin-bottom: 2rem;
}

.settings-section h3 {
  color: #1e3a8a;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label {
  font-weight: 500;
  font-size: 0.85rem;
  color: #333;
}

.form-input, .form-select, .form-textarea {
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.85rem;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #f59e0b;
}

.form-hint {
  font-size: 0.7rem;
  color: #999;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.toggle-slider {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #f59e0b;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.toggle-label {
  font-size: 0.85rem;
  color: #333;
}

/* Form Actions */
.settings-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-primary {
  background: #f59e0b;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #d97706;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-outline {
  background: transparent;
  border: 1px solid #e5e7eb;
  color: #333;
}

.btn-outline:hover {
  border-color: #f59e0b;
  color: #f59e0b;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Notification */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

.notification.success {
  background: #d1fae5;
  color: #065f46;
  border-left: 4px solid #10b981;
}

.notification.error {
  background: #fee2e2;
  color: #991b1b;
  border-left: 4px solid #ef4444;
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

@media (max-width: 768px) {
  .settings-tabs {
    gap: 0.25rem;
  }
  
  .tab-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .settings-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>