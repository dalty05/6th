<!-- frontend/src/components/admin/RoleManager.vue -->

<template>
  <div class="role-manager">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading roles...</p>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Header -->
      <div class="role-header">
        <div class="header-left">
          <h1><i class="fas fa-user-tag"></i> Role Management</h1>
          <p>Create and manage roles with fine-grained permissions</p>
        </div>
        <button @click="openCreateModal" class="btn-primary">
          <i class="fas fa-plus"></i> Create Role
        </button>
      </div>

      <!-- Stats -->
      <div class="stats-row">
        <div class="stat-box">
          <span class="stat-number">{{ roles?.length || 0 }}</span>
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
            <div class="assigned-components">
              <span class="label">Components:</span>
              <div class="component-tags">
                <span 
                  v-for="rc in getRoleComponents(role.id)" 
                  :key="rc.component_id"
                  class="component-tag"
                  @click="openComponentActions(role, rc)"
                >
                  <i :class="rc.component?.icon"></i> 
                  {{ rc.component?.label || 'Unknown' }}
                  <span class="action-summary">
                    {{ getActionSummary(rc.effective_actions || rc.action_overrides) }}
                  </span>
                  <span class="edit-actions-hint">
                    <i class="fas fa-edit"></i>
                  </span>
                </span>
                <span v-if="!getRoleComponents(role.id) || getRoleComponents(role.id).length === 0" class="no-components">
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
    </template>

    <!-- ============================================================
         CREATE/EDIT ROLE MODAL
         ============================================================ -->
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

          <!-- Component Assignment - Now in its own card/box -->
          <div class="form-section component-assignment-section">
            <div class="component-card">
              <div class="component-card-header">
                <div class="card-header-left">
                  <i class="fas fa-cubes"></i>
                  <h4>Assign Components</h4>
                </div>
                <span class="component-count-badge">
                  {{ form.component_ids.length }} selected
                </span>
              </div>
              
              <p class="hint">Click a component to add it to this role, then configure its actions</p>
              
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
                    <i class="fas fa-check-double"></i> Select All
                  </button>
                  <button @click="deselectAllComponents" class="btn-sm btn-outline">
                    <i class="fas fa-times"></i> Deselect All
                  </button>
                </div>
              </div>

              <!-- Component Grid -->
              <div class="modal-component-grid">
                <template v-for="comp in filteredComponents" :key="comp.id">
                  <div 
                    v-if="comp && comp.id"
                    class="modal-component-item"
                    :class="{ selected: isComponentSelected(comp.id) }"
                  >
                    <!-- Click on check or info to toggle selection -->
                    <div class="modal-component-check" @click="toggleComponent(comp.id)">
                      <i 
                        class="fas" 
                        :class="isComponentSelected(comp.id) ? 'fa-check-square' : 'fa-square'"
                      ></i>
                    </div>
                    
                    <div class="modal-component-info" @click="toggleComponent(comp.id)">
                      <i :class="comp.icon || 'fas fa-puzzle-piece'"></i>
                      <span>{{ comp.label }}</span>
                      <small class="component-key">{{ comp.key }}</small>
                    </div>
                    
                    <!-- Action Toggles -->
                    <div v-if="isComponentSelected(comp.id)" class="modal-component-actions" @click.stop>
                      <div 
                        v-for="action in getAvailableActions(comp.key)" 
                        :key="action"
                        class="action-toggle"
                      >
                        <label class="toggle-label" @click.stop>
                          <span class="action-name">{{ action }}</span>
                          <div class="toggle-switch small">
                            <input 
                              type="checkbox" 
                              :checked="getActionOverride(comp.id, action)"
                              @change="toggleActionOverride(comp.id, action, $event.target.checked)"
                              @click.stop
                            >
                            <span class="toggle-slider"></span>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
              
              <div v-if="filteredComponents.length === 0 && !loading" class="no-components">
                <i class="fas fa-cubes"></i>
                <p>No components available</p>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <span v-if="editingRole" class="selected-count">
            {{ form.component_ids.length }} components selected
          </span>
          <button @click="closeModal" class="btn-cancel">Cancel</button>
          <button @click="saveRole" class="btn-primary" :disabled="saving">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            {{ saving ? 'Saving...' : (editingRole ? 'Update Role' : 'Create Role') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================
         COMPONENT ACTIONS MODAL
         ============================================================ -->
    <div v-if="showActionsModal" class="modal-overlay" @click.self="closeActionsModal">
      <div class="modal-container medium">
        <div class="modal-header">
          <h2>
            <i :class="selectedActionComponent?.icon"></i>
            {{ selectedActionComponent?.label }}
            <small>in {{ selectedActionRole?.name }}</small>
          </h2>
          <button class="close-btn" @click="closeActionsModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="actions-info">
            <p>Configure which actions this role can perform on this component.</p>
            <p class="hint">Uncheck actions to restrict access.</p>
          </div>

          <div class="actions-grid-detailed">
            <div 
              v-for="action in availableActions" 
              :key="action"
              class="action-item-detailed"
            >
              <div class="action-info">
                <span class="action-icon" :class="{ allowed: selectedActionOverrides[action] }">
                  <i :class="getActionIcon(action)"></i>
                </span>
                <div>
                  <div class="action-name-detailed">{{ action }}</div>
                  <div class="action-description">{{ getActionDescription(action) }}</div>
                </div>
              </div>
              <div class="action-toggle-detailed">
                <label class="toggle-label">
                  <span class="action-status" :class="{ allowed: selectedActionOverrides[action] }">
                    {{ selectedActionOverrides[action] ? 'Allowed' : 'Denied' }}
                  </span>
                  <div class="toggle-switch">
                    <input 
                      type="checkbox" 
                      v-model="selectedActionOverrides[action]"
                      @change="saveActionOverrides"
                    >
                    <span class="toggle-slider"></span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="actions-presets">
            <span class="preset-label">Quick Presets:</span>
            <button @click="setActionsPreset('full')" class="preset-btn">Full Access</button>
            <button @click="setActionsPreset('readonly')" class="preset-btn">Read Only</button>
            <button @click="setActionsPreset('none')" class="preset-btn">No Access</button>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeActionsModal" class="btn-cancel">Close</button>
          <button @click="saveActionOverrides" class="btn-primary" :disabled="savingActions">
            {{ savingActions ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================
         ASSIGN USERS MODAL
         ============================================================ -->
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

// ============================================================
// STATE
// ============================================================

const roles = ref([])
const allComponents = ref([])
const roleComponents = ref({})
const loading = ref(true)
const saving = ref(false)
const savingActions = ref(false)

// Modals
const showModal = ref(false)
const showActionsModal = ref(false)
const showAssignModal = ref(false)
const editingRole = ref(null)
const selectedRole = ref(null)
const selectedActionRole = ref(null)
const selectedActionComponent = ref(null)
const selectedActionRC = ref(null)
const selectedUserIds = ref([])

// Form
const form = ref({
  name: '',
  description: '',
  component_ids: []
})

// Component actions
const componentActionOverrides = ref({})
const selectedActionOverrides = ref({})

// Search
const componentSearch = ref('')
const userSearch = ref('')
const users = ref([])

// ============================================================
// COMPUTED
// ============================================================

const sortedRoles = computed(() => {
  if (!roles.value || roles.value.length === 0) return []
  return [...roles.value].sort((a, b) => {
    if (a.is_system && !b.is_system) return -1
    if (!a.is_system && b.is_system) return 1
    return a.name.localeCompare(b.name)
  })
})

const systemRoles = computed(() => {
  if (!roles.value) return 0
  return roles.value.filter(r => r.is_system).length
})

const customRoles = computed(() => {
  if (!roles.value) return 0
  return roles.value.filter(r => !r.is_system).length
})

const filteredComponents = computed(() => {
  let components = allComponents.value || []
  
  if (!Array.isArray(components)) return []
  
  // Filter out invalid components
  components = components.filter(comp => {
    if (!comp) return false
    if (comp.id === undefined || comp.id === null || comp.id === '') return false
    return true
  })
  
  // Apply search filter
  if (componentSearch.value && componentSearch.value.trim()) {
    const search = componentSearch.value.toLowerCase().trim()
    components = components.filter(c => 
      (c.label && c.label.toLowerCase().includes(search)) || 
      (c.key && c.key.toLowerCase().includes(search))
    )
  }
  
  return components
})

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const search = userSearch.value.toLowerCase()
  return users.value.filter(u => 
    u.full_name.toLowerCase().includes(search) || 
    u.email.toLowerCase().includes(search)
  )
})

const availableActions = computed(() => {
  if (!selectedActionComponent.value) return []
  return getAvailableActions(selectedActionComponent.value.key)
})

// ============================================================
// METHODS - COMPONENT ACTIONS
// ============================================================

const getAvailableActions = (componentKey) => {
  if (!componentKey) return ['read']
  
  const actionMap = {
    'overview': ['read'],
    'products': ['create', 'read', 'update', 'delete'],
    'blog': ['create', 'read', 'update', 'delete'],
    'jobs': ['create', 'read', 'update', 'delete'],
    'outlets': ['create', 'read', 'update', 'delete'],
    'statistics': ['read'],
    'contacts': ['read', 'update', 'delete'],
    'newsletter': ['create', 'read', 'update', 'delete'],
    'users': ['create', 'read', 'update', 'delete'],
    'permissions': ['read', 'update'],
    'roles': ['create', 'read', 'update', 'delete'],
    'components': ['create', 'read', 'update', 'delete'],
    'tours': ['create', 'read', 'update', 'delete'],
    'tour-packages': ['create', 'read', 'update', 'delete'],
    'tour-calendar': ['read', 'update'],
    'tour-payments': ['read', 'update'],
    'tour-reports': ['read'],
    'tour-staff': ['read', 'update'],
    'bookings': ['create', 'read', 'update', 'delete', 'approve', 'reject'],
    'tour_settings': ['read', 'update'],
    'partners': ['create', 'read', 'update', 'delete'],
    'partner-links': ['create', 'read', 'update', 'delete'],
    'partner-analytics': ['read'],
    'profile': ['read', 'update'],
    'activities': ['read'],
  }
  return actionMap[componentKey] || ['read']
}

const getActionSummary = (effectiveActions) => {
  if (!effectiveActions) return ''
  if (typeof effectiveActions !== 'object') return ''
  
  const enabled = Object.keys(effectiveActions).filter(k => effectiveActions[k] === true)
  if (enabled.length === 0) return '🚫'
  if (enabled.length === 1) return enabled[0]
  if (enabled.length === 2) return enabled.join(', ')
  return `${enabled.length} actions`
}

const getActionIcon = (action) => {
  const icons = {
    'create': 'fas fa-plus-circle',
    'read': 'fas fa-eye',
    'update': 'fas fa-edit',
    'delete': 'fas fa-trash-alt',
    'approve': 'fas fa-check-circle',
    'reject': 'fas fa-times-circle'
  }
  return icons[action] || 'fas fa-circle'
}

const getActionDescription = (action) => {
  const descriptions = {
    'create': 'Create new items',
    'read': 'View existing items',
    'update': 'Edit existing items',
    'delete': 'Remove items',
    'approve': 'Approve pending items',
    'reject': 'Reject pending items'
  }
  return descriptions[action] || action
}

const getRoleComponents = (roleId) => {
  if (!roleId) return []
  return roleComponents.value[roleId] || []
}

const getActionOverride = (componentId, action) => {
  if (!componentId) return false
  
  const id = String(componentId)
  
  if (!componentActionOverrides.value[id]) {
    const comp = allComponents.value.find(c => String(c.id) === id)
    if (comp) {
      const actions = getAvailableActions(comp.key)
      const overrides = {}
      for (const a of actions) {
        overrides[a] = true
      }
      componentActionOverrides.value[id] = { ...overrides }
    } else {
      componentActionOverrides.value[id] = {}
    }
  }
  
  return componentActionOverrides.value[id]?.[action] ?? false
}

const toggleActionOverride = (componentId, action, value) => {
  if (!componentId) return
  
  const id = String(componentId)
  
  if (!componentActionOverrides.value[id]) {
    const comp = allComponents.value.find(c => String(c.id) === id)
    if (comp) {
      const actions = getAvailableActions(comp.key)
      const overrides = {}
      for (const a of actions) {
        overrides[a] = true
      }
      componentActionOverrides.value[id] = { ...overrides }
    } else {
      componentActionOverrides.value[id] = {}
    }
  }
  
  if (componentActionOverrides.value[id]) {
    componentActionOverrides.value[id] = {
      ...componentActionOverrides.value[id],
      [action]: value
    }
  }
}

const isComponentSelected = (componentId) => {
  if (!componentId) return false
  const id = String(componentId)
  return form.value.component_ids.some(cid => String(cid) === id)
}

const toggleComponent = (componentId) => {
  if (!componentId) {
    console.warn('⚠️ Cannot toggle component: ID is null or undefined')
    return
  }
  
  const id = String(componentId)
  
  // Check if component exists
  const comp = allComponents.value.find(c => String(c.id) === id)
  if (!comp) {
    console.warn('⚠️ Component with ID', id, 'not found')
    return
  }
  
  const index = form.value.component_ids.findIndex(cid => String(cid) === id)
  if (index > -1) {
    form.value.component_ids.splice(index, 1)
    delete componentActionOverrides.value[id]
  } else {
    form.value.component_ids.push(id)
    const actions = getAvailableActions(comp.key)
    const overrides = {}
    for (const a of actions) {
      overrides[a] = true
    }
    componentActionOverrides.value[id] = { ...overrides }
  }
}

const selectAllComponents = () => {
  form.value.component_ids = allComponents.value.map(c => String(c.id))
  for (const comp of allComponents.value) {
    const id = String(comp.id)
    const actions = getAvailableActions(comp.key)
    const overrides = {}
    for (const a of actions) {
      overrides[a] = true
    }
    componentActionOverrides.value[id] = { ...overrides }
  }
}

const deselectAllComponents = () => {
  form.value.component_ids = []
  componentActionOverrides.value = {}
}

// ============================================================
// METHODS - LOAD DATA
// ============================================================

const loadRoles = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/roles')
    roles.value = response.data || []
    for (const role of roles.value) {
      await loadRoleComponents(role.id)
    }
  } catch (error) {
    console.error('Error loading roles:', error)
    toast.error('Failed to load roles')
    roles.value = []
  } finally {
    loading.value = false
  }
}

