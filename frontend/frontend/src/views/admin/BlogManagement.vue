<template>
  <div class="blog-management">
    <div class="header">
      <h2>Blog Management</h2>
      <PermissionGuard resource="blog" action="create">
        <button @click="showAddModal = true" class="btn-primary">
          <i class="fas fa-plus"></i> Add Post
        </button>
      </PermissionGuard>
    </div>
    
    <DataTable 
      :data="posts" 
      :columns="columns" 
      :loading="loading"
      :search-keys="['title', 'author', 'status']"
      search-placeholder="Search posts..."
    >
      <template #actions="{ row }">
        <PermissionGuard resource="blog" action="update">
          <button @click="editPost(row)" class="btn-edit">
            <i class="fas fa-edit"></i> Edit
          </button>
        </PermissionGuard>
        <PermissionGuard resource="blog" action="delete">
          <button @click="confirmDelete(row)" class="btn-delete">
            <i class="fas fa-trash"></i> Delete
          </button>
        </PermissionGuard>
      </template>
    </DataTable>
    
    <div class="coming-soon-notice">
      <i class="fas fa-info-circle"></i>
      <p>Full blog management with rich text editor, image upload, and SEO tools coming soon!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from './DataTable.vue'
import PermissionGuard from './PermissionGuard.vue'
import axios from 'axios'

const posts = ref([])
const loading = ref(false)
const showAddModal = ref(false)

const columns = [
  { key: 'featured_image', label: 'Image', type: 'image', width: '80px' },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'status', label: 'Status', type: 'status', sortable: true },
  { key: 'views', label: 'Views', sortable: true, width: '100px' },
  { key: 'created_at', label: 'Date', type: 'date', sortable: true, width: '120px' }
]

const fetchPosts = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/blog?simple=true&per_page=100')
    posts.value = Array.isArray(response.data) ? response.data : (response.data.items || [])
  } catch (error) {
    console.error('Error fetching posts:', error)
    posts.value = []
  } finally {
    loading.value = false
  }
}

const editPost = (post) => {
  console.log('Edit post:', post)
  alert('Edit functionality coming soon!')
}

const confirmDelete = (post) => {
  if (confirm(`Delete "${post.title}"?`)) {
    console.log('Delete post:', post.id)
    alert('Delete functionality coming soon!')
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.blog-management {
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