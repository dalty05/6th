<template>
  <div class="overview">
    <div class="welcome-card">
      <div class="welcome-header">
        <h2>Welcome, {{ user?.full_name || 'Administrator' }}!</h2>
        <p>This is your personalized dashboard. You have access to {{ components.length }} components.</p>
      </div>
      
      <div class="quick-stats">
        <div class="stat">
          <span class="stat-value">{{ components.length }}</span>
          <span class="stat-label">Available Components</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ roleName || 'User' }}</span>
          <span class="stat-label">Your Role</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ user?.email || 'N/A' }}</span>
          <span class="stat-label">Email</span>
        </div>
      </div>
      
      <div class="quick-actions" v-if="components.length > 1">
        <h4>Quick Actions</h4>
        <div class="action-grid">
          <div 
            v-for="comp in quickActions" 
            :key="comp.key"
            class="action-card"
            @click="navigateTo(comp)"
          >
            <i :class="comp.icon || 'fas fa-cube'"></i>
            <span>{{ comp.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'

const router = useRouter()
const user = ref(null)
const components = ref([])
const roleName = ref('')

// Components to show as quick actions (first 6 non-overview components)
const quickActions = computed(() => {
  return components.value
    .filter(c => c.key !== 'overview')
    .slice(0, 6)
})

const navigateTo = (component) => {
  if (component.path) {
    router.push(component.path)
  }
}

onMounted(() => {
  user.value = authService.getUser()
  components.value = permissionService.getDashboardComponents()
  roleName.value = permissionService.getRoleName() || 'User'
})
</script>

<style scoped>
.overview {
  padding: 1rem;
}

.welcome-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.welcome-header h2 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.welcome-header p {
  color: #6b7280;
}

.quick-stats {
  display: flex;
  gap: 2rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a8a;
}

.stat-label {
  font-size: 0.85rem;
  color: #6b7280;
}

.quick-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.quick-actions h4 {
  color: #1e3a8a;
  margin-bottom: 1rem;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.75rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
}

.action-card:hover {
  background: #dbeafe;
  border-color: #1e3a8a;
  transform: translateY(-2px);
}

.action-card i {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.action-card span {
  font-size: 0.85rem;
  color: #374151;
  text-align: center;
}
</style>