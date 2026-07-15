<template>
  <div class="outlet-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1>Outlet Locations</h1>
        <p>Manage physical shops, depots, and office branches</p>
      </div>
      <button @click="openCreateModal" class="btn-create">
        <i class="fas fa-plus"></i> Add Location
      </button>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-map-marker-alt"></i></div>
        <div class="stat-info">
          <h3>{{ outlets.length }}</h3>
          <p>Total Locations</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-building"></i></div>
        <div class="stat-info">
          <h3>{{ officeCount }}</h3>
          <p>Office Branches</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-warehouse"></i></div>
        <div class="stat-info">
          <h3>{{ depotCount }}</h3>
          <p>Depots</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-store"></i></div>
        <div class="stat-info">
          <h3>{{ outletCount }}</h3>
          <p>Retail Outlets</p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading locations...</p>
    </div>

    <!-- Outlets Grid -->
    <div v-else class="outlets-grid">
      <div v-for="outlet in outlets" :key="outlet.id" class="outlet-card">
        <div class="outlet-header">
          <div class="outlet-icon">
            <i :class="getCategoryIcon(outlet.category)"></i>
          </div>
          <div class="outlet-info">
            <h3>{{ outlet.name }}</h3>
            <span class="category-badge">{{ getCategoryLabel(outlet.category) }}</span>
            <span :class="['status-badge', outlet.is_active ? 'active' : 'inactive']">
              {{ outlet.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="outlet-actions">
            <button @click="editOutlet(outlet)" class="action-btn edit" title="Edit">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="deleteOutlet(outlet.id)" class="action-btn delete" title="Delete">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
        
        <div class="outlet-body">
          <p><i class="fas fa-map-marker-alt"></i> {{ outlet.address }}, {{ outlet.city || 'N/A' }}</p>
          <p v-if="outlet.phone"><i class="fas fa-phone"></i> {{ outlet.phone }}</p>
          <p v-if="outlet.email"><i class="fas fa-envelope"></i> {{ outlet.email }}</p>
          <p v-if="outlet.working_hours"><i class="fas fa-clock"></i> {{ outlet.working_hours }}</p>
          <div class="services" v-if="outlet.services && outlet.services.length">
            <span v-for="service in outlet.services" :key="service" class="service-tag">
              {{ service }}
            </span>
          </div>
        </div>
        
        <div class="outlet-footer">
          <a :href="getDirectionsUrl(outlet)" target="_blank" class="directions-link">
            <i class="fas fa-directions"></i> Get Directions
          </a>
          <span class="coordinates">{{ outlet.latitude }}, {{ outlet.longitude }}</span>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="!loading && outlets.length === 0" class="no-results">
      <i class="fas fa-map-marker-alt"></i>
      <h3>No Locations Added</h3>
      <p>Click "Add Location" to create your first outlet</p>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-container large">
        <div class="modal-header">
          <h2>{{ editingOutlet ? 'Edit Location' : 'Add New Location' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveOutlet" class="outlet-form">
          <div class="form-row">
            <div class="form-group full">
              <label>Location Name *</label>
              <input type="text" v-model="form.name" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Category *</label>
              <select v-model="form.category" required>
                <option value="">Select Category</option>
                <option value="office_branch">🏢 Office Branch</option>
                <option value="depot">🚚 Depot / Distribution Center</option>
                <option value="outlet">🏪 Retail Outlet</option>
              </select>
            </div>
            <div class="form-group">
              <label>City</label>
              <input type="text" v-model="form.city">
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Address *</label>
              <input type="text" v-model="form.address" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Latitude *</label>
              <input type="number" step="any" v-model="form.latitude" required placeholder="e.g., 0.0500">
            </div>
            <div class="form-group">
              <label>Longitude *</label>
              <input type="number" step="any" v-model="form.longitude" required placeholder="e.g., 37.6500">
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Phone</label>
              <input type="tel" v-model="form.phone">
            </div>
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="form.email">
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Working Hours</label>
              <input type="text" v-model="form.working_hours" placeholder="e.g., Mon-Fri: 8am-5pm, Sat: 9am-1pm">
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Description</label>
              <textarea v-model="form.description" rows="3"></textarea>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Services Offered</label>
              <div class="services-checkboxes">
                <label v-for="service in serviceOptions" :key="service" class="checkbox-label">
                  <input type="checkbox" :value="service" v-model="form.services"> {{ service }}
                </label>
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.is_active"> Active (visible to customers)
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Saving...' : (editingOutlet ? 'Update Location' : 'Add Location') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

const outlets = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingOutlet = ref(null)

const serviceOptions = [
  'Product Purchase',
  'Order Pickup',
  'Customer Support',
  'Bulk Orders',
  'Account Services',
  'Farm Inputs'
]

const form = ref({
  name: '',
  category: '',
  description: '',
  address: '',
  city: '',
  latitude: '',
  longitude: '',
  phone: '',
  email: '',
  working_hours: '',
  services: [],
  is_active: true
})

// Computed
const officeCount = computed(() => outlets.value.filter(o => o.category === 'office_branch').length)
const depotCount = computed(() => outlets.value.filter(o => o.category === 'depot').length)
const outletCount = computed(() => outlets.value.filter(o => o.category === 'outlet').length)

// Methods
const loadOutlets = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/outlets')
    outlets.value = response.data
  } catch (error) {
    toast.error('Failed to load locations')
  } finally {
    loading.value = false
  }
}

const getCategoryIcon = (category) => {
  const icons = {
    office_branch: 'fas fa-building',
    depot: 'fas fa-warehouse',
    outlet: 'fas fa-store'
  }
  return icons[category] || 'fas fa-map-marker-alt'
}

const getCategoryLabel = (category) => {
  const labels = {
    office_branch: '🏢 Office Branch',
    depot: '🚚 Depot',
    outlet: '🏪 Retail Outlet'
  }
  return labels[category] || category
}

const getDirectionsUrl = (outlet) => {
  return `https://www.google.com/maps/dir/?api=1&destination=${outlet.latitude},${outlet.longitude}`
}

const openCreateModal = () => {
  editingOutlet.value = null
  form.value = {
    name: '',
    category: '',
    description: '',
    address: '',
    city: '',
    latitude: '',
    longitude: '',
    phone: '',
    email: '',
    working_hours: '',
    services: [],
    is_active: true
  }
  showModal.value = true
}

const editOutlet = (outlet) => {
  editingOutlet.value = outlet
  form.value = {
    name: outlet.name,
    category: outlet.category,
    description: outlet.description || '',
    address: outlet.address,
    city: outlet.city || '',
    latitude: outlet.latitude,
    longitude: outlet.longitude,
    phone: outlet.phone || '',
    email: outlet.email || '',
    working_hours: outlet.working_hours || '',
    services: outlet.services || [],
    is_active: outlet.is_active
  }
  showModal.value = true
}

const saveOutlet = async () => {
  if (!form.value.name || !form.value.category || !form.value.address || !form.value.latitude || !form.value.longitude) {
    toast.error('Please fill in all required fields')
    return
  }
  
  saving.value = true
  try {
    if (editingOutlet.value) {
      await api.put(`/admin/outlets/${editingOutlet.value.id}`, form.value)
      toast.success('Location updated successfully')
    } else {
      await api.post('/admin/outlets', form.value)
      toast.success('Location added successfully')
    }
    closeModal()
    await loadOutlets()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save location')
  } finally {
    saving.value = false
  }
}

const deleteOutlet = async (id) => {
  if (confirm('Are you sure you want to delete this location?')) {
    try {
      await api.delete(`/admin/outlets/${id}`)
      toast.success('Location deleted')
      await loadOutlets()
    } catch (error) {
      toast.error('Failed to delete location')
    }
  }
}

const closeModal = () => {
  showModal.value = false
  editingOutlet.value = null
}

onMounted(() => {
  loadOutlets()
})
</script>

<style scoped>
.outlet-management {
  padding: 1.5rem;
  background: #f8fafc;
  min-height: 100vh;
}

/* Header */
.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
  font-size: 1.8rem;
}

.header-left p {
  color: #6b7280;
  margin: 0;
}

.btn-create {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.btn-create:hover {
  background: #f59e0b;
  transform: translateY(-2px);
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.blue { background: #e0e7ff; color: #1e3a8a; }
.stat-icon.green { background: #d1fae5; color: #065f46; }
.stat-icon.orange { background: #fed7aa; color: #9a3412; }
.stat-icon.purple { background: #e0e7ff; color: #1e3a8a; }

.stat-info h3 {
  font-size: 1.5rem;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 0;
  color: #6b7280;
  font-size: 0.8rem;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #1e3a8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Outlets Grid */
.outlets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.25rem;
}

.outlet-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
}

.outlet-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
  border-color: #f59e0b;
}

.outlet-header {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.outlet-icon i {
  font-size: 2rem;
  color: #1e3a8a;
}

.outlet-info {
  flex: 1;
}

.outlet-info h3 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: #1e3a8a;
}

.category-badge {
  display: inline-block;
  background: #e5e7eb;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  margin-right: 0.5rem;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.outlet-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s;
}

.action-btn.edit { color: #3b82f6; }
.action-btn.edit:hover { background: #dbeafe; }
.action-btn.delete { color: #ef4444; }
.action-btn.delete:hover { background: #fee2e2; }

.outlet-body {
  padding: 1.25rem;
}

.outlet-body p {
  margin: 0.5rem 0;
  font-size: 0.8rem;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.outlet-body i {
  width: 20px;
  color: #9ca3af;
}

.services {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.service-tag {
  background: #e5e7eb;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  color: #374151;
}

.outlet-footer {
  padding: 0.75rem 1.25rem;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.7rem;
}

.directions-link {
  color: #f59e0b;
  text-decoration: none;
}

.directions-link:hover {
  text-decoration: underline;
}

.coordinates {
  color: #9ca3af;
}

/* No Results */
.no-results {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 16px;
}

.no-results i {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.no-results h3 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  background: white;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #9ca3af;
}

.outlet-form {
  padding: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 200px;
}

.form-group.full {
  flex: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 0.8rem;
  color: #374151;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.85rem;
}

.services-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel {
  background: #e5e7eb;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  cursor: pointer;
}

.btn-submit {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .outlet-management {
    padding: 1rem;
  }
  
  .outlets-grid {
    grid-template-columns: 1fr;
  }
  
  .management-header {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .form-row {
    flex-direction: column;
  }
}
</style>