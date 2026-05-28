<template>
  <div class="blog-management">
    <div class="header">
      <h2>Blog Management</h2>
      <PermissionGuard resource="blog" action="create">
        <button @click="openCreateModal" class="btn-primary">
          <i class="fas fa-plus"></i> Write Post
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
          <button @click="openEditModal(row)" class="btn-edit">
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
    
    <!-- Blog Post Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container glass-card modal-large">
        <div class="modal-header">
          <h2>{{ editingPost ? 'Edit Post' : 'Create New Post' }}</h2>
          <button @click="closeModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="savePost" class="modal-form">
          <div class="form-group">
            <label>Title *</label>
            <input type="text" v-model="postForm.title" required>
          </div>
          
          <div class="form-group">
            <label>Slug *</label>
            <input type="text" v-model="postForm.slug" required>
            <small>URL-friendly version of the title (e.g., my-first-post)</small>
          </div>
          
          <div class="form-group">
            <label>Excerpt</label>
            <textarea v-model="postForm.excerpt" rows="2" placeholder="Short summary of the post"></textarea>
          </div>
          
          <div class="form-group">
            <label>Content *</label>
            <EasyMDE v-model="postForm.content" :options="editorOptions" />
          </div>
          
          <div class="form-row two-columns">
            <div class="form-group">
              <label>Status</label>
              <select v-model="postForm.status">
                <option value="published">Published</option>
                <option value="draft">Draft</option>
              </select>
            </div>
            <div class="form-group">
              <label>Featured Image</label>
              <div class="image-upload-area small" @click="triggerFileUpload">
                <input type="file" ref="fileInput" @change="handleFileSelect" accept="image/*" style="display: none">
                <div v-if="postForm.featured_image || imagePreview" class="image-preview small">
                  <img :src="imagePreview || postForm.featured_image" alt="Featured image">
                  <button type="button" @click.stop="removeImage" class="remove-image-btn small">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <div v-else class="upload-placeholder small">
                  <i class="fas fa-image"></i>
                  <span>Click to upload</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-save"></i>
              {{ saving ? 'Saving...' : 'Publish Post' }}
            </button>
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-container glass-card modal-small">
        <div class="modal-header">
          <h2>Delete Post</h2>
          <button @click="closeDeleteModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ postToDelete?.title }}</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>
        </div>
        <div class="modal-actions">
          <button @click="deletePost" class="btn-danger">
            <i class="fas fa-trash"></i> Delete Permanently
          </button>
          <button @click="closeDeleteModal" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import EasyMDE from 'vue3-easymde'
import 'easymde/dist/easymde.min.css'
import DataTable from './DataTable.vue'
import PermissionGuard from './PermissionGuard.vue'
import api from '@/services/api'

const posts = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingPost = ref(null)
const postToDelete = ref(null)
const imagePreview = ref('')
const fileInput = ref(null)

const editorOptions = {
  autosave: {
    enabled: true,
    uniqueId: 'blog-content',
    delay: 1000
  },
  toolbar: [
    'bold', 'italic', 'heading', '|',
    'quote', 'code', 'unordered-list', 'ordered-list', '|',
    'link', 'image', 'table', '|',
    'preview', 'guide'
  ],
  placeholder: 'Write your blog content here...'
}

const postForm = ref({
  title: '',
  slug: '',
  excerpt: '',
  content: '',
  featured_image: '',
  status: 'published'
})

const columns = [
  { key: 'featured_image', label: 'Image', type: 'image', width: '80px' },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'status', label: 'Status', type: 'status', sortable: true },
  { key: 'views', label: 'Views', sortable: true, width: '100px' },
  { key: 'created_at', label: 'Date', type: 'date', sortable: true, width: '120px' }
]

const generateSlug = (title) => {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

// Watch title to auto-generate slug
import { watch } from 'vue'
watch(() => postForm.value.title, (newTitle) => {
  if (!editingPost.value && newTitle) {
    postForm.value.slug = generateSlug(newTitle)
  }
})

const fetchPosts = async () => {
  loading.value = true
  try {
    const response = await api.get('/blog?simple=true&per_page=100')
    posts.value = Array.isArray(response.data) ? response.data : (response.data.items || [])
  } catch (error) {
    console.error('Error fetching posts:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingPost.value = null
  postForm.value = {
    title: '',
    slug: '',
    excerpt: '',
    content: '',
    featured_image: '',
    status: 'published'
  }
  imagePreview.value = ''
  showModal.value = true
}

const openEditModal = (post) => {
  editingPost.value = post
  postForm.value = { ...post }
  imagePreview.value = ''
  showModal.value = true
}

const savePost = async () => {
  saving.value = true
  try {
    if (editingPost.value) {
      await api.put(`/admin/blog/${editingPost.value.id}`, postForm.value)
      toast.success('Post updated successfully')
    } else {
      await api.post('/admin/blog', postForm.value)
      toast.success('Post created successfully')
    }
    await fetchPosts()
    closeModal()
  } catch (error) {
    console.error('Error saving post:', error)
  } finally {
    saving.value = false
  }
}

const confirmDelete = (post) => {
  postToDelete.value = post
  showDeleteModal.value = true
}

const deletePost = async () => {
  try {
    await api.delete(`/admin/blog/${postToDelete.value.id}`)
    toast.success('Post deleted successfully')
    await fetchPosts()
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting post:', error)
  }
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await uploadImage(file)
  }
}

const uploadImage = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('folder', 'blogs')
  
  try {
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    postForm.value.featured_image = response.data.url
    imagePreview.value = URL.createObjectURL(file)
    toast.success('Image uploaded successfully')
  } catch (error) {
    console.error('Error uploading image:', error)
    toast.error('Failed to upload image')
  }
}

const removeImage = () => {
  postForm.value.featured_image = ''
  imagePreview.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const closeModal = () => {
  showModal.value = false
  editingPost.value = null
  imagePreview.value = ''
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  postToDelete.value = null
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
/* Reuse styles from ProductsManagement.vue */
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
  max-width: 1000px;
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

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.7rem;
  color: #999;
}

.image-upload-area {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-upload-area.small {
  min-height: 100px;
}

.image-upload-area:hover {
  border-color: #f59e0b;
  background: #fef3c7;
}

.upload-placeholder {
  text-align: center;
  padding: 1.5rem;
}

.upload-placeholder.small {
  padding: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.upload-placeholder i {
  font-size: 2rem;
  color: #999;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 150px;
}

.image-preview.small {
  height: 100px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
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
}
</style>