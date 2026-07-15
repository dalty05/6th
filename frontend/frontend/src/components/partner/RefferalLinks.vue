<template>
  <div class="referral-links">
    <div class="page-header">
      <div>
        <h1>Referral Links</h1>
        <p>Create and manage your referral links to track marketing performance</p>
      </div>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Create New Link
      </button>
    </div>

    <!-- Stats Summary -->
    <div class="stats-row">
      <div class="stat-chip">
        <span class="stat-label">Total Links</span>
        <span class="stat-value">{{ links.length }}</span>
      </div>
      <div class="stat-chip">
        <span class="stat-label">Total Clicks</span>
        <span class="stat-value">{{ totalClicks }}</span>
      </div>
      <div class="stat-chip">
        <span class="stat-label">Avg Conversion</span>
        <span class="stat-value">{{ avgConversionRate }}%</span>
      </div>
    </div>

    <!-- Links Grid -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your links...</p>
    </div>

    <div v-else-if="links.length === 0" class="empty-state">
      <i class="fas fa-link"></i>
      <h3>No Referral Links Yet</h3>
      <p>Create your first referral link to start tracking your marketing campaigns</p>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Create Your First Link
      </button>
    </div>

    <div v-else class="links-grid">
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
      <div class="modal-container modal-medium glass-card">
        <div class="modal-header">
          <h2>{{ editingLink ? 'Edit Link' : 'Create New Link' }}</h2>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveLink" class="modal-form">
          <div class="form-group">
            <label class="form-label">Link Name *</label>
            <input type="text" v-model="form.name" class="form-input" placeholder="e.g., Summer Campaign 2024" required>
            <div class="form-hint">Give your link a memorable name for easy identification</div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Destination URL</label>
            <input type="url" v-model="form.destination_url" class="form-input" placeholder="https://merudairy.co.ke/shop">
            <div class="form-hint">Where should users be redirected? Leave blank to use homepage</div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Campaign Name (Optional)</label>
            <input type="text" v-model="form.campaign_name" class="form-input" placeholder="e.g., Summer Sale 2024">
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label class="toggle-switch">
                <input type="checkbox" v-model="form.is_active">
                <span class="toggle-slider"></span>
                <span class="toggle-label">Active Status</span>
              </label>
            </div>
            
            <div class="form-group">
              <label class="form-label">Expiry Date (Optional)</label>
              <input type="date" v-model="form.expires_at" class="form-input">
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ saving ? 'Saving...' : 'Save Link' }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-container modal-small glass-card">
        <div class="modal-header">
          <h2>Delete Link</h2>
          <button @click="closeDeleteModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ linkToDelete?.name }}</strong>?</p>
          <p class="warning-text">This action cannot be undone and all click data will be lost.</p>
        </div>
        <div class="modal-actions">
          <button @click="deleteLink" class="btn btn-danger">
            <i class="fas fa-trash"></i> Delete Permanently
          </button>
          <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { toast } from 'vue3-toastify'
import referralService from '@/services/referral'
import ReferralLinkCard from '@/components/partner/ReferralLinkCard.vue'

const links = ref([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingLink = ref(null)
const linkToDelete = ref(null)

const form = ref({
  name: '',
  destination_url: '',
  campaign_name: '',
  is_active: true,
  expires_at: ''
})

const totalClicks = computed(() => {
  return links.value.reduce((sum, link) => sum + (link.total_clicks || 0), 0)
})

const avgConversionRate = computed(() => {
  if (links.value.length === 0) return 0
  const total = links.value.reduce((sum, link) => sum + (link.conversion_rate || 0), 0)
  return Math.round(total / links.value.length)
})

const loadLinks = async () => {
  loading.value = true
  try {
    const response = await referralService.getLinks()
    links.value = response
  } catch (error) {
    toast.error('Failed to load links')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingLink.value = null
  form.value = {
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
  form.value = {
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
      await referralService.updateLink(editingLink.value.id, form.value)
      toast.success('Link updated successfully')
    } else {
      await referralService.createLink(form.value)
      toast.success('Link created successfully')
    }
    await loadLinks()
    closeModal()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save link')
  } finally {
    saving.value = false
  }
}

const toggleLinkStatus = async (link) => {
  try {
    await referralService.toggleLinkStatus(link.id, !link.is_active)
    toast.success(link.is_active ? 'Link deactivated' : 'Link activated')
    await loadLinks()
  } catch (error) {
    toast.error('Failed to update link status')
  }
}

const confirmDelete = (link) => {
  linkToDelete.value = link
  showDeleteModal.value = true
}

const deleteLink = async () => {
  try {
    await referralService.deleteLink(linkToDelete.value.id)
    toast.success('Link deleted successfully')
    await loadLinks()
    closeDeleteModal()
  } catch (error) {
    toast.error('Failed to delete link')
  }
}

const closeModal = () => {
  showModal.value = false
  editingLink.value = null
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
.referral-links {
  min-height: 100vh;
  background: var(--gray-50);
  padding: var(--spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
  gap: var(--spacing-4);
}

.page-header h1 {
  color: var(--primary-blue);
  margin: 0 0 var(--spacing-1) 0;
}

.page-header p {
  color: var(--gray-500);
  margin: 0;
}

.stats-row {
  display: flex;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
}

.stat-chip {
  background: white;
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  box-shadow: var(--shadow-sm);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--gray-500);
}

.stat-value {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--primary-blue);
}

.links-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.loading-state, .empty-state {
  text-align: center;
  padding: var(--spacing-12);
  background: white;
  border-radius: var(--radius-xl);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid var(--gray-200);
  border-top-color: var(--accent-orange);
  border-radius: 50%;
  margin: 0 auto var(--spacing-4);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state i {
  font-size: var(--text-5xl);
  color: var(--gray-300);
  margin-bottom: var(--spacing-4);
}

.empty-state h3 {
  color: var(--primary-blue);
  margin-bottom: var(--spacing-2);
}

.empty-state p {
  color: var(--gray-500);
  margin-bottom: var(--spacing-4);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-4);
}

@media (max-width: 768px) {
  .referral-links {
    padding: var(--spacing-4);
  }
  
  .page-header {
    flex-direction: column;
  }
  
  .stats-row {
    justify-content: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>