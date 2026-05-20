<template>
  <div class="admin-dashboard">
    <div class="admin-sidebar">
      <h2>Admin Panel</h2>
      <nav>
        <button @click="activeTab = 'products'" :class="{ active: activeTab === 'products' }">
          Manage Products
        </button>
        <button @click="activeTab = 'blog'" :class="{ active: activeTab === 'blog' }">
          Manage Blog
        </button>
        <button @click="handleLogout" class="logout-btn">Logout</button>
      </nav>
    </div>
    
    <div class="admin-content">
      <!-- Products Management -->
      <div v-if="activeTab === 'products'" class="products-admin">
        <div class="admin-header">
          <h3>Products</h3>
          <button @click="showProductModal = true" class="btn btn-primary">Add New Product</button>
        </div>
        
        <table class="admin-table">
          <thead>
            <tr><th>Image</th><th>Name</th><th>Category</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="product in products" :key="product.id">
              <td>
                <img v-if="product.image_url" :src="product.image_url" width="50" style="border-radius: 4px;">
                <div v-else class="no-image">No image</div>
              </td>
              <td>{{ product.name }}</td>
              <td>{{ product.category }}</td>
              <td>
                <button @click="editProduct(product)" class="edit-btn">Edit</button>
                <button @click="deleteProduct(product.id)" class="delete-btn">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Blog Management -->
      <div v-if="activeTab === 'blog'" class="blog-admin">
        <div class="admin-header">
          <h3>Blog Posts</h3>
          <button @click="showBlogModal = true" class="btn btn-primary">Add New Post</button>
        </div>
        
        <table class="admin-table">
          <thead>
            <tr><th>Image</th><th>Title</th><th>Status</th><th>Views</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="post in blogPosts" :key="post.id">
              <td>
                <img v-if="post.featured_image" :src="post.featured_image" width="50" style="border-radius: 4px;">
                <div v-else class="no-image">No image</div>
              </td>
              <td>{{ post.title }}</td>
              <td>{{ post.status }}</td>
              <td>{{ post.views }}</td>
              <td>
                <button @click="editPost(post)" class="edit-btn">Edit</button>
                <button @click="deletePost(post.id)" class="delete-btn">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Product Modal with Image Upload -->
    <div class="modal" v-if="showProductModal" @click.self="showProductModal = false">
      <div class="modal-content large">
        <h3>{{ editingProduct ? 'Edit Product' : 'Add Product' }}</h3>
        <form @submit.prevent="saveProduct">
          <input type="text" v-model="productForm.name" placeholder="Product Name" required>
          
          <select v-model="productForm.category">
            <option value="">Select Category</option>
            <option value="Fresh Milk">Fresh Milk</option>
            <option value="Yoghurt">Yoghurt</option>
            <option value="Lala">Lala</option>
            <option value="Ghee">Ghee</option>
          </select>
          
          <textarea v-model="productForm.description" placeholder="Description" rows="3" required></textarea>
          <textarea v-model="productForm.benefits" placeholder="Key Benefits" rows="2"></textarea>
          <input type="text" v-model="productForm.packaging_sizes" placeholder="Packaging Sizes (e.g., 500ml, 1L, 2L)">
          <textarea v-model="productForm.nutritional_info" placeholder="Nutritional Information" rows="2"></textarea>
          <textarea v-model="productForm.ingredients" placeholder="Ingredients" rows="2"></textarea>
          
          <!-- Image Upload Component -->
          <div class="form-group">
            <label>Product Image</label>
            <ImageUpload
              :currentImage="productForm.image_url"
              folder="products"
              :entityId="editingProduct?.id"
              entityType="product"
              @image-uploaded="(url) => productForm.image_url = url"
              @image-removed="productForm.image_url = ''"
            />
          </div>
          
          <label class="checkbox-label">
            <input type="checkbox" v-model="productForm.featured"> Featured Product
          </label>
          
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary">Save</button>
            <button type="button" @click="closeProductModal" class="btn">Cancel</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Blog Modal with Image Upload -->
    <div class="modal" v-if="showBlogModal" @click.self="showBlogModal = false">
      <div class="modal-content large">
        <h3>{{ editingPost ? 'Edit Post' : 'Add Blog Post' }}</h3>
        <form @submit.prevent="savePost">
          <input type="text" v-model="blogForm.title" placeholder="Title" required>
          <input type="text" v-model="blogForm.slug" placeholder="URL Slug (e.g., my-post-title)" required>
          <input type="text" v-model="blogForm.excerpt" placeholder="Short Excerpt">
          <textarea v-model="blogForm.content" placeholder="Full Content" rows="8" required></textarea>
          
          <!-- Image Upload Component -->
          <div class="form-group">
            <label>Featured Image</label>
            <ImageUpload
              :currentImage="blogForm.featured_image"
              folder="blogs"
              :entityId="editingPost?.id"
              entityType="blog"
              @image-uploaded="(url) => blogForm.featured_image = url"
              @image-removed="blogForm.featured_image = ''"
            />
          </div>
          
          <select v-model="blogForm.status">
            <option value="published">Published</option>
            <option value="draft">Draft</option>
          </select>
          
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary">Save</button>
            <button type="button" @click="closeBlogModal" class="btn">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import router from '../../router'
