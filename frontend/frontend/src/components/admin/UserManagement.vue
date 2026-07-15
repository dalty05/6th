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

    <!-- Search and Filter -->
    <div class="search-section">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input type="text" v-model="searchQuery" placeholder="Search users by name or email...">
      </div>
      <div class="filter-options">
        <select v-model="roleFilter" class="filter-select">
          <option value="">All Roles</option>
          <option v-for="role in roles" :key="role.id" :value="role.name">
            {{ role.name }}
          </option>
        </select>
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="pending">Pending</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading users...</p>
    </div>

    <!-- Users Table -->
    <div v-else class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>User</th>
            <th>Role</th>
            <th>Status</th>
            <th>Referral Stats</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id">
            <td class="user-cell">
              <div class="user-avatar">
                <i class="fas fa-user-circle"></i>
              </div>
              <div class="user-details">
                <div class="user-name">{{ user.full_name }}</div>
                <div class="user-email">{{ user.email }}</div>
              </div>
            </td>
            <td>
              <span :class="['role-badge', getRoleClass(user.role)]">
                {{ getRoleLabel(user.role) }}
              </span>
            </td>
            <td>
              <div class="status-group">
                <span :class="['status', user.is_active ? 'active' : 'inactive']">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span v-if="!user.is_approved" class="status pending">
                  Pending
                </span>
              </div>
            </td>
            <td>
              <div class="referral-stats">
                <span><i class="fas fa-mouse-pointer"></i> {{ user.total_clicks || 0 }}</span>
                <span><i class="fas fa-chart-line"></i> {{ user.total_conversions || 0 }}</span>
                <span v-if="user.referral_code" class="ref-code">
                  <i class="fas fa-link"></i> {{ user.referral_code }}
                </span>
              </div>
            </td>
            <td>
              <div class="date-info">
                <div>{{ formatDate(user.created_at) }}</div>
                <div v-if="user.last_login" class="last-login">
                  <i class="fas fa-clock"></i> {{ formatDate(user.last_login) }}
                </div>
              </div>
            </td>
            <td>
              <div class="action-buttons">
                <!-- Edit -->
                <button @click="editUser(user)" class="action-btn edit" title="Edit">
                  <i class="fas fa-edit"></i>
                </button>
                
                <!-- Approve -->
                <button v-if="!user.is_approved" @click="approveUser(user.id)" class="action-btn approve" title="Approve">
                  <i class="fas fa-check-circle"></i>
                </button>
                
                <!-- Suspend -->
                <button v-if="user.is_active && user.id !== currentUserId" @click="suspendUser(user)" class="action-btn suspend" title="Suspend">
                  <i class="fas fa-ban"></i>
                </button>
                
                <!-- Activate -->
                <button v-if="!user.is_active && user.id !== currentUserId" @click="activateUser(user.id)" class="action-btn activate" title="Activate">
                  <i class="fas fa-play-circle"></i>
                </button>
                
                <!-- Reset Password -->
                <button @click="openResetModal(user)" class="action-btn reset" title="Reset Password">
                  <i class="fas fa-key"></i>
                </button>
                
                <!-- Delete -->
                <button v-if="user.id !== currentUserId" @click="openDeleteModal(user)" class="action-btn delete" title="Delete">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="6" class="no-results">
              <i class="fas fa-users-slash"></i>
              <p>No users found matching your search</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="filteredUsers.length > 0">
      <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
        <i class="fas fa-chevron-left"></i> Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <span class="items-info">{{ filteredUsers.length }} total users</span>
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
            <select v-model="form.role_id" required>
              <option :value="null" disabled>Select role</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.name }}
              </option>
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

    <!-- Reset Password Modal -->
    <div class="modal-overlay" v-if="showResetModal" @click.self="closeResetModal">
      <div class="modal-container modal-sm">
        <div class="modal-header">
          <h2>Reset Password</h2>
          <button class="close-btn" @click="closeResetModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="reset-info">
            <i class="fas fa-exclamation-triangle"></i>
            <p>You are about to reset the password for:</p>
            <div class="user-info-display">
              <strong>{{ resetUserData?.full_name }}</strong>
              <span>{{ resetUserData?.email }}</span>
            </div>
          </div>
          
          <div class="password-display" v-if="newPassword">
            <label>New Password:</label>
            <div class="password-result">
              <code>{{ newPassword }}</code>
              <button @click="copyPassword" class="copy-btn" title="Copy password">
                <i class="fas fa-copy"></i>
              </button>
            </div>
            <p class="warning">Copy this password now. It will not be shown again.</p>
          </div>

          <div class="form-actions" :class="{ 'justify-center': !!newPassword }">
            <template v-if="!newPassword">
              <button @click="closeResetModal" class="btn-cancel">Cancel</button>
              <button @click="confirmResetPassword" class="btn-warning" :disabled="resetting">
                <i v-if="resetting" class="fas fa-spinner fa-spin"></i>
                {{ resetting ? 'Resetting...' : 'Reset Password' }}
              </button>
            </template>
            <template v-else>
              <button @click="closeResetModal" class="btn-submit">Done</button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Suspend Modal -->
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
        <div class="modal-header" style="background: linear-gradient(135deg, #dc2626, #b91c1c);">
          <h2>⚠️ Permanently Delete User</h2>
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
            <p><strong>The following data will be permanently deleted:</strong></p>
            <ul>
              <li><i class="fas fa-link"></i> All referral links and click data</li>
              <li><i class="fas fa-lock"></i> All custom permissions</li>
              <li><i class="fas fa-history"></i> All activity logs</li>
              <li><i class="fas fa-key"></i> Login history and OTP records</li>
              <li><i class="fas fa-calendar-check"></i> Tour bookings and payments</li>
              <li><i class="fas fa-newspaper"></i> Blog posts (author will be removed)</li>
            </ul>
          </div>
          
          <div class="confirm-input">
            <label>Type <strong>"DELETE"</strong> to confirm:</label>
            <input 
              type="text" 
              v-model="deleteConfirmText" 
              placeholder="DELETE" 
              class="delete-confirm-input"
              @keyup.enter="confirmDelete"
            >
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

