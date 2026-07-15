<template>
  <div class="tour-manager-packages">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1><i class="fas fa-tag"></i> Tour Packages</h1>
        <p class="subtitle">Create and manage tour packages with pricing and discounts</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i> New Package
      </button>
    </div>

    <!-- Stats Summary -->
    <div class="stats-summary">
      <div class="stat-chip">
        <span class="chip-label">Total Packages</span>
        <span class="chip-value">{{ packages.length }}</span>
      </div>
      <div class="stat-chip">
        <span class="chip-label">Active</span>
        <span class="chip-value active">{{ activePackages }}</span>
      </div>
      <div class="stat-chip">
        <span class="chip-label">Inactive</span>
        <span class="chip-value inactive">{{ inactivePackages }}</span>
      </div>
      <div class="stat-chip">
        <span class="chip-label">Featured</span>
        <span class="chip-value featured">{{ featuredPackages }}</span>
      </div>
    </div>

    <!-- Search -->
    <div class="search-section">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search packages by name..."
          @input="applySearch"
        >
      </div>
      <div class="filter-options">
        <select v-model="statusFilter" class="filter-select" @change="applySearch">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <select v-model="featuredFilter" class="filter-select" @change="applySearch">
          <option value="">All</option>
          <option value="featured">Featured</option>
          <option value="not-featured">Not Featured</option>
        </select>
      </div>
    </div>

    <!-- Packages Grid -->
    <div class="packages-grid">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading packages...</p>
      </div>

      <div v-else-if="filteredPackages.length === 0" class="empty-state">
        <i class="fas fa-box-open"></i>
        <h3>No Packages Found</h3>
        <p>Create your first tour package to get started</p>
        <button @click="openCreateModal" class="btn-primary small">
          <i class="fas fa-plus"></i> Create Package
        </button>
      </div>

      <div v-else v-for="pkg in filteredPackages" :key="pkg.id" class="package-card">
        <div class="package-image">
          <img :src="pkg.image_url || '/images/tour-placeholder.jpg'" :alt="pkg.name">
          <div class="package-status" :class="{ active: pkg.is_active }">
            {{ pkg.is_active ? 'Active' : 'Inactive' }}
          </div>
          <div v-if="pkg.is_featured" class="featured-badge">
            <i class="fas fa-star"></i> Featured
          </div>
        </div>

        <div class="package-info">
          <h3>{{ pkg.name }}</h3>
          <p class="package-description">{{ pkg.short_description || truncate(pkg.description, 100) }}</p>
          
          <div class="package-meta">
            <span class="meta-item">
              <i class="fas fa-users"></i> {{ pkg.min_people }}-{{ pkg.max_people }}
            </span>
            <span class="meta-item">
              <i class="fas fa-clock"></i> {{ pkg.duration_hours }}h
            </span>
            <span class="meta-item price">
              <i class="fas fa-tag"></i> KES {{ formatPrice(pkg.base_price) }}
            </span>
              <span class="meta-item commitment">
                <i class="fas fa-percent"></i> {{ pkg.commitment_percentage || 30 }}% Deposit
              </span>
          </div>

          <div class="package-discounts">
            <span class="discount-label">Discount Tiers:</span>
            <div class="discount-tags">
              <span v-for="(discount, tier) in pkg.discount_tiers" :key="tier" class="discount-tag">
                {{ tier }}: {{ (discount * 100) }}%
              </span>
            </div>
          </div>

          <div class="package-includes">
            <span class="include-label">Includes:</span>
            <div class="include-tags">
              <span v-for="item in pkg.includes?.slice(0, 3) || []" :key="item" class="include-tag">
                <i class="fas fa-check-circle"></i> {{ item }}
              </span>
              <span v-if="(pkg.includes?.length || 0) > 3" class="include-tag more">
                +{{ pkg.includes.length - 3 }} more
              </span>
            </div>
          </div>

          <div class="package-actions">
            <button @click="editPackage(pkg)" class="btn-edit">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button @click="togglePackageStatus(pkg)" class="btn-toggle" :class="{ active: pkg.is_active }">
              <i :class="pkg.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
              {{ pkg.is_active ? 'Deactivate' : 'Activate' }}
            </button>
            <button @click="toggleFeatured(pkg)" class="btn-featured" :class="{ active: pkg.is_featured }">
              <i :class="pkg.is_featured ? 'fas fa-star' : 'far fa-star'"></i>
            </button>
            <button @click="deletePackage(pkg)" class="btn-delete">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container package-modal">
        <div class="modal-header">
          <h2>
            <i class="fas fa-tag"></i>
            {{ editingPackage ? 'Edit Package' : 'Create New Package' }}
          </h2>
          <button class="modal-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form @submit.prevent="savePackage" class="package-form">
          <div class="form-grid">
            <!-- Basic Info -->
            <div class="form-group full-width">
              <label>Package Name *</label>
              <input type="text" v-model="form.name" required placeholder="e.g., Standard Factory Tour">
            </div>

            <div class="form-group full-width">
              <label>Slug *</label>
              <input type="text" v-model="form.slug" required placeholder="e.g., standard-factory-tour">
              <small class="hint">URL-friendly name (lowercase, hyphens instead of spaces)</small>
            </div>

            <div class="form-group full-width">
              <label>Description *</label>
              <textarea v-model="form.description" rows="3" required placeholder="Detailed description of the tour"></textarea>
            </div>

            <div class="form-group full-width">
              <label>Short Description</label>
              <input type="text" v-model="form.short_description" placeholder="Brief summary (max 200 chars)">
            </div>

            <!-- Pricing -->
            <div class="form-group">
              <label>Base Price (KES) *</label>
              <input type="number" v-model="form.base_price" required min="0" step="100">
            </div>

            <div class="form-group">
              <label>Duration (Hours)</label>
              <input type="number" v-model="form.duration_hours" min="1" max="24">
            </div>

            <div class="form-group">
              <label>Min People</label>
              <input type="number" v-model="form.min_people" min="1">
            </div>

            <div class="form-group">
              <label>Max People</label>
              <input type="number" v-model="form.max_people" min="1" max="500">
            </div>

            <!-- Discount Tiers -->
            <div class="form-group full-width">
              <label>Discount Tiers</label>
              <div class="discount-tiers">
                <div v-for="(tier, key) in form.discount_tiers" :key="key" class="tier-row">
                  <span class="tier-label">{{ key }}</span>
                  <input type="number" v-model="form.discount_tiers[key]" min="0" max="1" step="0.01">
                  <span class="tier-percent">{{ (form.discount_tiers[key] * 100) }}%</span>
                </div>
              </div>
              <small class="hint">Example: 0.05 = 5% discount</small>
            </div>

            <!-- Includes -->
            <div class="form-group full-width">
              <label>Includes</label>
              <div class="tag-input">
                <input 
                  type="text" 
                  v-model="includeInput" 
                  placeholder="Add item and press Enter"
                  @keyup.enter="addInclude"
                >
                <button type="button" @click="addInclude" class="btn-add-tag">
                  <i class="fas fa-plus"></i>
                </button>
              </div>
              <div class="tags">
                <span v-for="(item, index) in form.includes" :key="index" class="tag">
                  {{ item }}
                  <button type="button" @click="removeInclude(index)" class="tag-remove">
                    <i class="fas fa-times"></i>
                  </button>
                </span>
              </div>
            </div>

            <!-- Excludes -->
            <div class="form-group full-width">
              <label>Excludes</label>
              <div class="tag-input">
                <input 
                  type="text" 
                  v-model="excludeInput" 
                  placeholder="Add item and press Enter"
                  @keyup.enter="addExclude"
                >
                <button type="button" @click="addExclude" class="btn-add-tag">
                  <i class="fas fa-plus"></i>
                </button>
              </div>
              <div class="tags">
                <span v-for="(item, index) in form.excludes" :key="index" class="tag">
                  {{ item }}
                  <button type="button" @click="removeExclude(index)" class="tag-remove">
                    <i class="fas fa-times"></i>
                  </button>
                </span>
              </div>
            </div>

            <!-- Image -->
            <div class="form-group">
              <label>Image URL</label>
              <input type="url" v-model="form.image_url" placeholder="https://example.com/image.jpg">
            </div>

            <!-- Status -->
            <div class="form-group">
              <label>Status</label>
              <div class="toggle-group">
                <label class="toggle">
                  <input type="checkbox" v-model="form.is_active">
                  <span class="toggle-slider"></span>
                </label>
                <span>{{ form.is_active ? 'Active' : 'Inactive' }}</span>
              </div>
            </div>

            <div class="form-group">
              <label>Featured</label>
              <div class="toggle-group">
                <label class="toggle">
                  <input type="checkbox" v-model="form.is_featured">
                  <span class="toggle-slider"></span>
                </label>
                <span>{{ form.is_featured ? 'Featured' : 'Not Featured' }}</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Commitment Deposit (%)</label>
            <div class="commitment-input">
              <input 
                type="number" 
                v-model="form.commitment_percentage" 
                min="0" 
                max="100" 
                step="1"
              >
              <span class="percent-sign">%</span>
            </div>
            <small class="hint">Default: 30% of total price</small>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" :disabled="submitting" class="btn-submit">
              <span v-if="!submitting">
                <i class="fas fa-save"></i> {{ editingPackage ? 'Update' : 'Create' }} Package
              </span>
              <span v-else>
                <i class="fas fa-spinner fa-spin"></i> Saving...
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-container delete-modal">
        <div class="modal-header" style="background: linear-gradient(135deg, #dc2626, #b91c1c);">
          <h3><i class="fas fa-exclamation-triangle"></i> Delete Package</h3>
          <button class="modal-close" @click="showDeleteModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ packageToDelete?.name }}</strong>?</p>
          <p class="warning">This action cannot be undone. All associated bookings will be affected.</p>
          <div class="form-actions">
            <button @click="showDeleteModal = false" class="btn-cancel">Cancel</button>
            <button @click="confirmDelete" class="btn-danger">
              <i class="fas fa-trash"></i> Delete Package
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// ============================================================
// STATE
// ============================================================
const packages = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const featuredFilter = ref('')
const submitting = ref(false)

