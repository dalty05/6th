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
        <div v-for="resource in resources" :key="resource.name" class="resource-card">
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
import { ref, onMounted, computed } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'
import authService from '@/services/auth'

const users = ref([])
const selectedUserId = ref('')
const selectedUser = ref(null)
const resources = ref([])
const customPermissions = ref([])
const roleDefaults = ref({})
const loading = ref(false)
const saving = ref(false)

// Check if current user is super admin
const currentUser = authService.getUser()
const isSuperAdmin = computed(() => currentUser?.role === 'super_admin')

// Load all users
const loadUsers = async () => {
  if (!isSuperAdmin.value) return
  
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error) {
    console.error('Error loading users:', error)
    toast.error('Failed to load users')
  }
}

// Load available resources - FIXED ENDPOINT
const loadResources = async () => {
  if (!isSuperAdmin.value) return
  
  try {
    // Use the correct endpoint: /permissions/resources (not resources-list)
    const response = await api.get('/permissions/resources')
    resources.value = response.data
  } catch (error) {
    console.error('Error loading resources:', error)
    toast.error('Failed to load resources')
  }
}

// Load permissions for selected user
const loadUserPermissions = async () => {
  if (!selectedUserId.value || !isSuperAdmin.value) {
    selectedUser.value = null
    return
  }
  
  loading.value = true
  try {
    const response = await api.get(`/permissions/users/${selectedUserId.value}`)
    selectedUser.value = response.data.user
    customPermissions.value = response.data.custom_permissions || []
    roleDefaults.value = response.data.role_defaults || {}
  } catch (error) {
    console.error('Error loading user permissions:', error)
    toast.error('Failed to load user permissions')
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
      is_allowed: isAllowed,
      id: null
    })
  }
}

// Save custom permissions
const savePermissions = async () => {
  saving.value = true
  
  try {
    for (const perm of customPermissions.value) {
      await api.post(`/permissions/users/${selectedUserId.value}`, {
        resource: perm.resource,
        action: perm.action,
        is_allowed: perm.is_allowed
      })
    }
    
    toast.success('Permissions saved successfully')
    await loadUserPermissions()
  } catch (error) {
    console.error('Error saving permissions:', error)
    toast.error('Failed to save permissions')
  } finally {
    saving.value = false
  }
}

// Reset to role defaults
const resetToRoleDefaults = async () => {
  if (!confirm('Reset all custom permissions for this user to role defaults?')) {
    return
  }
  
  saving.value = true
  try {
    for (const perm of customPermissions.value) {
      if (perm.id) {
        await api.delete(`/permissions/users/${selectedUserId.value}/${perm.id}`)
      }
    }
    
    customPermissions.value = []
    toast.success('Reset to role defaults')
    await loadUserPermissions()
  } catch (error) {
    console.error('Error resetting permissions:', error)
    toast.error('Failed to reset permissions')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (isSuperAdmin.value) {
    loadUsers()
    loadResources()
  }
})
</script>

<style scoped>
.permission-manager {
  padding: 1.5rem;
  background: #f8fafc;
  min-height: 100vh;
}

.admin-header {
  margin-bottom: 1.5rem;
}

.admin-header h2 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
}

.admin-header p {
  color: #6b7280;
  margin: 0;
}

.warning-banner {
  background: #fef3c7;
  color: #92400e;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.access-denied {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
}

.access-denied i {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.access-denied h3 {
  color: #991b1b;
  margin-bottom: 0.5rem;
}

.user-selector {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.user-selector label {
  font-weight: 600;
  color: #374151;
}

.user-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  min-width: 300px;
  font-size: 0.9rem;
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

.user-info-card {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #f59e0b;
}

.user-info-card h3 {
  margin: 0 0 0.25rem;
  color: #1e3a8a;
}

.user-info-card p {
  margin: 0.25rem 0;
  color: #6b7280;
}

.info-text {
  font-size: 0.8rem;
  color: #9ca3af;
  margin-top: 0.5rem !important;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.resource-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.resource-header {
  background: #f8fafc;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.resource-header h4 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1rem;
}

.resource-name {
  font-size: 0.7rem;
  color: #9ca3af;
}

.actions-list {
  padding: 0.75rem;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.action-row:last-child {
  border-bottom: none;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.action-name {
  font-size: 0.85rem;
  text-transform: capitalize;
}

.role-default-badge {
  font-size: 0.7rem;
  color: #9ca3af;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-save {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-reset {
  background: #e5e7eb;
  color: #374151;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-save:hover {
  background: #f59e0b;
}

.btn-reset:hover {
  background: #d1d5db;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
}

.empty-state i {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
}

@media (max-width: 768px) {
  .permission-manager {
    padding: 1rem;
  }
  
  .permissions-grid {
    grid-template-columns: 1fr;
  }
  
  .user-selector select {
    min-width: 100%;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-save, .btn-reset {
    width: 100%;
  }
}
</style>