const loadRoleComponents = async (roleId) => {
  try {
    const response = await api.get(`/admin/roles/${roleId}/components`)
    const components = response.data.components || []
    roleComponents.value[roleId] = components.filter(rc => rc && rc.component_id)
  } catch (error) {
    console.error(`Error loading components for role ${roleId}:`, error)
    roleComponents.value[roleId] = []
  }
}

const loadComponents = async () => {
  try {
    const response = await api.get('/admin/permissions/resources')
    console.log('📦 Components response:', response.data)

    let componentsData = []

    if (Array.isArray(response.data)) {
      componentsData = response.data
    } else if (response.data && Array.isArray(response.data.data)) {
      componentsData = response.data.data
    } else if (response.data && Array.isArray(response.data.components)) {
      componentsData = response.data.components
    } else {
      console.warn('⚠️ Unexpected components response structure:', response.data)
      componentsData = []
    }

    // Transform the data to match what the frontend expects
    const validComponents = componentsData
      .filter(comp => comp && comp.name)
      .map((comp) => ({
        id: comp.name,  // Use name as id
        key: comp.name,
        label: comp.label || comp.name || 'Unknown',
        icon: getComponentIcon(comp.name),
        actions: comp.actions || ['read']
      }))

    console.log('✅ Transformed components:', validComponents)
    allComponents.value = validComponents
    
    if (validComponents.length === 0) {
      toast.warning('No components found. Please check your permissions configuration.')
    }
  } catch (error) {
    console.error('Error loading components:', error)
    toast.error('Failed to load components')
    allComponents.value = []
  }
}