import ImageUpload from '../../components/ImageUpload.vue'

export default {
  name: 'AdminDashboard',
  components: {
    ImageUpload
  },
  data() {
    return {
      activeTab: 'products',
      products: [],
      blogPosts: [],
      showProductModal: false,
      showBlogModal: false,
      editingProduct: null,
      editingPost: null,
      productForm: {
        name: '', category: '', description: '', benefits: '',
        packaging_sizes: '', nutritional_info: '', ingredients: '',
        image_url: '', featured: false
      },
      blogForm: {
        title: '', slug: '', excerpt: '', content: '',
        featured_image: '', status: 'published'
      }
    }
  },
  mounted() {
    this.checkAuth()
    this.fetchProducts()
    this.fetchBlogPosts()
  },
  methods: {
    async checkAuth() {
      try {
        const response = await axios.get('/api/admin/check')
        if (!response.data.is_admin) {
          router.push('/')
        }
      } catch {
        router.push('/')
      }
    },
    async fetchProducts() {
      const response = await axios.get('/api/products')
      this.products = response.data
    },
    async fetchBlogPosts() {
      const response = await axios.get('/api/blog')
      this.blogPosts = response.data
    },
    editProduct(product) {
      this.editingProduct = product
      this.productForm = { ...product }
      this.showProductModal = true
    },
    async saveProduct() {
      try {
        if (this.editingProduct) {
          await axios.put(`/api/admin/products/${this.editingProduct.id}`, this.productForm)
        } else {
          await axios.post('/api/admin/products', this.productForm)
        }
        this.closeProductModal()
        this.fetchProducts()
        alert('Product saved successfully!')
      } catch (error) {
        console.error('Error saving product:', error)
        alert('Error saving product')
      }
    },
    async deleteProduct(id) {
      if (confirm('Delete this product?')) {
        await axios.delete(`/api/admin/products/${id}`)
        this.fetchProducts()
      }
    },
    editPost(post) {
      this.editingPost = post
      this.blogForm = { ...post }
      this.showBlogModal = true
    },
    async savePost() {
      try {
        if (this.editingPost) {
          await axios.put(`/api/admin/blog/${this.editingPost.id}`, this.blogForm)
        } else {
          await axios.post('/api/admin/blog', this.blogForm)
        }
        this.closeBlogModal()
        this.fetchBlogPosts()
        alert('Blog post saved successfully!')
      } catch (error) {
        console.error('Error saving blog post:', error)
        alert('Error saving blog post')
      }
    },
    async deletePost(id) {
      if (confirm('Delete this post?')) {
        await axios.delete(`/api/admin/blog/${id}`)
        this.fetchBlogPosts()
      }
    },
    closeProductModal() {
      this.showProductModal = false
      this.productForm = { name: '', category: '', description: '', benefits: '', packaging_sizes: '', nutritional_info: '', ingredients: '', image_url: '', featured: false }
      this.editingProduct = null
    },
    closeBlogModal() {
      this.showBlogModal = false
      this.blogForm = { title: '', slug: '', excerpt: '', content: '', featured_image: '', status: 'published' }
      this.editingPost = null
    },
    async handleLogout() {
      await axios.post('/api/admin/logout')
      localStorage.removeItem('isAdmin')
      router.push('/')
    }
  }
}
</script>

<style scoped>
/* Previous styles remain, add these new ones */
.form-group {
  margin: 1rem 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--primary-blue);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1rem 0;
  cursor: pointer;
}

.no-image {
  width: 50px;
  height: 50px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #999;
  border-radius: 4px;
}

/* Same modal and table styles as before */
.admin-dashboard {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: 250px;
  background: var(--primary-blue);
  color: white;
  padding: 2rem;
}

.admin-sidebar h2 {
  margin-bottom: 2rem;
}

.admin-sidebar nav {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.admin-sidebar button {
  background: rgba(255,255,255,0.1);
  border: none;
  padding: 12px;
  color: white;
  cursor: pointer;
  border-radius: 8px;
  text-align: left;
}

.admin-sidebar button.active {
  background: rgba(255,255,255,0.3);
}

.logout-btn {
  margin-top: 2rem;
  background: #dc2626 !important;
}

.admin-content {
  flex: 1;
  padding: 2rem;
  background: var(--gray-light);
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.admin-table {
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.admin-table th,
.admin-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.edit-btn, .delete-btn {
  padding: 5px 10px;
  margin: 0 5px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.edit-btn {
  background: var(--primary-blue);
  color: white;
}

.delete-btn {
  background: #dc2626;
  color: white;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  padding: 2rem;
}

.modal-content.large {
  max-width: 700px;
}

.modal-content input,
.modal-content select,
.modal-content textarea {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
</style>