<template>
  <div class="products-management">
    <div class="header">
      <h2>Products Management</h2>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i> Add Product
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading products...</p>
    </div>
    
    <div v-else class="products-table">
      <table class="data-table">
        <thead>
          <tr>
            <th>Image</th>
            <th>Name</th>
            <th>Category</th>
            <th>Description</th>
            <th>Featured</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>
              <img v-if="product.image_url" :src="product.image_url" class="product-image" @error="handleImageError">
              <div v-else class="no-image">📦</div>
            </td>
            <td><strong>{{ product.name || 'N/A' }}</strong></td>
            <td>{{ product.category || 'Uncategorized' }}</td>
            <td class="description-cell">{{ truncate(product.description, 80) }}</td>
            <td>
              <span class="status-badge" :class="product.featured ? 'active' : 'inactive'">
                {{ product.featured ? 'Featured' : 'Standard' }}
              </span>
            </td>
            <td class="actions-cell">
              <button @click="editProduct(product)" class="btn-edit" title="Edit">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="confirmDelete(product)" class="btn-delete" title="Delete">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
          <tr v-if="products.length === 0">
            <td colspan="6" class="empty-row">No products found. Click "Add Product" to create one.</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ editingProduct ? 'Edit Product' : 'Create Product' }}</h2>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveProduct" class="modal-form">
          <div class="form-group">
            <label>Product Name *</label>
            <input type="text" v-model="productForm.name" required>
          </div>
          
          <div class="form-group">
            <label>Category</label>
            <select v-model="productForm.category">
              <option value="">Select Category</option>
              <option value="Fresh Milk">Fresh Milk</option>
              <option value="Yoghurt">Yoghurt</option>
              <option value="Lala">Lala</option>
              <option value="Ghee">Ghee</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="productForm.description" rows="3" required></textarea>
          </div>
          
          <div class="form-group">
            <label>Benefits</label>
            <textarea v-model="productForm.benefits" rows="2" placeholder="Key benefits of this product"></textarea>
          </div>
          
          <div class="form-group">
            <label>Packaging Sizes</label>
            <input type="text" v-model="productForm.packaging_sizes" placeholder="e.g., 500ml, 1L, 2L">
          </div>
          
          <div class="form-group">
            <label>Image URL</label>
            <input type="text" v-model="productForm.image_url" placeholder="https://...">
          </div>
          
          <div class="form-group checkbox">
            <label>
              <input type="checkbox" v-model="productForm.featured">
              Featured Product
            </label>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Product' }}
            </button>
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-container small">
        <div class="modal-header">
          <h2>Confirm Delete</h2>
          <button @click="closeDeleteModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ productToDelete?.name }}</strong>?</p>
          <p class="warning">This action cannot be undone.</p>
        </div>
        <div class="modal-actions">
          <button @click="deleteProduct" class="btn-danger">Delete</button>
          <button @click="closeDeleteModal" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

export default {
  name: 'ProductsManagement',
  emits: ['refresh'],
  setup(props, { emit }) {
    const products = ref([])
    products.value = [] // Always give it a default empty array!

    const safeSetProducts = (value) => {
      // Guarantee an array to prevent `products.value is not iterable`.
      if (Array.isArray(value)) return value
      if (value && Array.isArray(value.products)) return value.products
      return []
    }

    const loading = ref(false)
    const saving = ref(false)
    const showModal = ref(false)
    const showDeleteModal = ref(false)
    const editingProduct = ref(null)
    const productToDelete = ref(null)
    
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
    
    const fetchProducts = async () => {
      loading.value = true
      try {
        const response = await api.get('/products')
        // API shape may be either:
        // - { data: [...] }
        // - { data: { products: [...] } }
        const payload = response?.data
        products.value = safeSetProducts(payload)
      } catch (error) {
        console.error('Error fetching products:', error)
        products.value = []
        toast.error('Failed to load products')
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
      showModal.value = true
    }
    
    const editProduct = (product) => {
      editingProduct.value = product
      productForm.value = { ...product }
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
        emit('refresh')
        closeModal()
      } catch (error) {
        console.error('Error saving product:', error)
        toast.error(error.response?.data?.error || 'Failed to save product')
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
        emit('refresh')
        closeDeleteModal()
      } catch (error) {
        console.error('Error deleting product:', error)
        toast.error('Failed to delete product')
      }
    }
    
    const truncate = (text, length) => {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    }
    
    const handleImageError = (e) => {
      e.target.style.display = 'none'
      e.target.parentElement.innerHTML = '📦'
    }
    
    const closeModal = () => {
      showModal.value = false
      editingProduct.value = null
    }
    
    const closeDeleteModal = () => {
      showDeleteModal.value = false
      productToDelete.value = null
    }
    
    onMounted(() => {
      fetchProducts()
    })
    
    return {
      products,
      loading,
      saving,
      showModal,
      showDeleteModal,
      editingProduct,
      productToDelete,
      productForm,
      openCreateModal,
      editProduct,
      saveProduct,
      confirmDelete,
      deleteProduct,
      truncate,
      handleImageError,
      closeModal,
      closeDeleteModal
    }
  }
}
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
}

.loading-state {
  text-align: center;
  padding: 3rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #1e3a8a;
}

.product-image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 8px;
}

.no-image {
  width: 50px;
  height: 50px;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.description-cell {
  max-width: 300px;
  word-break: break-word;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #f3f4f6;
  color: #374151;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.btn-edit, .btn-delete {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-edit {
  background: #3b82f6;
  color: white;
}

.btn-delete {
  background: #dc2626;
  color: white;
}

.btn-edit:hover, .btn-delete:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

.empty-row {
  text-align: center;
  padding: 2rem;
  color: #999;
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
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-container.small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
  font-size: 1.2rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
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
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: #333;
  font-size: 0.85rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.9rem;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
}

.warning {
  font-size: 0.8rem;
  color: #dc2626;
  margin-top: 0.5rem;
}
</style>