// Helper function to map component names to icons
const getComponentIcon = (componentName) => {
  const iconMap = {
    'overview': 'fas fa-home',
    'products': 'fas fa-box',
    'blog': 'fas fa-blog',
    'jobs': 'fas fa-briefcase',
    'outlets': 'fas fa-store',
    'statistics': 'fas fa-chart-bar',
    'contacts': 'fas fa-address-book',
    'newsletter': 'fas fa-envelope',
    'users': 'fas fa-users',
    'permissions': 'fas fa-lock',
    'roles': 'fas fa-user-tag',
    'components': 'fas fa-cubes',
    'tours': 'fas fa-map-marked-alt',
    'tour-packages': 'fas fa-boxes',
    'tour-calendar': 'fas fa-calendar-alt',
    'tour-payments': 'fas fa-credit-card',
    'tour-reports': 'fas fa-file-alt',
    'tour-staff': 'fas fa-user-tie',
    'bookings': 'fas fa-ticket-alt',
    'tour_settings': 'fas fa-cog',
    'partners': 'fas fa-handshake',
    'partner-links': 'fas fa-link',
    'partner-analytics': 'fas fa-chart-line',
    'profile': 'fas fa-user',
    'activities': 'fas fa-activity'
  }
  return iconMap[componentName] || 'fas fa-puzzle-piece'
}

