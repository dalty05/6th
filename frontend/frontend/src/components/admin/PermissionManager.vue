<template>
  <div class="permission-manager">
    <!-- Header -->
    <div class="permission-header">
      <div class="header-content">
        <h1><i class="fas fa-shield-alt"></i> Permission Manager</h1>
        <p class="subtitle">Manage user permissions and access control</p>
      </div>
      <div class="header-actions">
        <button v-if="isSuperAdmin" @click="refreshData" class="btn-refresh" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'spinning': loading }"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Warning Banner -->
    <div class="warning-banner" v-if="!isSuperAdmin">
      <i class="fas fa-shield-alt"></i>
      <span>Super admin access required to manage permissions</span>
    </div>

    <!-- Super Admin Controls -->
    <div v-if="isSuperAdmin" class="controls-section">
      <!-- User Selector -->
      <div class="user-selector">
        <label for="userSelect">Select User:</label>
        <select 
          id="userSelect"
          v-model="selectedUserId" 
          @change="loadUserPermissions"
          :disabled="loading"
        >
          <option value="">-- Select User --</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.full_name }} ({{ user.email }}) - {{ user.role }}
          </option>
        </select>
      </div>

      <!-- Quick Stats -->
      <div v-if="selectedUser" class="user-stats">
        <div class="stat-item">
          <span class="stat-label">Custom Permissions:</span>
          <span class="stat-value">{{ customPermissions.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Role:</span>
          <span class="stat-value role-badge" :class="selectedUser.role">
            {{ selectedUser.role.toUpperCase() }}
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading permissions...</p>
    </div>

    <!-- Access Denied -->
    <div v-else-if="!isSuperAdmin" class="access-denied">
      <i class="fas fa-lock"></i>
      <h3>Access Denied</h3>
      <p>Only Super Administrators can manage permissions</p>
    </div>

    <!-- No User Selected -->
    <div v-else-if="!selectedUser" class="empty-state">
      <i class="fas fa-user-lock"></i>
      <h3>Select a user to manage permissions</h3>
      <p>Choose a user from the dropdown above to view and edit their permissions</p>
    </div>

    <!-- Permission Editor -->
    <div v-else-if="selectedUser && isSuperAdmin" class="permissions-editor">
      <!-- User Info Card -->
      <div class="user-info-card">
        <div class="user-avatar">
          <span>{{ userInitials }}</span>
        </div>
        <div class="user-details">
          <h3>{{ selectedUser.full_name }}</h3>
          <p class="user-email">{{ selectedUser.email }}</p>
          <div class="user-meta">
            <span class="role-badge" :class="selectedUser.role">
              {{ selectedUser.role.toUpperCase() }}
            </span>
            <span class="status-badge" :class="{ active: selectedUser.is_active, inactive: !selectedUser.is_active }">
              {{ selectedUser.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
        <div class="user-info-hint">
          <i class="fas fa-info-circle"></i>
          Check boxes to grant permission. Uncheck to deny. Empty boxes use role defaults.
        </div>
      </div>

      <!-- Resources Grid -->
      <div class="permissions-grid">
        <!-- Core Resources -->
        <div v-for="resource in availableResources" :key="resource.name" class="resource-card">
          <div class="resource-header">
            <h4>{{ resource.label }}</h4>
            <span class="resource-name">{{ resource.name }}</span>
            <span v-if="hasCustomPermission(resource.name)" class="custom-badge">
              <i class="fas fa-pen"></i> Custom
            </span>
          </div>
          <div class="actions-list">
            <div v-for="action in resource.actions" :key="action" class="action-row">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="isCustomAllowed(resource.name, action)"
                  @change="togglePermission(resource.name, action, $event.target.checked)"
                  :disabled="saving"
                >
                <span class="action-name">{{ action }}</span>
              </label>
              <span class="role-default-badge" :class="{ allowed: getRoleDefault(resource.name, action) }">
                {{ getRoleDefault(resource.name, action) ? '✓ Default' : '✗ Default' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button @click="resetToRoleDefaults" class="btn-reset" :disabled="saving || customPermissions.length === 0">
          <i class="fas fa-undo"></i>
          {{ saving ? 'Resetting...' : 'Reset to Role Defaults' }}
        </button>
        <button @click="savePermissions" class="btn-save" :disabled="saving">
          <i v-if="!saving" class="fas fa-save"></i>
          <i v-else class="fas fa-spinner fa-spin"></i>
          {{ saving ? 'Saving...' : 'Save Custom Permissions' }}
        </button>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="successMessage" class="alert-success">
        <i class="fas fa-check-circle"></i> {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert-error">
        <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'
import authService from '@/services/auth'

export default {
  name: 'PermissionManager',
  
  data() {
    return {
      users: [],
      selectedUserId: '',
      selectedUser: null,
      resources: [],
      customPermissions: [],
      roleDefaults: {},
      loading: false,
      saving: false,
      successMessage: '',
      errorMessage: '',
      messageTimeout: null
    }
  },

  computed: {
    currentUser() {
      return authService.getUser()
    },
    
    isSuperAdmin() {
      return this.currentUser?.role === 'super_admin'
    },
    
    userInitials() {
      if (!this.selectedUser?.full_name) return 'U'
      return this.selectedUser.full_name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    },
    
    availableResources() {
      // Combine core resources with any from API
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
        { name: 'newsletter', label: 'Newsletter', actions: ['create', 'read', 'update', 'delete'] },
        { name: 'tours', label: '🏭 Tours', actions: ['create', 'read', 'update', 'delete'] },
        { name: 'bookings', label: '📋 Bookings', actions: ['create', 'read', 'update', 'delete', 'approve', 'reject'] },
        { name: 'tour_settings', label: '⚙️ Tour Settings', actions: ['read', 'update'] },
        { name: 'profile', label: '👤 Profile', actions: ['read', 'update'] }
      ]
      
      // If API resources are loaded, merge them
      if (this.resources && this.resources.length > 0) {
        return this.resources
      }
      
      return coreResources
    }
  },

  watch: {
    selectedUserId(newVal) {
      if (!newVal) {
        this.selectedUser = null
        this.customPermissions = []
        this.roleDefaults = {}
      }
    }
  },

  mounted() {
    if (this.isSuperAdmin) {
      this.loadUsers()
      this.loadResources()
    }
  },

  beforeUnmount() {
    if (this.messageTimeout) {
      clearTimeout(this.messageTimeout)
    }
  },

  methods: {
    async loadUsers() {
      if (!this.isSuperAdmin) return
      
      try {
        const response = await api.get('/admin/users')
        this.users = response.data || []
      } catch (error) {
        console.error('Error loading users:', error)
        this.showError('Failed to load users')
      }
    },

    async loadResources() {
      if (!this.isSuperAdmin) return
      
      try {
        const response = await api.get('/permissions/resources')
        this.resources = response.data || []
        console.log('✅ Resources loaded:', this.resources.length)
      } catch (error) {
        console.error('Error loading resources:', error)
        // Use fallback resources
        this.resources = []
        // Don't show error for 404 - use fallback
        if (error.response?.status !== 404) {
          this.showError('Failed to load resources')
        }
      }
    },

    async loadUserPermissions() {
      if (!this.selectedUserId || !this.isSuperAdmin) {
        this.selectedUser = null
        this.customPermissions = []
        this.roleDefaults = {}
        return
      }
      
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await api.get(`/permissions/users/${this.selectedUserId}`)
        this.selectedUser = response.data.user
        this.customPermissions = response.data.custom_permissions || []
        this.roleDefaults = response.data.role_defaults || {}
        
        console.log(`✅ Loaded permissions for user: ${this.selectedUser.full_name}`)
        console.log('📋 Custom permissions:', this.customPermissions.length)
      } catch (error) {
        console.error('Error loading user permissions:', error)
        this.showError(error.response?.data?.error || 'Failed to load user permissions')
        this.selectedUser = null
        this.customPermissions = []
        this.roleDefaults = {}
      } finally {
        this.loading = false
      }
    },

    hasCustomPermission(resource) {
      return this.customPermissions.some(p => p.resource === resource)
    },

    isCustomAllowed(resource, action) {
      const perm = this.customPermissions.find(p => p.resource === resource && p.action === action)
      return perm ? perm.is_allowed : false
    },

    getRoleDefault(resource, action) {
      const defaults = this.roleDefaults[resource]
      if (!defaults) return false
      
      if (Array.isArray(defaults)) {
        return defaults.includes(action)
      }
      if (typeof defaults === 'object') {
        return defaults[action] === true
      }
      return false
    },

    togglePermission(resource, action, isAllowed) {
      const existingIndex = this.customPermissions.findIndex(
        p => p.resource === resource && p.action === action
      )
      
      if (existingIndex !== -1) {
        if (!isAllowed) {
          // Remove if unchecked
          this.customPermissions.splice(existingIndex, 1)
        } else {
          // Update if checked
          this.customPermissions[existingIndex].is_allowed = isAllowed
        }
      } else if (isAllowed) {
        // Add new if checked and not exists
        this.customPermissions.push({
          resource,
          action,
          is_allowed: true,
          id: null
        })
      }
      
      // Clear messages on change
      this.successMessage = ''
      this.errorMessage = ''
    },

    async savePermissions() {
      if (!this.selectedUserId) {
        this.showError('No user selected')
        return
      }
      
      this.saving = true
      this.errorMessage = ''
      this.successMessage = ''
      
      try {
        // Save each custom permission
        for (const perm of this.customPermissions) {
          await api.post(`/permissions/users/${this.selectedUserId}`, {
            resource: perm.resource,
            action: perm.action,
            is_allowed: perm.is_allowed
          })
        }
        
        this.showSuccess('Permissions saved successfully!')
        await this.loadUserPermissions()
        
      } catch (error) {
        console.error('Error saving permissions:', error)
        this.showError(error.response?.data?.error || 'Failed to save permissions')
      } finally {
        this.saving = false
      }
    },

    async resetToRoleDefaults() {
      if (!this.selectedUserId) {
        this.showError('No user selected')
        return
      }
      
      if (!confirm('Reset all custom permissions for this user to role defaults?')) {
        return
      }
      
      this.saving = true
      this.errorMessage = ''
      this.successMessage = ''
      
      try {
        // Delete all custom permissions for this user
        for (const perm of this.customPermissions) {
          if (perm.id) {
            await api.delete(`/permissions/users/${this.selectedUserId}/${perm.id}`)
          }
        }
        
        this.customPermissions = []
        this.showSuccess('Reset to role defaults successfully!')
        await this.loadUserPermissions()
        
      } catch (error) {
        console.error('Error resetting permissions:', error)
        this.showError(error.response?.data?.error || 'Failed to reset permissions')
      } finally {
        this.saving = false
      }
    },

    async refreshData() {
      this.errorMessage = ''
      this.successMessage = ''
      await this.loadUsers()
      await this.loadResources()
      if (this.selectedUserId) {
        await this.loadUserPermissions()
      }
      toast.info('Data refreshed')
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