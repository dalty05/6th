<template>
  <main>
    <section class="products-page">
      <div class="container">
        <!-- Hero Description Section -->
        <div class="products-hero">
          <div class="products-hero-content">
            <h1 class="section-title">Our Products</h1>
            <div class="products-description">
              <p>Discover the full range of Mount Kenya Milk products, crafted with care from the finest milk sourced from our cooperative farmers around the scenic Mount Kenya region. From fresh pasteurized milk to delicious yoghurts and traditional delicacies, each product maintains the highest standards of quality and nutrition.</p>
              <p>Whether you're looking for daily fresh milk, healthy probiotic yoghurts, or traditional fermented lala and pure ghee for cooking, our diverse product line caters to every need. All our products undergo rigorous quality testing to ensure you and your family receive nothing but the best.</p>
            </div>
            <div class="product-categories-badge">
              <span class="badge">🥛 Fresh Milk</span>
              <span class="badge">🍦 Yoghurt</span>
              <span class="badge">🥤 Lala</span>
              <span class="badge">🧈 Ghee</span>
            </div>
          </div>
        </div>
        
        <!-- Category Filters -->
        <div class="category-filters">
          <button v-for="cat in categories" :key="cat" 
                  @click="selectedCategory = cat"
                  :class="{ active: selectedCategory === cat }"
                  class="filter-btn">
            {{ cat }}
          </button>
        </div>
        
        <!-- Products Grid - Reduced Card Sizes -->
        <div class="products-grid">
          <div class="product-card" v-for="product in filteredProducts" :key="product.id">
            <div class="product-image-container">
              <img 
                v-if="product.image_url" 
                :src="product.image_url" 
                :alt="product.name"
                @error="handleImageError"
                class="product-image"
              >
              <div v-else class="image-placeholder">
                <svg width="100%" height="100%" viewBox="0 0 200 150" fill="none">
                  <rect width="200" height="150" fill="#e0e7ff"/>
                  <text x="100" y="85" text-anchor="middle" fill="#1e3a8a" font-size="12">No Image</text>
                </svg>
              </div>
            </div>
            
            <div class="product-info">
              <h3>{{ product.name }}</h3>
              <p class="product-category">{{ product.category }}</p>
              <p class="product-description">{{ truncate(product.description, 80) }}</p>
              <router-link :to="`/products/${product.id}`" class="btn-link">Learn More →</router-link>
            </div>
          </div>
        </div>
        
        <div v-if="filteredProducts.length === 0" class="no-results">
          <p>No products found in this category.</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Products',
  data() {
    return {
      products: [],
      selectedCategory: 'All'
    }
  },
  computed: {
    categories() {
      const cats = ['All', ...new Set(this.products.map(p => p.category).filter(c => c))]
      return cats
    },
    filteredProducts() {
      if (this.selectedCategory === 'All') {
        return this.products
      }
      return this.products.filter(p => p.category === this.selectedCategory)
    }
  },
  mounted() {
    this.fetchProducts()
  },
  methods: {
    async fetchProducts() {
      try {
        const response = await axios.get('/api/products')
        this.products = response.data
      } catch (error) {
        console.error('Error fetching products:', error)
      }
    },
    truncate(text, length) {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    },
    handleImageError(e) {
      e.target.style.display = 'none'
      if (e.target.parentElement.querySelector('.image-placeholder')) {
        e.target.parentElement.querySelector('.image-placeholder').style.display = 'flex'
      }
    }
  }
}
</script>

<style scoped>
.products-page {
  padding: 3rem 0 4rem;
  min-height: 70vh;
  background: #f8fafc;
}

/* Products Hero Section */
.products-hero {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
  border-radius: 16px;
}

.products-hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.section-title {
  font-size: 2.5rem;
  color: var(--primary-blue);
  margin-bottom: 1.5rem;
  position: relative;
  display: inline-block;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: var(--accent-blue);
  border-radius: 2px;
}

.products-description {
  margin: 2rem 0;
  text-align: center;
}

.products-description p {
  color: #4a5568;
  line-height: 1.7;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.product-categories-badge {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

.badge {
  background: white;
  color: var(--primary-blue);
  padding: 0.5rem 1.2rem;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
}

/* Category Filters */
.category-filters {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2.5rem;
}

.filter-btn {
  padding: 0.5rem 1.2rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  font-size: 0.85rem;
  color: #4a5568;
}

.filter-btn:hover,
.filter-btn.active {
  background: var(--primary-blue);
  color: white;
  border-color: var(--primary-blue);
  transform: translateY(-2px);
}

/* Products Grid - Reduced Card Sizes */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.product-image-container {
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: #f5f5f5;
  position: relative;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
}

.product-info {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-info h3 {
  font-size: 1rem;
  color: var(--primary-blue);
  margin-bottom: 0.25rem;
  font-weight: 600;
  line-height: 1.3;
}

.product-category {
  color: var(--accent-blue);
  font-size: 0.7rem;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.product-description {
  color: #64748b;
  font-size: 0.8rem;
  line-height: 1.4;
  margin-bottom: 0.75rem;
  flex: 1;
}

.btn-link {
  color: var(--primary-blue);
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: gap 0.3s;
  margin-top: 0.5rem;
}

.btn-link:hover {
  gap: 0.5rem;
  color: var(--accent-blue);
}

/* No Results */
.no-results {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  background: white;
  border-radius: 12px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .products-page {
    padding: 2rem 0 3rem;
  }
  
  .products-hero {
    padding: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  .products-description p {
    font-size: 0.9rem;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
  }
  
  .product-image-container {
    height: 160px;
  }
  
  .product-info {
    padding: 0.75rem;
  }
  
  .product-info h3 {
    font-size: 0.9rem;
  }
  
  .product-description {
    font-size: 0.75rem;
  }
  
  .badge {
    padding: 0.35rem 1rem;
    font-size: 0.8rem;
  }
  
  .filter-btn {
    padding: 0.4rem 1rem;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: 1fr;
    max-width: 320px;
    margin: 0 auto;
  }
  
  .product-image-container {
    height: 200px;
  }
  
  .product-categories-badge {
    gap: 0.5rem;
  }
  
  .badge {
    font-size: 0.75rem;
    padding: 0.3rem 0.8rem;
  }
}
</style>