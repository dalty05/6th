<template>
  <div class="tour-manager-profile">
    <div class="profile-header">
      <h1><i class="fas fa-user-circle"></i> My Profile</h1>
      <p>View and manage your account information</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading profile...</p>
    </div>

    <!-- Profile Content -->
    <div v-else class="profile-content">
      <div class="profile-card">
        <!-- User Info -->
        <div class="user-info-section">
          <div class="user-avatar-large">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="user-details">
            <h2>{{ user.full_name }}</h2>
            <p class="user-email">{{ user.email }}</p>
            <div class="user-badges">
              <span class="role-badge">{{ roleDisplayName }}</span>
              <span v-if="user.is_tour_manager" class="role-badge tour-manager">
                <i class="fas fa-user-tie"></i> Tour Manager
              </span>
              <span v-else-if="user.is_tour_assistant" class="role-badge tour-assistant">
                <i class="fas fa-user"></i> Tour Assistant
              </span>
            </div>
          </div>
        </div>

        <!-- Profile Details -->
        <div class="info-grid">
          <div class="info-item">
            <label>Full Name</label>
            <p>{{ user.full_name }}</p>
          </div>
          <div class="info-item">
            <label>Email</label>
            <p>{{ user.email }}</p>
          </div>
          <div class="info-item">
            <label>Role</label>
            <p>{{ roleDisplayName }}</p>
          </div>
          <div class="info-item">
            <label>Member Since</label>
            <p>{{ formatDate(user.created_at) }}</p>
          </div>
          <div class="info-item">
            <label>Last Login</label>
            <p>{{ user.last_login ? formatDate(user.last_login) : 'Never' }}</p>
          </div>
          <div class="info-item" v-if="user.is_tour_manager || user.is_tour_assistant">
            <label>Tour Staff Status</label>
            <p>
              <span v-if="user.is_tour_manager" class="status-badge active">
                <i class="fas fa-check-circle"></i> Tour Manager
              </span>
              <span v-else-if="user.is_tour_assistant" class="status-badge active">
                <i class="fas fa-check-circle"></i> Tour Assistant
              </span>
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="profile-actions">
          <button @click="editProfile" class="btn btn-primary">
            <i class="fas fa-edit"></i> Edit Profile
          </button>
          <button @click="changePassword" class="btn btn-outline">
            <i class="fas fa-key"></i> Change Password
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Edit Profile</h2>
          <button @click="showEditModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" v-model="editForm.full_name" class="form-input">
          </div>
          <div class="form-actions">
            <button @click="showEditModal = false" class="btn btn-outline">Cancel</button>
            <button @click="saveProfile" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Change Password</h2>
          <button @click="showPasswordModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Current Password</label>
            <input type="password" v-model="passwordForm.current_password" class="form-input">
          </div>
          <div class="form-group">
            <label>New Password</label>
            <input type="password" v-model="passwordForm.new_password" class="form-input">
          </div>
          <div class="form-group">
            <label>Confirm New Password</label>
            <input type="password" v-model="passwordForm.confirm_password" class="form-input">
          </div>
          <div class="form-actions">
            <button @click="showPasswordModal = false" class="btn btn-outline">Cancel</button>
            <button @click="updatePassword" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Updating...' : 'Update Password' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import authService from '@/services/auth'
import api from '@/services/api'

const user = ref({})
const loading = ref(true)
const saving = ref(false)
const showEditModal = ref(false)
const showPasswordModal = ref(false)

const editForm = ref({ full_name: '' })
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const roleDisplayName = computed(() => {
  if (!user.value) return 'User'
  
  if (user.value.is_tour_manager || user.value.role === 'tour_manager') {
    return 'Tour Manager'
  }
  if (user.value.is_tour_assistant || user.value.role === 'tour_assistant') {
    return 'Tour Assistant'
  }
  if (user.value.role === 'admin' || user.value.role === 'super_admin') {
    return 'Administrator'
  }
  return user.value.role || 'User'
})

const loadProfile = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/profile')
    user.value = response.data
    editForm.value.full_name = user.value.full_name
  } catch (error) {
    toast.error('Failed to load profile')
  } finally {
    loading.value = false
  }
}

const editProfile = () => {
  editForm.value.full_name = user.value.full_name
  showEditModal.value = true
}

const saveProfile = async () => {
  saving.value = true
  try {
    await authService.updateProfile(editForm.value.full_name)
    user.value.full_name = editForm.value.full_name
    showEditModal.value = false
    toast.success('Profile updated successfully')
    await loadProfile()
  } catch (error) {
    toast.error('Failed to update profile')
  } finally {
    saving.value = false
  }
}

const changePassword = () => {
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  }
  showPasswordModal.value = true
}

const updatePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    toast.error('Passwords do not match')
    return
  }
  
  if (passwordForm.value.new_password.length < 8) {
    toast.error('Password must be at least 8 characters')
    return
  }
  
  saving.value = true
  try {
    await authService.changePassword(
      passwordForm.value.current_password,
      passwordForm.value.new_password
    )
    showPasswordModal.value = false
    toast.success('Password updated successfully')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to update password')
  } finally {
    saving.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-KE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
/* Same styles as Partner Profile component */
.tour-manager-profile {
  padding: 24px;
}

.profile-header {
  margin-bottom: 24px;
}

.profile-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.profile-header h1 i {
  color: #2563eb;
  margin-right: 8px;
}

.profile-header p {
  color: #64748b;
  margin: 0;
}

.loading-state {
  text-align: center;
  padding: 40px;
}

.spinner {
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
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.user-info-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 20px;
}

.user-avatar-large {
  font-size: 64px;
  color: #94a3b8;
}

.user-details h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  color: #1a1a2e;
}

.user-email {
  margin: 0 0 8px 0;
  color: #64748b;
}

.user-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.role-badge {
  display: inline-block;
  padding: 2px 12px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.tour-manager {
  background: #d1fae5;
  color: #065f46;
}

.role-badge.tour-assistant {
  background: #e0e7ff;
  color: #3730a3;
}

.status-badge.active {
  color: #16a34a;
}

.status-badge i {
  margin-right: 4px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.info-item label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.info-item p {
  margin: 0;
  font-size: 16px;
  color: #1a1a2e;
}

.profile-actions {
  display: flex;
  gap: 12px;
  padding-top: 20px;
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
  border: none;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-outline {
  background: transparent;
  color: #1a1a2e;
  border: 2px solid #e2e8f0;
}

.btn-outline:hover {
  background: #f8fafc;
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
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #94a3b8;
  cursor: pointer;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #1a1a2e;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .user-info-section {
    flex-direction: column;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-actions {
    flex-direction: column;
  }
  
  .profile-actions .btn {
    justify-content: center;
  }
}
</style>