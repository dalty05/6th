<template>
  <div class="user-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1>User Management</h1>
        <p>Manage system users and their access levels</p>
      </div>
      <button @click="openCreateModal" class="btn-create">
        <i class="fas fa-plus"></i> Add User
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <h3>{{ users.length }}</h3>
          <p>Total Users</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
          <h3>{{ activeUsers }}</h3>
          <p>Active</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-user-clock"></i></div>
        <div class="stat-info">
          <h3>{{ pendingUsers }}</h3>
          <p>Pending Approval</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-user-tag"></i></div>
        <div class="stat-info">
          <h3>{{ adminCount }}</h3>
          <p>Admins</p>
        </div>
      </div>
    </div>

    <!-- Search -->
    <div class="search-box">
      <i class="fas fa-search"></i>
      <input type="text" v-model="searchQuery" placeholder="Search users by name or email...">
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading users...</p>
    </div>

    <!-- Users Grid -->
    <div v-else class="users-grid">
      <div v-for="user in paginatedUsers" :key="user.id" class="user-card">
        <div class="user-header">
          <div class="user-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="user-info">
            <h3>{{ user.full_name }}</h3>
            <span :class="['role-badge', getRoleClass(user.role)]">
              {{ getRoleLabel(user.role) }}
            </span>
          </div>
          <div class="user-status">
            <span :class="['status', user.is_active ? 'active' : 'inactive']">
              {{ user.is_active ? 'Active' : 'Inactive' }}
            </span>
            <span v-if="!user.is_approved" class="status pending">
              Pending
            </span>
          </div>
        </div>

        <div class="user-body">
          <p><i class="fas fa-envelope"></i> {{ user.email }}</p>
          <p v-if="user.referral_code"><i class="fas fa-link"></i> Code: {{ user.referral_code }}</p>
          <p><i class="fas fa-calendar"></i> Joined: {{ formatDate(user.created_at) }}</p>
          <p v-if="user.last_login"><i class="fas fa-clock"></i> Last login: {{ formatDate(user.last_login) }}</p>
        </div>

        <div class="user-footer">
          <div class="referral-stats">
            <span><i class="fas fa-mouse-pointer"></i> {{ user.total_clicks || 0 }} clicks</span>
            <span><i class="fas fa-chart-line"></i> {{ user.total_conversions || 0 }} conversions</span>
          </div>

        <div class="action-buttons">
  <!-- Edit button -->
  <button @click="editUser(user)" class="action-btn edit" title="Edit">
    <i class="fas fa-edit"></i>
  </button>
  
  <!-- Approve button -->
  <button v-if="!user.is_approved" @click="approveUser(user.id)" class="action-btn approve" title="Approve">
    <i class="fas fa-check-circle"></i>
  </button>
  
  <!-- Suspend button -->
  <button v-if="user.is_active && user.id !== currentUserId" @click="suspendUser(user)" class="action-btn suspend" title="Suspend">
    <i class="fas fa-ban"></i>
  </button>
  
  <!-- Activate button -->
  <button v-if="!user.is_active && user.id !== currentUserId" @click="activateUser(user.id)" class="action-btn activate" title="Activate">
    <i class="fas fa-play-circle"></i>
  </button>
  
  <!-- Reset Password button - opens modal -->
  <button @click="openResetModal(user)" class="action-btn reset" title="Reset Password">
    <i class="fas fa-key"></i>
  </button>
  
  <!-- Delete button -->
  <button v-if="user.id !== currentUserId" @click="openDeleteModal(user)" class="action-btn delete" title="Delete">
    <i class="fas fa-trash-alt"></i>
  </button>
