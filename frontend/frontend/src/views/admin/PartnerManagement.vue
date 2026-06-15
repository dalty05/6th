<template>
  <div class="partner-management">
    <div class="header">
      <h2>Partner Management</h2>
      <button @click="showCreateModal = true" class="btn-primary">
        <i class="fas fa-user-plus"></i> Add Partner
      </button>
    </div>
    
    <DataTable 
      :data="partners" 
      :columns="columns" 
      :loading="loading"
      :search-keys="['full_name', 'email', 'referral_code']"
      search-placeholder="Search partners..."
    >
      <template #actions="{ row }">
        <button @click="viewPartnerStats(row)" class="btn-view">
          <i class="fas fa-chart-line"></i> Stats
        </button>
        <button @click="editPartner(row)" class="btn-edit">
          <i class="fas fa-edit"></i> Edit
        </button>
        <button @click="regenerateCode(row)" class="btn-refresh">
          <i class="fas fa-sync-alt"></i> New Code
        </button>
      </template>
    </DataTable>
    
    <div class="coming-soon-notice">
      <i class="fas fa-info-circle"></i>
      <p>Partner management with referral analytics, commission tracking, and performance reports coming soon!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from './DataTable.vue'
import axios from 'axios'

const partners = ref([])
const loading = ref(false)
const showCreateModal = ref(false)

const columns = [
  { key: 'full_name', label: 'Partner Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'referral_code', label: 'Referral Code', sortable: true },
  { key: 'total_clicks', label: 'Clicks', sortable: true, width: '100px' },
  { key: 'total_conversions', label: 'Conversions', sortable: true, width: '120px' },
  { key: 'created_at', label: 'Joined', type: 'date', sortable: true, width: '120px' }
]

const fetchPartners = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/users?role=partner')
    partners.value = response.data.filter(u => u.role === 'partner')
  } catch (error) {
    console.error('Error fetching partners:', error)
    partners.value = []
  } finally {
    loading.value = false
  }

  
}

const viewPartnerStats = (partner) => {
  console.log('View stats for partner:', partner)
  alert(`Partner stats for ${partner.full_name} coming soon!`)
}

const editPartner = (partner) => {
  console.log('Edit partner:', partner)
  alert('Edit functionality coming soon!')
}

const regenerateCode = (partner) => {
  if (confirm(`Generate new referral code for ${partner.full_name}?`)) {
    console.log('Regenerate code for:', partner.id)
    alert('Code regeneration coming soon!')
  }
}

onMounted(() => {
  fetchPartners()
})
</script>

<style scoped>
.partner-management {
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
}

.btn-view {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.btn-edit {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.btn-refresh {
  background: #8b5cf6;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
}

.coming-soon-notice {
  margin-top: 2rem;
  padding: 1rem;
  background: #fef3c7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #92400e;
}

.coming-soon-notice i {
  font-size: 1.2rem;
}
</style>