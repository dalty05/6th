<template>
  <div class="products-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1>Products Management</h1>
        <p>Manage your dairy product catalog</p>
      </div>
      <button @click="openCreateModal" class="btn-create">
        <i class="fas fa-plus"></i> Add New Product
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <i class="fas fa-boxes"></i>
        </div>
        <div class="stat-info">
          <h3>{{ products.length }}</h3>
          <p>Total Products</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <i class="fas fa-star"></i>
        </div>
        <div class="stat-info">
          <h3>{{ featuredCount }}</h3>
          <p>Featured Products</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <i class="fas fa-tags"></i>
        </div>
        <div class="stat-info">
          <h3>{{ uniqueCategories.length }}</h3>
          <p>Categories</p>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search products..."
          @input="filterProducts"
        >
      </div>
      <select v-model="categoryFilter" @change="filterProducts" class="filter-select">
        <option value="all">All Categories</option>
        <option v-for="cat in uniqueCategories" :key="cat" :value="cat">{{ cat }}</option>
      </select>
      <select v-model="statusFilter" @change="filterProducts" class="filter-select">
        <option value="all">All Status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading products...</p>
    </div>

    <!-- Products Grid -->
    <div v-else class="products-grid">
      <div v-for="product in paginatedProducts" :key="product.id" class="product-card">
        <div class="product-image">
          <img 
            v-if="product.image_url" 
            :src="product.image_url" 
            :alt="product.name"
            @error="handleImageError"
          >
          <div v-else class="image-placeholder">
            <i class="fas fa-milk"></i>
          </div>
          <div class="product-badge" v-if="product.featured">
            <i class="fas fa-fire"></i> Featured
          </div>
        </div>
        
        <div class="product-info">
          <div class="product-header">
            <h3>{{ product.name }}</h3>
            <span :class="['status-badge', product.is_active !== false ? 'active' : 'inactive']">
              {{ product.is_active !== false ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <p class="product-category">
            <i class="fas fa-tag"></i> {{ product.category || 'Uncategorized' }}
          </p>
          <p class="product-description">{{ truncate(product.description, 100) }}</p>
          
          <div class="product-meta" v-if="product.packaging_sizes">
            <i class="fas fa-weight-hanging"></i> {{ product.packaging_sizes }}
          </div>
        </div>
        
        <div class="product-actions">
          <button @click="editProduct(product)" class="action-btn edit" title="Edit">
            <i class="fas fa-edit"></i> Edit
          </button>
          <button @click="toggleFeatured(product)" class="action-btn featured" :class="{ active: product.featured }" title="Toggle Featured">
            <i class="fas fa-star"></i>
          </button>
          <button @click="deleteProduct(product.id)" class="action-btn delete" title="Delete">
            <i class="fas fa-trash"></i> Delete
          </button>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="!loading && filteredProducts.length === 0" class="no-results">
      <i class="fas fa-box-open"></i>
      <h3>No Products Found</h3>
      <p>Try adjusting your search or filters</p>
      <button @click="clearFilters" class="btn-clear">Clear Filters</button>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="filteredProducts.length > 0">
      <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
        <i class="fas fa-chevron-left"></i> Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
        Next <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-container large">
        <div class="modal-header">
          <h2>{{ editingProduct ? 'Edit Product' : 'Create New Product' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveProduct" class="product-form">
          <div class="form-row">
            <div class="form-group full">
              <label>Product Name *</label>
              <input type="text" v-model="form.name" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Category *</label>
              <select v-model="form.category" required>
                <option value="">Select Category</option>
                <option value="Fresh Milk">🥛 Fresh Milk</option>
                <option value="Yoghurt">🍦 Yoghurt</option>
                <option value="Lala">🥤 Lala</option>
                <option value="Ghee">🧈 Ghee</option>
              </select>
            </div>
            <div class="form-group">
              <label>Packaging Sizes</label>
              <input type="text" v-model="form.packaging_sizes" placeholder="e.g., 500ml, 1L, 2L">
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Description *</label>
              <textarea v-model="form.description" rows="4" required placeholder="Detailed product description..."></textarea>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Key Benefits</label>
              <textarea v-model="form.benefits" rows="3" placeholder="List the key benefits of this product..."></textarea>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Ingredients</label>
              <textarea v-model="form.ingredients" rows="3" placeholder="List ingredients..."></textarea>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full">
              <label>Nutritional Information</label>
              <textarea v-model="form.nutritional_info" rows="3" placeholder="Per 100ml/g: Energy, Protein, Fat, etc."></textarea>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Product Image</label>
              <div class="image-upload-area" @click="$refs.imageInput.click()">
                <input type="file" ref="imageInput" @change="handleImageUpload" accept="image/*" style="display: none">
                <div v-if="form.image_preview" class="image-preview">
                  <img :src="form.image_preview" alt="Preview">
                  <button type="button" class="remove-image" @click.stop="removeImage">×</button>
                </div>
                <div v-else class="upload-placeholder">
                  <i class="fas fa-cloud-upload-alt"></i>
                  <p>Click to upload image</p>
                  <small>PNG, JPG, JPEG up to 5MB</small>
                </div>
              </div>
              <small v-if="form.image_url && !form.image_preview">Current image: {{ form.image_url }}</small>
            </div>
          </div>
          
          <div class="form-row checkbox-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.featured"> Featured Product
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Saving...' : (editingProduct ? 'Update Product' : 'Create Product') }}
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

const products = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingProduct = ref(null)

// Filters
const searchQuery = ref('')
const categoryFilter = ref('all')
const statusFilter = ref('all')
const currentPage = ref(1)
const itemsPerPage = 12

// Form data
const form = ref({
  name: '',
  category: '',
  description: '',
  benefits: '',
  packaging_sizes: '',
  nutritional_info: '',
  ingredients: '',
  featured: false,
  image_url: '',
  image_preview: null,
  image_file: null
})

// Computed
const featuredCount = computed(() => products.value.filter(p => p.featured).length)
const uniqueCategories = computed(() => {
  const cats = products.value.map(p => p.category).filter(c => c)
  return [...new Set(cats)]
})

const filteredProducts = computed(() => {
  let filtered = [...products.value]
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(query) || 
      (p.description && p.description.toLowerCase().includes(query))
    )
  }
  
  // Category filter
  if (categoryFilter.value !== 'all') {
    filtered = filtered.filter(p => p.category === categoryFilter.value)
  }
  
  // Status filter
  if (statusFilter.value === 'active') {
    filtered = filtered.filter(p => p.is_active !== false)
  } else if (statusFilter.value === 'inactive') {
    filtered = filtered.filter(p => p.is_active === false)
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredProducts.value.length / itemsPerPage))
const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredProducts.value.slice(start, start + itemsPerPage)
})

// Methods
const loadProducts = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/products')
    products.value = response.data
  } catch (error) {
    console.error('Error loading products:', error)
    toast.error('Failed to load products')
  } finally {
    loading.value = false
  }
}

