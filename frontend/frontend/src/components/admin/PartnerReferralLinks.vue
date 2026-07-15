<template>
  <div class="partner-layout">

    <!-- Main Content -->
    <main class="partner-main">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <button class="sidebar-toggle" @click="toggleSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <h1><i class="fas fa-link"></i> Referral Links</h1>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="openCreateModal">
            <i class="fas fa-plus"></i> Create Link
          </button>
        </div>
      </div>

      <!-- Page Content -->
      <div class="page-content">
        <!-- Stats Overview -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon blue"><i class="fas fa-link"></i></div>
            <div class="stat-info">
              <h3>{{ links.length }}</h3>
              <p>Total Links</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon green"><i class="fas fa-check-circle"></i></div>
            <div class="stat-info">
              <h3>{{ activeLinks }}</h3>
              <p>Active Links</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon orange"><i class="fas fa-mouse-pointer"></i></div>
            <div class="stat-info">
              <h3>{{ totalClicks }}</h3>
              <p>Total Clicks</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon purple"><i class="fas fa-chart-line"></i></div>
            <div class="stat-info">
              <h3>{{ totalConversions }}</h3>
              <p>Conversions</p>
            </div>
          </div>
        </div>

        <!-- Search and Filter -->
        <div class="search-section">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search links by name or campaign..."
            />
          </div>
          <div class="filter-options">
            <select v-model="statusFilter" class="filter-select">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading your links...</p>
        </div>

        <!-- Links Table -->
        <div v-else class="table-container">
          <table class="links-table">
            <thead>
              <tr>
                <th>Link Name</th>
                <th>Link Code</th>
                <th>Campaign</th>
                <th>Stats</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="link in paginatedLinks" :key="link.id">
                <td>
                  <div class="link-name">
                    <strong>{{ link.name }}</strong>
                  </div>
                </td>
                <td>
                  <div class="link-code-cell">
                    <code>{{ link.link_code }}</code>
                    <button @click="copyLinkCode(link.link_code)" class="copy-btn-small" title="Copy code">
                      <i class="fas fa-copy"></i>
                    </button>
                  </div>
                </td>
                <td>
                  <span class="campaign-name">{{ link.campaign_name || '—' }}</span>
                </td>
                <td>
                  <div class="stats-badge">
                    <span><i class="fas fa-mouse-pointer"></i> {{ link.total_clicks || 0 }}</span>
                    <span><i class="fas fa-users"></i> {{ link.unique_clicks || 0 }}</span>
                    <span><i class="fas fa-chart-line"></i> {{ link.conversions || 0 }}</span>
                  </div>
                </td>
                <td>
                  <span :class="['status-badge', link.is_active ? 'active' : 'inactive']">
                    {{ link.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <span class="date-text">{{ formatDate(link.created_at) }}</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="copyFullLink(link)" class="action-btn copy" title="Copy full link">
                      <i class="fas fa-copy"></i>
                    </button>
                    <button @click="toggleLinkStatus(link)" class="action-btn" :class="link.is_active ? 'suspend' : 'activate'" 
                            :title="link.is_active ? 'Deactivate' : 'Activate'">
                      <i :class="link.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
                    </button>
                    <button @click="openEditModal(link)" class="action-btn edit" title="Edit">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button @click="deleteLink(link.id)" class="action-btn delete" title="Delete">
                      <i class="fas fa-trash-alt"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredLinks.length === 0">
                <td colspan="7" class="no-results">
                  <i class="fas fa-link"></i>
                  <p>No referral links found</p>
                  <button @click="openCreateModal" class="btn-primary">
                    Create Your First Link
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="pagination" v-if="filteredLinks.length > 0">
          <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
            <i class="fas fa-chevron-left"></i> Previous
          </button>
          <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
          <span class="items-info">{{ filteredLinks.length }} total links</span>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
            Next <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </main>

    <!-- Create/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-container modal-md">
        <div class="modal-header">
          <h2>{{ editingLink ? 'Edit Referral Link' : 'Create Referral Link' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveLink" class="link-form">
            <div class="form-group">
              <label>Link Name *</label>
              <input 
                type="text" 
                v-model="linkForm.name" 
                placeholder="e.g., Summer Campaign, Product Launch"
                required
              />
            </div>
            <div class="form-group">
              <label>Campaign Name (Optional)</label>
              <input 
                type="text" 
                v-model="linkForm.campaign_name" 
                placeholder="e.g., Q4 Marketing, Referral Drive"
              />
            </div>
            <div class="form-group">
              <label>Destination URL</label>
              <input 
                type="url" 
                v-model="linkForm.destination_url" 
                placeholder="https://merudairy.co.ke/products"
              />
              <small class="help-text">Leave blank to use default destination</small>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="linkForm.is_active" />
                Active (link is live and trackable)
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                <i v-if="saving" class="fas fa-spinner fa-spin"></i>
                {{ saving ? 'Saving...' : (editingLink ? 'Update Link' : 'Create Link') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import authService from '@/services/auth'
import referralService from '@/services/referral'

const router = useRouter()
const sidebarRef = ref(null)
const links = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const showModal = ref(false)
const editingLink = ref(null)
const baseUrl = window.location.origin

const linkForm = ref({
  name: '',
  campaign_name: '',
  destination_url: '',
  is_active: true
})

// Computed
const activeLinks = computed(() => links.value.filter(l => l.is_active).length)
const totalClicks = computed(() => links.value.reduce((sum, l) => sum + (l.total_clicks || 0), 0))
const totalConversions = computed(() => links.value.reduce((sum, l) => sum + (l.conversions || 0), 0))

const filteredLinks = computed(() => {
  let result = links.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(l => 
      l.name.toLowerCase().includes(query) ||
      (l.campaign_name && l.campaign_name.toLowerCase().includes(query))
    )
  }
  
  if (statusFilter.value === 'active') {
    result = result.filter(l => l.is_active)
  } else if (statusFilter.value === 'inactive') {
    result = result.filter(l => !l.is_active)
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredLinks.value.length / itemsPerPage))
const paginatedLinks = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredLinks.value.slice(start, start + itemsPerPage)
})

// Methods
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleMobile()
  }
}

const loadLinks = async () => {
  loading.value = true
  try {
    const response = await referralService.getLinks()
    links.value = Array.isArray(response) ? response : []
  } catch (error) {
    toast.error('Failed to load referral links')
    links.value = []
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingLink.value = null
  linkForm.value = {
    name: '',
    campaign_name: '',
    destination_url: '',
    is_active: true
  }
  showModal.value = true
}

const openEditModal = (link) => {
  editingLink.value = link
  linkForm.value = {
    name: link.name,
    campaign_name: link.campaign_name || '',
    destination_url: link.destination_url || '',
    is_active: link.is_active
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingLink.value = null
  saving.value = false
}

const saveLink = async () => {
  if (!linkForm.value.name.trim()) {
    toast.error('Link name is required')
    return
  }

  saving.value = true
  try {
    if (editingLink.value) {
      await referralService.updateLink(editingLink.value.id, linkForm.value)
      toast.success('Link updated successfully')
    } else {
      await referralService.createLink(linkForm.value)
      toast.success('Link created successfully')
    }
    closeModal()
    await loadLinks()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save link')
  } finally {
    saving.value = false
  }
}

const toggleLinkStatus = async (link) => {
  try {
    await referralService.toggleLinkStatus(link.id)
    toast.success(`Link ${link.is_active ? 'deactivated' : 'activated'} successfully`)
    await loadLinks()
  } catch (error) {
    toast.error('Failed to update link status')
  }
}

const deleteLink = async (linkId) => {
  if (confirm('Are you sure you want to delete this referral link?')) {
    try {
      await referralService.deleteLink(linkId)
      toast.success('Link deleted successfully')
      await loadLinks()
    } catch (error) {
      toast.error('Failed to delete link')
    }
  }
}

const copyLinkCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    toast.success('Link code copied to clipboard')
  }).catch(() => {
    const textArea = document.createElement('textarea')
    textArea.value = code
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    toast.success('Link code copied to clipboard')
  })
}

const copyFullLink = (link) => {
  const fullLink = `${baseUrl}/r/${link.link_code}`
  navigator.clipboard.writeText(fullLink).then(() => {
    toast.success('Full referral link copied to clipboard')
  }).catch(() => {
    const textArea = document.createElement('textarea')
    textArea.value = fullLink
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    toast.success('Full referral link copied to clipboard')
  })
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

onMounted(() => {
  const user = authService.getUser()
  if (!user) {
    router.push('/')
    return
  }
  loadLinks()
})
</script>

<style scoped>
/* [Same styles as before - keep the complete CSS from the previous version] */
.partner-layout {
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
}

.partner-main {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-header h1 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-header h1 i {
  color: #f59e0b;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.page-content {
  flex: 1;
  padding: 1.5rem 2rem;
}

.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #0f172a;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.sidebar-toggle:hover {
  background: #f1f5f9;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon.blue { background: #dbeafe; color: #2563eb; }
.stat-icon.green { background: #d1fae5; color: #059669; }
.stat-icon.orange { background: #fef3c7; color: #d97706; }
.stat-icon.purple { background: #ede9fe; color: #7c3aed; }

.stat-info h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.stat-info p {
  font-size: 0.75rem;
  margin: 0;
  color: #6b7280;
}

/* Search */
.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  position: relative;
  min-width: 200px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-box input {
  width: 100%;
  padding: 0.6rem 0.75rem 0.6rem 2.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
}

.filter-options {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.6rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
  background: white;
  cursor: pointer;
}

/* Table */
.table-container {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.links-table {
  width: 100%;
  border-collapse: collapse;
}

.links-table thead {
  background: #f8fafc;
}

.links-table th {
  text-align: left;
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e5e7eb;
}

.links-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.links-table tbody tr:hover {
  background: #f8fafc;
}

.link-name strong {
  color: #0f172a;
  font-size: 0.9rem;
}

.link-code-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.link-code-cell code {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  background: #f1f5f9;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  color: #0f172a;
}

.copy-btn-small {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 4px;
  transition: 0.2s;
}

.copy-btn-small:hover {
  background: #e5e7eb;
  color: #0f172a;
}

.campaign-name {
  font-size: 0.85rem;
  color: #6b7280;
}

.stats-badge {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #4b5563;
}

.stats-badge i {
  color: #f59e0b;
  margin-right: 0.25rem;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.status-badge.active { background: #d1fae5; color: #065f46; }
.status-badge.inactive { background: #fee2e2; color: #991b1b; }

.date-text {
  font-size: 0.8rem;
  color: #6b7280;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: #f1f5f9;
  transform: scale(1.1);
}

.action-btn.copy { color: #3b82f6; }
.action-btn.edit { color: #f59e0b; }
.action-btn.suspend { color: #ef4444; }
.action-btn.activate { color: #10b981; }
.action-btn.delete { color: #ef4444; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.modal-container {
  width: 100%;
  max-width: 600px;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  animation: modalPop 0.25s ease;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: white;
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.15rem;
  font-weight: 600;
}

.modal-body {
  padding: 1.5rem;
}

.close-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  cursor: pointer;
  font-size: 1.3rem;
  transition: 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* Form */
.link-form .form-group {
  margin-bottom: 1rem;
}

.link-form label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.45rem;
}

.link-form input[type="text"],
.link-form input[type="url"] {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.7rem 0.9rem;
  transition: 0.2s;
  font-size: 0.9rem;
}

.link-form input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.help-text {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.25rem;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading & Empty States */
.loading-state {
  text-align: center;
  padding: 3rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-results {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.no-results i {
  font-size: 2.5rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

.no-results p {
  margin-bottom: 1rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-btn {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #f59e0b;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.85rem;
  color: #4b5563;
}

.items-info {
  font-size: 0.8rem;
  color: #9ca3af;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalPop {
  from {
    opacity: 0;
    transform: translateY(15px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .table-container {
    overflow-x: auto;
  }
  
  .links-table {
    min-width: 800px;
  }
}

@media (max-width: 768px) {
  .partner-main {
    margin-left: 0;
  }
  
  .sidebar-toggle {
    display: flex;
  }
  
  .page-header {
    padding: 0.75rem 1rem;
  }
  
  .page-content {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .search-section {
    flex-direction: column;
  }
  
  .filter-options {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>