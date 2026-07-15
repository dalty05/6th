<!-- frontend/src/components/admin/AdminSidebar.vue -->

<template>
  <aside class="admin-sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Logo -->
    <div class="sidebar-header">
      <div class="logo-container">
        <img src="/logo.png" alt="Meru Dairy" class="logo-img" />
        <span v-if="!isCollapsed" class="logo-text">Meru Dairy</span>
      </div>
      <button @click="toggleCollapse" class="collapse-btn">
        <i :class="isCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <!-- Group by section -->
      <div v-for="(group, section) in groupedComponents" :key="section" class="nav-section">
        <span v-if="!isCollapsed" class="nav-section-title">{{ section }}</span>
        
        <router-link
          v-for="comp in group"
          :key="comp.key"
          :to="`/admin/dashboard?tab=${comp.key}`"
          class="nav-item"
          :class="{ active: activeComponent === comp.key }"
          @click="navigate(comp.key)"
        >
          <i :class="comp.icon"></i>
          <span v-if="!isCollapsed">{{ comp.label }}</span>
          <span v-if="isCollapsed" class="tooltip">{{ comp.label }}</span>
        </router-link>
      </div>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <div v-if="!isCollapsed" class="user-details">
          <span class="user-name">{{ user?.full_name || 'User' }}</span>
          <span class="user-role">{{ user?.role || 'User' }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  components: {
    type: Array,
    default: () => []
  },
  activeComponent: {
    type: String,
    default: 'overview'
  }
})

const emit = defineEmits(['navigate'])

const route = useRoute()
const isCollapsed = ref(false)
const user = ref(null)

// Group components by section
const groupedComponents = computed(() => {
  const groups = {}
  
  // Sort components by order
  const sorted = [...props.components].sort((a, b) => (a.order || 0) - (b.order || 0))
  
  for (const comp of sorted) {
    const section = comp.section || 'Main'
    if (!groups[section]) groups[section] = []
    groups[section].push(comp)
  }
  
  return groups
})

const navigate = (key) => {
  emit('navigate', key)
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// Watch route changes to update active component
watch(() => route.query.tab, (tab) => {
  if (tab) {
    // Active component will be updated by parent
  }
}, { immediate: true })

// Load user data
import authService from '@/services/auth'
user.value = authService.getUser()

defineExpose({
  isCollapsed
})
</script>

<style scoped>
.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 280px;
  height: 100vh;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 100;
  overflow: hidden;
}

.admin-sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  white-space: nowrap;
}

.collapse-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: #f1f5f9;
  color: #1a1a2e;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.nav-section {
  margin-bottom: 8px;
}

.nav-section-title {
  display: block;
  padding: 8px 20px;
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  color: #64748b;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  position: relative;
}

.nav-item:hover {
  background: #f1f5f9;
  color: #1a1a2e;
}

.nav-item.active {
  background: #eff6ff;
  color: #2563eb;
  border-left-color: #2563eb;
}

.nav-item i {
  width: 20px;
  font-size: 16px;
  text-align: center;
  flex-shrink: 0;
}

.nav-item span {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.collapsed .nav-item {
  justify-content: center;
  padding: 10px;
}

.collapsed .nav-section-title {
  display: none;
}

.tooltip {
  position: absolute;
  left: 60px;
  top: 50%;
  transform: translateY(-50%);
  background: #1a1a2e;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}

.nav-item:hover .tooltip {
  opacity: 1;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  font-size: 32px;
  color: #94a3b8;
}

.user-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  white-space: nowrap;
}

.user-role {
  font-size: 12px;
  color: #94a3b8;
  text-transform: capitalize;
}

.collapsed .user-details {
  display: none;
}

/* Scrollbar */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    width: 280px;
  }
  
  .admin-sidebar.mobile-open {
    transform: translateX(0);
  }
}
</style>