const filterProducts = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
  categoryFilter.value = 'all'
  statusFilter.value = 'all'
  currentPage.value = 1
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const openCreateModal = () => {
  editingProduct.value = null
  form.value = {
    name: '',
    category: '',
    description: '',
    benefits: '',
    packaging_sizes: '',
    nutritional_info: '',
    ingredients: '',
    featured: false,
    image_url: '',
    image_preview: null,
    image_file: null
  }
  showModal.value = true
}

const editProduct = (product) => {
  editingProduct.value = product
  form.value = {
    name: product.name || '',
    category: product.category || '',
    description: product.description || '',
    benefits: product.benefits || '',
    packaging_sizes: product.packaging_sizes || '',
    nutritional_info: product.nutritional_info || '',
    ingredients: product.ingredients || '',
    featured: product.featured || false,
    image_url: product.image_url || '',
    image_preview: null,
    image_file: null
  }
  showModal.value = true
}

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    toast.error('Invalid file type. Please upload an image.')
    return
  }
  
  // Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    toast.error('File size must be less than 5MB')
    return
  }
  
  form.value.image_file = file
  form.value.image_preview = URL.createObjectURL(file)
}

const removeImage = () => {
  form.value.image_file = null
  form.value.image_preview = null
  if (editingProduct.value) {
    form.value.image_url = ''
  }
}

