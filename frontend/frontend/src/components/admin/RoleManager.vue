<template>
  <div class="role-manager">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2><i class="fas fa-user-tag"></i> Role Management</h2>
        <p>Create and manage roles with specific dashboard components</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i> Create Role
      </button>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-user-tag"></i></div>
        <div class="stat-info">
          <h3>{{ roles.length }}</h3>
          <p>Total Roles</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-check-circle"></i></div>
        <div class="stat-info">
          <h3>{{ activeRoles }}</h3>
          <p>Active Roles</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-cubes"></i></div>
        <div class="stat-info">
          <h3>{{ totalComponents }}</h3>
          <p>Available Components</p>
        </div>
      </div>
    </div>

    <!-- Roles Grid -->
    <div class="roles-grid">
      <div v-for="role in roles" :key="role.id" class="role-card">
        <div class="role-header">
          <div>
            <h3>{{ role.name }}</h3>
            <span class="role-badge" :class="role.is_system ? 'system' : 'custom'">
              {{ role.is_system ? 'System' : 'Custom' }}
            </span>
          </div>
          <span class="user-count">{{ role.user_count || 0 }} users</span>
        </div>
        
        <p class="role-description">{{ role.description || 'No description' }}</p>
        
        <div class="component-list">
          <span class="component-count">{{ role.component_count || 0 }} components</span>
          <div class="component-tags">
            <span v-for="comp in role.components" :key="comp.id" class="component-tag">
              <i :class="comp.icon"></i> {{ comp.label }}
            </span>
          </div>
        </div>
        
        <div class="role-actions">
          <button @click="editRole(role)" class="btn-icon edit" title="Edit Role">
            <i class="fas fa-edit"></i>
          </button>
          <button 
            @click="manageComponents(role)" 
            class="btn-icon components" 
            :disabled="role.is_system"
            :title="role.is_system ? 'Cannot modify system role' : 'Manage Components'"
          >
            <i class="fas fa-cubes"></i>
          </button>
          <button @click="viewUsers(role)" class="btn-icon users" title="View Users">
            <i class="fas fa-users"></i>
          </button>
          <button 
            @click="deleteRole(role)" 
            class="btn-icon delete" 
            :disabled="role.is_system"
            title="Delete Role"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Role Modal -->
    <div v-if="showRoleModal" class="modal-overlay" @click.self="closeRoleModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Role' : 'Create New Role' }}</h3>
          <button @click="closeRoleModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveRole">
            <div class="form-group">
              <label>Role Name *</label>
              <input 
                type="text" 
                v-model="roleForm.name" 
                placeholder="e.g., Content Manager"
                required
                :disabled="isEditing && roleForm.is_system"
              >
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="roleForm.description" placeholder="Describe this role's purpose"></textarea>
            </div>
            <div class="checkbox-group">
              <label class="checkbox">
                <input type="checkbox" v-model="roleForm.is_active"> Active
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeRoleModal" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ isEditing ? 'Update' : 'Create' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Component Assignment Modal -->
    <div v-if="showComponentModal" class="modal-overlay" @click.self="closeComponentModal">
      <div class="modal-container modal-lg">
        <div class="modal-header">
          <h3>Assign Components to {{ selectedRole?.name }}</h3>
          <button @click="closeComponentModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <p class="help-text">Select the components that users with this role should see in their dashboard.</p>
          
          <div class="component-grid">
            <div 
              v-for="comp in availableComponents" 
              :key="comp.id"
              class="component-select-item"
              :class="{ selected: selectedComponentIds.includes(comp.id) }"
              @click="toggleComponent(comp.id)"
            >
              <div class="component-icon">
                <i :class="comp.icon || 'fas fa-cube'"></i>
              </div>
              <div class="component-info">
                <h4>{{ comp.label }}</h4>
                <p>{{ comp.description || comp.key }}</p>
              </div>
              <div class="component-check">
                <i v-if="selectedComponentIds.includes(comp.id)" class="fas fa-check-circle"></i>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button @click="closeComponentModal" class="btn-cancel">Cancel</button>
            <button @click="saveComponentAssignments" class="btn-submit">Save Assignments</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Users List Modal -->
    <div v-if="showUsersModal" class="modal-overlay" @click.self="closeUsersModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Users with {{ selectedRole?.name }} Role</h3>
          <button @click="closeUsersModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="roleUsers.length === 0" class="empty-state">
            <i class="fas fa-users"></i>
            <p>No users assigned to this role yet</p>
          </div>
          <div v-else class="user-list">
            <div v-for="user in roleUsers" :key="user.id" class="user-item">
              <div class="user-avatar">
                <i class="fas fa-user-circle"></i>
              </div>
              <div class="user-info">
                <span class="user-name">{{ user.full_name }}</span>
                <span class="user-email">{{ user.email }}</span>
              </div>
              <button @click="removeUserFromRole(user)" class="btn-remove" title="Remove from role">
                <i class="fas fa-times"></i>
              </button>
            </div>
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