// ========== STATE ==========
const users = ref([])
const roles = ref([])
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Modal states
const showModal = ref(false)
const editingUser = ref(null)
const newUserPassword = ref('')

// Reset Password
const showResetModal = ref(false)
const resetUserData = ref(null)
const newPassword = ref('')
const resetting = ref(false)

// Suspend
const showSuspendModal = ref(false)
const suspendUserData = ref(null)
const suspendReason = ref('')

// Delete
const showDeleteModal = ref(false)
const deleteUserData = ref(null)
const deleteConfirmText = ref('')
const deleting = ref(false)

const currentUser = authService.getUser()
const currentUserId = computed(() => currentUser?.id)

const form = ref({
  full_name: '',
  email: '',
  role_id: null,
  role: 'partner',
  is_active: true,
  is_approved: true
})

// ========== COMPUTED ==========
const activeUsers = computed(() => users.value.filter(u => u.is_active).length)
const pendingUsers = computed(() => users.value.filter(u => !u.is_approved).length)
const adminCount = computed(() => users.value.filter(u => u.role === 'admin' || u.role === 'super_admin').length)

const filteredUsers = computed(() => {
  let result = users.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(u => 
      u.full_name.toLowerCase().includes(query) || 
      u.email.toLowerCase().includes(query)
    )
  }
  
  if (roleFilter.value) {
    result = result.filter(u => u.role === roleFilter.value)
  }
  
  if (statusFilter.value === 'active') {
    result = result.filter(u => u.is_active && u.is_approved)
  } else if (statusFilter.value === 'inactive') {
    result = result.filter(u => !u.is_active)
  } else if (statusFilter.value === 'pending') {
    result = result.filter(u => !u.is_approved)
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredUsers.value.slice(start, start + itemsPerPage)
})

// ========== METHODS ==========
const loadRoles = async () => {
  try {
    const response = await api.get('/admin/roles')
    roles.value = response.data.filter(r => r.is_active)
  } catch (error) {
    toast.error('Failed to load roles')
  }
}

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error) {
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

// ========== CREATE/EDIT USER ==========
const openCreateModal = () => {
  editingUser.value = null
  newUserPassword.value = ''
  form.value = {
    full_name: '',
    email: '',
    role_id: null,
    role: 'partner',
    is_active: true,
    is_approved: true
  }
  showModal.value = true
}

const editUser = (user) => {
  editingUser.value = user
  newUserPassword.value = ''
  const selectedRole = roles.value.find(r => r.id === user.role_id) || roles.value.find(r => r.name === user.role)
  form.value = {
    full_name: user.full_name,
    email: user.email,
    role_id: selectedRole ? selectedRole.id : null,
    role: selectedRole ? selectedRole.name : user.role,
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
      newUserPassword.value = response.data.temporary_password || response.data.user?.temporary_password
      toast.success('User created successfully')
    }
    closeModal()
    await loadUsers()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save user')
  }
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
  newUserPassword.value = ''
}

