<template>
  <div class="products-management">
    <div class="header">
      <h2>Products Management</h2>
      <PermissionGuard resource="products" action="create">
        <button @click="showAddModal = true" class="btn-primary">
          <i class="fas fa-plus"></i> Add Product
        </button>
      </PermissionGuard>
    </div>
    
    <DataTable 
      :data="products" 
      :columns="columns" 
      :loading="loading"
      :search-keys="['name', 'category', 'description']"
      search-placeholder="Search products..."
    >
      <template #actions="{ row }">
        <PermissionGuard resource="products" action="update">
          <button @click="editProduct(row)" class="btn-edit">
            <i class="fas fa-edit"></i> Edit
          </button>
        </PermissionGuard>
        <PermissionGuard resource="products" action="delete">
          <button @click="confirmDelete(row)" class="btn-delete">
            <i class="fas fa-trash"></i> Delete
          </button>
        </PermissionGuard>
      </template>
    </DataTable>
    
    <div class="coming-soon-notice">
      <i class="fas fa-info-circle"></i>
      <p>Full product management with image upload, categories, and bulk actions coming soon!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from './DataTable.vue'
import PermissionGuard from './PermissionGuard.vue'
import axios from 'axios'

const products = ref([])
const loading = ref(false)
const showAddModal = ref(false)

const columns = [
  { key: 'image_url', label: 'Image', type: 'image', width: '80px' },
  { key: 'name', label: 'Product Name', sortable: true },
  { key: 'category', label: 'Category', sortable: true },
  { key: 'description', label: 'Description', type: 'truncate', maxLength: 80 }
]

const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/products')
    products.value = response.data
  } catch (error) {
    console.error('Error fetching products:', error)
  } finally {
    loading.value = false
  }
}

const editProduct = (product) => {
  console.log('Edit product:', product)
  alert('Edit functionality coming soon!')
}

const confirmDelete = (product) => {
  if (confirm(`Delete "${product.name}"?`)) {
    console.log('Delete product:', product.id)
    alert('Delete functionality coming soon!')
  }
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