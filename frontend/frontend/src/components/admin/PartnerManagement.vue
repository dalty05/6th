<template>
  <div class="partner-management">
    <div class="header">
      <h2>Partner Management</h2>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-user-plus"></i> Add Partner
      </button>
    </div>
    
    <!-- Stats Overview -->
    <div class="partner-stats">
      <div class="stat-card">
        <i class="fas fa-users"></i>
        <div class="stat-info">
          <h3>{{ stats.totalPartners }}</h3>
          <p>Active Partners</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-mouse-pointer"></i>
        <div class="stat-info">
          <h3>{{ stats.totalClicks | formatNumber }}</h3>
          <p>Total Clicks</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-shopping-cart"></i>
        <div class="stat-info">
          <h3>{{ stats.totalConversions | formatNumber }}</h3>
          <p>Conversions</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-chart-line"></i>
        <div class="stat-info">
          <h3>{{ stats.avgConversionRate }}%</h3>
          <p>Avg Conversion Rate</p>
        </div>
      </div>
    </div>
    
    <!-- Partners Table -->
    <DataTable 
      :data="partners" 
      :columns="columns" 
      :loading="loading"
      :search-keys="['full_name', 'email', 'referral_code']"
      search-placeholder="Search partners..."
    >
      <template #actions="{ row }">
        <button @click="viewPartnerStats(row)" class="btn-view" title="View Stats">
          <i class="fas fa-chart-line"></i>
        </button>
        <button @click="editPartner(row)" class="btn-edit" title="Edit Partner">
          <i class="fas fa-edit"></i>
        </button>
        <button @click="regenerateCode(row)" class="btn-refresh" title="Regenerate Code">
          <i class="fas fa-sync-alt"></i>
        </button>
        <button @click="confirmDelete(row)" class="btn-delete" title="Delete Partner">
          <i class="fas fa-trash"></i>
        </button>
      </template>
    </DataTable>
    
    <!-- Create/Edit Partner Modal -->
    <div v-if="showPartnerModal" class="modal-overlay" @click.self="closePartnerModal">
      <div class="modal-container glass-card modal-medium">
        <div class="modal-header">
          <h2>{{ editingPartner ? 'Edit Partner' : 'Add New Partner' }}</h2>
          <button @click="closePartnerModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="savePartner" class="modal-form">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" v-model="partnerForm.full_name" required>
          </div>
          
          <div class="form-group">
            <label>Email *</label>
            <input type="email" v-model="partnerForm.email" required :disabled="!!editingPartner">
          </div>
          
          <div class="form-group" v-if="!editingPartner">
            <label>Password *</label>
            <input type="password" v-model="partnerForm.password" required>
            <small>Must be at least 8 characters</small>
          </div>
          
          <div class="form-group">
            <label>Status</label>
            <label class="toggle-switch">
              <input type="checkbox" v-model="partnerForm.is_active">
              <span class="toggle-slider"></span>
              <span class="toggle-label">{{ partnerForm.is_active ? 'Active' : 'Inactive' }}</span>
            </label>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ saving ? 'Saving...' : 'Save Partner' }}
            </button>
            <button type="button" @click="closePartnerModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Partner Stats Modal -->
    <div v-if="showStatsModal" class="modal-overlay" @click.self="closeStatsModal">
      <div class="modal-container glass-card modal-large">
        <div class="modal-header">
          <h2>Partner Statistics: {{ selectedPartner?.full_name }}</h2>
          <button @click="closeStatsModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="stats-content">
          <div class="stats-summary">
            <div class="summary-card">
              <div class="summary-value">{{ partnerStats.totalClicks || 0 }}</div>
              <div class="summary-label">Total Clicks</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ partnerStats.uniqueClicks || 0 }}</div>
              <div class="summary-label">Unique Clicks</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ partnerStats.totalConversions || 0 }}</div>
              <div class="summary-label">Conversions</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ partnerStats.conversionRate || 0 }}%</div>
              <div class="summary-label">Conversion Rate</div>
            </div>
          </div>
          
          <h4>Referral Links</h4>
          <div class="partner-links-list">
            <div v-for="link in partnerLinks" :key="link.id" class="partner-link-item">
              <div class="link-name">{{ link.name }}</div>
              <div class="link-stats">
                <span><i class="fas fa-mouse-pointer"></i> {{ link.total_clicks }}</span>
                <span><i class="fas fa-chart-line"></i> {{ link.conversion_rate }}%</span>
              </div>
            </div>
            <div v-if="partnerLinks.length === 0" class="no-data">
              No referral links created yet
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="closeStatsModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-container glass-card modal-small">
        <div class="modal-header">
          <h2>Delete Partner</h2>
          <button @click="closeDeleteModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ partnerToDelete?.full_name }}</strong>?</p>
          <p class="warning-text">This will also delete all associated referral links and click data.</p>
        </div>
        <div class="modal-actions">
          <button @click="deletePartner" class="btn-danger">
            <i class="fas fa-trash"></i> Delete Permanently
          </button>
          <button @click="closeDeleteModal" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import DataTable from './DataTable.vue'
import api from '@/services/api'

const partners = ref([])
const loading = ref(false)
const saving = ref(false)
const showPartnerModal = ref(false)
const showStatsModal = ref(false)
const showDeleteModal = ref(false)
const editingPartner = ref(null)
const selectedPartner = ref(null)
const partnerToDelete = ref(null)
const partnerStats = ref({})
const partnerLinks = ref([])

