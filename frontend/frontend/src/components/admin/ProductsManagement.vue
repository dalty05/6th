<template>
  <div class="products-management">
    <div class="header">
      <h2>Products Management</h2>
      <PermissionGuard resource="products" action="create">
        <button @click="openCreateModal" class="btn-primary">
          <i class="fas fa-plus"></i> Add Product
        </button>
      </PermissionGuard>
    </div>
    
    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="filters.search" 
          placeholder="Search products..."
          @input="debouncedSearch"
        >
      </div>
      <select v-model="filters.category" @change="applyFilters" class="filter-select">
        <option value="">All Categories</option>
        <option value="Fresh Milk">Fresh Milk</option>
        <option value="Yoghurt">Yoghurt</option>
        <option value="Lala">Lala</option>
        <option value="Ghee">Ghee</option>
      </select>
      <select v-model="filters.status" @change="applyFilters" class="filter-select">
        <option value="">All Status</option>
        <option value="featured">Featured Only</option>
        <option value="non-featured">Non-Featured</option>
      </select>
    </div>
    
    <!-- Products Table -->
    <DataTable 
      :data="filteredProducts" 
      :columns="columns" 
      :loading="loading"
      :search-keys="['name', 'category', 'description']"
      search-placeholder="Search products..."
      @search="handleSearch"
    >
      <template #actions="{ row }">
        <PermissionGuard resource="products" action="update">
          <button @click="openEditModal(row)" class="btn-edit" title="Edit">
            <i class="fas fa-edit"></i>
          </button>
        </PermissionGuard>
        <PermissionGuard resource="products" action="delete">
          <button @click="confirmDelete(row)" class="btn-delete" title="Delete">
            <i class="fas fa-trash"></i>
          </button>
        </PermissionGuard>
      </template>
    </DataTable>
    
    <!-- Product Modal (Create/Edit) -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container glass-card modal-large">
        <div class="modal-header">
          <h2>{{ editingProduct ? 'Edit Product' : 'Create New Product' }}</h2>
          <button @click="closeModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveProduct" class="modal-form">
          <div class="form-row two-columns">
            <div class="form-group">
              <label>Product Name *</label>
              <input type="text" v-model="productForm.name" required>
            </div>
            <div class="form-group">
              <label>Category *</label>
              <select v-model="productForm.category" required>
                <option value="">Select Category</option>
                <option value="Fresh Milk">Fresh Milk</option>
                <option value="Yoghurt">Yoghurt</option>
                <option value="Lala">Lala</option>
                <option value="Ghee">Ghee</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>Description *</label>
            <textarea v-model="productForm.description" rows="4" required></textarea>
          </div>
          
          <div class="form-group">
            <label>Key Benefits</label>
            <textarea v-model="productForm.benefits" rows="2" placeholder="List key benefits of this product"></textarea>
          </div>
          
          <div class="form-row two-columns">
            <div class="form-group">
              <label>Packaging Sizes</label>
              <input type="text" v-model="productForm.packaging_sizes" placeholder="e.g., 500ml, 1L, 2L">
            </div>
            <div class="form-group">
              <label>Featured Product</label>
              <label class="toggle-switch">
                <input type="checkbox" v-model="productForm.featured">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          <div class="form-group">
            <label>Nutritional Information</label>
            <textarea v-model="productForm.nutritional_info" rows="3" placeholder="Nutritional facts per serving"></textarea>
          </div>
          
          <div class="form-group">
            <label>Ingredients</label>
            <textarea v-model="productForm.ingredients" rows="3" placeholder="List all ingredients"></textarea>
          </div>
          
          <!-- Image Upload Section -->
          <div class="form-group">
            <label>Product Image</label>
            <div class="image-upload-area" @click="triggerFileUpload" @dragover.prevent @drop.prevent="handleDrop">
              <input type="file" ref="fileInput" @change="handleFileSelect" accept="image/*" style="display: none">
              
              <div v-if="productForm.image_url || imagePreview" class="image-preview">
                <img :src="imagePreview || productForm.image_url" alt="Product image">
                <div class="image-overlay">
                  <button type="button" @click.stop="removeImage" class="remove-image-btn">
                    <i class="fas fa-trash"></i> Remove
                  </button>
                </div>
              </div>
              <div v-else class="upload-placeholder">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Click or drag image here</p>
                <small>PNG, JPG, GIF up to 5MB</small>
              </div>
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ saving ? 'Saving...' : 'Save Product' }}
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
          <h2>Delete Product</h2>
          <button @click="closeDeleteModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ productToDelete?.name }}</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>
        </div>
        <div class="modal-actions">
          <button @click="deleteProduct" class="btn-danger">
            <i class="fas fa-trash"></i> Delete Permanently
          </button>
          <button @click="closeDeleteModal" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { toast } from 'vue3-toastify'
