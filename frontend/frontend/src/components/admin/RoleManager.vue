<!-- frontend/src/components/admin/RoleManager.vue -->

<template>
  <div class="role-manager">
    <!-- Header -->
    <div class="role-header">
      <div class="header-left">
        <h1><i class="fas fa-user-tag"></i> Role Management</h1>
        <p>Create and manage roles with component-based permissions</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i> Create Role
      </button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-box">
        <span class="stat-number">{{ roles.length }}</span>
        <span class="stat-label">Total Roles</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ systemRoles }}</span>
        <span class="stat-label">System Roles</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ customRoles }}</span>
        <span class="stat-label">Custom Roles</span>
      </div>
    </div>

    <!-- Role List -->
    <div class="role-list">
      <div v-for="role in sortedRoles" :key="role.id" class="role-card">
        <div class="role-card-header">
          <div class="role-info">
            <h3>
              {{ role.name }}
              <span v-if="role.is_system" class="system-badge">System</span>
            </h3>
            <p>{{ role.description || 'No description' }}</p>
          </div>
          <div class="role-stats">
            <span class="user-count">
              <i class="fas fa-users"></i> {{ role.user_count || 0 }} users
            </span>
            <span class="component-count">
              <i class="fas fa-cubes"></i> {{ role.component_count || 0 }} components
            </span>
          </div>
        </div>

        <div class="role-card-body">
          <!-- Assigned Components -->
          <div class="assigned-components">
            <span class="label">Components:</span>
            <div class="component-tags">
              <span 
                v-for="comp in role.components" 
                :key="comp.id"
                class="component-tag"
              >
                <i :class="comp.icon"></i> {{ comp.label }}
              </span>
              <span v-if="!role.components || role.components.length === 0" class="no-components">
                No components assigned
              </span>
            </div>
          </div>
        </div>

        <div class="role-card-footer">
          <button @click="editRole(role)" class="btn-edit">
            <i class="fas fa-edit"></i> Edit
          </button>
          <button 
            v-if="!role.is_system" 
            @click="deleteRole(role.id)" 
            class="btn-delete"
          >
            <i class="fas fa-trash"></i> Delete
          </button>
          <button @click="assignUsers(role)" class="btn-users">
            <i class="fas fa-user-plus"></i> Assign Users
          </button>
        </div>
      </div>

      <div v-if="roles.length === 0" class="no-roles">
        <i class="fas fa-user-tag"></i>
        <h3>No Roles Created</h3>
        <p>Create your first role to start managing permissions</p>
        <button @click="openCreateModal" class="btn-primary">Create Role</button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container large">
        <div class="modal-header">
          <h2>{{ editingRole ? 'Edit Role' : 'Create New Role' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <!-- Role Details -->
          <div class="form-section">
            <h4>Role Details</h4>
            <div class="form-row">
              <div class="form-group">
                <label>Role Name *</label>
                <input 
                  type="text" 
                  v-model="form.name" 
                  placeholder="e.g., Content Manager"
                  required
                >
              </div>
              <div class="form-group">
                <label>Description</label>
                <input 
                  type="text" 
                  v-model="form.description" 
                  placeholder="Brief description of this role"
                >
              </div>
            </div>
          </div>

          <!-- Component Assignment -->
          <div class="form-section">
            <h4>Assign Components</h4>
            <p class="hint">Select the components this role should have access to</p>
            
            <!-- Search & Filter -->
            <div class="component-toolbar">
              <div class="search-box">
                <i class="fas fa-search"></i>
                <input 
                  type="text" 
                  v-model="componentSearch" 
                  placeholder="Search components..."
                >
              </div>
              <div class="toolbar-actions">
                <button @click="selectAllComponents" class="btn-sm btn-outline">
                  Select All
                </button>
                <button @click="deselectAllComponents" class="btn-sm btn-outline">
                  Deselect All
                </button>
              </div>
            </div>

            <!-- Component Grid -->
            <div class="component-grid">
              <div 
                v-for="comp in filteredComponents" 
                :key="comp.id"
                class="component-item"
                :class="{ selected: isComponentSelected(comp.id) }"
                @click="toggleComponent(comp.id)"
              >
                <div class="component-check">
                  <i 
                    class="fas" 
                    :class="isComponentSelected(comp.id) ? 'fa-check-square' : 'fa-square'"
                  ></i>
                </div>
                <div class="component-info">
                  <i :class="comp.icon"></i>
                  <span>{{ comp.label }}</span>
                  <small class="component-key">{{ comp.key }}</small>
                </div>
              </div>
            </div>
            
            <div v-if="filteredComponents.length === 0" class="no-components">
              <i class="fas fa-cubes"></i>
              <p>No components available</p>
            </div>
          </div>

          <!-- Role Templates -->
          <div class="form-section" v-if="!editingRole">
            <h4>Use Template (Optional)</h4>
            <p class="hint">Start with a pre-configured role template</p>
            <div class="template-grid">
              <div 
                v-for="template in roleTemplates" 
                :key="template.name"
                class="template-item"
                :class="{ active: selectedTemplate === template.name }"
                @click="applyTemplate(template)"
              >
                <i :class="template.icon"></i>
                <div>
                  <strong>{{ template.label }}</strong>
                  <span>{{ template.description }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeModal" class="btn-cancel">Cancel</button>
          <button @click="saveRole" class="btn-primary" :disabled="saving">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            {{ saving ? 'Saving...' : (editingRole ? 'Update Role' : 'Create Role') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Assign Users Modal -->
    <div v-if="showAssignModal" class="modal-overlay" @click.self="closeAssignModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Assign Users to {{ selectedRole?.name }}</h2>
          <button class="close-btn" @click="closeAssignModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="userSearch" 
              placeholder="Search users..."
            >
          </div>
          
          <div class="user-list">
            <div 
              v-for="user in filteredUsers" 
              :key="user.id"
              class="user-item"
            >
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  :value="user.id"
                  v-model="selectedUserIds"
                >
                <div class="user-info">
                  <span class="user-name">{{ user.full_name }}</span>
                  <span class="user-email">{{ user.email }}</span>
                  <span class="user-role-badge">{{ user.role }}</span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <span class="selected-count">{{ selectedUserIds.length }} users selected</span>
          <button @click="closeAssignModal" class="btn-cancel">Cancel</button>
          <button @click="assignUsersToRole" class="btn-primary" :disabled="saving">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            {{ saving ? 'Assigning...' : 'Assign Users' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

// State
const roles = ref([])
const allComponents = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showAssignModal = ref(false)
const editingRole = ref(null)
const selectedRole = ref(null)
const selectedUserIds = ref([])
const componentSearch = ref('')
const userSearch = ref('')
const selectedTemplate = ref('')

// Form
const form = ref({
  name: '',
  description: '',
  component_ids: []
})

// Role Templates
const roleTemplates = [
  {
    name: 'tour_manager',
    label: 'Tour Manager',
    description: 'Full tour management access',
    icon: 'fas fa-ticket-alt',
    components: ['overview', 'tours', 'tour-packages', 'tour-calendar', 'tour-payments', 'tour-reports', 'tour-staff', 'profile']
  },
  {
    name: 'partner',
    label: 'Partner',
    description: 'Partner portal access',
    icon: 'fas fa-handshake',
    components: ['overview', 'partners', 'partner-links', 'partner-analytics', 'profile']
  },
  {
    name: 'content_manager',
    label: 'Content Manager',
    description: 'Manage all content',
    icon: 'fas fa-newspaper',
    components: ['overview', 'products', 'blog', 'jobs', 'outlets', 'newsletter', 'contacts', 'profile']
  },
  {
    name: 'hr',
    label: 'HR Manager',
    description: 'Manage jobs and contacts',
    icon: 'fas fa-users',
    components: ['overview', 'jobs', 'contacts', 'profile']
  },
  {
    name: 'custom',
    label: 'Custom',
    description: 'Start with empty role',
    icon: 'fas fa-cog',
    components: []
  }
]

// Computed
const sortedRoles = computed(() => {
  return [...roles.value].sort((a, b) => {
    // System roles first
    if (a.is_system && !b.is_system) return -1
    if (!a.is_system && b.is_system) return 1
    return a.name.localeCompare(b.name)
  })
})

const systemRoles = computed(() => {
  return roles.value.filter(r => r.is_system).length
})

const customRoles = computed(() => {
  return roles.value.filter(r => !r.is_system).length
})

const filteredComponents = computed(() => {
  if (!componentSearch.value) return allComponents.value
  const search = componentSearch.value.toLowerCase()
  return allComponents.value.filter(c => 
    c.label.toLowerCase().includes(search) || 
    c.key.toLowerCase().includes(search)
  )
})

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const search = userSearch.value.toLowerCase()
  return users.value.filter(u => 
    u.full_name.toLowerCase().includes(search) || 
    u.email.toLowerCase().includes(search)
  )
})

// Methods
const loadRoles = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/roles')
    roles.value = response.data || []
  } catch (error) {
    toast.error('Failed to load roles')
  } finally {
    loading.value = false
  }
}

const loadComponents = async () => {
  try {
    const response = await api.get('/admin/permissions/resources')
    allComponents.value = response.data || []
  } catch (error) {
    toast.error('Failed to load components')
  }
}

const loadUsers = async () => {
  try {
    const response = await api.get('/admin/users')
    users.value = response.data || []
  } catch (error) {
    users.value = []
  }
}

const openCreateModal = () => {
  editingRole.value = null
  form.value = {
    name: '',
    description: '',
    component_ids: []
  }
  selectedTemplate.value = ''
  showModal.value = true
}

const editRole = (role) => {
  editingRole.value = role
  form.value = {
    name: role.name,
    description: role.description || '',
    component_ids: role.components?.map(c => c.id) || []
  }
  showModal.value = true
}

const isComponentSelected = (componentId) => {
  return form.value.component_ids.includes(componentId)
}

const toggleComponent = (componentId) => {
  const index = form.value.component_ids.indexOf(componentId)
  if (index > -1) {
    form.value.component_ids.splice(index, 1)
  } else {
    form.value.component_ids.push(componentId)
  }
}

const selectAllComponents = () => {
  form.value.component_ids = allComponents.value.map(c => c.id)
}

const deselectAllComponents = () => {
  form.value.component_ids = []
}

const applyTemplate = (template) => {
  selectedTemplate.value = template.name
  const componentKeys = template.components
  const compIds = allComponents.value
    .filter(c => componentKeys.includes(c.key))
    .map(c => c.id)
  form.value.component_ids = compIds
  
  // Auto-fill name if empty
  if (!form.value.name) {
    form.value.name = template.label
  }
}

const saveRole = async () => {
  if (!form.value.name) {
    toast.error('Role name is required')
    return
  }

  saving.value = true
  try {
    const data = {
      name: form.value.name,
      description: form.value.description,
      component_ids: form.value.component_ids
    }

    if (editingRole.value) {
      await api.put(`/admin/roles/${editingRole.value.id}`, data)
      toast.success('Role updated successfully')
    } else {
      await api.post('/admin/roles', data)
      toast.success('Role created successfully')
    }

    closeModal()
    await loadRoles()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save role')
  } finally {
    saving.value = false
  }
}

const deleteRole = async (roleId) => {
  if (!confirm('Are you sure you want to delete this role? This action cannot be undone.')) {
    return
  }

  try {
    await api.delete(`/admin/roles/${roleId}`)
    toast.success('Role deleted successfully')
    await loadRoles()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to delete role')
  }
}

const assignUsers = (role) => {
  selectedRole.value = role
  selectedUserIds.value = []
  showAssignModal.value = true
}

const assignUsersToRole = async () => {
  if (selectedUserIds.value.length === 0) {
    toast.error('Please select at least one user')
    return
  }

  saving.value = true
  try {
    // Assign each user to the role
    for (const userId of selectedUserIds.value) {
      await api.put(`/admin/users/${userId}`, {
        role_id: selectedRole.value.id
      })
    }
    
    toast.success(`${selectedUserIds.value.length} users assigned to ${selectedRole.value.name}`)
    closeAssignModal()
    await loadRoles()
  } catch (error) {
    toast.error('Failed to assign users')
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editingRole.value = null
  form.value = {
    name: '',
    description: '',
    component_ids: []
  }
  selectedTemplate.value = ''
}

const closeAssignModal = () => {
  showAssignModal.value = false
  selectedRole.value = null
  selectedUserIds.value = []
}

const users = ref([])

onMounted(() => {
  loadRoles()
  loadComponents()
  loadUsers()
})
</script>

<style scoped>
.role-manager {
  padding: 24px;
}

.role-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.role-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.role-header h1 i {
  color: #2563eb;
  margin-right: 8px;
}

.role-header p {
  color: #64748b;
  margin: 0;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-box {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

.role-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.role-card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.role-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.role-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.role-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-info p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.system-badge {
  font-size: 11px;
  background: #dbeafe;
  color: #2563eb;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.role-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #64748b;
}

.role-stats i {
  margin-right: 4px;
}

.role-card-body {
  margin-bottom: 12px;
}

.assigned-components {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.assigned-components .label {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  padding-top: 4px;
}

.component-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.component-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  background: #f1f5f9;
  border-radius: 12px;
  font-size: 12px;
  color: #1a1a2e;
}

.component-tag i {
  font-size: 11px;
  color: #64748b;
}

.no-components {
  font-size: 13px;
  color: #94a3b8;
  font-style: italic;
}

.role-card-footer {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.btn-edit, .btn-delete, .btn-users {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-edit {
  background: #dbeafe;
  color: #2563eb;
}

.btn-edit:hover {
  background: #bfdbfe;
}

.btn-delete {
  background: #fee2e2;
  color: #dc2626;
}

.btn-delete:hover {
  background: #fecaca;
}

.btn-users {
  background: #f1f5f9;
  color: #64748b;
}

.btn-users:hover {
  background: #e2e8f0;
}

.btn-primary {
  padding: 8px 20px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  padding: 8px 20px;
  background: #f1f5f9;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-outline {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-outline:hover {
  background: #f1f5f9;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 13px;
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
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
}

.modal-container.large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #94a3b8;
  cursor: pointer;
  padding: 0 8px;
}

.close-btn:hover {
  color: #1a1a2e;
}

.modal-body {
  padding: 24px;
  max-height: calc(90vh - 140px);
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
}

.form-section {
  margin-bottom: 24px;
}

.form-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.form-section .hint {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 12px 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.form-group input {
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #2563eb;
}

/* Component Toolbar */
.component-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 0 12px;
  flex: 1;
  min-width: 200px;
}

.search-box i {
  color: #94a3b8;
}

.search-box input {
  border: none;
  background: transparent;
  padding: 8px 8px;
  font-size: 14px;
  width: 100%;
}

.search-box input:focus {
  outline: none;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

/* Component Grid */
.component-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding: 4px;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 2px solid #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.component-item:hover {
  border-color: #dbeafe;
  background: #f8fafc;
}

.component-item.selected {
  border-color: #2563eb;
  background: #eff6ff;
}

.component-check {
  font-size: 18px;
  color: #94a3b8;
  flex-shrink: 0;
}

.component-item.selected .component-check {
  color: #2563eb;
}

.component-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.component-info i {
  color: #64748b;
}

.component-key {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}

/* Templates */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.template-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 2px solid #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.template-item:hover {
  border-color: #dbeafe;
  background: #f8fafc;
}

.template-item.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.template-item i {
  font-size: 20px;
  color: #2563eb;
}

.template-item strong {
  display: block;
  font-size: 14px;
  color: #1a1a2e;
}

.template-item span {
  font-size: 12px;
  color: #64748b;
}

/* User List */
.user-list {
  max-height: 300px;
  overflow-y: auto;
}

.user-item {
  padding: 8px 4px;
  border-bottom: 1px solid #f1f5f9;
}

.user-item:last-child {
  border-bottom: none;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.checkbox-label:hover {
  background: #f8fafc;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #2563eb;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.user-name {
  font-weight: 500;
  color: #1a1a2e;
}

.user-email {
  font-size: 13px;
  color: #64748b;
}

.user-role-badge {
  font-size: 11px;
  background: #f1f5f9;
  color: #64748b;
  padding: 2px 10px;
  border-radius: 12px;
}

.selected-count {
  font-size: 14px;
  color: #64748b;
  margin-right: auto;
}

.no-roles, .no-components {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}

.no-roles i, .no-components i {
  font-size: 48px;
  margin-bottom: 16px;
}

.no-roles h3 {
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.no-roles p {
  margin: 0 0 16px 0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .role-card-header {
    flex-direction: column;
  }
  
  .role-stats {
    justify-content: flex-start;
  }
  
  .component-grid {
    grid-template-columns: 1fr;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>