// Modal states
const showModal = ref(false)
const editingPackage = ref(null)
const showDeleteModal = ref(false)
const packageToDelete = ref(null)

// Form
const form = ref({
  name: '',
  slug: '',
  description: '',
  short_description: '',
  base_price: 0,
  min_people: 1,
  max_people: 300,
  duration_hours: 2,
  commitment_percentage: 30.0,
  discount_tiers: {
    '1-50': 0.05,
    '51-100': 0.10,
    '101-150': 0.15,
    '151-200': 0.20,
    '201+': 0.25
  },
  includes: [],
  excludes: [],
  image_url: '',
  is_active: true,
  is_featured: false
})

const includeInput = ref('')
const excludeInput = ref('')

// ============================================================
// COMPUTED
// ============================================================
const activePackages = computed(() => 
  packages.value.filter(p => p.is_active).length
)

const inactivePackages = computed(() => 
  packages.value.filter(p => !p.is_active).length
)

const featuredPackages = computed(() => 
  packages.value.filter(p => p.is_featured).length
)

const filteredPackages = computed(() => {
  let result = packages.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p => 
      p.name.toLowerCase().includes(query) ||
      p.description.toLowerCase().includes(query)
    )
  }
  
  if (statusFilter.value) {
    result = result.filter(p => 
      statusFilter.value === 'active' ? p.is_active : !p.is_active
    )
  }
  
  if (featuredFilter.value === 'featured') {
    result = result.filter(p => p.is_featured)
  } else if (featuredFilter.value === 'not-featured') {
    result = result.filter(p => !p.is_featured)
  }
  
  return result
})

