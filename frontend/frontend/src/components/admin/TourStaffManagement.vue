<template>
  <div class="tour-staff-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1><i class="fas fa-users-cog"></i> Tour Staff Management</h1>
        <p>Manage tour managers and assistants who handle factory tours</p>
      </div>
      <button @click="openCreateModal" class="btn-create">
        <i class="fas fa-plus"></i> Add Tour Staff
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <h3>{{ staffList.length }}</h3>
          <p>Total Staff</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
          <h3>{{ activeStaff }}</h3>
          <p>Active</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-user-tie"></i></div>
        <div class="stat-info">
          <h3>{{ managerCount }}</h3>
          <p>Managers</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-user"></i></div>
        <div class="stat-info">
          <h3>{{ assistantCount }}</h3>
          <p>Assistants</p>
        </div>
      </div>
    </div>

    <!-- Debug/Error Banner -->
    <div v-if="errorMessage" class="error-banner">
      <i class="fas fa-exclamation-triangle"></i>
      <span>{{ errorMessage }}</span>
      <button @click="errorMessage = ''" class="error-close">&times;</button>
    </div>

    <div v-if="debugInfo" class="debug-banner">
      <i class="fas fa-info-circle"></i>
      <span>{{ debugInfo }}</span>
      <button @click="debugInfo = ''" class="debug-close">&times;</button>
    </div>

    <!-- Search and Filter -->
    <div class="search-section">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input type="text" v-model="searchQuery" placeholder="Search staff by name or email...">
      </div>
      <div class="filter-options">
        <select v-model="roleFilter" class="filter-select">
          <option value="">All Roles</option>
          <option value="tour_manager">Tour Manager</option>
          <option value="tour_assistant">Tour Assistant</option>
        </select>
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <button @click="loadStaff" class="btn-refresh" title="Refresh">
          <i class="fas fa-sync" :class="{ 'spinning': loading }"></i>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading staff...</p>
    </div>

    <!-- Show All Users Button (if no tour staff found) -->
    <div v-else-if="allUsers.length > 0 && staffList.length === 0" class="no-staff-banner">
      <i class="fas fa-users"></i>
      <div>
        <h4>No Tour Staff Found</h4>
        <p>You have {{ allUsers.length }} users in the system. Would you like to:</p>
        <div class="no-staff-actions">
          <button @click="openCreateModal" class="btn-create small">
            <i class="fas fa-plus"></i> Add Tour Staff
          </button>
          <button @click="showAllUsers = !showAllUsers" class="btn-secondary small">
            <i class="fas fa-eye"></i> {{ showAllUsers ? 'Hide' : 'View' }} All Users
          </button>
        </div>
      </div>
    </div>

    <!-- Staff Table -->
    <div v-else class="table-container">
      <table class="staff-table">
        <thead>
          <tr>
            <th>Staff Member</th>
            <th>Role</th>
            <th>Status</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="staff in paginatedUsers" :key="staff.id">
            <td class="user-cell">
              <div class="user-avatar">
                <i class="fas fa-user-circle"></i>
              </div>
              <div class="user-details">
                <div class="user-name">{{ staff.full_name }}</div>
                <div class="user-email">{{ staff.email }}</div>
              </div>
            </td>
            <td>
              <!-- ✅ Check BOTH flags and role -->
              <span v-if="staff.is_tour_manager || staff.is_tour_assistant || staff.role === 'tour_manager' || staff.role === 'tour_assistant'" 
                    :class="['role-badge', (staff.is_tour_manager || staff.role === 'tour_manager') ? 'manager' : 'assistant']">
                <i :class="(staff.is_tour_manager || staff.role === 'tour_manager') ? 'fas fa-user-tie' : 'fas fa-user'"></i>
                {{ (staff.is_tour_manager || staff.role === 'tour_manager') ? 'Tour Manager' : 'Tour Assistant' }}
              </span>
              <span v-else class="role-badge no-role">
                <i class="fas fa-user"></i> {{ staff.role || 'Regular User' }}
              </span>
            </td>
            <td>
              <span :class="['status', staff.is_active ? 'active' : 'inactive']">
                <i :class="staff.is_active ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
                {{ staff.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <div class="date-info">
                <div>{{ formatDate(staff.created_at) }}</div>
                <div v-if="staff.last_login" class="last-login">
                  <i class="fas fa-clock"></i> {{ formatDate(staff.last_login) }}
                </div>
              </div>
            </td>
            <td>
              <div class="action-buttons">
                <!-- ✅ Promote to Tour Staff (checks BOTH flags and role) -->
                <button v-if="!staff.is_tour_manager && !staff.is_tour_assistant && staff.role !== 'tour_manager' && staff.role !== 'tour_assistant'" 
                        @click="promoteToTourStaff(staff)" 
                        class="action-btn promote" 
                        title="Promote to Tour Staff">
                  <i class="fas fa-arrow-up"></i>
                </button>
                
                <!-- Edit -->
                <button @click="editStaff(staff)" class="action-btn edit" title="Edit">
                  <i class="fas fa-edit"></i>
                </button>
                
                <!-- Toggle Status -->
                <button 
                  @click="toggleStaffStatus(staff)" 
                  class="action-btn" 
                  :class="staff.is_active ? 'suspend' : 'activate'"
                  :title="staff.is_active ? 'Deactivate' : 'Activate'"
                >
                  <i :class="staff.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
                
                <!-- Reset Password -->
                <button @click="openResetModal(staff)" class="action-btn reset" title="Reset Password">
                  <i class="fas fa-key"></i>
                </button>
                
                <!-- Delete -->
                <button @click="openDeleteModal(staff)" class="action-btn delete" title="Delete">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="paginatedUsers.length === 0">
            <td colspan="5" class="no-results">
              <i class="fas fa-users-slash"></i>
              <p>No users found matching your search</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="displayUsers.length > 0">
      <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
        <i class="fas fa-chevron-left"></i> Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <span class="items-info">{{ displayUsers.length }} total users</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
        Next <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-container modal-lg">
        <div class="modal-header">
          <h2>{{ editingStaff ? 'Edit Tour Staff' : 'Add Tour Staff' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <form @submit.prevent="saveStaff" class="staff-form">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" v-model="form.full_name" required>
          </div>
          <div class="form-group">
            <label>Email *</label>
            <input type="email" v-model="form.email" required :disabled="!!editingStaff">
          </div>
          <div class="form-group" v-if="!editingStaff">
            <label>Password *</label>
            <input type="password" v-model="form.password" required placeholder="Enter a strong password">
          </div>
          <div class="form-group">
            <label>Role *</label>
            <select v-model="form.role" required>
              <option value="tour_manager">Tour Manager</option>
              <option value="tour_assistant">Tour Assistant</option>
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
            <button type="submit" class="btn-submit">{{ editingStaff ? 'Update' : 'Create' }}</button>
          </div>
        </form>
        <div v-if="newUserPassword" class="password-info">
          <hr>
          <h4>Staff Created Successfully!</h4>
          <p><strong>Temporary Password:</strong> <code>{{ newUserPassword }}</code></p>
          <p class="warning">Please share this password with the staff member. It will not be shown again.</p>
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

    <!-- Delete Confirmation Modal -->
    <div class="modal-overlay" v-if="showDeleteModal" @click.self="closeDeleteModal">
      <div class="modal-container modal-sm">
        <div class="modal-header" style="background: linear-gradient(135deg, #dc2626, #b91c1c);">
          <h2>⚠️ Permanently Delete Staff</h2>
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
              <span class="value">{{ getRoleDisplay(deleteUserData) }}</span>
            </div>
          </div>
          
          <div class="delete-items-list">
            <p><strong>The following data will be deleted:</strong></p>
            <ul>
              <li><i class="fas fa-calendar-alt"></i> All tour bookings managed</li>
              <li><i class="fas fa-clock"></i> All activity logs</li>
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

    <!-- Promote Modal -->
    <div class="modal-overlay" v-if="showPromoteModal" @click.self="closePromoteModal">
      <div class="modal-container modal-sm">
        <div class="modal-header">
          <h2>Promote to Tour Staff</h2>
          <button class="close-btn" @click="closePromoteModal">&times;</button>
        </div>
        <div class="modal-body">
          <p>Promote <strong>{{ promoteUserData?.full_name }}</strong> to:</p>
          <div class="form-group">
            <select v-model="promoteRole" class="form-control">
              <option value="tour_manager">Tour Manager</option>
              <option value="tour_assistant">Tour Assistant</option>
            </select>
          </div>
          <div class="form-actions">
            <button @click="closePromoteModal" class="btn-cancel">Cancel</button>
            <button @click="confirmPromote" class="btn-submit">Promote</button>
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
const allUsers = ref([])
const staffList = ref([])
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const showAllUsers = ref(false)
const debugInfo = ref('')
const errorMessage = ref('')

// Modal states
const showModal = ref(false)
const editingStaff = ref(null)
const newUserPassword = ref('')

// Reset Password
const showResetModal = ref(false)
const resetUserData = ref(null)
const newPassword = ref('')
const resetting = ref(false)

// Delete
const showDeleteModal = ref(false)
const deleteUserData = ref(null)
const deleteConfirmText = ref('')
const deleting = ref(false)

// Promote
const showPromoteModal = ref(false)
const promoteUserData = ref(null)
const promoteRole = ref('tour_manager')

const currentUser = authService.getUser()

const form = ref({
  full_name: '',
  email: '',
  password: '',
  role: 'tour_manager',
  is_active: true,
  is_approved: true
})

// ========== COMPUTED ==========
const activeStaff = computed(() => staffList.value.filter(s => s.is_active).length)
const managerCount = computed(() => staffList.value.filter(s => s.is_tour_manager || s.role === 'tour_manager').length)
const assistantCount = computed(() => staffList.value.filter(s => s.is_tour_assistant || s.role === 'tour_assistant').length)

// Users to display - show staff or all users based on toggle
const displayUsers = computed(() => {
  let result = showAllUsers.value ? allUsers.value : staffList.value
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s => 
      s.full_name.toLowerCase().includes(query) || 
      s.email.toLowerCase().includes(query)
    )
  }
  
  // Role filter - check BOTH flags AND role
  if (roleFilter.value === 'tour_manager') {
    result = result.filter(s => s.is_tour_manager || s.role === 'tour_manager')
  } else if (roleFilter.value === 'tour_assistant') {
    result = result.filter(s => s.is_tour_assistant || s.role === 'tour_assistant')
  }
  
  // Status filter
  if (statusFilter.value === 'active') {
    result = result.filter(s => s.is_active)
  } else if (statusFilter.value === 'inactive') {
    result = result.filter(s => !s.is_active)
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(displayUsers.value.length / itemsPerPage))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return displayUsers.value.slice(start, start + itemsPerPage)
})

// ========== HELPERS ==========
const isTourStaff = (user) => {
  return user.is_tour_manager || 
         user.is_tour_assistant || 
         user.role === 'tour_manager' || 
         user.role === 'tour_assistant'
}

const getRoleDisplay = (user) => {
  if (!user) return 'Regular User'
  if (user.is_tour_manager || user.role === 'tour_manager') return 'Tour Manager'
  if (user.is_tour_assistant || user.role === 'tour_assistant') return 'Tour Assistant'
  return user.role || 'Regular User'
}

// ========== METHODS ==========
const loadStaff = async () => {
  loading.value = true
  errorMessage.value = ''
  debugInfo.value = 'Loading users...'
  
  try {
    const response = await api.get('/admin/users')
    allUsers.value = response.data
    
    console.log('✅ Total users loaded:', allUsers.value.length)
    
    // Debug: Show sample user fields
    if (allUsers.value.length > 0) {
      const sample = allUsers.value[0]
      console.log('🔍 Sample user fields:', Object.keys(sample))
      console.log('🔍 Sample user tour flags:', {
        is_tour_manager: sample.is_tour_manager,
        is_tour_assistant: sample.is_tour_assistant,
        role: sample.role
      })
    }
    
    // ✅ Filter users who are tour staff (check BOTH flags AND role)
    staffList.value = allUsers.value.filter(u => isTourStaff(u))
    
    console.log('✅ Tour staff found:', staffList.value.length)
    
    // Debug: Show all user roles
    const roles = allUsers.value.map(u => `${u.full_name}: role=${u.role}, is_tour_manager=${u.is_tour_manager}, is_tour_assistant=${u.is_tour_assistant}`)
    console.log('📋 All user tour status:', roles)
    
    if (staffList.value.length === 0) {
      debugInfo.value = `ℹ️ No tour staff found. Found ${allUsers.value.length} total users. Use "View All Users" to see them.`
    } else {
      debugInfo.value = `✅ Found ${staffList.value.length} tour staff members out of ${allUsers.value.length} total users`
    }
    
    setTimeout(() => {
      debugInfo.value = ''
    }, 8000)
    
  } catch (error) {
    console.error('Error loading staff:', error)
    
    if (error.response?.status === 400) {
      errorMessage.value = `Server returned 400: ${error.response?.data?.error || 'Bad request.'}`
    } else {
      toast.error('Failed to load staff list')
    }
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

// ========== PROMOTE USER ==========
const promoteToTourStaff = (user) => {
  promoteUserData.value = user
  promoteRole.value = 'tour_manager'
  showPromoteModal.value = true
}

const closePromoteModal = () => {
  showPromoteModal.value = false
  promoteUserData.value = null
}

const confirmPromote = async () => {
  if (!promoteUserData.value) return
  
  try {
    const isManager = promoteRole.value === 'tour_manager'
    
    await api.put(`/admin/users/${promoteUserData.value.id}`, {
      full_name: promoteUserData.value.full_name,
      email: promoteUserData.value.email,
      role: promoteRole.value,
      is_tour_manager: isManager,
      is_tour_assistant: !isManager,
      is_active: promoteUserData.value.is_active,
      is_approved: promoteUserData.value.is_approved
    })
    toast.success(`${promoteUserData.value.full_name} promoted to ${isManager ? 'Tour Manager' : 'Tour Assistant'}`)
    closePromoteModal()
    await loadStaff()
  } catch (error) {
    console.error('Error promoting user:', error)
    toast.error(error.response?.data?.error || 'Failed to promote user')
  }
}

// ========== CREATE/EDIT STAFF ==========
const openCreateModal = () => {
  editingStaff.value = null
  newUserPassword.value = ''
  form.value = {
    full_name: '',
    email: '',
    password: '',
    role: 'tour_manager',
    is_active: true,
    is_approved: true
  }
  showModal.value = true
}

const editStaff = (staff) => {
  editingStaff.value = staff
  newUserPassword.value = ''
  
  // Determine role from flags OR role field
  let role = 'tour_manager'
  if (staff.is_tour_assistant || staff.role === 'tour_assistant') {
    role = 'tour_assistant'
  }
  
  form.value = {
    full_name: staff.full_name,
    email: staff.email,
    password: '',
    role: role,
    is_active: staff.is_active,
    is_approved: staff.is_approved
  }
  showModal.value = true
}

const saveStaff = async () => {
  try {
    const isManager = form.value.role === 'tour_manager'
    
    if (editingStaff.value) {
      await api.put(`/admin/users/${editingStaff.value.id}`, {
        full_name: form.value.full_name,
        email: form.value.email,
        role: form.value.role,
        is_tour_manager: isManager,
        is_tour_assistant: !isManager,
        is_active: form.value.is_active,
        is_approved: form.value.is_approved
      })
      toast.success('Staff updated successfully')
    } else {
      const response = await api.post('/admin/users', {
        full_name: form.value.full_name,
        email: form.value.email,
        password: form.value.password,
        role: form.value.role,
        is_tour_manager: isManager,
        is_tour_assistant: !isManager,
        is_active: form.value.is_active,
        is_approved: form.value.is_approved
      })
      newUserPassword.value = response.data.user?.temporary_password
      toast.success('Staff created successfully')
    }
    closeModal()
    await loadStaff()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save staff')
  }
}

const closeModal = () => {
  showModal.value = false
  editingStaff.value = null
  newUserPassword.value = ''
}

// ========== TOGGLE STATUS ==========
const toggleStaffStatus = async (staff) => {
  const action = staff.is_active ? 'deactivate' : 'activate'
  if (!confirm(`Are you sure you want to ${action} ${staff.full_name}?`)) return
  
  try {
    await api.put(`/admin/users/${staff.id}`, {
      is_active: !staff.is_active
    })
    toast.success(`${staff.full_name} ${action}d successfully`)
    await loadStaff()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to update staff status')
  }
}

// ========== RESET PASSWORD ==========
const openResetModal = (staff) => {
  resetUserData.value = staff
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
    resetting.value = false
  } catch (error) {
    console.error('Error resetting password:', error)
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

// ========== DELETE ==========
const openDeleteModal = (staff) => {
  deleteUserData.value = staff
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
    toast.success(`${deleteUserData.value.full_name} has been permanently deleted`)
    closeDeleteModal()
    await loadStaff()
  } catch (error) {
    console.error('Error deleting staff:', error)
    toast.error(error.response?.data?.error || 'Failed to delete staff')
  } finally {
    deleting.value = false
  }
}

// ========== FORMAT DATE ==========
const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return 'Invalid date'
  }
}

// ========== LIFECYCLE ==========
onMounted(() => {
  loadStaff()
})
</script>

<style scoped>

.error-banner {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-left: 4px solid #dc2626;
}

.error-banner .error-close {
  background: none;
  border: none;
  color: #991b1b;
  font-size: 1.2rem;
  cursor: pointer;
  margin-left: auto;
  padding: 0 0.5rem;
}



.debug-banner .debug-close {
  background: none;
  border: none;
  color: #1e3a8a;
  font-size: 1.2rem;
  cursor: pointer;
  margin-left: auto;
  padding: 0 0.5rem;
}



.no-staff-banner i {
  font-size: 2.5rem;
  color: #f59e0b;
}

.no-staff-banner h4 {
  margin: 0 0 0.25rem;
  color: #92400e;
}

.no-staff-banner p {
  margin: 0 0 0.75rem;
  color: #78350f;
}

.no-staff-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-secondary.small {
  padding: 0.3rem 0.8rem;
  font-size: 0.85rem;
}

.btn-refresh {
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #d1d5db;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.role-badge.no-role {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.promote {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.promote:hover {
  background: #a7f3d0;
}

@media (max-width: 768px) {
  .no-staff-banner {
    flex-direction: column;
    text-align: center;
  }
  
  .no-staff-actions {
    justify-content: center;
  }
}



.error-banner .error-close:hover {
  opacity: 0.7;
}

.debug-banner {
  background: #dbeafe;
  color: #1e3a8a;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-left: 4px solid #1e3a8a;
}


.debug-banner .debug-close:hover {
  opacity: 0.7;
}

.no-staff-banner {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}



.no-staff-banner h4 {
  margin: 0 0 0.25rem;
  color: #92400e;
}

.no-staff-banner p {
  margin: 0 0 0.75rem;
  color: #78350f;
}

.no-staff-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-secondary.small {
  padding: 0.3rem 0.8rem;
  font-size: 0.85rem;
}

.btn-refresh {
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #d1d5db;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.role-badge.no-role {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.promote {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.promote:hover {
  background: #a7f3d0;
}

/* Make table responsive */
@media (max-width: 768px) {
  .no-staff-banner {
    flex-direction: column;
    text-align: center;
  }
  
  .no-staff-actions {
    justify-content: center;
  }
}
</style>
<style scoped>
.tour-staff-management {
  padding: 1.5rem;
  background: #f8fafc;
  min-height: 100vh;
}

/* Header */
.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1.8rem;
}

.header-left h1 i {
  color: #f59e0b;
}

.header-left p {
  margin: 0.25rem 0 0;
  color: #6b7280;
}

.btn-create {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-create:hover {
  background: #1a2e6b;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
}

.btn-create.small {
  padding: 0.4rem 1rem;
  font-size: 0.9rem;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: white;
}

.stat-icon.blue { background: #1e3a8a; }
.stat-icon.green { background: #059669; }
.stat-icon.purple { background: #7c3aed; }
.stat-icon.orange { background: #f59e0b; }

.stat-info h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #1e293b;
}

.stat-info p {
  margin: 0;
  color: #6b7280;
  font-size: 0.85rem;
}

/* Search */
.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
  background: white;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid #e5e7eb;
}

.search-box i {
  color: #9ca3af;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.9rem;
  padding: 0.25rem 0;
}

.filter-options {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  font-size: 0.9rem;
  color: #374151;
  cursor: pointer;
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

/* Table */
.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.staff-table {
  width: 100%;
  border-collapse: collapse;
}

.staff-table th {
  background: #f8fafc;
  color: #1e3a8a;
  font-weight: 600;
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 2px solid #e5e7eb;
  font-size: 0.85rem;
}

.staff-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.staff-table tr:hover td {
  background: #f8fafc;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #dbeafe;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e3a8a;
  font-size: 1.5rem;
}

.user-details .user-name {
  font-weight: 500;
  color: #1e293b;
}

.user-details .user-email {
  font-size: 0.85rem;
  color: #6b7280;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge.manager {
  background: #dbeafe;
  color: #1e3a8a;
}

.role-badge.assistant {
  background: #fef3c7;
  color: #92400e;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status.active {
  background: #d1fae5;
  color: #065f46;
}

.status.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.booking-stats {
  display: flex;
  gap: 0.75rem;
}

.stat-item {
  font-size: 0.85rem;
  color: #374151;
}

.stat-item i {
  margin-right: 0.25rem;
  color: #6b7280;
}

.stat-item.completed {
  color: #059669;
}

.stat-item.completed i {
  color: #059669;
}

.date-info {
  font-size: 0.85rem;
  color: #374151;
}

.last-login {
  font-size: 0.75rem;
  color: #9ca3af;
}

.last-login i {
  margin-right: 0.25rem;
}

.action-buttons {
  display: flex;
  gap: 0.3rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn.edit {
  background: #dbeafe;
  color: #1e3a8a;
}

.action-btn.edit:hover {
  background: #bfdbfe;
}

.action-btn.suspend {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.suspend:hover {
  background: #fde68a;
}

.action-btn.activate {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.activate:hover {
  background: #a7f3d0;
}

.action-btn.reset {
  background: #e0e7ff;
  color: #4338ca;
}

.action-btn.reset:hover {
  background: #c7d2fe;
}

.action-btn.delete {
  background: #fee2e2;
  color: #991b1b;
}

.action-btn.delete:hover {
  background: #fecaca;
}

.no-results {
  text-align: center;
  padding: 3rem;
}

.no-results i {
  font-size: 2rem;
  color: #9ca3af;
  display: block;
  margin-bottom: 0.5rem;
}

.no-results p {
  color: #6b7280;
  margin-bottom: 1rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.page-btn {
  padding: 0.4rem 1rem;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  color: #374151;
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

.page-info, .items-info {
  font-size: 0.85rem;
  color: #6b7280;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-lg { max-width: 600px; width: 95%; }
.modal-sm { max-width: 450px; width: 95%; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 12px 12px 0 0;
}

.modal-header h2 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0 0.5rem;
}

.close-btn:hover {
  color: #1f2937;
}

.modal-body {
  padding: 1.5rem;
}

.staff-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1e3a8a;
  box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.1);
}

.form-group input:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.checkbox-group {
  display: flex;
  gap: 1.5rem;
  margin: 1rem 0;
  flex-wrap: wrap;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 400;
}

.checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
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

.form-actions.justify-center {
  justify-content: center;
}

.btn-cancel {
  background: #e5e7eb;
  color: #374151;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancel:hover {
  background: #d1d5db;
}

.btn-submit {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-submit:hover {
  background: #1a2e6b;
}

.btn-warning {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}

.btn-warning:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Password Info */
.password-info {
  padding: 1rem 1.5rem 1.5rem;
}

.password-info code {
  background: #1e293b;
  color: #fbbf24;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
}

.password-info .warning {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

/* Reset Modal */
.reset-info {
  text-align: center;
  margin-bottom: 1.5rem;
}

.reset-info i {
  font-size: 2rem;
  color: #f59e0b;
  display: block;
  margin-bottom: 0.5rem;
}

.user-info-display {
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 8px;
  margin-top: 0.5rem;
}

.user-info-display strong {
  display: block;
  color: #1e293b;
}

.user-info-display span {
  font-size: 0.85rem;
  color: #6b7280;
}

.password-display {
  margin-top: 1rem;
}

.password-display label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #374151;
}

.password-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.password-result code {
  flex: 1;
  font-size: 0.9rem;
  color: #1e293b;
}

.copy-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  font-size: 1rem;
}

.copy-btn:hover {
  color: #1e293b;
}

/* Delete Modal */
.delete-warning {
  text-align: center;
  margin-bottom: 1.5rem;
}

.delete-warning i {
  font-size: 2rem;
  color: #dc2626;
  display: block;
  margin-bottom: 0.5rem;
}

.delete-user-info {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.user-detail {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.user-detail:last-child {
  border-bottom: none;
}

.user-detail .label {
  color: #6b7280;
}

.user-detail .value {
  color: #1e293b;
  font-weight: 500;
}

.delete-items-list {
  margin: 1rem 0;
}

.delete-items-list ul {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0;
}

.delete-items-list li {
  padding: 0.25rem 0;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.delete-items-list li i {
  color: #dc2626;
}

.confirm-input {
  margin: 1rem 0;
}

.confirm-input label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #374151;
}

.delete-confirm-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  text-align: center;
  font-weight: 700;
  letter-spacing: 2px;
  transition: border-color 0.2s;
}

.delete-confirm-input:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

@media (max-width: 768px) {
  .tour-staff-management {
    padding: 1rem;
  }
  
  .management-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-section {
    flex-direction: column;
  }
  
  .filter-options {
    flex-wrap: wrap;
  }
  
  .filter-select {
    flex: 1;
    min-width: 120px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .staff-table {
    font-size: 0.8rem;
  }
  
  .staff-table th,
  .staff-table td {
    padding: 0.5rem;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
  
  .action-btn {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
  
  .modal-lg {
    width: 98%;
    margin: 0.5rem;
  }
  
  .modal-sm {
    width: 98%;
    margin: 0.5rem;
  }
}
</style>