<template>
  <main>
    <section class="product-detail">
      <div class="container">
        <div class="product-detail-grid" v-if="product">
          <div class="product-gallery">
            <div class="main-image">
              <img 
                v-if="product.image_url" 
                :src="product.image_url" 
                :alt="product.name"
                @error="handleImageError"
                class="product-main-image"
              >
              <div v-else class="image-placeholder-large">
                <svg width="100%" height="400" viewBox="0 0 500 400" fill="none">
                  <rect width="500" height="400" fill="#e0e7ff"/>
                  <text x="250" y="200" text-anchor="middle" fill="#1e3a8a" font-size="18">Product Image</text>
                </svg>
              </div>
            </div>
          </div>
          
          <div class="product-detail-info">
            <h1>{{ product.name }}</h1>
            <p class="category">{{ product.category }}</p>
            
            <div class="description">
              <h3>Description</h3>
              <p>{{ product.description }}</p>
            </div>
            
            <div class="benefits" v-if="product.benefits">
              <h3>Key Benefits</h3>
              <p>{{ product.benefits }}</p>
            </div>
            
            <div class="packaging" v-if="product.packaging_sizes">
              <h3>Packaging Sizes</h3>
              <p>{{ product.packaging_sizes }}</p>
            </div>
            
            <div class="ingredients" v-if="product.ingredients">
              <h3>Ingredients</h3>
              <p>{{ product.ingredients }}</p>
            </div>
            
            <div class="nutritional" v-if="product.nutritional_info">
              <h3>Nutritional Information</h3>
              <p>{{ product.nutritional_info }}</p>
            </div>
            
            <router-link to="/shop" class="btn btn-primary shop-now">Shop Online</router-link>
          </div>
        </div>
        
        <div v-else class="loading">
          <p>Loading product details...</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import axios from 'axios'
import { useTitle } from '../composables/useTitle'

export default {
  name: 'ProductDetail',
  data() {
    return {
      product: null
    }
  },
  setup() {
    const { setTitle } = useTitle()
    return { setTitle }
  },
  mounted() {
    this.fetchProduct()
  },
  methods: {
    async fetchProduct() {
      try {
        const id = this.$route.params.id
        const response = await axios.get(`/api/products/${id}`)
        this.product = response.data
        
        // Set dynamic title with product name
        if (this.product && this.product.name) {
          this.setTitle(this.product.name)
        }
      } catch (error) {
        console.error('Error fetching product:', error)
        this.$router.push('/products')
      }
    }
  },
  watch: {
    product: {
      handler(newProduct) {
        if (newProduct && newProduct.name) {
          this.setTitle(newProduct.name)
        }
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.product-detail {
  padding: 4rem 0;
  min-height: 70vh;
}

.product-detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

.product-gallery {
  position: sticky;
  top: 100px;
}

.main-image {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.product-main-image {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: contain;
  display: block;
  background: white;
}

.image-placeholder-large {
  width: 100%;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.product-detail-info h1 {
  color: var(--primary-blue);
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.category {
  color: var(--accent-blue);
  font-size: 1rem;
  margin-bottom: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.product-detail-info h3 {
  color: var(--primary-blue);
  margin: 1.5rem 0 0.5rem 0;
  font-size: 1.2rem;
}

.product-detail-info p {
  line-height: 1.6;
  color: #555;
}

.description p,
.benefits p,
.packaging p,
.ingredients p,
.nutritional p {
  margin-bottom: 0;
}

.shop-now {
  margin-top: 2rem;
  display: inline-block;
}

.loading {
  text-align: center;
  padding: 3rem;
}

/* Responsive Design */
@media (max-width: 968px) {
  .product-detail-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .product-gallery {
    position: relative;
    top: 0;
  }
  
  .product-main-image {
    max-height: 400px;
  }
  
  .product-detail-info h1 {
    font-size: 1.75rem;
  }
}

@media (max-width: 768px) {
  .product-detail {
    padding: 2rem 0;
  }
  
  .product-main-image {
    max-height: 300px;
  }
  
  .image-placeholder-large {
    height: 300px;
  }
  
  .product-detail-info h1 {
    font-size: 1.5rem;
  }
  
  .product-detail-info h3 {
    font-size: 1.1rem;
  }
}
</style>