</div>
          


        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="!loading && filteredUsers.length === 0" class="no-results">
      <i class="fas fa-users-slash"></i>
      <h3>No Users Found</h3>
      <p>Try adjusting your search</p>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="filteredUsers.length > 0">
      <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
        <i class="fas fa-chevron-left"></i> Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
        Next <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-container modal-lg">
        <div class="modal-header">
          <h2>{{ editingUser ? 'Edit User' : 'Add New User' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <form @submit.prevent="saveUser" class="user-form">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" v-model="form.full_name" required>
          </div>
          <div class="form-group">
            <label>Email *</label>
            <input type="email" v-model="form.email" required :disabled="!!editingUser">
          </div>
          <div class="form-group">
            <label>Role *</label>
            <select v-model="form.role" required>
              <option value="super_admin">Super Admin</option>
              <option value="admin">Admin</option>
              <option value="partner">Partner</option>
            </select>
          </div>
          <div class="checkbox-group">
            <label class="checkbox">
              <input type="checkbox" v-model="form.is_active"> Active
            </label>
            <label class="checkbox">
              <input type="checkbox" v-model="form.is_approved"> Approved
            </label>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">{{ editingUser ? 'Update' : 'Create' }}</button>
          </div>
        </form>
        <div v-if="newUserPassword" class="password-info">
          <hr>
          <h4>User Created Successfully!</h4>
          <p><strong>Temporary Password:</strong> <code>{{ newUserPassword }}</code></p>
          <p class="warning">Please share this password with the user. It will not be shown again.</p>
        </div>
      </div>
    </div>

    <!-- suspend modal -->
    <div class="modal-overlay" v-if="showSuspendModal" @click.self="closeSuspendModal">
    <div class="modal-container modal-sm">
      <div class="modal-header">
        <h2>Suspend User</h2>
        <button class="close-btn" @click="closeSuspendModal">&times;</button>
      </div>
      <div class="modal-body">
        <p>You are about to suspend <strong>{{ suspendUserData?.full_name }}</strong></p>
        <div class="form-group">
          <label>Reason for suspension *</label>
          <textarea v-model="suspendReason" rows="4" placeholder="Please provide a reason for suspending this user..."></textarea>
        </div>
        <div class="form-actions">
          <button @click="closeSuspendModal" class="btn-cancel">Cancel</button>
          <button @click="confirmSuspend" class="btn-danger" :disabled="!suspendReason.trim()">
            Confirm Suspension
          </button>
        </div>
      </div>
    </div>
  </div>
    
    <!-- Delete Confirmation Modal -->  
   <div class="modal-overlay" v-if="showDeleteModal" @click.self="closeDeleteModal">
    <div class="modal-container modal-sm">
      <div class="modal-header">
        <h2 class="delete-title">⚠️ Permanently Delete User</h2>
        <button class="close-btn" @click="closeDeleteModal">&times;</button>
      </div>
      <div class="modal-body">
        <div class="delete-warning">
          <i class="fas fa-exclamation-triangle"></i>
          <p>This action <strong>cannot be undone</strong>. This will permanently delete:</p>
        </div>
        
        <div class="delete-user-info">
          <div class="user-detail">
            <span class="label">Name:</span>
            <span class="value">{{ deleteUserData?.full_name }}</span>
          </div>
          <div class="user-detail">
            <span class="label">Email:</span>
            <span class="value">{{ deleteUserData?.email }}</span>
          </div>
          <div class="user-detail">
            <span class="label">Role:</span>
            <span class="value">{{ getRoleLabel(deleteUserData?.role) }}</span>
          </div>
        </div>
        
        <div class="delete-items-list">
          <p><strong>The following data will be deleted:</strong></p>
          <ul>
            <li><i class="fas fa-link"></i> All referral links and click data</li>
            <li><i class="fas fa-lock"></i> All custom permissions</li>
            <li><i class="fas fa-history"></i> All activity logs</li>
            <li><i class="fas fa-key"></i> Login history and OTP records</li>
          </ul>
        </div>
        
        <div class="confirm-input">
          <label>Type <strong>"DELETE"</strong> to confirm:</label>
          <input type="text" v-model="deleteConfirmText" placeholder="DELETE" class="delete-confirm-input">
        </div>
        
        <div class="form-actions">
          <button @click="closeDeleteModal" class="btn-cancel">Cancel</button>
          <button 
            @click="confirmDelete" 
            class="btn-danger" 
            :disabled="deleteConfirmText !== 'DELETE' || deleting"
          >
            <i v-if="deleting" class="fas fa-spinner fa-spin"></i>
            {{ deleting ? 'Deleting...' : 'Permanently Delete' }}
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
import api from '@/services/api'
import authService from '@/services/auth'



const showDeleteModal = ref(false)
const deleteUserData = ref(null)
const deleteConfirmText = ref('')
const deleting = ref(false)

const users = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingUser = ref(null)
const newUserPassword = ref('')
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 12



const showSuspendModal = ref(false)
const suspendUserData = ref(null)
const suspendReason = ref('')



const currentUser = authService.getUser()
const currentUserId = computed(() => currentUser?.id)

const form = ref({
  full_name: '',
  email: '',
  role: 'partner',
  is_active: true,
  is_approved: true
})

// Computed
const activeUsers = computed(() => users.value.filter(u => u.is_active).length)
const pendingUsers = computed(() => users.value.filter(u => !u.is_approved).length)
const adminCount = computed(() => users.value.filter(u => u.role === 'admin' || u.role === 'super_admin').length)

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(u => 
    u.full_name.toLowerCase().includes(query) || 
    u.email.toLowerCase().includes(query)
  )
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredUsers.value.slice(start, start + itemsPerPage)
})

