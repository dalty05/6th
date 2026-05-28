<template>
  <div class="system-settings">
    <div class="header">
      <h2>System Settings</h2>
    </div>
    
    <div class="settings-section">
      <h3>General Settings</h3>
      <div class="settings-form">
        <div class="form-group">
          <label>Site Name</label>
          <input type="text" v-model="settings.site_name" placeholder="Mount Kenya Milk">
        </div>
        <div class="form-group">
          <label>Site Description</label>
          <textarea v-model="settings.site_description" rows="3" placeholder="Site description..."></textarea>
        </div>
        <div class="form-group">
          <label>Contact Email</label>
          <input type="email" v-model="settings.contact_email" placeholder="info@merudairy.co.ke">
        </div>
        <div class="form-group">
          <label>Contact Phone</label>
          <input type="text" v-model="settings.contact_phone" placeholder="+254 XXX XXX XXX">
        </div>
      </div>
    </div>
    
    <div class="settings-section">
      <h3>Email Settings</h3>
      <div class="settings-form">
        <div class="form-group">
          <label>SMTP Server</label>
          <input type="text" v-model="settings.smtp_server" placeholder="smtp.gmail.com">
        </div>
        <div class="form-group">
          <label>SMTP Port</label>
          <input type="number" v-model="settings.smtp_port" placeholder="587">
        </div>
        <div class="form-group">
          <label>SMTP Username</label>
          <input type="email" v-model="settings.smtp_username" placeholder="your-email@gmail.com">
        </div>
        <div class="form-group">
          <label>SMTP Password</label>
          <input type="password" v-model="settings.smtp_password" placeholder="••••••••">
        </div>
      </div>
    </div>
    
    <div class="settings-actions">
      <button @click="saveSettings" class="btn-primary">
        <i class="fas fa-save"></i> Save Settings
      </button>
      <button @click="resetSettings" class="btn-secondary">
        <i class="fas fa-undo"></i> Reset
      </button>
    </div>
    
    <div class="coming-soon-notice">
      <i class="fas fa-info-circle"></i>
      <p>Advanced settings including SEO, analytics integration, and backup options coming soon!</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const settings = ref({
  site_name: 'Mount Kenya Milk',
  site_description: 'Kenya\'s largest dairy co-operative',
  contact_email: 'info@merudairy.co.ke',
  contact_phone: '+254 710 901 376',
  smtp_server: '',
  smtp_port: '',
  smtp_username: '',
  smtp_password: ''
})

const saveSettings = () => {
  console.log('Saving settings:', settings.value)
  alert('Settings saved successfully! (Demo)')
}

const resetSettings = () => {
  settings.value = {
    site_name: 'Mount Kenya Milk',
    site_description: 'Kenya\'s largest dairy co-operative',
    contact_email: 'info@merudairy.co.ke',
    contact_phone: '+254 710 901 376',
    smtp_server: '',
    smtp_port: '',
    smtp_username: '',
    smtp_password: ''
  }
  alert('Settings reset to default')
}
</script>

<style scoped>
.system-settings {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.header {
  margin-bottom: 1.5rem;
}

.header h2 {
  color: #1e3a8a;
  margin: 0;
}

.settings-section {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.settings-section h3 {
  color: #1e3a8a;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.settings-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
}

.settings-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.coming-soon-notice {
  margin-top: 1rem;
  padding: 1rem;
  background: #fef3c7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #92400e;
}
</style>