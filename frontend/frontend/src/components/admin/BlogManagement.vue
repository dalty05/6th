<!-- frontend/src/components/admin/BlogManagement.vue -->
<template>
  <div class="blog-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1>Blog Management</h1>
        <p>Create, manage, and publish blog posts</p>
      </div>
      <div class="header-actions">
        <button @click="openCreateModal" class="btn-create">
          <i class="fas fa-plus"></i> Write New Post
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-newspaper"></i></div>
        <div class="stat-info">
          <h3>{{ posts.length }}</h3>
          <p>Total Posts</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-check-circle"></i></div>
        <div class="stat-info">
          <h3>{{ publishedCount }}</h3>
          <p>Published</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-pencil-alt"></i></div>
        <div class="stat-info">
          <h3>{{ draftCount }}</h3>
          <p>Drafts</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-eye"></i></div>
        <div class="stat-info">
          <h3>{{ totalViews }}</h3>
          <p>Total Views</p>
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
          placeholder="Search posts by title..."
          @input="filterPosts"
        >
      </div>
      <select v-model="statusFilter" @change="filterPosts" class="filter-select">
        <option value="all">All Status</option>
        <option value="published">Published</option>
        <option value="draft">Draft</option>
      </select>
      <select v-model="authorFilter" @change="filterPosts" class="filter-select" v-if="isSuperAdmin">
        <option value="all">All Authors</option>
        <option v-for="author in uniqueAuthors" :key="author" :value="author">
          {{ author }}
        </option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading posts...</p>
    </div>

    <!-- Blog Cards Grid -->
    <div v-else class="blog-grid">
      <div v-for="post in filteredPosts" :key="post.id" class="blog-card">
        <!-- Featured Image -->
        <div class="blog-image" @click="openBlogDetail(post)">
          <img v-if="post.featured_image" :src="post.featured_image" :alt="post.title" @error="handleImageError">
          <div v-else class="image-placeholder">
            <i class="fas fa-newspaper"></i>
          </div>
          <div class="image-overlay">
            <button class="quick-view-btn">
              <i class="fas fa-eye"></i> Quick View
            </button>
          </div>
        </div>

        <!-- Status Badge -->
        <div class="status-badge" :class="post.status">
          <i v-if="post.status === 'published'" class="fas fa-check-circle"></i>
          <i v-else class="fas fa-pencil-alt"></i>
          {{ post.status === 'published' ? 'Published' : 'Draft' }}
        </div>

        <!-- Blog Content -->
        <div class="blog-content">
          <div class="blog-meta">
            <span class="blog-date">
              <i class="far fa-calendar-alt"></i> {{ formatDate(post.created_at) }}
            </span>
            <span class="blog-views">
              <i class="far fa-eye"></i> {{ post.views || 0 }} views
            </span>
            <span class="blog-author">
              <i class="far fa-user"></i> {{ post.author || 'Admin' }}
            </span>
          </div>

          <h3 class="blog-title">{{ truncate(post.title, 60) }}</h3>
          <p class="blog-excerpt">{{ truncate(post.excerpt || post.content, 120) }}</p>

          <!-- Actions -->
          <div class="blog-actions">
            <button @click="editPost(post)" class="action-btn edit" title="Edit">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button 
              v-if="isSuperAdmin && post.status === 'draft'" 
              @click="publishPost(post.id)" 
              class="action-btn publish" 
              title="Publish"
            >
              <i class="fas fa-check-circle"></i> Publish
            </button>
            <button 
              v-if="isSuperAdmin && post.status === 'published'" 
              @click="unpublishPost(post.id)" 
              class="action-btn unpublish" 
              title="Unpublish"
            >
              <i class="fas fa-eye-slash"></i> Unpublish
            </button>
            <button 
              @click="deletePost(post.id)" 
              class="action-btn delete" 
              title="Delete"
              :disabled="!canDeletePost(post)"
            >
              <i class="fas fa-trash"></i> Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="!loading && filteredPosts.length === 0" class="no-results">
      <i class="fas fa-newspaper"></i>
      <h3>No Blog Posts Found</h3>
      <p>Try adjusting your search or filters</p>
      <button @click="clearFilters" class="btn-clear">Clear Filters</button>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="filteredPosts.length > 0">
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
          <h2>{{ editingPost ? 'Edit Blog Post' : 'Create New Post' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        
        <form @submit.prevent="savePost" class="blog-form">
          <div class="form-group">
            <label>Title *</label>
            <input type="text" v-model="form.title" required placeholder="Enter post title">
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Slug *</label>
              <input type="text" v-model="form.slug" placeholder="url-friendly-slug">
            </div>
          </div>
          
          <div class="form-group">
            <label>Excerpt / Summary</label>
            <textarea v-model="form.excerpt" rows="2" placeholder="Brief summary of the post..."></textarea>
          </div>
          
          <div class="form-group">
            <label>Content *</label>
            <textarea v-model="form.content" rows="10" required placeholder="Write your blog content here..."></textarea>
          </div>
          
          <div class="form-group">
            <label>Featured Image</label>
            <div class="image-upload-area" @click="$refs.imageInput.click()">
              <input type="file" ref="imageInput" @change="handleImageUpload" accept="image/*" style="display: none">
              <div v-if="form.image_preview" class="image-preview">
                <img :src="form.image_preview" alt="Preview">
                <button type="button" class="remove-image" @click.stop="removeImage">×</button>
              </div>
              <div v-else class="upload-placeholder">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Click to upload featured image</p>
                <small>PNG, JPG, JPEG up to 5MB</small>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Saving...' : (editingPost ? 'Update Post' : 'Create Post') }}
            </button>
          </div>
        </form>
        
        <!-- Status Info for non-super admin -->
        <div v-if="!isSuperAdmin" class="status-info">
          <i class="fas fa-info-circle"></i>
          Your post will be saved as <strong>Draft</strong>. Only Super Admin can publish.
        </div>
      </div>
    </div>

    <!-- Blog Detail Modal (Quick View) -->
    <div class="modal-overlay" v-if="showDetailModal" @click.self="closeDetailModal">
      <div class="modal-container detail-modal">
        <div class="modal-header">
          <h2>{{ selectedPost?.title }}</h2>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="detail-image" v-if="selectedPost?.featured_image">
            <img :src="selectedPost.featured_image" :alt="selectedPost.title">
          </div>
          <div class="detail-meta">
            <span><i class="far fa-calendar-alt"></i> {{ formatDate(selectedPost?.created_at) }}</span>
            <span><i class="far fa-eye"></i> {{ selectedPost?.views || 0 }} views</span>
            <span><i class="far fa-user"></i> {{ selectedPost?.author || 'Admin' }}</span>
            <span :class="['status-badge-small', selectedPost?.status]">
              {{ selectedPost?.status === 'published' ? 'Published' : 'Draft' }}
            </span>
          </div>
          <div class="detail-excerpt" v-if="selectedPost?.excerpt">
            <i class="fas fa-quote-left"></i>
            <p>{{ selectedPost.excerpt }}</p>
          </div>
          <div class="detail-content">
            <p>{{ truncate(selectedPost?.content || selectedPost?.excerpt, 500) }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeDetailModal" class="btn-secondary">Close</button>
          <button @click="editPost(selectedPost); closeDetailModal()" class="btn-primary">Edit Post</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'
import authService from '@/services/auth'

const posts = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showDetailModal = ref(false)
const editingPost = ref(null)
const selectedPost = ref(null)

// Filters
const searchQuery = ref('')
const statusFilter = ref('all')
const authorFilter = ref('all')
const currentPage = ref(1)
const itemsPerPage = 9

// Current user
const currentUser = authService.getUser()
const isSuperAdmin = computed(() => currentUser?.role === 'super_admin')

// Form data
const form = ref({
  title: '',
  slug: '',
  excerpt: '',
  content: '',
  featured_image: '',
  image_preview: null,
  image_file: null
})

// Computed
const publishedCount = computed(() => posts.value.filter(p => p.status === 'published').length)
const draftCount = computed(() => posts.value.filter(p => p.status === 'draft').length)
const totalViews = computed(() => posts.value.reduce((sum, p) => sum + (p.views || 0), 0))

const uniqueAuthors = computed(() => {
  const authors = posts.value.map(p => p.author).filter(a => a)
  return [...new Set(authors)]
})

const filteredPosts = computed(() => {
  let filtered = [...posts.value]
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.title.toLowerCase().includes(query) || 
      (p.excerpt && p.excerpt.toLowerCase().includes(query))
    )
  }
  
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(p => p.status === statusFilter.value)
  }
  
  if (authorFilter.value !== 'all' && isSuperAdmin.value) {
    filtered = filtered.filter(p => p.author === authorFilter.value)
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredPosts.value.length / itemsPerPage))
const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredPosts.value.slice(start, start + itemsPerPage)
})

