<template>
  <div class="permission-manager">
    <div class="admin-header">
      <h2>Permission Manager</h2>
      <p>Override role-based permissions for individual users</p>
      <div class="warning-banner" v-if="!isSuperAdmin">
        <i class="fas fa-shield-alt"></i>
        Super admin access required to manage permissions
      </div>
    </div>

    <!-- User Selector - Only visible to super admin -->
    <div v-if="isSuperAdmin" class="user-selector">
      <label>Select User:</label>
      <select v-model="selectedUserId" @change="loadUserPermissions">
        <option value="">-- Select User --</option>
        <option v-for="user in users" :key="user.id" :value="user.id">
          {{ user.full_name }} ({{ user.email }}) - {{ user.role }}
        </option>
      </select>
    </div>

    <!-- Access Denied for non-super admin -->
    <div v-else class="access-denied">
      <i class="fas fa-lock"></i>
      <h3>Access Denied</h3>
      <p>Only Super Administrators can manage permissions</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading permissions...</p>
    </div>

    <!-- Permission Editor -->
    <div v-else-if="selectedUser && isSuperAdmin" class="permissions-editor">
      <div class="user-info-card">
        <h3>{{ selectedUser.full_name }}</h3>
        <p>Role: <strong>{{ selectedUser.role.toUpperCase() }}</strong></p>
        <p class="info-text">Check boxes to grant permission. Uncheck to deny. Empty boxes use role defaults.</p>
      </div>

      <div class="permissions-grid">
        <!-- Core Resources -->
        <div v-for="resource in coreResources" :key="resource.name" class="resource-card">
          <div class="resource-header">
            <h4>{{ resource.label }}</h4>
            <span class="resource-name">{{ resource.name }}</span>
          </div>
          <div class="actions-list">
            <div v-for="action in resource.actions" :key="action" class="action-row">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="isCustomAllowed(resource.name, action)"
                  @change="togglePermission(resource.name, action, $event.target.checked)"
                >
                <span class="action-name">{{ action }}</span>
              </label>
              <span class="role-default-badge">
                Default: {{ getRoleDefault(resource.name, action) ? '✓' : '✗' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Tour Resources -->
        <div class="resource-section-divider">
          <h3>Tour Management</h3>
          <p>Permissions for factory tour management</p>
        </div>

        <div class="resource-card tour-resource">
          <div class="resource-header tour-header">
            <h4>🏭 Tours</h4>
            <span class="resource-name">tours</span>
          </div>
          <div class="actions-list">
            <div v-for="action in ['create', 'read', 'update', 'delete']" :key="action" class="action-row">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="isCustomAllowed('tours', action)"
                  @change="togglePermission('tours', action, $event.target.checked)"
                >
                <span class="action-name">{{ action }}</span>
              </label>
              <span class="role-default-badge">
                Default: {{ getRoleDefault('tours', action) ? '✓' : '✗' }}
              </span>
            </div>
          </div>
        </div>

        <div class="resource-card tour-resource">
          <div class="resource-header tour-header">
            <h4>📋 Bookings</h4>
            <span class="resource-name">bookings</span>
          </div>
          <div class="actions-list">
            <div v-for="action in ['create', 'read', 'update', 'delete', 'approve', 'reject']" :key="action" class="action-row">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="isCustomAllowed('bookings', action)"
                  @change="togglePermission('bookings', action, $event.target.checked)"
                >
                <span class="action-name">{{ action }}</span>
              </label>
              <span class="role-default-badge">
                Default: {{ getRoleDefault('bookings', action) ? '✓' : '✗' }}
              </span>
            </div>
          </div>
        </div>

        <div class="resource-card tour-resource">
          <div class="resource-header tour-header">
            <h4>⚙️ Tour Settings</h4>
            <span class="resource-name">tour_settings</span>
          </div>
          <div class="actions-list">
            <div v-for="action in ['read', 'update']" :key="action" class="action-row">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="isCustomAllowed('tour_settings', action)"
                  @change="togglePermission('tour_settings', action, $event.target.checked)"
                >
                <span class="action-name">{{ action }}</span>
              </label>
              <span class="role-default-badge">
                Default: {{ getRoleDefault('tour_settings', action) ? '✓' : '✗' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button @click="resetToRoleDefaults" class="btn-reset" :disabled="saving">
          Reset to Role Defaults
        </button>
        <button @click="savePermissions" class="btn-save" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save Custom Permissions' }}
        </button>
      </div>
    </div>

    <!-- No User Selected -->
    <div v-else-if="!loading && !selectedUser && isSuperAdmin" class="empty-state">
      <i class="fas fa-user-lock"></i>
      <h3>Select a user to manage permissions</h3>
      <p>Choose a user from the dropdown above to view and edit their permissions</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'  // ✅ Add watch import
import { toast } from 'vue3-toastify'
import api from '@/services/api'
import authService from '@/services/auth'

// Define all reactive variables
const users = ref([])
const selectedUserId = ref('')
const selectedUser = ref(null)
const resources = ref([])
const customPermissions = ref([])
const roleDefaults = ref({})
const loading = ref(false)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const messageTimeout = ref(null)

// Check if current user is super admin
const currentUser = authService.getUser()
const isSuperAdmin = computed(() => currentUser?.role === 'super_admin')

// Core resources (without tour resources)
const coreResources = [
  { name: 'products', label: 'Products', actions: ['create', 'read', 'update', 'delete'] },
  { name: 'blog', label: 'Blog Posts', actions: ['create', 'read', 'update', 'delete'] },
  { name: 'jobs', label: 'Job Management', actions: ['create', 'read', 'update', 'delete'] },
  { name: 'outlets', label: 'Outlet Locations', actions: ['create', 'read', 'update', 'delete'] },
  { name: 'users', label: 'User Management', actions: ['create', 'read', 'update', 'delete'] },
  { name: 'partners', label: 'Partners', actions: ['create', 'read', 'update', 'delete'] },
  { name: 'referrals', label: 'Referrals', actions: ['create', 'read', 'update', 'delete'] },
  { name: 'statistics', label: 'Statistics', actions: ['read'] },
  { name: 'contacts', label: 'Contact Messages', actions: ['read', 'update', 'delete'] },
  { name: 'newsletter', label: 'Newsletter', actions: ['create', 'read', 'update', 'delete'] }
]

// Load all users
const loadUsers = async () => {
  if (!isSuperAdmin.value) return
  
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error) {
    toast.error('Failed to load users')
  }
}

// Load available resources
const loadResources = async () => {
  if (!isSuperAdmin.value) return
  
  try {
    const response = await api.get('/admin/permissions/resources')
    resources.value = response.data
  } catch (error) {
    toast.error('Failed to load resources')
  }
}

// Load permissions for selected user
const loadUserPermissions = async () => {
  if (!selectedUserId.value || !isSuperAdmin.value) {
    selectedUser.value = null
    customPermissions.value = []
    roleDefaults.value = {}
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await api.get(`/admin/permissions/users/${selectedUserId.value}`)
    selectedUser.value = response.data.user
    customPermissions.value = response.data.custom_permissions || []
    roleDefaults.value = response.data.role_defaults || {}
    
  
  } catch (error) {
    const msg = error.response?.data?.error || 'Failed to load user permissions'
    errorMessage.value = msg
    toast.error(msg)
    selectedUser.value = null
    customPermissions.value = []
    roleDefaults.value = {}
  } finally {
    loading.value = false
  }
}

// Check if a permission is set as custom (overridden)
const isCustomAllowed = (resource, action) => {
  const perm = customPermissions.value.find(p => p.resource === resource && p.action === action)
  return perm ? perm.is_allowed : false
}

// Get role default for display
const getRoleDefault = (resource, action) => {
  const defaults = roleDefaults.value[resource]
  if (Array.isArray(defaults)) {
    return defaults.includes(action)
  }
  if (typeof defaults === 'object') {
    return defaults[action] === true
  }
  return false
}

// Toggle a permission
const togglePermission = (resource, action, isAllowed) => {
  const existingIndex = customPermissions.value.findIndex(p => p.resource === resource && p.action === action)
  
  if (existingIndex !== -1) {
    if (!isAllowed) {
      customPermissions.value.splice(existingIndex, 1)
    } else {
      customPermissions.value[existingIndex].is_allowed = isAllowed
    }
  } else if (isAllowed) {
    customPermissions.value.push({
      resource,
      action,
      is_allowed: true,
      id: null
    })
  }
  
  // Clear messages on change
  successMessage.value = ''
  errorMessage.value = ''
}

// Save custom permissions
const savePermissions = async () => {
  if (!selectedUserId.value) {
    errorMessage.value = 'No user selected'
    toast.error('No user selected')
    return
  }
  
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    for (const perm of customPermissions.value) {
      await api.post(`/admin/permissions/users/${selectedUserId.value}`, {
        resource: perm.resource,
        action: perm.action,
        is_allowed: perm.is_allowed
      })
    }
    
    successMessage.value = 'Permissions saved successfully!'
    toast.success('Permissions saved successfully!')
    await loadUserPermissions()
    
  } catch (error) {
    const msg = error.response?.data?.error || 'Failed to save permissions'
    errorMessage.value = msg
    toast.error(msg)
  } finally {
    saving.value = false
  }
}

// Reset to role defaults
const resetToRoleDefaults = async () => {
  if (!selectedUserId.value) {
    errorMessage.value = 'No user selected'
    toast.error('No user selected')
    return
  }
  
  if (!confirm('Reset all custom permissions for this user to role defaults?')) {
    return
  }
  
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    for (const perm of customPermissions.value) {
      if (perm.id) {
        await api.delete(`/admin/permissions/users/${selectedUserId.value}/${perm.id}`)
      }
    }
    
    customPermissions.value = []
    successMessage.value = 'Reset to role defaults successfully!'
    toast.success('Reset to role defaults successfully!')
    await loadUserPermissions()
    
  } catch (error) {
    const msg = error.response?.data?.error || 'Failed to reset permissions'
    errorMessage.value = msg
    toast.error(msg)
  } finally {
    saving.value = false
  }
}

// ✅ Watch for user ID changes
watch(selectedUserId, (newVal) => {
  if (!newVal) {
    selectedUser.value = null
    customPermissions.value = []
    roleDefaults.value = {}
  }
})

// Mounted lifecycle
onMounted(() => {
  if (isSuperAdmin.value) {
    loadUsers()
    loadResources()
  }
})
</script>

<style scoped>
/* ... existing styles ... */
</style>
<style scoped>
.permission-manager {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.permission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.header-content h1 i {
  color: #2563eb;
  margin-right: 12px;
}

.subtitle {
  color: #64748b;
  margin: 0;
  font-size: 16px;
}

.btn-refresh {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
}

.btn-refresh:hover:not(:disabled) {
  background: #f1f5f9;
  color: #1a1a2e;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Warning Banner */
.warning-banner {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  color: #92400e;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

/* Controls Section */
.controls-section {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.user-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-selector label {
  font-weight: 600;
  color: #1a1a2e;
  font-size: 14px;
}

.user-selector select {
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  min-width: 250px;
  background: #f8fafc;
  transition: all 0.2s;
}

.user-selector select:focus {
  outline: none;
  border-color: #2563eb;
}

.user-stats {
  display: flex;
  align-items: center;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.stat-label {
  color: #64748b;
}

.stat-value {
  font-weight: 600;
  color: #1a1a2e;
}

.role-badge {
  padding: 2px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.role-badge.super_admin {
  background: #fef3c7;
  color: #92400e;
}

.role-badge.admin {
  background: #dbeafe;
  color: #1e40af;
}

.role-badge.tour_manager {
  background: #d1fae5;
  color: #065f46;
}

.role-badge.tour_assistant {
  background: #e0e7ff;
  color: #3730a3;
}

.role-badge.partner {
  background: #fce4ec;
  color: #9a3412;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #94a3b8;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

/* Access Denied */
.access-denied,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.access-denied i,
.empty-state i {
  font-size: 48px;
  color: #94a3b8;
  margin-bottom: 16px;
}

.access-denied h3,
.empty-state h3 {
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.access-denied p,
.empty-state p {
  color: #64748b;
  margin: 0;
}

/* User Info Card */
.user-info-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
}

.user-details h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
  color: #1a1a2e;
}

.user-email {
  margin: 0 0 8px 0;
  color: #64748b;
}

.user-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status-badge {
  padding: 2px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.user-info-hint {
  margin-left: auto;
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  padding: 8px 16px;
  border-radius: 8px;
}

/* Permissions Grid */
.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.resource-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.resource-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e1;
}

.resource-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f1f5f9;
  flex-wrap: wrap;
}

.resource-header h4 {
  margin: 0;
  font-size: 15px;
  color: #1a1a2e;
}

.resource-name {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
  background: #f1f5f9;
  padding: 1px 8px;
  border-radius: 4px;
}

.custom-badge {
  font-size: 11px;
  color: #2563eb;
  background: #dbeafe;
  padding: 1px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #2563eb;
  cursor: pointer;
}

.action-name {
  text-transform: capitalize;
  color: #1a1a2e;
}

.role-default-badge {
  font-size: 11px;
  color: #94a3b8;
}

.role-default-badge.allowed {
  color: #16a34a;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
}

.btn-reset,
.btn-save {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-reset {
  background: #f1f5f9;
  color: #64748b;
}

.btn-reset:hover:not(:disabled) {
  background: #e2e8f0;
  color: #1a1a2e;
}

.btn-reset:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-save {
  background: #2563eb;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Alert Messages */
.alert-success,
.alert-error {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.alert-success {
  background: #dcfce7;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.alert-error {
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

/* Responsive */
@media (max-width: 768px) {
  .permission-manager {
    padding: 16px;
  }
  
  .permission-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .user-selector {
    flex-direction: column;
    align-items: stretch;
  }
  
  .user-selector select {
    min-width: unset;
  }
  
  .user-stats {
    justify-content: space-around;
  }
  
  .user-info-card {
    flex-direction: column;
    text-align: center;
  }
  
  .user-info-hint {
    margin-left: 0;
  }
  
  .permissions-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    justify-content: center;
  }
}
</style>