<template>
  <div class="user-management">
    <div class="header">
      <h2>User Management</h2>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-user-plus"></i> Create User
      </button>
    </div>
    
    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="filters.search" 
          placeholder="Search users..."
          @input="debouncedSearch"
        >
      </div>
      <select v-model="filters.role" @change="applyFilters" class="filter-select">
        <option value="">All Roles</option>
        <option value="super_admin">Super Admin</option>
        <option value="admin">Admin</option>
        <option value="partner">Partner</option>
      </select>
      <select v-model="filters.status" @change="applyFilters" class="filter-select">
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
    
    <!-- Users Table -->
    <DataTable 
      :data="filteredUsers" 
      :columns="columns" 
      :loading="loading"
      :search-keys="['full_name', 'email']"
    >
      <template #actions="{ row }">
        <button @click="openEditModal(row)" class="btn-edit" title="Edit User">
          <i class="fas fa-edit"></i>
        </button>
        <button @click="openPermissionsModal(row)" class="btn-permissions" title="Manage Permissions">
          <i class="fas fa-lock"></i>
        </button>
        <button v-if="row.role !== 'super_admin'" @click="confirmDelete(row)" class="btn-delete" title="Delete User">
          <i class="fas fa-trash"></i>
        </button>
      </template>
    </DataTable>
    
    <!-- Create/Edit User Modal -->
    <div v-if="showUserModal" class="modal-overlay" @click.self="closeUserModal">
      <div class="modal-container glass-card modal-medium">
        <div class="modal-header">
          <h2>{{ editingUser ? 'Edit User' : 'Create New User' }}</h2>
          <button @click="closeUserModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveUser" class="modal-form">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" v-model="userForm.full_name" required>
          </div>
          
          <div class="form-group">
            <label>Email *</label>
            <input type="email" v-model="userForm.email" required :disabled="!!editingUser">
          </div>
          
          <div class="form-group" v-if="!editingUser">
            <label>Password *</label>
            <input type="password" v-model="userForm.password" required>
            <small>Must be at least 8 characters with uppercase, lowercase, and number</small>
          </div>
          
          <div class="form-group">
            <label>Role *</label>
            <select v-model="userForm.role" required>
              <option value="admin">Administrator</option>
              <option value="partner">Marketing Partner</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Status</label>
            <label class="toggle-switch">
              <input type="checkbox" v-model="userForm.is_active">
              <span class="toggle-slider"></span>
              <span class="toggle-label">{{ userForm.is_active ? 'Active' : 'Inactive' }}</span>
            </label>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ saving ? 'Saving...' : 'Save User' }}
            </button>
            <button type="button" @click="closeUserModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Permission Editor Modal -->
    <div v-if="showPermissionsModal" class="modal-overlay" @click.self="closePermissionsModal">
      <div class="modal-container glass-card modal-large">
        <div class="modal-header">
          <h2>Permissions: {{ selectedUser?.full_name }}</h2>
          <button @click="closePermissionsModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="permissions-editor">
          <div class="permissions-toolbar">
            <div class="template-selector">
              <span>Apply Template:</span>
              <select v-model="selectedTemplate" class="template-select">
                <option value="">Select template...</option>
                <option value="admin_full">Admin - Full Access</option>
                <option value="admin_limited">Admin - Limited</option>
                <option value="partner_full">Partner - Full Access</option>
                <option value="partner_readonly">Partner - Read Only</option>
                <option value="partner_creator">Partner - Creator</option>
              </select>
              <button @click="applyTemplate" class="btn-sm">Apply</button>
            </div>
            <button @click="resetPermissions" class="btn-sm btn-outline">Reset to Default</button>
          </div>
          
          <div class="permissions-grid">
            <div v-for="resource in resources" :key="resource.id" class="permission-card">
              <div class="resource-header">
                <i class="fas" :class="getResourceIcon(resource.id)"></i>
                <div>
                  <h4>{{ resource.name }}</h4>
                  <p>{{ resource.description }}</p>
                </div>
              </div>
              
              <div class="permission-actions">
                <label class="permission-checkbox">
                  <input type="checkbox" v-model="permissions[resource.id].create">
                  <span>Create</span>
                </label>
                <label class="permission-checkbox">
                  <input type="checkbox" v-model="permissions[resource.id].read">
                  <span>Read</span>
                </label>
                <label class="permission-checkbox">
                  <input type="checkbox" v-model="permissions[resource.id].update">
                  <span>Update</span>
                </label>
                <label class="permission-checkbox">
                  <input type="checkbox" v-model="permissions[resource.id].delete">
                  <span>Delete</span>
                </label>
              </div>
              
              <div class="permission-level" :class="getPermissionLevelClass(resource.id)">
                {{ getPermissionLevelText(resource.id) }}
              </div>
            </div>
          </div>
          
          <div class="modal-actions">
            <button @click="savePermissions" class="btn-primary" :disabled="savingPermissions">
              <i v-if="savingPermissions" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              Save Permissions
            </button>
            <button @click="closePermissionsModal" class="btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-container glass-card modal-small">
        <div class="modal-header">
          <h2>Delete User</h2>
          <button @click="closeDeleteModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ userToDelete?.full_name }}</strong>?</p>
          <p class="warning-text">This action cannot be undone. All associated data will be lost.</p>
        </div>
        <div class="modal-actions">
          <button @click="deleteUser" class="btn-danger">
            <i class="fas fa-trash"></i> Delete Permanently
          </button>
          <button @click="closeDeleteModal" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { toast } from 'vue3-toastify'