// ========== STATE ==========
const roles = ref([])
const availableComponents = ref([])
const selectedRole = ref(null)
const selectedComponentIds = ref([])
const roleUsers = ref([])

const showRoleModal = ref(false)
const showComponentModal = ref(false)
const showUsersModal = ref(false)
const isEditing = ref(false)
const loading = ref(false)

const roleForm = ref({
  id: null,
  name: '',
  description: '',
  is_active: true,
  is_system: false
})

// ========== COMPUTED ==========
const activeRoles = computed(() => roles.value.filter(r => r.is_active).length)
const totalComponents = computed(() => availableComponents.value.length)

// ========== LOAD DATA ==========
const loadRoles = async () => {
  try {
    const response = await api.get('/roles')
    roles.value = response.data
    console.log('✅ Roles loaded:', roles.value.length)
  } catch (error) {
    console.error('Error loading roles:', error)
    toast.error('Failed to load roles')
  }
}

const loadComponents = async () => {
  try {
    const response = await api.get('/components')
    availableComponents.value = response.data
    console.log('✅ Components loaded:', availableComponents.value.length)
  } catch (error) {
    console.error('Error loading components:', error)
    toast.error('Failed to load components')
  }
}

// ========== ROLE CRUD ==========
const openCreateModal = () => {
  isEditing.value = false
  roleForm.value = {
    id: null,
    name: '',
    description: '',
    is_active: true,
    is_system: false
  }
  showRoleModal.value = true
}

const editRole = (role) => {
  isEditing.value = true
  roleForm.value = {
    id: role.id,
    name: role.name,
    description: role.description || '',
    is_active: role.is_active,
    is_system: role.is_system
  }
  showRoleModal.value = true
}

const saveRole = async () => {
  if (!roleForm.value.name.trim()) {
    toast.error('Role name is required')
    return
  }
  
  loading.value = true
  try {
    if (isEditing.value) {
      await api.put(`/roles/${roleForm.value.id}`, roleForm.value)
      toast.success('Role updated successfully')
    } else {
      await api.post('/roles', roleForm.value)
      toast.success('Role created successfully')
    }
    closeRoleModal()
    await loadRoles()
  } catch (error) {
    console.error('Error saving role:', error)
    toast.error(error.response?.data?.error || 'Failed to save role')
  } finally {
    loading.value = false
  }
}

const deleteRole = async (role) => {
  if (role.is_system) {
    toast.error('Cannot delete system role')
    return
  }
  
  if (!confirm(`Are you sure you want to delete the "${role.name}" role?`)) return
  
  try {
    await api.delete(`/roles/${role.id}`)
    toast.success('Role deleted successfully')
    await loadRoles()
  } catch (error) {
    console.error('Error deleting role:', error)
    toast.error(error.response?.data?.error || 'Failed to delete role')
  }
}

const closeRoleModal = () => {
  showRoleModal.value = false
  isEditing.value = false
}

// ========== COMPONENT ASSIGNMENT ==========
const manageComponents = async (role) => {

  if (role.is_system) {
    toast.warning('System roles cannot be modified')
    return
  }
  
  selectedRole.value = role
  
  selectedComponentIds.value = role.components?.map(c => c.id) || []
  console.log('📋 Current component IDs for role:', selectedComponentIds.value)
  showComponentModal.value = true
}

const toggleComponent = (componentId) => {
  const index = selectedComponentIds.value.indexOf(componentId)
  if (index > -1) {
    selectedComponentIds.value.splice(index, 1)
  } else {
    selectedComponentIds.value.push(componentId)
  }
  console.log('📋 Selected component IDs:', selectedComponentIds.value)
}

const saveComponentAssignments = async () => {
  if (!selectedRole.value) {
    toast.error('No role selected')
    return
  }
  
  // ✅ Check again before saving
  if (selectedRole.value.is_system) {
    toast.error('Cannot modify system role')
    closeComponentModal()
    return
  }
  
  try {
    // ✅ Convert proxy array to regular array
    const componentIds = Array.isArray(selectedComponentIds.value) 
      ? selectedComponentIds.value 
      : [...selectedComponentIds.value]
    
    const payload = {
      component_ids: componentIds
    }
    
    console.log('📤 Assigning components to role:', selectedRole.value.id)
    console.log('📤 Component IDs:', payload)
    
    await api.put(`/roles/${selectedRole.value.id}/components`, payload)
    toast.success('Components assigned successfully')
    closeComponentModal()
    await loadRoles()
  } catch (error) {
    console.error('Error assigning components:', error)
    console.error('Response:', error.response?.data)
    
    // ✅ Better error message
    const errorMsg = error.response?.data?.error || 'Failed to assign components'
    toast.error(errorMsg)
  }
}