// ========== APPROVE ==========
const approveUser = async (userId) => {
  try {
    await api.post(`/admin/users/${userId}/approve`)
    toast.success('User approved')
    await loadUsers()
  } catch (error) {
    toast.error('Failed to approve user')
  }
}

// ========== SUSPEND ==========
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

// ========== ACTIVATE ==========
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

// ========== RESET PASSWORD ==========
const openResetModal = (user) => {
  resetUserData.value = user
  newPassword.value = ''
  resetting.value = false
  showResetModal.value = true
}

const closeResetModal = () => {
  showResetModal.value = false
  resetUserData.value = null
  newPassword.value = ''
  resetting.value = false
}

const confirmResetPassword = async () => {
  if (!resetUserData.value) return
  
  resetting.value = true
  try {
    const response = await api.post(`/admin/users/${resetUserData.value.id}/reset-password`)
    newPassword.value = response.data.new_password
    toast.success('Password reset successfully')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to reset password')
    resetting.value = false
  }
}

const copyPassword = () => {
  if (newPassword.value) {
    navigator.clipboard.writeText(newPassword.value).then(() => {
      toast.success('Password copied to clipboard')
    }).catch(() => {
      const textArea = document.createElement('textarea')
      textArea.value = newPassword.value
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      toast.success('Password copied to clipboard')
    })
  }
}

// ========== DELETE - WITH CASCADE ==========
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
    // ✅ This will trigger the cascade delete on the backend
    await api.delete(`/admin/users/${deleteUserData.value.id}`)
    toast.success(`User ${deleteUserData.value.email} has been permanently deleted with all related data`)
    closeDeleteModal()
    await loadUsers()
  } catch (error) {
    console.error('Delete error:', error)
    const errorMsg = error.response?.data?.error || 'Failed to delete user. Check console for details.'
    toast.error(errorMsg)
  } finally {
    deleting.value = false
  }
}

// ========== HELPERS ==========
const getRoleLabel = (role) => {
  const roleItem = roles.value.find(r => r.name === role)
  if (roleItem) {
    return roleItem.name
  }
  const roleMap = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    tour_manager: 'Tour Manager',
    tour_assistant: 'Tour Assistant',
    partner: 'Partner'
  }
  return roleMap[role] || role || 'Unknown'
}

const getRoleClass = (role) => {
  const classes = {
    super_admin: 'role-super',
    admin: 'role-admin',
    tour_manager: 'role-tour-manager',
    tour_assistant: 'role-tour-assistant',
    partner: 'role-partner'
  }
  return classes[role] || ''
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  await loadRoles()
  await loadUsers()
})
</script>



<style scoped>
.user-management {
  padding: 0;
}

/* ========== HEADER ========== */
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
  transition: all 0.2s;
}

.btn-create:hover {
  background: #1a2d6e;
  transform: translateY(-1px);
}

