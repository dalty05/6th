<!-- frontend/src/views/ProductDetail.vue -->

<template>
  <div class="product-detail-page">
    <div class="container">
      <!-- Breadcrumb -->
      <nav class="breadcrumb">
        <router-link to="/">Home</router-link>
        <span>/</span>
        <router-link to="/">Products</router-link>
        <span>/</span>
        <span class="current">{{ product?.name || 'Product' }}</span>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading product...</p>
      </div>

      <!-- Product Not Found -->
      <div v-else-if="!product" class="not-found">
        <i class="fas fa-box-open"></i>
        <h2>Product Not Found</h2>
        <p>Sorry, the product you're looking for doesn't exist.</p>
        <router-link to="/" class="btn-home">Return Home</router-link>
      </div>

      <!-- Product Content -->
      <div v-else class="product-content">
        <div class="product-grid">
          <!-- Product Image -->
          <div class="product-image-section">
            <div class="product-image-main">
              <img 
                v-if="product.image_url" 
                :src="product.image_url" 
                :alt="product.name"
                @error="handleImageError"
              >
              <div v-else class="image-placeholder">
                <i class="fas fa-milk"></i>
              </div>
              <div class="featured-badge" v-if="product.featured">
                <i class="fas fa-star"></i> Featured
              </div>
            </div>
          </div>

          <!-- Product Info -->
          <div class="product-info-section">
            <div class="product-category-badge">
              <i class="fas fa-tag"></i> {{ product.category || 'Uncategorized' }}
            </div>
            
            <h1 class="product-title">{{ product.name }}</h1>
            
            <div class="product-description" v-html="product.description"></div>

            <!-- Product Details -->
            <div class="product-details">
              <div v-if="product.packaging_sizes" class="detail-item">
                <i class="fas fa-weight-hanging"></i>
                <span><strong>Packaging:</strong> {{ product.packaging_sizes }}</span>
              </div>
              
              <div v-if="product.ingredients" class="detail-item">
                <i class="fas fa-list"></i>
                <span><strong>Ingredients:</strong> {{ product.ingredients }}</span>
              </div>
              
              <div v-if="product.nutritional_info" class="detail-item">
                <i class="fas fa-chart-line"></i>
                <span><strong>Nutritional Info:</strong> {{ product.nutritional_info }}</span>
              </div>
              
              <div v-if="product.benefits" class="detail-item">
                <i class="fas fa-heart"></i>
                <span><strong>Benefits:</strong> {{ product.benefits }}</span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="product-actions">
              <a 
                href="https://shop.mountkenyamilk.co.ke/" 
                target="_blank" 
                class="btn btn-primary btn-large"
              >
                <i class="fas fa-shopping-cart"></i> Shop Online
              </a>
              <button @click="openOutletsModal" class="btn btn-outline btn-large">
                <i class="fas fa-store"></i> Find Physical Stores
              </button>
            </div>

            <!-- Explore More Products -->
            <div class="explore-more">
              <router-link to="/" class="btn btn-secondary btn-large">
                <i class="fas fa-boxes"></i> Explore More Products
              </router-link>
            </div>

            <!-- Share and QR Code -->
            <div class="product-share-section">
              <div class="share-buttons">
                <span class="share-label">Share:</span>
                <button @click="shareProduct" class="share-btn facebook">
                  <i class="fab fa-facebook-f"></i>
                </button>
                <button @click="shareProduct" class="share-btn twitter">
                  <i class="fab fa-twitter"></i>
                </button>
                <button @click="shareProduct" class="share-btn whatsapp">
                  <i class="fab fa-whatsapp"></i>
                </button>
                <button @click="shareProduct" class="share-btn email">
                  <i class="fas fa-envelope"></i>
                </button>
                <button @click="copyProductLink" class="share-btn copy">
                  <i class="fas fa-copy"></i>
                </button>
              </div>

              <!-- QR Code -->
              <div v-if="product.qr_code_url" class="product-qr">
                <img :src="product.qr_code_url" alt="QR Code" class="qr-image">
                <p class="qr-hint">Scan to view product details</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Related Products -->
        <div v-if="relatedProducts.length > 0" class="related-products">
          <h2>You May Also Like</h2>
          <div class="related-grid">
            <div v-for="related in relatedProducts" :key="related.id" class="related-card">
              <router-link :to="`/product/${related.slug || related.id}`">
                <img 
                  v-if="related.image_url" 
                  :src="related.image_url" 
                  :alt="related.name"
                  @error="handleImageError"
                >
                <div v-else class="related-placeholder">
                  <i class="fas fa-milk"></i>
                </div>
                <h3>{{ related.name }}</h3>
                <p>{{ truncate(related.description, 60) }}</p>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Outlets Modal -->
    <div class="modal-overlay" v-if="showOutletsModal" @click.self="showOutletsModal = false">
      <div class="modal-container outlets-modal">
        <div class="modal-header">
          <h2><i class="fas fa-store"></i> Find Our Stores & Depots</h2>
          <button class="close-btn" @click="showOutletsModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <!-- Reuse the OutletsModal component -->
          <OutletsModal @close="showOutletsModal = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue3-toastify'
import api from '@/services/api'
import OutletsModal from '@/components/modals/OutletsModal.vue'