// ============================================================
// METHODS
// ============================================================
const loadPackages = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/tour/packages')
    packages.value = response.data.packages || []
  } catch (error) {
    alert('Failed to load packages')
  } finally {
    loading.value = false
  }
}

const applySearch = () => {
  // Search is handled by computed property
}

const openCreateModal = () => {
  editingPackage.value = null
  resetForm()
  showModal.value = true
}

const editPackage = (pkg) => {
  editingPackage.value = pkg
  form.value = {
    name: pkg.name,
    slug: pkg.slug,
    description: pkg.description,
    short_description: pkg.short_description || '',
    base_price: pkg.base_price,
    min_people: pkg.min_people || 1,
    max_people: pkg.max_people || 300,
    commitment_percentage: pkg.commitment_percentage || 30.0,
    duration_hours: pkg.duration_hours || 2,
    discount_tiers: pkg.discount_tiers || form.value.discount_tiers,
    includes: pkg.includes || [],
    excludes: pkg.excludes || [],
    image_url: pkg.image_url || '',
    is_active: pkg.is_active,
    is_featured: pkg.is_featured
  }
  showModal.value = true
}

const resetForm = () => {
  form.value = {
    name: '',
    slug: '',
    description: '',
    short_description: '',
    base_price: 0,
    min_people: 1,
    max_people: 300,
    duration_hours: 2,
    discount_tiers: {
      '1-50': 0.05,
      '51-100': 0.10,
      '101-150': 0.15,
      '151-200': 0.20,
      '201+': 0.25
    },
    includes: [],
    excludes: [],
    image_url: '',
    is_active: true,
    is_featured: false
  }
  includeInput.value = ''
  excludeInput.value = ''
}

const closeModal = () => {
  showModal.value = false
  editingPackage.value = null
}