const loadUsers = async () => {
  try {
    const response = await api.get('/admin/users')
    users.value = response.data || []
  } catch (error) {
    console.error('Error loading users:', error)
    users.value = []
  }
}

// ============================================================
// METHODS - ROLE CRUD
// ============================================================

const openCreateModal = () => {
  // Ensure components are loaded
  if (allComponents.value.length === 0) {
    loadComponents()
  }
  
  editingRole.value = null
  form.value = { name: '', description: '', component_ids: [] }
  componentActionOverrides.value = {}
  showModal.value = true
}

const editRole = (role) => {
  if (!role || !role.id) {
    console.error('Invalid role')
    return
  }
  
  // Ensure components are loaded
  if (allComponents.value.length === 0) {
    loadComponents()
  }
  
  console.log('📝 Editing role:', role.name)
  editingRole.value = role
  
  const freshOverrides = {}
  const componentIds = []
  const rcList = getRoleComponents(role.id)
  
  for (const rc of rcList) {
    if (!rc || !rc.component_id) continue
    
    const compId = String(rc.component_id)
    componentIds.push(compId)
    
    const overrides = rc.action_overrides || {}
    const comp = allComponents.value.find(c => String(c.id) === compId)
    if (comp) {
      const actions = getAvailableActions(comp.key)
      for (const action of actions) {
        if (!(action in overrides)) {
          overrides[action] = true
        }
      }
    }
    freshOverrides[compId] = { ...overrides }
  }
  
  form.value = {
    name: role.name,
    description: role.description || '',
    component_ids: componentIds
  }
  
  componentActionOverrides.value = freshOverrides
  
  console.log('✅ Form ready:', {
    component_ids: form.value.component_ids,
    overrides: componentActionOverrides.value
  })
  
  showModal.value = true
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
      
      for (const compId of form.value.component_ids) {
        const overrides = componentActionOverrides.value[String(compId)] || {}
        if (Object.keys(overrides).length === 0) continue
        
        try {
          await api.put(`/admin/roles/${editingRole.value.id}/components/${compId}`, {
            action_overrides: overrides
          })
        } catch (err) {
          console.warn(`Failed to save overrides for component ${compId}:`, err)
        }
      }
      
      toast.success('Role updated successfully')
    } else {
      await api.post('/admin/roles', data)
      toast.success('Role created successfully')
    }

    closeModal()
    await loadRoles()
  } catch (error) {
    console.error('Error saving role:', error)
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
    console.error('Error deleting role:', error)
    toast.error(error.response?.data?.error || 'Failed to delete role')
  }
}