const stats = ref({
  totalPartners: 0,
  totalClicks: 0,
  totalConversions: 0,
  avgConversionRate: 0
})

const partnerForm = ref({
  full_name: '',
  email: '',
  password: '',
  is_active: true
})

const columns = [
  { key: 'full_name', label: 'Partner Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'referral_code', label: 'Referral Code', sortable: true },
  { key: 'total_clicks', label: 'Clicks', sortable: true, width: '100px' },
  { key: 'total_conversions', label: 'Conversions', sortable: true, width: '120px' },
  { key: 'created_at', label: 'Joined', type: 'date', sortable: true, width: '120px' },
  { key: 'is_active', label: 'Status', type: 'status', sortable: true, width: '100px' }
]

const fetchPartners = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users?role=partner')
    partners.value = response.data.filter(u => u.role === 'partner')
    
    // Calculate stats
    stats.value.totalPartners = partners.value.length
    stats.value.totalClicks = partners.value.reduce((sum, p) => sum + (p.total_clicks || 0), 0)
    stats.value.totalConversions = partners.value.reduce((sum, p) => sum + (p.total_conversions || 0), 0)
    const totalWithClicks = partners.value.filter(p => (p.total_clicks || 0) > 0).length
    const totalRate = partners.value.reduce((sum, p) => {
      const rate = p.total_clicks ? ((p.total_conversions || 0) / p.total_clicks) * 100 : 0
      return sum + rate
    }, 0)
    stats.value.avgConversionRate = totalWithClicks ? Math.round(totalRate / totalWithClicks) : 0
  } catch (error) {
    console.error('Error fetching partners:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingPartner.value = null
  partnerForm.value = {
    full_name: '',
    email: '',
    password: '',
    is_active: true
  }
  showPartnerModal.value = true
}

const editPartner = (partner) => {
  editingPartner.value = partner
  partnerForm.value = {
    full_name: partner.full_name,
    email: partner.email,
    password: '',
    is_active: partner.is_active
  }
  showPartnerModal.value = true
}

const savePartner = async () => {
  saving.value = true
  try {
    if (editingPartner.value) {
      await api.put(`/admin/users/${editingPartner.value.id}`, {
        full_name: partnerForm.value.full_name,
        is_active: partnerForm.value.is_active
      })
      toast.success('Partner updated successfully')
    } else {
      await api.post('/admin/users', {
        ...partnerForm.value,
        role: 'partner'
      })
      toast.success('Partner created successfully')
    }
    await fetchPartners()
    closePartnerModal()
  } catch (error) {
    console.error('Error saving partner:', error)
  } finally {
    saving.value = false
  }
}

const viewPartnerStats = async (partner) => {
  selectedPartner.value = partner
  showStatsModal.value = true
  
  try {
    const response = await api.get(`/referral/partner/${partner.id}/stats`)
    partnerStats.value = response.data.stats || {}
    partnerLinks.value = response.data.links || []
  } catch (error) {
    console.error('Error fetching partner stats:', error)
  }
}

const regenerateCode = async (partner) => {
  if (confirm(`Generate new referral code for ${partner.full_name}? The old code will stop working.`)) {
    try {
      const response = await api.post(`/admin/users/${partner.id}/regenerate-code`)
      toast.success('Referral code regenerated')
      await fetchPartners()
    } catch (error) {
      console.error('Error regenerating code:', error)
    }
  }
}

const confirmDelete = (partner) => {
  partnerToDelete.value = partner
  showDeleteModal.value = true
}

const deletePartner = async () => {
  try {
    await api.delete(`/admin/users/${partnerToDelete.value.id}`)
    toast.success('Partner deleted successfully')
    await fetchPartners()
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting partner:', error)
  }
}

const closePartnerModal = () => {
  showPartnerModal.value = false
  editingPartner.value = null
}

const closeStatsModal = () => {
  showStatsModal.value = false
  selectedPartner.value = null
  partnerStats.value = {}
  partnerLinks.value = []
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  partnerToDelete.value = null
}

// Number format filter
const formatNumber = (value) => {
  if (!value) return '0'
  if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M'
  if (value >= 1000) return (value / 1000).toFixed(1) + 'K'
  return value.toString()
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

.partner-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-card i {
  font-size: 1.8rem;
  color: #f59e0b;
}

.stat-info h3 {
  font-size: 1.3rem;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 0;
  color: #666;
  font-size: 0.75rem;
}

.btn-view, .btn-edit, .btn-refresh, .btn-delete {
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 0.25rem;
}

.btn-view {
  background: #10b981;
  color: white;
}

.btn-edit {
  background: #3b82f6;
  color: white;
}

.btn-refresh {
  background: #8b5cf6;
  color: white;
}

.btn-delete {
  background: #dc2626;
  color: white;
}

/* Stats Modal */
.stats-content {
  padding: 1.5rem;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-card {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
}

.summary-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #1e3a8a;
}

.summary-label {
  font-size: 0.75rem;
  color: #666;
}

.partner-links-list {
  max-height: 300px;
  overflow-y: auto;
}

.partner-link-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.link-name {
  font-weight: 500;
  color: #1e3a8a;
}

.link-stats {
  display: flex;
  gap: 1rem;
  color: #666;
  font-size: 0.8rem;
}

.link-stats i {
  margin-right: 0.25rem;
  color: #f59e0b;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
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
  max-width: 700px;
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

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.7rem;
  color: #999;
}

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
  .partner-stats {
    grid-template-columns: 1fr 1fr;
  }
  
  .stats-summary {
    grid-template-columns: 1fr 1fr;
  }
}
</style>