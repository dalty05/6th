<template>
  <div class="partner-links">
    <div class="page-header">
      <div>
        <h1>Referral Links</h1>
        <p>Create and manage your referral links to track your marketing performance</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i> Create New Link
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your links...</p>
    </div>
    
    <div v-else-if="links.length === 0" class="empty-state">
      <i class="fas fa-link"></i>
      <h3>No Referral Links Yet</h3>
      <p>Create your first referral link to start tracking your marketing campaigns</p>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i> Create Your First Link
      </button>
    </div>
    
    <div v-else class="links-container">
      <ReferralLinkCard 
        v-for="link in links" 
        :key="link.id"
        :link="link"
        @edit="editLink"
        @toggle="toggleLinkStatus"
        @delete="confirmDelete"
      />
    </div>
    
    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container glass-card">
        <div class="modal-header">
          <h2>{{ editingLink ? 'Edit Link' : 'Create New Link' }}</h2>
          <button @click="closeModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveLink" class="modal-form">
          <div class="form-group">
            <label>Link Name *</label>
            <input 
              type="text" 
              v-model="linkForm.name" 
              placeholder="e.g., Summer Campaign 2024"
              required
            >
            <small>Give your link a memorable name for easy identification</small>
          </div>
          
          <div class="form-group">
            <label>Destination URL</label>
            <input 
              type="url" 
              v-model="linkForm.destination_url" 
              placeholder="https://merudairy.co.ke/shop"
            >
            <small>Where should users be redirected? Leave blank to use homepage</small>
          </div>
          
          <div class="form-group">
            <label>Campaign Name (Optional)</label>
            <input 
              type="text" 
              v-model="linkForm.campaign_name" 
              placeholder="e.g., Summer Sale 2024"
            >
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Active Status</label>
              <label class="toggle-switch">
                <input type="checkbox" v-model="linkForm.is_active">
                <span class="toggle-slider"></span>
              </label>
            </div>
            
            <div class="form-group">
              <label>Expiry Date (Optional)</label>
              <input type="date" v-model="linkForm.expires_at">
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ saving ? 'Saving...' : 'Save Link' }}
            </button>
            <button type="button" @click="closeModal" class="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-container glass-card modal-small">
        <div class="modal-header">
          <h2>Delete Link</h2>
          <button @click="closeDeleteModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ linkToDelete?.name }}</strong>?</p>
          <p class="warning-text">This action cannot be undone and all click data will be lost.</p>
        </div>
        
        <div class="modal-actions">
          <button @click="deleteLink" class="btn-danger">
            <i class="fas fa-trash"></i> Delete Permanently
          </button>
          <button @click="closeDeleteModal" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import referralService from '@/services/referral'
import ReferralLinkCard from '@/components/partner/ReferralLinkCard.vue'

const links = ref([])
const loading = ref(true)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingLink = ref(null)
const linkToDelete = ref(null)
const saving = ref(false)

const linkForm = ref({
  name: '',
  destination_url: '',
  campaign_name: '',
  is_active: true,
  expires_at: ''
})

const loadLinks = async () => {
  loading.value = true
  try {
    const response = await referralService.getLinks()
    links.value = response
  } catch (error) {
    console.error('Error loading links:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingLink.value = null
  linkForm.value = {
    name: '',
    destination_url: '',
    campaign_name: '',
    is_active: true,
    expires_at: ''
  }
  showModal.value = true
}

const editLink = (link) => {
  editingLink.value = link
  linkForm.value = {
    name: link.name,
    destination_url: link.destination_url || '',
    campaign_name: link.campaign_name || '',
    is_active: link.is_active,
    expires_at: link.expires_at ? link.expires_at.split('T')[0] : ''
  }
  showModal.value = true
}

const saveLink = async () => {
  saving.value = true
  try {
    if (editingLink.value) {
      await referralService.updateLink(editingLink.value.id, linkForm.value)
    } else {
      await referralService.createLink(linkForm.value)
    }
    await loadLinks()
    closeModal()
  } catch (error) {
    console.error('Error saving link:', error)
    alert('Failed to save link. Please try again.')
  } finally {
    saving.value = false
  }
}

const toggleLinkStatus = async (link) => {
  try {
    await referralService.toggleLinkStatus(link.id, !link.is_active)
    await loadLinks()
  } catch (error) {
    console.error('Error toggling link status:', error)
    alert('Failed to update link status.')
  }
}

const confirmDelete = (link) => {
  linkToDelete.value = link
  showDeleteModal.value = true
}

const deleteLink = async () => {
  try {
    await referralService.deleteLink(linkToDelete.value.id)
    await loadLinks()
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting link:', error)
    alert('Failed to delete link.')
  }
}

const closeModal = () => {
  showModal.value = false
  editingLink.value = null
  linkForm.value = {
    name: '',
    destination_url: '',
    campaign_name: '',
    is_active: true,
    expires_at: ''
  }
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  linkToDelete.value = null
}

onMounted(() => {
  loadLinks()
})
</script>

<style scoped>
.partner-links {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h1 {
  color: #1e3a8a;
  margin-bottom: 0.25rem;
}

.page-header p {
  color: #666;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
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

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 16px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state i {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 1.5rem;
}

.links-container {
  max-width: 1000px;
  margin: 0 auto;
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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
  margin-bottom: 1.25rem;
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

.form-group input:focus {
  outline: none;
  border-color: #f59e0b;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.7rem;
  color: #999;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
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

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
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

@media (max-width: 768px) {
  .partner-links {
    padding: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>