const saveProduct = async () => {
  if (!form.value.name || !form.value.description || !form.value.category) {
    toast.error('Please fill in all required fields')
    return
  }
  
  saving.value = true
  
  try {
    let imageUrl = form.value.image_url
    
    // Upload image if new file selected
    if (form.value.image_file) {
      const uploadData = new FormData()
      uploadData.append('file', form.value.image_file)
      uploadData.append('folder', 'products')
      
      const uploadResponse = await api.post('/upload', uploadData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      imageUrl = uploadResponse.data.url
    }
    
    const productData = {
      name: form.value.name,
      category: form.value.category,
      description: form.value.description,
      benefits: form.value.benefits,
      packaging_sizes: form.value.packaging_sizes,
      nutritional_info: form.value.nutritional_info,
      ingredients: form.value.ingredients,
      featured: form.value.featured,
      image_url: imageUrl
    }
    
    if (editingProduct.value) {
      await api.put(`/admin/products/${editingProduct.value.id}`, productData)
      toast.success('Product updated successfully')
    } else {
      await api.post('/admin/products', productData)
      toast.success('Product created successfully')
    }
    
    closeModal()
    await loadProducts()
  } catch (error) {
    console.error('Error saving product:', error)
    toast.error(error.response?.data?.error || 'Failed to save product')
  } finally {
    saving.value = false
  }
}

const deleteProduct = async (id) => {
  if (confirm('Are you sure you want to delete this product?')) {
    try {
      await api.delete(`/admin/products/${id}`)
      toast.success('Product deleted')
      await loadProducts()
    } catch (error) {
      console.error('Error deleting product:', error)
      toast.error('Failed to delete product')
    }
  }
}

const toggleFeatured = async (product) => {
  try {
    const updatedProduct = { ...product, featured: !product.featured }
    await api.put(`/admin/products/${product.id}`, updatedProduct)
    toast.success(product.featured ? 'Removed from featured' : 'Added to featured')
    await loadProducts()
  } catch (error) {
    console.error('Error toggling featured:', error)
    toast.error('Failed to update featured status')
  }
}

const closeModal = () => {
  showModal.value = false
  editingProduct.value = null
  if (form.value.image_preview) {
    URL.revokeObjectURL(form.value.image_preview)
  }
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const handleImageError = (event) => {
  event.target.src = '/images/placeholder.png'
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.products-management {
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

/* Filters */
.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  position: relative;
  min-width: 250px;
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
  border-radius: 10px;
  font-size: 0.85rem;
  background: white;
}

.filter-select {
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  font-size: 0.85rem;
  cursor: pointer;
}

/* Products Grid */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
  border-color: #f59e0b;
}

.product-image {
  position: relative;
  height: 200px;
  background: #f8fafc;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #cbd5e1;
  font-size: 3rem;
}

.product-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #f59e0b;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
}

.product-info {
  padding: 1rem;
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.product-header h3 {
  font-size: 1rem;
  color: #1e3a8a;
  margin: 0;
}

.status-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.product-category {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.product-description {
  font-size: 0.8rem;
  color: #4b5563;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.product-meta {
  font-size: 0.7rem;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.action-btn {
  flex: 1;
  padding: 0.4rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  transition: all 0.3s;
}

.action-btn.edit {
  background: #3b82f6;
  color: white;
}

.action-btn.edit:hover {
  background: #2563eb;
}

.action-btn.featured {
  background: #e5e7eb;
  color: #6b7280;
}

.action-btn.featured.active {
  background: #f59e0b;
  color: white;
}

.action-btn.delete {
  background: #ef4444;
  color: white;
}

.action-btn.delete:hover {
  background: #dc2626;
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

.btn-clear {
  margin-top: 1rem;
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.page-btn {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #1e3a8a;
  color: white;
  border-color: #1e3a8a;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.85rem;
  color: #6b7280;
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
  max-width: 750px;
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

.product-form {
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

.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}

/* Image Upload */
.image-upload-area {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: #f8fafc;
}

.image-upload-area:hover {
  border-color: #f59e0b;
  background: #fef3c7;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 150px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.remove-image {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #ef4444;
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
}

.upload-placeholder {
  text-align: center;
  padding: 2rem;
}

.upload-placeholder i {
  font-size: 2rem;
  color: #9ca3af;
  margin-bottom: 0.5rem;
}

.checkbox-row {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  .products-management {
    padding: 1rem;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .management-header {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filters-bar {
    flex-direction: column;
  }
  
  .search-box {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .form-row {
    flex-direction: column;
  }
}
</style>