const savePackage = async () => {
  // Validate slug
  form.value.slug = form.value.slug.toLowerCase().replace(/\s+/g, '-')
  
  submitting.value = true
  try {
    let response
    if (editingPackage.value) {
      response = await axios.put(`/api/admin/tour/packages/${editingPackage.value.id}`, form.value)
    } else {
      response = await axios.post('/api/admin/tour/packages', form.value)
    }
    
    await loadPackages()
    closeModal()
    alert(editingPackage.value ? 'Package updated successfully!' : 'Package created successfully!')
  } catch (error) {
    alert(error.response?.data?.error || 'Failed to save package')
  } finally {
    submitting.value = false
  }
}

const togglePackageStatus = async (pkg) => {
  try {
    await axios.put(`/api/admin/tour/packages/${pkg.id}`, {
      is_active: !pkg.is_active
    })
    await loadPackages()
  } catch (error) {
    alert('Failed to update package status')
  }
}

const toggleFeatured = async (pkg) => {
  try {
    await axios.put(`/api/admin/tour/packages/${pkg.id}`, {
      is_featured: !pkg.is_featured
    })
    await loadPackages()
  } catch (error) {
    alert('Failed to update featured status')
  }
}

const deletePackage = (pkg) => {
  packageToDelete.value = pkg
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    await axios.delete(`/api/admin/tour/packages/${packageToDelete.value.id}`)
    await loadPackages()
    showDeleteModal.value = false
    packageToDelete.value = null
    alert('Package deleted successfully')
  } catch (error) {
    alert('Failed to delete package')
  }
}

// Tag management
const addInclude = () => {
  if (includeInput.value.trim()) {
    form.value.includes.push(includeInput.value.trim())
    includeInput.value = ''
  }
}

const removeInclude = (index) => {
  form.value.includes.splice(index, 1)
}

const addExclude = () => {
  if (excludeInput.value.trim()) {
    form.value.excludes.push(excludeInput.value.trim())
    excludeInput.value = ''
  }
}

const removeExclude = (index) => {
  form.value.excludes.splice(index, 1)
}

// Helpers
const formatPrice = (amount) => {
  return (amount || 0).toLocaleString('en-KE', { 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  })
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}


onMounted(() => {
  loadPackages()
})
</script>

<style scoped>



.meta-item.commitment {
  color: #f59e0b;
  font-weight: 500;
}





.commitment-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.commitment-input input {
  flex: 1;
}

.percent-sign {
  font-weight: 600;
  color: #1e3a8a;
  font-size: 16px;
  min-width: 24px;
}



.tour-manager-packages {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============================================
   PAGE HEADER
   ============================================ */









.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  color: #1e3a8a;
  margin: 0 0 4px;
  font-size: 1.8rem;
}

.page-header h1 i {
  color: #f59e0b;
  margin-right: 12px;
}

.subtitle {
  color: #6b7280;
  margin: 0;
}