// ============================================================
// METHODS - COMPONENT ACTIONS MODAL
// ============================================================

const openComponentActions = (role, roleComponent) => {
  if (!role || !role.id) {
    console.error('Invalid role')
    return
  }
  
  if (!roleComponent || !roleComponent.component_id) {
    console.error('Invalid roleComponent:', roleComponent)
    return
  }
  
  selectedActionRole.value = role
  selectedActionComponent.value = roleComponent.component
  selectedActionRC.value = roleComponent
  
  const existingOverrides = roleComponent.action_overrides || {}
  const freshOverrides = { ...existingOverrides }
  const actions = getAvailableActions(roleComponent.component?.key || '')
  
  for (const action of actions) {
    if (!(action in freshOverrides)) {
      freshOverrides[action] = true
    }
  }
  
  selectedActionOverrides.value = freshOverrides
  showActionsModal.value = true
}

const saveActionOverrides = async () => {
  if (!selectedActionRC.value || !selectedActionRole.value) {
    toast.error('Missing role or component data')
    return
  }
  
  if (!selectedActionRC.value.component_id) {
    toast.error('Invalid component ID')
    return
  }
  
  savingActions.value = true
  try {
    await api.put(
      `/admin/roles/${selectedActionRole.value.id}/components/${selectedActionRC.value.component_id}`,
      { action_overrides: selectedActionOverrides.value }
    )
    
    toast.success('Action permissions updated')
    
    const rcList = roleComponents.value[selectedActionRole.value.id]
    if (rcList) {
      const rc = rcList.find(r => r.component_id === selectedActionRC.value.component_id)
      if (rc) {
        rc.action_overrides = { ...selectedActionOverrides.value }
        rc.effective_actions = { ...selectedActionOverrides.value }
      }
    }
    closeActionsModal()
  } catch (error) {
    console.error('Error saving action overrides:', error)
    toast.error(error.response?.data?.error || 'Failed to update action permissions')
  } finally {
    savingActions.value = false
  }
}