/* ========== STATS ========== */
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
.stat-icon.purple { background: #ede9fe; color: #5b21b6; }

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

/* ========== SEARCH ========== */
.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  position: relative;
  min-width: 200px;
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

.filter-options {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.6rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
  background: white;
  cursor: pointer;
}

/* ========== TABLE ========== */
.table-container {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table thead {
  background: #f8fafc;
}

.users-table th {
  text-align: left;
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e5e7eb;
}

.users-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.users-table tbody tr:hover {
  background: #f8fafc;
}

/* ========== USER CELL ========== */
.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar i {
  font-size: 2rem;
  color: #9ca3af;
}

.user-details .user-name {
  font-weight: 600;
  color: #1e3a8a;
}

.user-details .user-email {
  font-size: 0.8rem;
  color: #6b7280;
}

/* ========== ROLE BADGE - UPDATED ========== */
.role-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.role-super { background: #1e3a8a; color: white; }
.role-admin { background: #f59e0b; color: white; }
.role-tour-manager { background: #8b5cf6; color: white; }
.role-tour-assistant { background: #06b6d4; color: white; }
.role-partner { background: #10b981; color: white; }

/* ========== STATUS ========== */
.status-group {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.status {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 500;
}

.status.active { background: #d1fae5; color: #065f46; }
.status.inactive { background: #fee2e2; color: #991b1b; }
.status.pending { background: #fef3c7; color: #92400e; }

/* ========== REFERRAL STATS ========== */
.referral-stats {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #4b5563;
  flex-wrap: wrap;
}

.referral-stats i {
  margin-right: 0.25rem;
  color: #9ca3af;
}

.referral-stats .ref-code {
  font-size: 0.7rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

/* ========== DATE INFO ========== */
.date-info {
  font-size: 0.8rem;
  color: #4b5563;
}

.last-login {
  font-size: 0.7rem;
  color: #9ca3af;
}

.last-login i {
  margin-right: 0.25rem;
}

/* ========== ACTION BUTTONS ========== */
.action-buttons {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: #f1f5f9;
  transform: scale(1.1);
}

.action-btn.edit { color: #3b82f6; }
.action-btn.approve { color: #10b981; }
.action-btn.suspend { color: #f59e0b; }
.action-btn.activate { color: #10b981; }
.action-btn.reset { color: #8b5cf6; }
.action-btn.delete { color: #ef4444; }

/* ========== LOADING ========== */
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

/* ========== NO RESULTS ========== */
.no-results {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.no-results i {
  font-size: 2.5rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

/* ========== PAGINATION ========== */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.page-btn {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #1e3a8a;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.85rem;
  color: #4b5563;
}

.items-info {
  font-size: 0.8rem;
  color: #9ca3af;
}

/* ========== MODALS ========== */
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
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0,0,0,0.25);
  animation: modalPop 0.25s ease;
}

.modal-sm { max-width: 500px; }
.modal-md { max-width: 650px; }
.modal-lg { max-width: 800px; }

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #1e3a8a, #2563eb);
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
  background: rgba(255,255,255,0.15);
  color: white;
  cursor: pointer;
  font-size: 1.3rem;
  transition: 0.2s;
}

.close-btn:hover {
  background: rgba(255,255,255,0.25);
}

/* ========== FORM ========== */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.45rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 0.8rem 0.9rem;
  transition: 0.2s;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37,99,235,0.12);
}

.checkbox-group {
  display: flex;
  gap: 1.5rem;
  margin: 1rem 0;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #374151;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-submit {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-submit:hover {
  background: #1d4ed8;
}

.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-warning {
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}

.btn-warning:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.justify-center {
  justify-content: center !important;
}

.password-info {
  padding: 1rem 1.5rem 1.5rem;
}

.password-info hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 0 0 1rem;
}

.password-info h4 {
  color: #10b981;
  margin: 0 0 0.5rem;
}

.password-info code {
  background: #f3f4f6;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a8a;
}

.password-info .warning {
  font-size: 0.8rem;
  color: #f59e0b;
  margin: 0.5rem 0 0;
}

/* ========== RESET PASSWORD MODAL ========== */
.reset-info {
  text-align: center;
  padding: 1rem;
  background: #fef3c7;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.reset-info i {
  font-size: 2rem;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

.reset-info p {
  margin: 0.5rem 0;
  color: #92400e;
}

.user-info-display {
  background: white;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.5rem;
}

.user-info-display strong {
  display: block;
  color: #1e3a8a;
}

.user-info-display span {
  font-size: 0.85rem;
  color: #6b7280;
}

.password-display {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.password-display label {
  font-weight: 600;
  color: #065f46;
  display: block;
  margin-bottom: 0.5rem;
}

.password-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
}

.password-result code {
  flex: 1;
  font-size: 1rem;
  color: #1e3a8a;
  font-weight: 600;
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
  background: #f3f4f6;
  color: #1e3a8a;
}

.password-display .warning {
  font-size: 0.8rem;
  color: #92400e;
  margin: 0.5rem 0 0;
}

/* ========== DELETE MODAL ========== */
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

/* ========== ANIMATIONS ========== */
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

/* ========== RESPONSIVE ========== */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .search-section {
    flex-direction: column;
  }
  
  .filter-options {
    width: 100%;
  }
  
  .filter-select {
    flex: 1;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .users-table {
    font-size: 0.8rem;
    min-width: 700px;
  }
  
  .users-table th,
  .users-table td {
    padding: 0.5rem;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
}
</style>