// Methods
const loadPosts = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/blog')
    posts.value = response.data
  } catch (error) {
    console.error('Error loading posts:', error)
    toast.error('Failed to load blog posts')
  } finally {
    loading.value = false
  }
}

const filterPosts = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = 'all'
  authorFilter.value = 'all'
  currentPage.value = 1
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const openCreateModal = () => {
  editingPost.value = null
  form.value = {
    title: '',
    slug: '',
    excerpt: '',
    content: '',
    featured_image: '',
    image_preview: null,
    image_file: null
  }
  showModal.value = true
}

const editPost = (post) => {
  editingPost.value = post
  form.value = {
    title: post.title,
    slug: post.slug,
    excerpt: post.excerpt || '',
    content: post.content,
    featured_image: post.featured_image || '',
    image_preview: null,
    image_file: null
  }
  showModal.value = true
}

const openBlogDetail = (post) => {
  selectedPost.value = post
  showDetailModal.value = true
}

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    toast.error('Invalid file type. Please upload an image.')
    return
  }
  
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
  if (editingPost.value) {
    form.value.featured_image = ''
  }
}

const savePost = async () => {
  if (!form.value.title || !form.value.content) {
    toast.error('Please fill in title and content')
    return
  }
  
  // Auto-generate slug if not provided
  if (!form.value.slug && form.value.title) {
    form.value.slug = form.value.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
  }
  
  saving.value = true
  
  try {
    let featuredImage = form.value.featured_image
    
    if (form.value.image_file) {
      const uploadData = new FormData()
      uploadData.append('file', form.value.image_file)
      uploadData.append('folder', 'blogs')
      
      const uploadResponse = await api.post('/upload', uploadData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      featuredImage = uploadResponse.data.url
    }
    
    const postData = {
      title: form.value.title,
      slug: form.value.slug,
      excerpt: form.value.excerpt,
      content: form.value.content,
      featured_image: featuredImage
    }
    
    if (editingPost.value) {
      await api.put(`/admin/blog/${editingPost.value.id}`, postData)
      toast.success('Blog post updated successfully')
    } else {
      await api.post('/admin/blog', postData)
      toast.success('Blog post created successfully')
    }
    
    closeModal()
    await loadPosts()
  } catch (error) {
    console.error('Error saving post:', error)
    toast.error(error.response?.data?.error || 'Failed to save post')
  } finally {
    saving.value = false
  }
}

const publishPost = async (id) => {
  if (confirm('Publish this blog post? It will be visible to the public.')) {
    try {
      await api.post(`/admin/blog/${id}/publish`)
      toast.success('Blog post published successfully')
      await loadPosts()
    } catch (error) {
      console.error('Error publishing post:', error)
      toast.error('Failed to publish post')
    }
  }
}

const unpublishPost = async (id) => {
  if (confirm('Unpublish this blog post? It will be hidden from the public.')) {
    try {
      await api.post(`/admin/blog/${id}/unpublish`)
      toast.success('Blog post unpublished')
      await loadPosts()
    } catch (error) {
      console.error('Error unpublishing post:', error)
      toast.error('Failed to unpublish post')
    }
  }
}

const deletePost = async (id) => {
  if (confirm('Are you sure you want to delete this blog post? This action cannot be undone.')) {
    try {
      await api.delete(`/admin/blog/${id}`)
      toast.success('Blog post deleted')
      await loadPosts()
    } catch (error) {
      console.error('Error deleting post:', error)
      toast.error('Failed to delete post')
    }
  }
}

const canDeletePost = (post) => {
  if (isSuperAdmin.value) return true
  // Admin can only delete their own draft posts
  return post.status === 'draft' && post.author === currentUser?.full_name
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const handleImageError = (event) => {
  event.target.src = '/images/placeholder.png'
}

const closeModal = () => {
  showModal.value = false
  editingPost.value = null
  if (form.value.image_preview) {
    URL.revokeObjectURL(form.value.image_preview)
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedPost.value = null
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.blog-management {
  padding: 0;
}

/* Header */
.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e3a8a;
  margin: 0 0 0.25rem;
}

.header-left p {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0;
}

.btn-create {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-create:hover {
  background: #f59e0b;
  transform: translateY(-1px);
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.blue { background: #e0e7ff; color: #1e3a8a; }
.stat-icon.green { background: #d1fae5; color: #065f46; }
.stat-icon.orange { background: #fed7aa; color: #9a3412; }
.stat-icon.purple { background: #e0e7ff; color: #1e3a8a; }

.stat-icon i {
  font-size: 1.25rem;
}

.stat-info h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  font-size: 0.75rem;
  margin: 0;
  color: #6b7280;
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
  border-radius: 8px;
  font-size: 0.85rem;
}

.filter-select {
  padding: 0.6rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  font-size: 0.85rem;
  cursor: pointer;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #1e3a8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Blog Grid - Cards */
.blog-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.blog-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
  position: relative;
}

.blog-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

.blog-image {
  height: 180px;
  background: #f8fafc;
  overflow: hidden;
  cursor: pointer;
  position: relative;
}

.blog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.blog-card:hover .blog-image img {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #cbd5e1;
  font-size: 2rem;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.blog-image:hover .image-overlay {
  opacity: 1;
}

.quick-view-btn {
  background: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
}

/* Status Badge */
.status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.status-badge.published {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.draft {
  background: #fef3c7;
  color: #92400e;
}

/* Blog Content */
.blog-content {
  padding: 1rem;
}

.blog-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.7rem;
  color: #9ca3af;
}

.blog-meta i {
  margin-right: 0.25rem;
}

.blog-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a8a;
  margin: 0 0 0.5rem;
  line-height: 1.4;
}

.blog-excerpt {
  font-size: 0.8rem;
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Blog Actions */
.blog-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.action-btn {
  flex: 1;
  padding: 0.4rem 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.7rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  transition: all 0.2s;
}

.action-btn.edit {
  background: #3b82f6;
  color: white;
}

.action-btn.edit:hover {
  background: #2563eb;
}

.action-btn.publish {
  background: #10b981;
  color: white;
}

.action-btn.publish:hover {
  background: #059669;
}

.action-btn.unpublish {
  background: #f59e0b;
  color: white;
}

.action-btn.unpublish:hover {
  background: #d97706;
}

.action-btn.delete {
  background: #ef4444;
  color: white;
}

.action-btn.delete:hover {
  background: #dc2626;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* No Results */
.no-results {
  text-align: center;
  padding: 3rem;
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
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #1e3a8a;
  color: white;
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
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-container.large {
  max-width: 700px;
}

.modal-container.detail-modal {
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  background: white;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e3a8a;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #9ca3af;
}

.modal-body {
  padding: 1.25rem;
}

.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Blog Form */
.blog-form {
  padding: 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 0.8rem;
  color: #374151;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Image Upload */
.image-upload-area {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
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
  border-radius: 8px;
  cursor: pointer;
}

.btn-submit {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-info {
  padding: 0.75rem 1.25rem;
  background: #fef3c7;
  border-top: 1px solid #e5e7eb;
  font-size: 0.8rem;
  color: #92400e;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Detail Modal */
.detail-image {
  margin-bottom: 1rem;
  border-radius: 12px;
  overflow: hidden;
}

.detail-image img {
  width: 100%;
  height: auto;
  max-height: 250px;
  object-fit: cover;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.status-badge-small {
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
}

.status-badge-small.published {
  background: #d1fae5;
  color: #065f46;
}

.status-badge-small.draft {
  background: #fef3c7;
  color: #92400e;
}

.detail-excerpt {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  font-style: italic;
  color: #4b5563;
}

.btn-secondary {
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-primary {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

/* Responsive */
@media (max-width: 1200px) {
  .blog-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .blog-grid {
    grid-template-columns: 1fr;
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
    gap: 0;
  }
}
</style>