const setActionsPreset = (preset) => {
  const actions = getAvailableActions(selectedActionComponent.value?.key || '')
  const freshOverrides = {}
  
  if (preset === 'full') {
    for (const action of actions) {
      freshOverrides[action] = true
    }
  } else if (preset === 'readonly') {
    for (const action of actions) {
      freshOverrides[action] = (action === 'read')
    }
  } else if (preset === 'none') {
    for (const action of actions) {
      freshOverrides[action] = false
    }
  }
  
  selectedActionOverrides.value = freshOverrides
}

const closeActionsModal = () => {
  showActionsModal.value = false
  selectedActionRole.value = null
  selectedActionComponent.value = null
  selectedActionRC.value = null
  selectedActionOverrides.value = {}
}

// ============================================================
// METHODS - USER ASSIGNMENT
// ============================================================

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
    for (const userId of selectedUserIds.value) {
      await api.put(`/admin/users/${userId}`, { role_id: selectedRole.value.id })
    }
    toast.success(`${selectedUserIds.value.length} users assigned to ${selectedRole.value.name}`)
    closeAssignModal()
    await loadRoles()
  } catch (error) {
    console.error('Error assigning users:', error)
    toast.error('Failed to assign users')
  } finally {
    saving.value = false
  }
}

// ============================================================
// MODAL CONTROLS
// ============================================================