import DataTable from './DataTable.vue'
import api from '@/services/api'

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const savingPermissions = ref(false)
const showUserModal = ref(false)
const showPermissionsModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const selectedUser = ref(null)
const userToDelete = ref(null)
const selectedTemplate = ref('')

const filters = ref({
  search: '',
  role: '',
  status: ''
})

const userForm = ref({
  full_name: '',
  email: '',
  password: '',
  role: 'admin',
  is_active: true
})

const permissions = ref({})
const resources = [
  { id: 'products', name: 'Products', description: 'Manage dairy products catalog' },
  { id: 'blog', name: 'Blog Posts', description: 'Create and manage blog content' },
  { id: 'users', name: 'Users', description: 'Manage user accounts' },
  { id: 'partners', name: 'Partners', description: 'Manage partner accounts' },
  { id: 'referrals', name: 'Referrals', description: 'Referral links and tracking' },
  { id: 'statistics', name: 'Statistics', description: 'View analytics and reports' },
  { id: 'settings', name: 'Settings', description: 'System configuration' }
]

const columns = [
  { key: 'full_name', label: 'Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'role', label: 'Role', type: 'status', sortable: true },
  { key: 'is_active', label: 'Status', type: 'status', sortable: true },
  { key: 'created_at', label: 'Joined', type: 'date', sortable: true, width: '120px' },
  { key: 'last_login', label: 'Last Login', type: 'date', sortable: true, width: '140px' }
]

const filteredUsers = computed(() => {
  let result = [...users.value]
  
  if (filters.value.role) {
    result = result.filter(u => u.role === filters.value.role)
  }
  
  if (filters.value.status === 'active') {
    result = result.filter(u => u.is_active === true)
  } else if (filters.value.status === 'inactive') {
    result = result.filter(u => u.is_active === false)
  }
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(u => 
      u.full_name.toLowerCase().includes(search) ||
      u.email.toLowerCase().includes(search)
    )
  }
  
  return result
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error) {
    console.error('Error fetching users:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingUser.value = null
  userForm.value = {
    full_name: '',
    email: '',
    password: '',
    role: 'admin',
    is_active: true
  }
  showUserModal.value = true
}

const openEditModal = (user) => {
  editingUser.value = user
  userForm.value = {
    full_name: user.full_name,
    email: user.email,
    password: '',
    role: user.role,
    is_active: user.is_active
  }
  showUserModal.value = true
}

const saveUser = async () => {
  saving.value = true
  try {
    if (editingUser.value) {
      await api.put(`/admin/users/${editingUser.value.id}`, {
        full_name: userForm.value.full_name,
        role: userForm.value.role,
        is_active: userForm.value.is_active
      })
      toast.success('User updated successfully')
    } else {
      await api.post('/admin/users', userForm.value)
      toast.success('User created successfully')
    }
    await fetchUsers()
    closeUserModal()
  } catch (error) {
    console.error('Error saving user:', error)
  } finally {
    saving.value = false
  }
}

const openPermissionsModal = async (user) => {
  selectedUser.value = user
  showPermissionsModal.value = true
  await loadUserPermissions(user.id)
}

const loadUserPermissions = async (userId) => {
  try {
    const response = await api.get(`/permissions/users/${userId}/permissions`)
    permissions.value = response.data
  } catch (error) {
    console.error('Error loading permissions:', error)
    // Initialize default permissions structure
    const defaultPerms = {}
    resources.forEach(resource => {
      defaultPerms[resource.id] = {
        create: false,
        read: false,
        update: false,
        delete: false
      }
    })
    permissions.value = defaultPerms
  }
}

const savePermissions = async () => {
  savingPermissions.value = true
  try {
    await api.put(`/permissions/users/${selectedUser.value.id}/permissions`, {
      permissions: permissions.value
    })
    toast.success('Permissions saved successfully')
    closePermissionsModal()
  } catch (error) {
    console.error('Error saving permissions:', error)
  } finally {
    savingPermissions.value = false
  }
}

const applyTemplate = () => {
  if (!selectedTemplate.value) return
  
  const templates = {
    admin_full: {
      products: { create: true, read: true, update: true, delete: true },
      blog: { create: true, read: true, update: true, delete: true },
      users: { create: false, read: true, update: false, delete: false },
      partners: { create: true, read: true, update: true, delete: false },
      referrals: { create: true, read: true, update: true, delete: false },
      statistics: { create: false, read: true, update: false, delete: false },
      settings: { create: false, read: false, update: false, delete: false }
    },
    admin_limited: {
      products: { create: true, read: true, update: true, delete: false },
      blog: { create: true, read: true, update: true, delete: false },
      users: { create: false, read: false, update: false, delete: false },
      partners: { create: false, read: true, update: false, delete: false },
      referrals: { create: true, read: true, update: false, delete: false },
      statistics: { create: false, read: true, update: false, delete: false },
      settings: { create: false, read: false, update: false, delete: false }
    },
    partner_full: {
      products: { create: false, read: true, update: false, delete: false },
      blog: { create: false, read: true, update: false, delete: false },
      users: { create: false, read: false, update: false, delete: false },
      partners: { create: false, read: false, update: false, delete: false },
      referrals: { create: true, read: true, update: true, delete: false },
      statistics: { create: false, read: true, update: false, delete: false },
      settings: { create: false, read: false, update: false, delete: false }
    },
    partner_readonly: {
      products: { create: false, read: true, update: false, delete: false },
      blog: { create: false, read: true, update: false, delete: false },
      users: { create: false, read: false, update: false, delete: false },
      partners: { create: false, read: false, update: false, delete: false },
      referrals: { create: false, read: true, update: false, delete: false },
      statistics: { create: false, read: true, update: false, delete: false },
      settings: { create: false, read: false, update: false, delete: false }
    },
    partner_creator: {
      products: { create: false, read: true, update: false, delete: false },
      blog: { create: false, read: true, update: false, delete: false },
      users: { create: false, read: false, update: false, delete: false },
      partners: { create: false, read: false, update: false, delete: false },
      referrals: { create: true, read: true, update: true, delete: true },
      statistics: { create: false, read: true, update: false, delete: false },
      settings: { create: false, read: false, update: false, delete: false }
    }
  }
  
  const template = templates[selectedTemplate.value]
  if (template) {
    permissions.value = template
    toast.success(`Template "${selectedTemplate.value}" applied`)
  }
}

const resetPermissions = async () => {
  try {
    await api.post(`/permissions/users/${selectedUser.value.id}/reset-permissions`)
    await loadUserPermissions(selectedUser.value.id)
    toast.success('Permissions reset to default')
  } catch (error) {
    console.error('Error resetting permissions:', error)
  }
}

const getResourceIcon = (resourceId) => {
  const icons = {
    products: 'fa-box-open',
    blog: 'fa-newspaper',
    users: 'fa-users',
    partners: 'fa-handshake',
    referrals: 'fa-link',
    statistics: 'fa-chart-line',
    settings: 'fa-cog'
  }
  return icons[resourceId] || 'fa-key'
}

const getPermissionLevelClass = (resourceId) => {
  const perms = permissions.value[resourceId]
  if (!perms) return 'level-none'
  if (perms.delete) return 'level-full'
  if (perms.update) return 'level-edit'
  if (perms.create) return 'level-create'
  if (perms.read) return 'level-read'
  return 'level-none'
}

const getPermissionLevelText = (resourceId) => {
  const perms = permissions.value[resourceId]
  if (!perms) return 'No Access'
  if (perms.delete) return 'Full Control'
  if (perms.update) return 'Can Edit'
  if (perms.create) return 'Can Create'
  if (perms.read) return 'View Only'
  return 'No Access'
}

const confirmDelete = (user) => {
  userToDelete.value = user
  showDeleteModal.value = true
}

const deleteUser = async () => {
  try {
    await api.delete(`/admin/users/${userToDelete.value.id}`)
    toast.success('User deleted successfully')
    await fetchUsers()
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting user:', error)
  }
}

const applyFilters = () => {
  // Filters are reactive
}

const debouncedSearch = useDebounceFn(() => {
  applyFilters()
}, 300)

const closeUserModal = () => {
  showUserModal.value = false
  editingUser.value = null
}

const closePermissionsModal = () => {
  showPermissionsModal.value = false
  selectedUser.value = null
  selectedTemplate.value = ''
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  userToDelete.value = null
}

onMounted(() => {
  fetchUsers()
})





defineExpose({
  fetchUsers
})
</script>

<style scoped>
.user-management {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header h2 {
  color: #1e3a8a;
  margin: 0;
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
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  flex: 1;
  min-width: 200px;
}

.search-box i {
  color: #999;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  width: 100%;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.btn-edit, .btn-permissions, .btn-delete {
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 0.25rem;
  transition: all 0.3s;
}

.btn-edit {
  background: #3b82f6;
  color: white;
}

.btn-permissions {
  background: #8b5cf6;
  color: white;
}

.btn-delete {
  background: #dc2626;
  color: white;
}

.btn-edit:hover, .btn-permissions:hover, .btn-delete:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

/* Permissions Editor */
.permissions-editor {
  padding: 1.5rem;
}

.permissions-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
  gap: 1rem;
}

.template-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.template-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
}

.btn-sm {
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline {
  background: transparent;
  border: 1px solid #e5e7eb;
  color: #666;
}

.btn-outline:hover {
  background: #f8fafc;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
}

.permission-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.3s;
}

.permission-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.resource-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.resource-header i {
  font-size: 1.2rem;
  color: #f59e0b;
}

.resource-header h4 {
  margin: 0;
  color: #1e3a8a;
}

.resource-header p {
  margin: 0;
  font-size: 0.7rem;
  color: #666;
}

.permission-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.permission-checkbox {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  font-size: 0.8rem;
}

.permission-checkbox input {
  cursor: pointer;
}

.permission-level {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 600;
  text-align: center;
}

.level-full {
  background: #d1fae5;
  color: #065f46;
}

.level-edit {
  background: #dbeafe;
  color: #1e40af;
}

.level-create {
  background: #fef3c7;
  color: #92400e;
}

.level-read {
  background: #e5e7eb;
  color: #374151;
}

.level-none {
  background: #fee2e2;
  color: #991b1b;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.toggle-slider {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #f59e0b;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.toggle-label {
  font-size: 0.85rem;
  color: #333;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-medium {
  max-width: 500px;
}

.modal-large {
  max-width: 900px;
}

.modal-small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

.modal-form, .modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #f59e0b;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.7rem;
  color: #999;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  margin-top: 1rem;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.warning-text {
  font-size: 0.85rem;
  color: #dc2626;
  margin-top: 0.5rem;
}

.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
  }
  
  .permissions-grid {
    grid-template-columns: 1fr;
  }
  
  .permissions-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .template-selector {
    flex-wrap: wrap;
  }
}
</style>