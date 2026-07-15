<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>My Profile</h1>
      <p class="subtitle">Manage your account settings and preferences</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading profile...</p>
    </div>

    <!-- Profile Content -->
    <div v-else class="profile-content">
      <!-- Profile Card -->
      <div class="profile-card glass-card">
        <div class="profile-avatar">
          <div class="avatar-circle">
            <span>{{ userInitials }}</span>
          </div>
          <div class="role-badge" :class="roleClass">
            <i :class="roleIcon"></i> {{ roleDisplayName }}
          </div>
        </div>

        <div class="profile-info">
          <div class="info-group">
            <label>Full Name</label>
            <div class="info-value">
              <span>{{ user.full_name }}</span>
              <button @click="editField('full_name')" class="edit-btn">
                <i class="fas fa-pen"></i>
              </button>
            </div>
          </div>

          <div class="info-group">
            <label>Email Address</label>
            <div class="info-value">
              <span>{{ user.email }}</span>
              <span class="verified-badge" v-if="user.email_verified">
                <i class="fas fa-check-circle"></i> Verified
              </span>
              <span class="unverified-badge" v-else>
                <i class="fas fa-exclamation-circle"></i> Unverified
              </span>
            </div>
          </div>

          <div class="info-group">
            <label>Role</label>
            <div class="info-value">
              <span>{{ roleDisplayName }}</span>
            </div>
          </div>

          <div class="info-group">
            <label>Member Since</label>
            <div class="info-value">
              <span>{{ formatDate(user.created_at) }}</span>
            </div>
          </div>

          <div class="info-group">
            <label>Last Login</label>
            <div class="info-value">
              <span>{{ user.last_login ? formatDate(user.last_login) : 'Never' }}</span>
            </div>
          </div>

          <div class="info-group" v-if="user.referral_code">
            <label>Referral Code</label>
            <div class="info-value referral-code">
              <code>{{ user.referral_code }}</code>
              <button @click="copyReferralCode" class="copy-btn">
                <i class="fas fa-copy"></i> Copy
              </button>
            </div>
          </div>

          <div class="info-group" v-if="user.is_tour_manager || user.is_tour_assistant">
            <label>Tour Staff Status</label>
            <div class="info-value">
              <span class="tour-badge" v-if="user.is_tour_manager">
                <i class="fas fa-user-tie"></i> Tour Manager
              </span>
              <span class="tour-badge assistant" v-else-if="user.is_tour_assistant">
                <i class="fas fa-user"></i> Tour Assistant
              </span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="profile-actions">
          <button @click="openEditProfile" class="btn btn-primary">
            <i class="fas fa-user-edit"></i> Edit Profile
          </button>
          <button @click="openChangePassword" class="btn btn-outline">
            <i class="fas fa-key"></i> Change Password
          </button>
        </div>
      </div>

      <!-- Activity Log -->
      <div class="activity-section" v-if="activities.length > 0">
        <h3><i class="fas fa-history"></i> Recent Activity</h3>
        <div class="activity-list">
          <div v-for="activity in activities" :key="activity.id" class="activity-item">
            <div class="activity-icon" :class="activity.type">
              <i :class="getActivityIcon(activity.action)"></i>
            </div>
            <div class="activity-content">
              <p>{{ activity.description }}</p>
              <span class="activity-time">{{ formatDate(activity.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Edit Profile</h2>
          <button @click="closeEditModal" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Full Name</label>
            <input 
              type="text" 
              v-model="editForm.full_name" 
              placeholder="Enter your full name"
              class="form-input"
            >
          </div>
          <div class="form-actions">
            <button @click="closeEditModal" class="btn btn-outline">Cancel</button>
            <button @click="saveProfile" class="btn btn-primary" :disabled="saving">
              <span v-if="!saving">Save Changes</span>
              <span v-else><i class="fas fa-spinner fa-spin"></i> Saving...</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="closePasswordModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Change Password</h2>
          <button @click="closePasswordModal" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Current Password</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input 
                :type="showCurrentPassword ? 'text' : 'password'" 
                v-model="passwordForm.current_password" 
                placeholder="Enter current password"
                class="form-input"
              >
              <button @click="showCurrentPassword = !showCurrentPassword" class="toggle-password">
                <i :class="showCurrentPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>New Password</label>
            <div class="input-wrapper">
              <i class="fas fa-key input-icon"></i>
              <input 
                :type="showNewPassword ? 'text' : 'password'" 
                v-model="passwordForm.new_password" 
                placeholder="Enter new password"
                class="form-input"
              >
              <button @click="showNewPassword = !showNewPassword" class="toggle-password">
                <i :class="showNewPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <div class="password-requirements">
              <p :class="{ valid: passwordValid.length >= 8 }">
                <i :class="passwordValid.length >= 8 ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
                At least 8 characters
              </p>
              <p :class="{ valid: passwordValid.hasUpper }">
                <i :class="passwordValid.hasUpper ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
                One uppercase letter
              </p>
              <p :class="{ valid: passwordValid.hasLower }">
                <i :class="passwordValid.hasLower ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
                One lowercase letter
              </p>
              <p :class="{ valid: passwordValid.hasNumber }">
                <i :class="passwordValid.hasNumber ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
                One number
              </p>
            </div>
          </div>

          <div class="form-group">
            <label>Confirm New Password</label>
            <div class="input-wrapper">
              <i class="fas fa-check input-icon"></i>
              <input 
                :type="showConfirmPassword ? 'text' : 'password'" 
                v-model="passwordForm.confirm_password" 
                placeholder="Confirm new password"
                class="form-input"
              >
              <button @click="showConfirmPassword = !showConfirmPassword" class="toggle-password">
                <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <p v-if="passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password" class="error-message">
              Passwords do not match
            </p>
          </div>

          <div class="form-actions">
            <button @click="closePasswordModal" class="btn btn-outline">Cancel</button>
            <button 
              @click="changePassword" 
              class="btn btn-primary" 
              :disabled="!canChangePassword || saving"
            >
              <span v-if="!saving">Update Password</span>
              <span v-else><i class="fas fa-spinner fa-spin"></i> Updating...</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="alert-success">
      <i class="fas fa-check-circle"></i> {{ successMessage }}
    </div>
    <div v-if="errorMessage" class="alert-error">
      <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'
import api from '@/services/api'

export default {
  name: 'MyProfile',
  
  data() {
    return {
      loading: true,
      saving: false,
      user: {},
      activities: [],
      
      // Edit Profile
      showEditModal: false,
      editForm: {
        full_name: ''
      },
      
      // Change Password
      showPasswordModal: false,
      showCurrentPassword: false,
      showNewPassword: false,
      showConfirmPassword: false,
      passwordForm: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
      
      successMessage: '',
      errorMessage: '',
      messageTimeout: null
    }
  },

  computed: {
    userInitials() {
      if (!this.user.full_name) return 'U'
      return this.user.full_name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    },
    
    roleDisplayName() {
      return authService.getRoleDisplayName() || 'User'
    },
    
    roleClass() {
      const role = this.user.role || 'user'
      return {
        'super-admin': role === 'super_admin',
        'admin': role === 'admin',
        'tour-manager': role === 'tour_manager',
        'tour-assistant': role === 'tour_assistant',
        'partner': role === 'partner'
      }
    },
    
    roleIcon() {
      const role = this.user.role || 'user'
      const icons = {
        'super_admin': 'fas fa-crown',
        'admin': 'fas fa-user-shield',
        'tour_manager': 'fas fa-user-tie',
        'tour_assistant': 'fas fa-user',
        'partner': 'fas fa-handshake'
      }
      return icons[role] || 'fas fa-user'
    },
    
    passwordValid() {
      const pwd = this.passwordForm.new_password || ''
      return {
        length: pwd.length >= 8,
        hasUpper: /[A-Z]/.test(pwd),
        hasLower: /[a-z]/.test(pwd),
        hasNumber: /\d/.test(pwd)
      }
    },
    
    canChangePassword() {
      return (
        this.passwordForm.current_password &&
        this.passwordForm.new_password &&
        this.passwordForm.confirm_password &&
        this.passwordForm.new_password === this.passwordForm.confirm_password &&
        this.passwordValid.length &&
        this.passwordValid.hasUpper &&
        this.passwordValid.hasLower &&
        this.passwordValid.hasNumber
      )
    }
  },

  mounted() {
    this.loadProfile()
  },

  beforeUnmount() {
    if (this.messageTimeout) {
      clearTimeout(this.messageTimeout)
    }
  },

  methods: {
    async loadProfile() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await api.get('/admin/profile')
        this.user = response.data
        this.editForm.full_name = this.user.full_name
        
        // Load activities
        await this.loadActivities()
        
      } catch (error) {
        
        this.errorMessage = error.response?.data?.error || 'Failed to load profile'
      } finally {
        this.loading = false
      }
    },
    
    async loadActivities() {
      try {
        const response = await api.get('/admin/activities?limit=10')
        this.activities = response.data.activities || []
      } catch (error) {
        this.activities = []
      }
    },
    
    editField(field) {
      if (field === 'full_name') {
        this.openEditProfile()
      }
    },
    
    openEditProfile() {
      this.editForm.full_name = this.user.full_name
      this.showEditModal = true
    },
    
    closeEditModal() {
      this.showEditModal = false
    },
    
    async saveProfile() {
      this.saving = true
      this.errorMessage = ''
      
      try {
        const response = await authService.updateProfile(this.editForm.full_name)
        this.user = response.user || this.user
        this.showEditModal = false
        this.showSuccess('Profile updated successfully!')
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to update profile'
        this.showError(this.errorMessage)
      } finally {
        this.saving = false
      }
    },
    
    openChangePassword() {
      this.passwordForm = {
        current_password: '',
        new_password: '',
        confirm_password: ''
      }
      this.showPasswordModal = true
    },
    
    closePasswordModal() {
      this.showPasswordModal = false
    },
    
    async changePassword() {
      if (!this.canChangePassword) return
      
      this.saving = true
      this.errorMessage = ''
      
      try {
        await authService.changePassword(
          this.passwordForm.current_password,
          this.passwordForm.new_password
        )
        this.showPasswordModal = false
        this.showSuccess('Password changed successfully!')
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to change password'
        this.showError(this.errorMessage)
      } finally {
        this.saving = false
      }
    },
    
    async copyReferralCode() {
      if (!this.user.referral_code) return
      
      try {
        await navigator.clipboard.writeText(this.user.referral_code)
        this.showSuccess('Referral code copied!')
      } catch (error) {
        
        // Fallback
        const input = document.createElement('input')
        input.value = this.user.referral_code
        document.body.appendChild(input)
        input.select()
        document.execCommand('copy')
        document.body.removeChild(input)
        this.showSuccess('Referral code copied!')
      }
    },
    
    getActivityIcon(action) {
      const icons = {
        'login': 'fas fa-sign-in-alt',
        'logout': 'fas fa-sign-out-alt',
        'update': 'fas fa-edit',
        'create': 'fas fa-plus',
        'delete': 'fas fa-trash',
        'view': 'fas fa-eye',
        'booking': 'fas fa-calendar-check',
        'payment': 'fas fa-money-bill'
      }
      return icons[action] || 'fas fa-circle'
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-KE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    showSuccess(message) {
      this.successMessage = message
      if (this.messageTimeout) clearTimeout(this.messageTimeout)
      this.messageTimeout = setTimeout(() => {
        this.successMessage = ''
      }, 5000)
    },
    
    showError(message) {
      this.errorMessage = message
      if (this.messageTimeout) clearTimeout(this.messageTimeout)
      this.messageTimeout = setTimeout(() => {
        this.errorMessage = ''
      }, 5000)
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 32px;
}

.profile-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.profile-header .subtitle {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.loading-state {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.profile-avatar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.role-badge.super-admin {
  background: #fef3c7;
  color: #92400e;
}

.role-badge.admin {
  background: #dbeafe;
  color: #1e40af;
}

.role-badge.tour-manager {
  background: #d1fae5;
  color: #065f46;
}

.role-badge.tour-assistant {
  background: #e0e7ff;
  color: #3730a3;
}

.role-badge.partner {
  background: #fce4ec;
  color: #9a3412;
}

.profile-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-group {
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-group:last-child {
  border-bottom: none;
}

.info-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  color: #1a1a2e;
  flex-wrap: wrap;
}

.edit-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #f1f5f9;
  color: #2563eb;
}

.verified-badge {
  color: #16a34a;
  font-size: 13px;
}

.unverified-badge {
  color: #dc2626;
  font-size: 13px;
}

.referral-code {
  font-family: monospace;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 6px;
}

.copy-btn {
  background: #e2e8f0;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: #cbd5e1;
}

.tour-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.tour-badge {
  background: #d1fae5;
  color: #065f46;
}

.tour-badge.assistant {
  background: #e0e7ff;
  color: #3730a3;
}

.profile-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-outline {
  background: transparent;
  color: #1a1a2e;
  border: 2px solid #e2e8f0;
}

.btn-outline:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #94a3b8;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.activity-section {
  background: white;
  border-radius: 16px;
  padding: 24px 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.activity-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #1a1a2e;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.login {
  background: #dbeafe;
  color: #1e40af;
}

.activity-icon.update {
  background: #d1fae5;
  color: #065f46;
}

.activity-icon.create {
  background: #fef3c7;
  color: #92400e;
}

.activity-icon.delete {
  background: #fee2e2;
  color: #dc2626;
}

.activity-content {
  flex: 1;
}

.activity-content p {
  margin: 0;
  font-size: 14px;
  color: #1a1a2e;
}

.activity-time {
  font-size: 12px;
  color: #94a3b8;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1a1a2e;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #94a3b8;
  cursor: pointer;
}

.modal-close:hover {
  color: #1a1a2e;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: #94a3b8;
}

.form-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
}

.password-requirements {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.password-requirements p {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}

.password-requirements p.valid {
  color: #16a34a;
}

.error-message {
  color: #dc2626;
  font-size: 13px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.alert-success {
  padding: 12px 16px;
  background: #dcfce7;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-error {
  padding: 12px 16px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-info {
    grid-template-columns: 1fr;
  }
  
  .profile-actions {
    flex-direction: column;
  }
  
  .profile-avatar {
    flex-direction: column;
    text-align: center;
  }
}

.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
}
</style>