// Methods
const loadUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error) {
    console.error('Error loading users:', error)
    toast.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const openCreateModal = () => {
  editingUser.value = null
  newUserPassword.value = ''
  form.value = {
    full_name: '',
    email: '',
    role: 'partner',
    is_active: true,
    is_approved: true
  }
  showModal.value = true
}

const editUser = (user) => {
  editingUser.value = user
  newUserPassword.value = ''
  form.value = {
    full_name: user.full_name,
    email: user.email,
    role: user.role,
    is_active: user.is_active,
    is_approved: user.is_approved
  }
  showModal.value = true
}

const saveUser = async () => {
  try {
    if (editingUser.value) {
      await api.put(`/admin/users/${editingUser.value.id}`, form.value)
      toast.success('User updated successfully')
    } else {
      const response = await api.post('/admin/users', form.value)
      newUserPassword.value = response.data.user?.temporary_password
      toast.success('User created successfully')
    }
    closeModal()
    await loadUsers()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save user')
  }
}

const approveUser = async (userId) => {
  try {
    await api.post(`/admin/users/${userId}/approve`)
    toast.success('User approved')
    await loadUsers()
  } catch (error) {
    toast.error('Failed to approve user')
  }
}

const suspendUser = (user) => {
  suspendUserData.value = user
  suspendReason.value = ''
  showSuspendModal.value = true
}

const confirmSuspend = async () => {
  if (!suspendReason.value.trim()) {
    toast.error('Please provide a reason for suspension')
    return
  }
  
  try {
    await api.post(`/admin/users/${suspendUserData.value.id}/suspend`, {
      reason: suspendReason.value
    })
    toast.success('User suspended successfully')
    closeSuspendModal()
    await loadUsers()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to suspend user')
  }
}

const closeSuspendModal = () => {
  showSuspendModal.value = false
  suspendUserData.value = null
  suspendReason.value = ''
}


const activateUser = async (userId) => {
  if (confirm('Activate this user? They will be able to log in again.')) {
    try {
      await api.post(`/admin/users/${userId}/activate`)
      toast.success('User activated successfully')
      await loadUsers()
    } catch (error) {
      toast.error('Failed to activate user')
    }
  }
}

const resetPassword = async (userId) => {
  if (confirm('Reset password for this user?')) {
    try {
      const response = await api.post(`/admin/users/${userId}/reset-password`)
      const newPassword = response.data.new_password
      alert(`New password: ${newPassword}\n\nPlease share this with the user.`)
      toast.success('Password reset successfully')
    } catch (error) {
      toast.error('Failed to reset password')
    }
  }
}

const openDeleteModal = (user) => {
  deleteUserData.value = user
  deleteConfirmText.value = ''
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  deleteUserData.value = null
  deleteConfirmText.value = ''
  deleting.value = false
}

const confirmDelete = async () => {
  if (deleteConfirmText.value !== 'DELETE') {
    toast.error('Please type DELETE to confirm')
    return
  }
  
  deleting.value = true
  try {
    await api.delete(`/admin/users/${deleteUserData.value.id}`)
    toast.success(`User ${deleteUserData.value.email} has been permanently deleted`)
    closeDeleteModal()
    await loadUsers()
  } catch (error) {
    console.error('Error deleting user:', error)
    toast.error(error.response?.data?.error || 'Failed to delete user')
  } finally {
    deleting.value = false
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
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
  newUserPassword.value = ''
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
/* delete functionality styles */

.delete-title {
  color: #dc2626 !important;
}

.delete-warning {
  text-align: center;
  padding: 1rem;
  background: #fef2f2;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.delete-warning i {
  font-size: 2rem;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.delete-warning p {
  margin: 0;
  color: #991b1b;
}

.delete-user-info {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.user-detail {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.user-detail:last-child {
  border-bottom: none;
}

.user-detail .label {
  font-weight: 600;
  color: #374151;
}

.user-detail .value {
  color: #1e3a8a;
  font-weight: 500;
}

.delete-items-list {
  background: #fef3c7;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.delete-items-list p {
  margin: 0 0 0.5rem;
  color: #92400e;
}

.delete-items-list ul {
  margin: 0;
  padding-left: 1.5rem;
}

.delete-items-list li {
  margin: 0.25rem 0;
  color: #78350f;
  font-size: 0.85rem;
}

.delete-items-list li i {
  margin-right: 0.5rem;
  width: 16px;
}

.confirm-input {
  margin-bottom: 1rem;
}

.confirm-input label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #374151;
}

.delete-confirm-input {
  width: 100%;
  padding: 0.6rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  text-align: center;
  font-weight: bold;
  letter-spacing: 2px;
}

.delete-confirm-input:focus {
  outline: none;
  border-color: #dc2626;
}

.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}


/* buttons */
.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-danger:hover {
  background: #b91c1c;
}




.user-management {
  padding: 0;
}

/* Header */
.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e3a8a;
  margin: 0 0 0.25rem;
}

.header-left p {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0;
}

.btn-create {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue { background: #e0e7ff; color: #1e3a8a; }
.stat-icon.green { background: #d1fae5; color: #065f46; }
.stat-icon.orange { background: #fed7aa; color: #9a3412; }
.stat-icon.purple { background: #e0e7ff; color: #1e3a8a; }

.stat-icon i { font-size: 1.25rem; }

.stat-info h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  font-size: 0.75rem;
  margin: 0;
  color: #6b7280;
}

/* Search */
.search-box {
  position: relative;
  margin-bottom: 1.5rem;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-box input {
  width: 100%;
  padding: 0.6rem 0.75rem 0.6rem 2.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
}

/* Loading */
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

/* Users Grid */
.users-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.user-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: all 0.2s;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.user-avatar i {
  font-size: 2.5rem;
  color: #9ca3af;
}

.user-info {
  flex: 1;
}

.user-info h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a8a;
  margin: 0 0 0.25rem;
}

.role-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 600;
}

.role-super { background: #1e3a8a; color: white; }
.role-admin { background: #f59e0b; color: white; }
.role-partner { background: #10b981; color: white; }

.user-status {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-end;
}

.status {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.65rem;
}

.status.active { background: #d1fae5; color: #065f46; }
.status.inactive { background: #fee2e2; color: #991b1b; }
.status.pending { background: #fef3c7; color: #92400e; }

.user-body {
  padding: 1rem;
}

.user-body p {
  margin: 0.5rem 0;
  font-size: 0.8rem;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-body i {
  width: 20px;
  color: #9ca3af;
}

.user-footer {
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.referral-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-size: 0.7rem;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.action-btn.edit { color: #3b82f6; }
.action-btn.approve { color: #10b981; }
.action-btn.suspend { color: #f59e0b; }
.action-btn.activate { color: #10b981; }
.action-btn.reset { color: #8b5cf6; }
.action-btn.delete { color: #ef4444; }

.action-btn:hover {
  background: #f1f5f9;
}

/* No Results */
.no-results {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
}

.no-results i {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.page-btn {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
/* =========================
   UNIVERSAL MODAL SYSTEM
========================= */

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
  animation: fadeIn .2s ease;
}

.modal-container {
  width: 100%;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 25px 50px rgba(0,0,0,.25),
    0 10px 25px rgba(0,0,0,.1);
  animation: modalPop .25s ease;
}

.modal-sm {
  max-width: 500px;
}

.modal-md {
  max-width: 650px;
}

.modal-lg {
  max-width: 800px;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(
    135deg,
    #1e3a8a,
    #2563eb
  );
  color: white;
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.15rem;
  font-weight: 600;
}

.modal-body,
.user-form {
  padding: 1.5rem;
}

.close-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,.15);
  color: white;
  cursor: pointer;
  font-size: 1.3rem;
  transition: .2s;
}

.close-btn:hover {
  background: rgba(255,255,255,.25);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: .85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: .45rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: .8rem .9rem;
  transition: .2s;
  font-size: .9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37,99,235,.12);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: .75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 10px;
  padding: .75rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 10px;
  padding: .75rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:hover {
  background: #1d4ed8;
}

.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 10px;
  padding: .75rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-danger:disabled {
  opacity: .6;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modalPop {
  from {
    opacity: 0;
    transform: translateY(15px) scale(.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .users-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .users-grid {
    grid-template-columns: 1fr;
  }
  
  .user-header {
    flex-wrap: wrap;
  }
  
  .action-buttons {
    justify-content: center;
  }
}
</style>