const closeComponentModal = () => {
  showComponentModal.value = false
  selectedRole.value = null
  selectedComponentIds.value = []
}

// ========== USER MANAGEMENT ==========
const viewUsers = async (role) => {
  selectedRole.value = role
  try {
    const response = await api.get(`/roles/${role.id}/users`)
    roleUsers.value = response.data
    showUsersModal.value = true
  } catch (error) {
    console.error('Error loading users:', error)
    toast.error('Failed to load users')
  }
}

const removeUserFromRole = async (user) => {
  if (!confirm(`Remove ${user.full_name} from ${selectedRole.value.name}?`)) return
  
  try {
    await api.put(`/users/${user.id}/role`, { role_id: null })
    toast.success('User removed from role')
    await viewUsers(selectedRole.value)
  } catch (error) {
    console.error('Error removing user:', error)
    toast.error('Failed to remove user')
  }
}

const closeUsersModal = () => {
  showUsersModal.value = false
  selectedRole.value = null
  roleUsers.value = []
}

// ========== LIFECYCLE ==========
onMounted(() => {
  loadRoles()
  loadComponents()
})
</script>





<style scoped>


.role-card.system-role {
  border-color: #d1d5db;
  background: #f9fafb;
}

.role-card.system-role .role-header h3 {
  color: #6b7280;
}

.btn-icon.components.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f3f4f6;
  color: #9ca3af;
}

.btn-icon.components.disabled:hover {
  background: #f3f4f6;
}


.role-manager {
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h2 {
  margin: 0;
  color: #1e3a8a;
}

.page-header p {
  margin: 0;
  color: #6b7280;
}

.btn-primary {
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

.btn-primary:hover {
  background: #1a2e6b;
  transform: translateY(-1px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.stat-icon.blue { background: #1e3a8a; }
.stat-icon.green { background: #059669; }
.stat-icon.purple { background: #7c3aed; }

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

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.role-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
  transition: all 0.3s;
}

.role-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.role-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.role-header h3 {
  margin: 0;
  color: #1e3a8a;
}

.role-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-weight: 500;
}

.role-badge.system {
  background: #dbeafe;
  color: #1e3a8a;
}

.role-badge.custom {
  background: #fef3c7;
  color: #92400e;
}

.user-count {
  font-size: 0.85rem;
  color: #6b7280;
}

.role-description {
  color: #6b7280;
  margin-bottom: 1rem;
}

.component-list {
  margin-bottom: 1rem;
}

.component-count {
  font-size: 0.85rem;
  color: #6b7280;
  display: block;
  margin-bottom: 0.5rem;
}

.component-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.component-tag {
  background: #f3f4f6;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: #374151;
}

.role-actions {
  display: flex;
  gap: 0.5rem;
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon.edit {
  background: #dbeafe;
  color: #1e3a8a;
}

.btn-icon.edit:hover {
  background: #bfdbfe;
}

.btn-icon.components {
  background: #fef3c7;
  color: #92400e;
}

.btn-icon.components:hover {
  background: #fde68a;
}

.btn-icon.users {
  background: #d1fae5;
  color: #065f46;
}

.btn-icon.users:hover {
  background: #a7f3d0;
}

.btn-icon.delete {
  background: #fee2e2;
  color: #991b1b;
}

.btn-icon.delete:hover:not(:disabled) {
  background: #fecaca;
}

.btn-icon.delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-lg {
  max-width: 700px;
  width: 95%;
}

.modal-container {
  max-width: 500px;
  width: 95%;
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
}

.modal-header h3 {
  margin: 0;
  color: #1e3a8a;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.form-group input:disabled {
  background: #f3f4f6;
}

.checkbox-group {
  margin: 1rem 0;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  background: #e5e7eb;
  color: #374151;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-submit {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.component-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0;
}

.component-select-item {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.component-select-item:hover {
  border-color: #1e3a8a;
}

.component-select-item.selected {
  border-color: #1e3a8a;
  background: #dbeafe;
}

.component-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #1e3a8a;
  flex-shrink: 0;
}

.component-info {
  flex: 1;
}

.component-info h4 {
  margin: 0;
  font-size: 0.9rem;
  color: #1e293b;
}

.component-info p {
  margin: 0;
  font-size: 0.75rem;
  color: #6b7280;
}

.component-check {
  color: #1e3a8a;
  font-size: 1.2rem;
}

.help-text {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 8px;
  background: #f8fafc;
}

.user-avatar {
  font-size: 1.5rem;
  color: #1e3a8a;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  display: block;
}

.user-email {
  font-size: 0.85rem;
  color: #6b7280;
}

.btn-remove {
  background: #fee2e2;
  border: none;
  color: #991b1b;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-remove:hover {
  background: #fecaca;
}

@media (max-width: 768px) {
  .roles-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .component-grid {
    grid-template-columns: 1fr;
  }
}
</style>