import DataTable from './DataTable.vue'
import PermissionGuard from './PermissionGuard.vue'
import api from '@/services/api'

const products = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingProduct = ref(null)
const productToDelete = ref(null)
const imagePreview = ref('')
const fileInput = ref(null)

const filters = ref({
  search: '',
  category: '',
  status: ''
})

const productForm = ref({
  name: '',
  category: '',
  description: '',
  benefits: '',
  packaging_sizes: '',
  nutritional_info: '',
  ingredients: '',
  image_url: '',
  featured: false
})

const columns = [
  { key: 'image_url', label: 'Image', type: 'image', width: '80px' },
  { key: 'name', label: 'Product Name', sortable: true },
  { key: 'category', label: 'Category', sortable: true },
  { key: 'description', label: 'Description', type: 'truncate', maxLength: 80 },
  { key: 'featured', label: 'Featured', type: 'status' }
]

const filteredProducts = computed(() => {
  let result = [...products.value]
  
  if (filters.value.category) {
    result = result.filter(p => p.category === filters.value.category)
  }
  
  if (filters.value.status === 'featured') {
    result = result.filter(p => p.featured)
  } else if (filters.value.status === 'non-featured') {
    result = result.filter(p => !p.featured)
  }
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(p => 
      p.name.toLowerCase().includes(search) ||
      p.description.toLowerCase().includes(search) ||
      p.category?.toLowerCase().includes(search)
    )
  }
  
  return result
})

const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await api.get('/products')
    products.value = response.data
  } catch (error) {
    console.error('Error fetching products:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingProduct.value = null
  productForm.value = {
    name: '',
    category: '',
    description: '',
    benefits: '',
    packaging_sizes: '',
    nutritional_info: '',
    ingredients: '',
    image_url: '',
    featured: false
  }
  imagePreview.value = ''
  showModal.value = true
}

const openEditModal = (product) => {
  editingProduct.value = product
  productForm.value = { ...product }
  imagePreview.value = ''
  showModal.value = true
}

const saveProduct = async () => {
  saving.value = true
  try {
    if (editingProduct.value) {
      await api.put(`/admin/products/${editingProduct.value.id}`, productForm.value)
      toast.success('Product updated successfully')
    } else {
      await api.post('/admin/products', productForm.value)
      toast.success('Product created successfully')
    }
    await fetchProducts()
    closeModal()
  } catch (error) {
    console.error('Error saving product:', error)
  } finally {
    saving.value = false
  }
}

const confirmDelete = (product) => {
  productToDelete.value = product
  showDeleteModal.value = true
}

const deleteProduct = async () => {
  try {
    await api.delete(`/admin/products/${productToDelete.value.id}`)
    toast.success('Product deleted successfully')
    await fetchProducts()
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting product:', error)
  }
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await uploadImage(file)
  }
}

const handleDrop = async (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    await uploadImage(file)
  }
}

const uploadImage = async (file) => {
  if (file.size > 5 * 1024 * 1024) {
    toast.error('Image size must be less than 5MB')
    return
  }
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('folder', 'products')
  
  try {
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    productForm.value.image_url = response.data.url
    imagePreview.value = URL.createObjectURL(file)
    toast.success('Image uploaded successfully')
  } catch (error) {
    console.error('Error uploading image:', error)
    toast.error('Failed to upload image')
  }
}

const removeImage = () => {
  productForm.value.image_url = ''
  imagePreview.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const applyFilters = () => {
  // Filters are reactive, no additional action needed
}

const debouncedSearch = useDebounceFn(() => {
  applyFilters()
}, 300)

const handleSearch = (query) => {
  filters.value.search = query
}

const closeModal = () => {
  showModal.value = false
  editingProduct.value = null
  imagePreview.value = ''
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  productToDelete.value = null
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products-management {
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
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  flex: 1;
  min-width: 200px;
}

.search-box i {
  color: #999;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  width: 100%;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
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

.btn-delete {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
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

.modal-large {
  max-width: 800px;
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

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-row.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
}

/* Toggle Switch */
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

/* Image Upload */
.image-upload-area {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-upload-area:hover {
  border-color: #f59e0b;
  background: #fef3c7;
}

.upload-placeholder {
  text-align: center;
  padding: 2rem;
}

.upload-placeholder i {
  font-size: 3rem;
  color: #999;
  margin-bottom: 1rem;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: 8px;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.remove-image-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
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
  .form-row.two-columns {
    grid-template-columns: 1fr;
  }
  
  .filters-bar {
    flex-direction: column;
  }
  
  .modal-large {
    max-width: 95%;
  }
}
</style>