const closeModal = () => {
  showModal.value = false
  editingRole.value = null
  form.value = { name: '', description: '', component_ids: [] }
  componentActionOverrides.value = {}
}

const closeAssignModal = () => {
  showAssignModal.value = false
  selectedRole.value = null
  selectedUserIds.value = []
}

// ============================================================
// LIFECYCLE
// ============================================================

onMounted(() => {
  loadRoles()
  loadComponents()
  loadUsers()
})
</script>

<style scoped>
/* ============================================================
   MAIN CONTAINER
   ============================================================ */
.role-manager {
  padding: 24px;
}

/* ============================================================
   LOADING STATE
   ============================================================ */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ============================================================
   HEADER
   ============================================================ */
.role-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.header-left h1 i {
  color: #2563eb;
  margin-right: 8px;
}

.header-left p {
  color: #64748b;
  margin: 0;
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

/* ============================================================
   STATS ROW
   ============================================================ */
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

/* ============================================================
   ROLE LIST
   ============================================================ */
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
  cursor: pointer;
  transition: all 0.2s;
}

.component-tag:hover {
  background: #e2e8f0;
}

.component-tag i {
  font-size: 11px;
  color: #64748b;
}

.action-summary {
  font-size: 10px;
  color: #64748b;
  background: #e2e8f0;
  padding: 1px 6px;
  border-radius: 10px;
  margin-left: 4px;
}

.edit-actions-hint {
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 10px;
  color: #94a3b8;
}