.btn-primary {
  padding: 10px 20px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-primary.small {
  padding: 8px 16px;
  font-size: 14px;
}

/* ============================================
   STATS SUMMARY
   ============================================ */
.stats-summary {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-chip {
  background: white;
  border-radius: 8px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  border: 1px solid #e5e7eb;
}

.chip-label {
  font-size: 13px;
  color: #6b7280;
}

.chip-value {
  font-weight: 700;
  font-size: 16px;
}

.chip-value.active { color: #10b981; }
.chip-value.inactive { color: #ef4444; }
.chip-value.featured { color: #f59e0b; }

/* ============================================
   SEARCH
   ============================================ */
.search-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
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
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.search-box input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.filter-options {
  display: flex;
  gap: 8px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

/* ============================================
   PACKAGES GRID
   ============================================ */
.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.package-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.package-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border-color: #f59e0b;
}

.package-image {
  height: 180px;
  position: relative;
  overflow: hidden;
  background: #f1f5f9;
}

.package-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.package-status {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.package-status.active {
  background: #d1fae5;
  color: #065f46;
}

.package-status:not(.active) {
  background: #fee2e2;
  color: #991b1b;
}

.featured-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: #f59e0b;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.featured-badge i {
  margin-right: 4px;
}

.package-info {
  padding: 16px;
}

.package-info h3 {
  margin: 0 0 4px;
  color: #1e3a8a;
  font-size: 1.1rem;
}

.package-description {
  color: #6b7280;
  font-size: 13px;
  margin: 0 0 12px;
  line-height: 1.4;
}

.package-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.meta-item {
  font-size: 13px;
  color: #4b5563;
}

.meta-item i {
  color: #f59e0b;
  margin-right: 4px;
}

.meta-item.price {
  font-weight: 600;
  color: #1e3a8a;
}

.package-discounts {
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
}

.discount-label {
  font-size: 12px;
  color: #6b7280;
  display: block;
  margin-bottom: 4px;
}

.discount-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.discount-tag {
  font-size: 11px;
  background: #e5e7eb;
  padding: 2px 8px;
  border-radius: 12px;
  color: #374151;
}

.package-includes {
  margin-bottom: 12px;
}

.include-label {
  font-size: 12px;
  color: #6b7280;
  display: block;
  margin-bottom: 4px;
}

.include-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.include-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  color: #065f46;
  background: #d1fae5;
  display: flex;
  align-items: center;
  gap: 4px;
}

.include-tag i {
  font-size: 9px;
}

.include-tag.more {
  background: #e5e7eb;
  color: #6b7280;
}

.package-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.package-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-edit {
  background: #dbeafe;
  color: #1e40af;
}

.btn-edit:hover {
  background: #bfdbfe;
}

.btn-toggle {
  background: #fef3c7;
  color: #92400e;
}

.btn-toggle:hover {
  background: #fde68a;
}

.btn-toggle.active {
  background: #d1fae5;
  color: #065f46;
}

.btn-toggle.active:hover {
  background: #a7f3d0;
}

.btn-featured {
  background: #f3f4f6;
  color: #6b7280;
}

.btn-featured:hover {
  background: #e5e7eb;
}

.btn-featured.active {
  background: #fef3c7;
  color: #f59e0b;
}

.btn-featured.active:hover {
  background: #fde68a;
}

.btn-delete {
  background: #fee2e2;
  color: #991b1b;
}

.btn-delete:hover {
  background: #fecaca;
}

/* ============================================
   LOADING & EMPTY STATES
   ============================================ */
.loading-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-state i {
  font-size: 48px;
  opacity: 0.3;
  display: block;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #1f2937;
  margin: 0 0 8px;
}

.empty-state p {
  margin: 0 0 16px;
}

/* ============================================
   MODAL
   ============================================ */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(0,0,0,0.1);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #ef4444;
  color: white;
}

.modal-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1.2rem;
}

.modal-header h2 i {
  color: #f59e0b;
  margin-right: 8px;
}

.modal-body {
  padding: 20px 24px 24px;
}

.package-form {
  padding: 20px 24px 24px;
}

/* ============================================
   FORM
   ============================================ */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  font-size: 13px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.hint {
  font-size: 12px;
  color: #6b7280;
}

/* Discount Tiers */
.discount-tiers {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tier-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}

.tier-label {
  font-weight: 500;
  min-width: 80px;
  font-size: 13px;
}

.tier-row input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  width: 80px;
}

.tier-percent {
  font-weight: 600;
  color: #f59e0b;
  min-width: 50px;
}

/* Tags */
.tag-input {
  display: flex;
  gap: 8px;
}

.tag-input input {
  flex: 1;
}

.btn-add-tag {
  padding: 6px 12px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-add-tag:hover {
  background: #d97706;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px 4px 12px;
  background: #dbeafe;
  color: #1e3a8a;
  border-radius: 4px;
  font-size: 13px;
}

.tag-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 0 2px;
}

.tag-remove:hover {
  color: #ef4444;
}

/* Toggle */
.toggle-group {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 4px;
}

.toggle {
  position: relative;
  width: 42px;
  height: 24px;
  cursor: pointer;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #cbd5e1;
  border-radius: 24px;
  transition: all 0.3s;
}

.toggle-slider:before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s;
}

.toggle input:checked + .toggle-slider {
  background: #10b981;
}

.toggle input:checked + .toggle-slider:before {
  transform: translateX(18px);
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 10px 24px;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: #4b5563;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-submit {
  padding: 10px 32px;
  background: #f59e0b;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-submit:hover:not(:disabled) {
  background: #d97706;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  padding: 10px 24px;
  background: #ef4444;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-danger:hover {
  background: #dc2626;
}

.warning {
  color: #ef4444;
  font-size: 13px;
  margin-top: 8px;
}

/* Delete Modal */
.delete-modal {
  max-width: 450px;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
  
  .search-section {
    flex-direction: column;
  }
  
  .filter-options {
    width: 100%;
  }
  
  .filter-select {
    flex: 1;
  }
  
  .packages-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-group.full-width {
    grid-column: 1;
  }
  
  .package-modal {
    max-width: 100%;
    margin: 10px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .package-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .package-actions {
    flex-direction: column;
  }
  
  .package-actions button {
    width: 100%;
    justify-content: center;
  }
  
  .stats-summary {
    flex-direction: column;
  }
  
  .stat-chip {
    justify-content: space-between;
  }
}
</style>