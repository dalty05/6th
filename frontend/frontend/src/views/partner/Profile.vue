<template>
  <div class="partner-layout">
    <!-- Sidebar -->
    <PartnerSidebar ref="sidebarRef" />

    <!-- Main Content -->
    <main class="partner-main">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <button class="sidebar-toggle" @click="toggleSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <h1><i class="fas fa-user"></i> Profile</h1>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="saveProfile" :disabled="saving">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-save"></i>
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>

      <!-- Page Content -->
      <div class="page-content">
        <div class="profile-grid">
          <!-- Profile Information -->
          <div class="profile-card glass-card">
            <div class="profile-header">
              <div class="profile-avatar">
                <i class="fas fa-user-circle"></i>
              </div>
              <div class="profile-title">
                <h2>{{ user?.full_name || 'Partner' }}</h2>
                <span :class="['role-badge', getRoleClass(user?.role)]">
                  {{ getRoleLabel(user?.role) }}
                </span>
              </div>
            </div>

            <form @submit.prevent="saveProfile" class="profile-form">
              <div class="form-group">
                <label>Full Name *</label>
                <input 
                  type="text" 
                  v-model="form.full_name" 
                  placeholder="Enter your full name"
                  required
                />
              </div>

              <div class="form-group">
                <label>Email Address *</label>
                <input 
                  type="email" 
                  v-model="form.email" 
                  placeholder="Enter your email"
                  disabled
                  class="disabled-input"
                />
                <small class="help-text">Email cannot be changed. Contact admin for assistance.</small>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>Total Clicks</label>
                  <input 
                    type="text" 
                    :value="stats.totalClicks || 0" 
                    disabled
                    class="disabled-input stat-input"
                  />
                </div>
                <div class="form-group">
                  <label>Total Conversions</label>
                  <input 
                    type="text" 
                    :value="stats.totalConversions || 0" 
                    disabled
                    class="disabled-input stat-input"
                  />
                </div>
              </div>
            </form>
          </div>

          <!-- Referral Code Section -->
          <div class="referral-section">
            <div class="glass-card">
              <h3><i class="fas fa-link"></i> Your Referral Code</h3>
              <div class="code-display">
                <div class="code-box">
                  <code>{{ user?.referral_code || 'Not generated' }}</code>
                  <button 
                    v-if="user?.referral_code" 
                    @click="copyReferralCode" 
                    class="copy-btn"
                    title="Copy referral code"
                  >
                    <i class="fas fa-copy"></i>
                  </button>
                </div>
                <p class="code-hint">
                  <i class="fas fa-info-circle"></i>
                  Share this code with customers to earn referral rewards
                </p>
              </div>
              <div class="referral-link-display">
                <label>Your Referral Link:</label>
                <div class="link-box">
                  <code>{{ fullReferralLink }}</code>
                  <CopyLinkButton 
                    v-if="user?.referral_code" 
                    :link="fullReferralLink" 
                  />
                </div>
              </div>
            </div>

            <!-- Stats Overview -->
            <div class="glass-card">
              <h3><i class="fas fa-chart-simple"></i> Performance Overview</h3>
              <div class="stats-overview">
                <div class="stat-item">
                  <span class="stat-label">Total Clicks</span>
                  <span class="stat-value">{{ stats.totalClicks || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Unique Visitors</span>
                  <span class="stat-value">{{ stats.uniqueClicks || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Conversions</span>
                  <span class="stat-value">{{ stats.totalConversions || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Conversion Rate</span>
                  <span class="stat-value">{{ conversionRate }}%</span>
                </div>
              </div>
            </div>

            <!-- Account Settings -->
            <div class="glass-card">
              <h3><i class="fas fa-cog"></i> Account Settings</h3>
              
              <div class="settings-item">
                <div class="settings-info">
                  <span class="settings-label">Account Status</span>
                  <span :class="['status-badge', user?.is_active ? 'active' : 'inactive']">
                    {{ user?.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div class="settings-info">
                  <span class="settings-label">Approval Status</span>
                  <span :class="['status-badge', user?.is_approved ? 'approved' : 'pending']">
                    {{ user?.is_approved ? 'Approved' : 'Pending Approval' }}
                  </span>
                </div>
                <div class="settings-info">
                  <span class="settings-label">Member Since</span>
                  <span class="settings-value">{{ formatDate(user?.created_at) }}</span>
                </div>
                <div class="settings-info">
                  <span class="settings-label">Last Login</span>
                  <span class="settings-value">{{ formatDate(user?.last_login) || 'Never' }}</span>
                </div>
              </div>

              <div class="settings-actions">
                <button @click="changePassword" class="btn-secondary">
                  <i class="fas fa-key"></i> Change Password
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Change Password Modal -->
    <div class="modal-overlay" v-if="showPasswordModal" @click.self="closePasswordModal">
      <div class="modal-container modal-sm">
        <div class="modal-header">
          <h2>Change Password</h2>
          <button class="close-btn" @click="closePasswordModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updatePassword" class="password-form">
            <div class="form-group">
              <label>Current Password *</label>
              <input 
                type="password" 
                v-model="passwordForm.current" 
                placeholder="Enter current password"
                required
              />
            </div>
            <div class="form-group">
              <label>New Password *</label>
              <input 
                type="password" 
                v-model="passwordForm.new" 
                placeholder="Enter new password (min 8 characters)"
                required
                minlength="8"
              />
            </div>
            <div class="form-group">
              <label>Confirm New Password *</label>
              <input 
                type="password" 
                v-model="passwordForm.confirm" 
                placeholder="Confirm new password"
                required
              />
              <small v-if="passwordForm.new && passwordForm.confirm && passwordForm.new !== passwordForm.confirm" class="error-text">
                Passwords do not match
              </small>
            </div>
            <div class="form-actions">
              <button type="button" @click="closePasswordModal" class="btn-cancel">Cancel</button>
              <button 
                type="submit" 
                class="btn-primary" 
                :disabled="passwordForm.new !== passwordForm.confirm || passwordForm.new.length < 8 || updatingPassword"
              >
                <i v-if="updatingPassword" class="fas fa-spinner fa-spin"></i>
                {{ updatingPassword ? 'Updating...' : 'Update Password' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import authService from '@/services/auth'
import referralService from '@/services/referral'
import api from '@/services/api'
import PartnerSidebar from '@/components/partner/PartnerSidebar.vue'
import CopyLinkButton from '@/components/partner/CopyLinkButton.vue'

const router = useRouter()
const sidebarRef = ref(null)
const user = ref(null)
const saving = ref(false)
const updatingPassword = ref(false)
const showPasswordModal = ref(false)

const stats = ref({
  totalClicks: 0,
  uniqueClicks: 0,
  totalConversions: 0
})

const form = ref({
  full_name: '',
  email: '',
  phone: ''
})

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

const baseUrl = window.location.origin

const fullReferralLink = computed(() => 
  user.value?.referral_code ? `${baseUrl}/r/${user.value.referral_code}` : ''
)

const conversionRate = computed(() => {
  const clicks = stats.value.totalClicks || 0
  const conversions = stats.value.totalConversions || 0
  if (clicks === 0) return 0
  return ((conversions / clicks) * 100).toFixed(1)
})

const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleMobile()
  }
}

const getRoleLabel = (role) => {
  const roles = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    partner: 'Partner'
  }
  return roles[role] || role
}

const getRoleClass = (role) => {
  const classes = {
    super_admin: 'role-super',
    admin: 'role-admin',
    partner: 'role-partner'
  }
  return classes[role] || ''
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const loadUserData = async () => {
  try {
    // Get user from auth service (already stored in localStorage)
    const currentUser = authService.getUser()
    if (currentUser) {
      user.value = currentUser
      form.value = {
        full_name: currentUser.full_name || '',
        email: currentUser.email || '',
        phone: currentUser.phone || ''
      }
    } else {
      toast.error('Failed to load profile data. Please refresh the page.')
    }
  } catch (error) {
    console.error('Error loading user data:', error)
    const storedUser = authService.getUser()
    if (storedUser) {
      user.value = storedUser
      form.value = {
        full_name: storedUser.full_name || '',
        email: storedUser.email || '',
        phone: storedUser.phone || ''
      }
    }
  }
}

const loadStats = async () => {
  try {
    const response = await referralService.getStats()
    stats.value = {
      totalClicks: response.total_clicks || 0,
      uniqueClicks: response.total_unique_clicks || 0,
      totalConversions: response.total_conversions || 0
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const saveProfile = async () => {
  if (!user.value?.id) {
    toast.error('User data not loaded')
    return
  }

  saving.value = true
  try {
    await api.put(`/admin/users/${user.value.id}`, {
      full_name: form.value.full_name,
      phone: form.value.phone
    })
    
    // Update local user data
    const updatedUser = { ...user.value, full_name: form.value.full_name }
    user.value = updatedUser
    authService.setUser(updatedUser)
    
    toast.success('Profile updated successfully')
  } catch (error) {
    console.error('Error saving profile:', error)
    toast.error(error.response?.data?.error || 'Failed to update profile')
  } finally {
    saving.value = false
  }
}

const copyReferralCode = () => {
  if (user.value?.referral_code) {
    navigator.clipboard.writeText(user.value.referral_code).then(() => {
      toast.success('Referral code copied to clipboard')
    }).catch(() => {
      const textArea = document.createElement('textarea')
      textArea.value = user.value.referral_code
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      toast.success('Referral code copied to clipboard')
    })
  }
}

const changePassword = () => {
  passwordForm.value = {
    current: '',
    new: '',
    confirm: ''
  }
  showPasswordModal.value = true
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  passwordForm.value = {
    current: '',
    new: '',
    confirm: ''
  }
  updatingPassword.value = false
}

const updatePassword = async () => {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    toast.error('Passwords do not match')
    return
  }
  
  if (passwordForm.value.new.length < 8) {
    toast.error('Password must be at least 8 characters')
    return
  }

  updatingPassword.value = true
  try {
    await api.post(`/admin/users/${user.value.id}/reset-password`, {
      new_password: passwordForm.value.new
    })
    toast.success('Password updated successfully')
    closePasswordModal()
  } catch (error) {
    console.error('Error updating password:', error)
    toast.error(error.response?.data?.error || 'Failed to update password')
  } finally {
    updatingPassword.value = false
  }
}

onMounted(() => {
  const currentUser = authService.getUser()
  if (!currentUser) {
    router.push('/')
    return
  }
  loadUserData()
  loadStats()
})
</script>

<style scoped>
.partner-layout {
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
}

.partner-main {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-header h1 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-header h1 i {
  color: #f59e0b;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.page-content {
  flex: 1;
  padding: 1.5rem 2rem;
}

.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #0f172a;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.sidebar-toggle:hover {
  background: #f1f5f9;
}

/* Profile Grid */
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.glass-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-bottom: 1.5rem;
}

.glass-card h3 {
  font-size: 1rem;
  color: #0f172a;
  margin: 0 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.glass-card h3 i {
  color: #f59e0b;
}

/* Profile Header */
.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.profile-avatar i {
  font-size: 4rem;
  color: #94a3b8;
}

.profile-title h2 {
  font-size: 1.3rem;
  color: #0f172a;
  margin: 0 0 0.25rem;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.role-super { background: #1e3a8a; color: white; }
.role-admin { background: #f59e0b; color: white; }
.role-partner { background: #10b981; color: white; }

/* Form */
.profile-form .form-group {
  margin-bottom: 1rem;
}

.profile-form label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.45rem;
}

.profile-form input {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.7rem 0.9rem;
  transition: 0.2s;
  font-size: 0.9rem;
}

.profile-form input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.disabled-input {
  background: #f8fafc;
  color: #6b7280;
  cursor: not-allowed;
}

.stat-input {
  font-weight: 600;
  color: #0f172a;
}

.help-text {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Code Display */
.code-display {
  margin-bottom: 1rem;
}

.code-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f1f5f9;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
}

.code-box code {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #0f172a;
  word-break: break-all;
}

.copy-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: 0.2s;
}

.copy-btn:hover {
  background: #e5e7eb;
  color: #0f172a;
}

.code-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0.5rem 0 0;
}

.code-hint i {
  color: #f59e0b;
  margin-right: 0.25rem;
}

.referral-link-display {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.referral-link-display label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.45rem;
}

.link-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f1f5f9;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
}

.link-box code {
  flex: 1;
  font-size: 0.8rem;
  color: #0f172a;
  word-break: break-all;
  font-family: 'Courier New', monospace;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.stat-item {
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.7rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin-top: 0.25rem;
}

/* Settings */
.settings-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.settings-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.settings-info:last-child {
  border-bottom: none;
}

.settings-label {
  font-size: 0.85rem;
  color: #6b7280;
}

.settings-value {
  font-size: 0.85rem;
  font-weight: 500;
  color: #0f172a;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.status-badge.active { background: #d1fae5; color: #065f46; }
.status-badge.inactive { background: #fee2e2; color: #991b1b; }
.status-badge.approved { background: #d1fae5; color: #065f46; }
.status-badge.pending { background: #fef3c7; color: #92400e; }

.settings-actions {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

/* Buttons */
.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.25rem;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.modal-container {
  width: 100%;
  max-width: 500px;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  animation: modalPop 0.25s ease;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: white;
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.15rem;
  font-weight: 600;
}

.modal-body {
  padding: 1.5rem;
}

.close-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  cursor: pointer;
  font-size: 1.3rem;
  transition: 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

.password-form .form-group {
  margin-bottom: 1rem;
}

.password-form label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.45rem;
}

.password-form input {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.7rem 0.9rem;
  transition: 0.2s;
  font-size: 0.9rem;
}

.password-form input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.error-text {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalPop {
  from {
    opacity: 0;
    transform: translateY(15px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .partner-main {
    margin-left: 0;
  }
  
  .sidebar-toggle {
    display: flex;
  }
  
  .page-header {
    padding: 0.75rem 1rem;
  }
  
  .page-content {
    padding: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .stats-overview {
    grid-template-columns: 1fr 1fr;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }
}
</style>