export default {
  name: 'ProductDetail',
  components: {
    OutletsModal
  },
  
  setup() {
    const route = useRoute()
    const product = ref(null)
    const relatedProducts = ref([])
    const loading = ref(true)
    const showOutletsModal = ref(false)

    const openOutletsModal = () => {
      showOutletsModal.value = true
      document.body.style.overflow = 'hidden'
    }

    const loadProduct = async () => {
      loading.value = true
      try {
        const slug = route.params.slug
        const response = await api.get(`/products/slug/${slug}`)
        product.value = response.data
        
        await loadRelatedProducts()
      } catch (error) {
        product.value = null
      } finally {
        loading.value = false
      }
    }

    const loadRelatedProducts = async () => {
      try {
        const response = await api.get('/products')
        const allProducts = response.data.data || []
        relatedProducts.value = allProducts
          .filter(p => p.id !== product.value.id && p.category === product.value.category)
          .slice(0, 4)
      } catch (error) {
        relatedProducts.value = []
      }
    }

    const shareProduct = () => {
      const url = window.location.href
      if (navigator.share) {
        navigator.share({
          title: product.value.name,
          text: `Check out ${product.value.name} - ${product.value.description}`,
          url: url
        }).catch(() => {})
      } else {
        navigator.clipboard.writeText(url).then(() => {
          toast.success('Product link copied to clipboard!')
        }).catch(() => {
          prompt('Copy this link:', url)
        })
      }
    }

    const copyProductLink = () => {
      const url = window.location.href
      navigator.clipboard.writeText(url).then(() => {
        toast.success('Product link copied to clipboard!')
      }).catch(() => {
        prompt('Copy this link:', url)
      })
    }

    const truncate = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const handleImageError = (event) => {
      event.target.src = '/images/placeholder.png'
    }

    onMounted(() => {
      loadProduct()
    })

    return {
      product,
      relatedProducts,
      loading,
      showOutletsModal,
      openOutletsModal,
      shareProduct,
      copyProductLink,
      truncate,
      handleImageError
    }
  }
}
</script>

<style scoped>
.product-detail-page {
  padding: 40px 0 60px;
  background: #f8fafc;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  margin-bottom: 32px;
  color: #64748b;
}

.breadcrumb a {
  color: #2563eb;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb .current {
  color: #1a1a2e;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Not Found */
.not-found {
  text-align: center;
  padding: 80px 0;
}

.not-found i {
  font-size: 64px;
  color: #cbd5e1;
  margin-bottom: 16px;
}

.not-found h2 {
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.not-found p {
  color: #64748b;
  margin: 0 0 24px 0;
}

.btn-home {
  display: inline-block;
  padding: 10px 24px;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-home:hover {
  background: #1d4ed8;
}

/* Product Grid */
.product-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.product-image-section {
  position: relative;
}

.product-image-main {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: #f1f5f9;
  aspect-ratio: 1;
}

.product-image-main img {
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
  font-size: 64px;
  color: #94a3b8;
  background: #f1f5f9;
}

.featured-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #f59e0b;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.product-info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.product-category-badge {
  display: inline-block;
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  width: fit-content;
}

.product-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}

.product-description {
  color: #475569;
  line-height: 1.8;
  font-size: 16px;
}

.product-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  color: #475569;
}

.detail-item i {
  color: #2563eb;
  width: 20px;
  margin-top: 2px;
}

/* Action Buttons */
.product-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  border: none;
  font-size: 16px;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-outline {
  background: transparent;
  color: #1a1a2e;
  border: 2px solid #e2e8f0;
}

.btn-outline:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}

.btn-secondary {
  background: #f1f5f9;
  color: #1a1a2e;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #e2e8f0;
  transform: translateY(-2px);
}

.btn-large {
  padding: 14px 32px;
  font-size: 16px;
}

/* Explore More */
.explore-more {
  margin-top: 4px;
}

.explore-more .btn {
  width: 100%;
  justify-content: center;
}

/* Share Section */
.product-share-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.share-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.share-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.share-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: white;
}

.share-btn.facebook {
  background: #1877f2;
}

.share-btn.twitter {
  background: #000000;
}

.share-btn.whatsapp {
  background: #25d366;
}

.share-btn.email {
  background: #ea4335;
}

.share-btn.copy {
  background: #64748b;
}

.share-btn:hover {
  transform: scale(1.1);
}

.product-qr {
  display: flex;
  align-items: center;
  gap: 12px;
}

.qr-image {
  width: 80px;
  height: 80px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 4px;
}

.qr-hint {
  font-size: 12px;
  color: #94a3b8;
}

/* Related Products */
.related-products {
  margin-top: 48px;
}

.related-products h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 24px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.related-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.related-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.related-card a {
  text-decoration: none;
  color: inherit;
  display: block;
}

.related-card img,
.related-placeholder {
  width: 100%;
  height: 150px;
  object-fit: cover;
  background: #f1f5f9;
}

.related-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #94a3b8;
}

.related-card h3 {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 12px 12px 4px;
}

.related-card p {
  font-size: 13px;
  color: #64748b;
  margin: 0 12px 12px;
  display: -webkit-box;
  /* -webkit-line-clamp: 2; */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Outlets Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container.outlets-modal {
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  background: white;
  border-radius: 16px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}

.modal-header h2 i {
  color: #2563eb;
  margin-right: 8px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0 8px;
}

.close-btn:hover {
  color: #1a1a2e;
}

.modal-body {
  padding: 24px;
  max-height: calc(90vh - 80px);
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .product-grid {
    grid-template-columns: 1fr;
    padding: 20px;
    gap: 24px;
  }

  .product-title {
    font-size: 24px;
  }

  .product-actions {
    flex-direction: column;
  }

  .product-actions .btn {
    justify-content: center;
  }

  .product-share-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .product-qr {
    align-self: center;
  }

  .related-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }

  .modal-container.outlets-modal {
    max-width: 100%;
    margin: 10px;
  }
}
</style>