.component-tag:hover .edit-actions-hint {
  opacity: 1;
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

.btn-sm {
  padding: 4px 12px;
  font-size: 13px;
}

.btn-outline {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-outline:hover {
  background: #f1f5f9;
}

/* ============================================================
   MODAL STYLES
   ============================================================ */
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

.modal-container.medium {
  max-width: 600px;
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

.modal-header h2 small {
  font-size: 14px;
  color: #64748b;
  font-weight: 400;
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

.selected-count {
  font-size: 14px;
  color: #64748b;
  margin-right: auto;
}

/* ============================================================
   FORM STYLES
   ============================================================ */
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

/* ============================================================
   COMPONENT ASSIGNMENT CARD (MODAL)
   ============================================================ */
.component-assignment-section {
  margin-top: 8px;
}

.component-card {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.component-card:hover {
  border-color: #cbd5e1;
}

.component-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header-left i {
  color: #2563eb;
  font-size: 20px;
}

.card-header-left h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.component-count-badge {
  background: #2563eb;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.component-card .hint {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 16px 0;
  padding-left: 34px;
}

.component-card .component-toolbar {
  background: white;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid #e2e8f0;
}

.component-card .modal-component-grid {
  background: white;
  border-radius: 8px;
  padding: 8px;
  border: 1px solid #e2e8f0;
  max-height: 350px;
  overflow-y: auto;
}

.component-card .no-components {
  background: white;
  border-radius: 8px;
  padding: 30px;
  border: 1px solid #e2e8f0;
}

/* Modal Component Grid Items */
.modal-component-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 8px;
  padding: 4px;
}

.modal-component-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 2px solid #f1f5f9;
  border-radius: 8px;
  transition: all 0.2s;
  flex-wrap: wrap;
  cursor: pointer;
}

.modal-component-item:hover {
  border-color: #dbeafe;
  background: #f8fafc;
}

.modal-component-item.selected {
  border-color: #2563eb;
  background: #eff6ff;
}

.modal-component-check {
  font-size: 18px;
  color: #94a3b8;
  flex-shrink: 0;
  cursor: pointer;
}

.modal-component-item.selected .modal-component-check {
  color: #2563eb;
}

.modal-component-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  flex: 1;
  cursor: pointer;
}

.modal-component-info i {
  color: #64748b;
}

.modal-component-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
  flex-wrap: wrap;
  padding: 4px 8px;
  background: #f8fafc;
  border-radius: 6px;
  cursor: default;
}

/* Toolbar inside modal */
.component-card .component-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.component-card .search-box {
  display: flex;
  align-items: center;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 0 12px;
  flex: 1;
  min-width: 200px;
}

.component-card .search-box i {
  color: #94a3b8;
}

.component-card .search-box input {
  border: none;
  background: transparent;
  padding: 8px 8px;
  font-size: 14px;
  width: 100%;
}

.component-card .search-box input:focus {
  outline: none;
}

.component-card .toolbar-actions {
  display: flex;
  gap: 8px;
}

/* Action Toggles (shared) */
.action-toggle {
  display: flex;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 11px;
}

.action-name {
  text-transform: capitalize;
  font-size: 10px;
  color: #64748b;
  min-width: 14px;
}

.toggle-switch {
  position: relative;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}

.toggle-switch.small {
  width: 28px;
  height: 16px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #cbd5e1;
  transition: 0.3s;
  border-radius: 22px;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
  background: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle-switch.small .toggle-slider::before {
  height: 10px;
  width: 10px;
  left: 3px;
  bottom: 3px;
}

.toggle-switch input:checked + .toggle-slider {
  background: #2563eb;
}

.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(18px);
}

.toggle-switch.small input:checked + .toggle-slider::before {
  transform: translateX(12px);
}

/* ============================================================
   ACTIONS MODAL DETAILED
   ============================================================ */
.actions-info {
  margin-bottom: 16px;
}

.actions-info p {
  margin: 0 0 4px 0;
  color: #1a1a2e;
}

.actions-info .hint {
  color: #64748b;
  font-size: 13px;
}

.actions-grid-detailed {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0;
}

.action-item-detailed {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #e2e8f0;
  transition: all 0.2s;
}

.action-item-detailed:hover {
  background: #f1f5f9;
}

.action-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #94a3b8;
  background: #e2e8f0;
}

.action-icon.allowed {
  color: #16a34a;
  background: #dcfce7;
}

.action-name-detailed {
  font-weight: 600;
  color: #1a1a2e;
  text-transform: capitalize;
}

.action-description {
  font-size: 12px;
  color: #64748b;
}

.action-toggle-detailed {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-status {
  font-size: 12px;
  font-weight: 500;
  min-width: 50px;
  text-align: right;
}

.action-status.allowed {
  color: #16a34a;
}

.action-status:not(.allowed) {
  color: #dc2626;
}

/* ============================================================
   PRESETS
   ============================================================ */
.actions-presets {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid #f1f5f9;
  flex-wrap: wrap;
}

.preset-label {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.preset-btn {
  padding: 4px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}

/* ============================================================
   USER LIST
   ============================================================ */
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

/* ============================================================
   EMPTY STATES
   ============================================================ */
.no-roles,
.no-components {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}

.no-roles i,
.no-components i {
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

/* ============================================================
   RESPONSIVE
   ============================================================ */
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
  
  .modal-component-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-component-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .modal-component-actions {
    margin-left: 36px;
    margin-top: 4px;
    width: 100%;
  }
  
  .actions-grid-detailed {
    gap: 4px;
  }
  
  .action-item-detailed {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .action-toggle-detailed {
    width: 100%;
    justify-content: space-between;
  }
  
  .component-card .component-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .component-card .toolbar-actions {
    justify-content: flex-end;
  }
  
  .role-card-footer {
    flex-wrap: wrap;
  }
  
  .component-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .component-card .hint {
    padding-left: 0;
  }
}
</style>