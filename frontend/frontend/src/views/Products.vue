<template>
  <main>
    <!-- Hero Section -->
    <section class="products-hero">
      <div class="hero-background">
        <div class="hero-overlay"></div>
        <div class="hero-pattern"></div>
      </div>
      
      <div class="container">
        <div class="hero-content">
          <div class="hero-text animate-fade-in-up">
            <span class="hero-badge">Our Range</span>
            <h1 class="hero-title">Premium <span class="highlight">Dairy Products</span></h1>
            <p class="hero-description">
              Discover our complete range of Mount Kenya Milk products, crafted with care 
              from the finest milk sourced from our cooperative farmers around the scenic 
              Mount Kenya region.
            </p>
            <div class="category-pills">
              <button 
                v-for="cat in categories" 
                :key="cat"
                @click="selectedCategory = cat"
                :class="['category-pill', { active: selectedCategory === cat }]"
              >
                {{ cat }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <span>Browse our collection</span>
        <div class="scroll-mouse"></div>
      </div>
    </section>

    <!-- Products Grid Section -->
    <section class="products-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Premium Quality</span>
          <h2 class="section-title">From Our Farms to Your Table</h2>
          <p class="section-subtitle">
            Each product is carefully crafted to deliver the highest quality nutrition
          </p>
        </div>
        
        <div class="products-grid">
          <div 
            v-for="product in filteredProducts" 
            :key="product.id" 
            class="product-card glass-card animate-on-scroll"
          >
            <div class="product-image">
              <img 
                v-if="product.image_url" 
                :src="product.image_url" 
                :alt="product.name"
                @error="handleImageError"
              >
              <div v-else class="image-placeholder">
                <span>🥛</span>
              </div>
              <div class="product-overlay">
                <router-link :to="`/products/${product.id}`" class="view-details">
                  View Details
                  <span class="arrow">→</span>
                </router-link>
              </div>
            </div>
            
            <div class="product-info">
              <div class="product-category">{{ product.category }}</div>
              <h3>{{ product.name }}</h3>
              <p>{{ truncate(product.description, 100) }}</p>
              
              <div class="product-features" v-if="product.benefits">
                <div class="feature-item">
                  <span class="feature-icon">✓</span>
                  <span>{{ truncate(product.benefits, 60) }}</span>
                </div>
              </div>
              
              <div class="product-packaging" v-if="product.packaging_sizes">
                <span class="packaging-label">Available sizes:</span>
                <div class="packaging-sizes">
                  <span v-for="size in product.packaging_sizes.split(',')" :key="size" class="size-badge">
                    {{ size.trim() }}
                  </span>
                </div>
              </div>
              
              <router-link :to="`/products/${product.id}`" class="product-link">
                Learn More
                <span class="arrow">→</span>
              </router-link>
            </div>
          </div>
        </div>
        
        <div v-if="filteredProducts.length === 0" class="no-results glass-card">
          <div class="no-results-icon">🔍</div>
          <h3>No products found</h3>
          <p>Try adjusting your category filter</p>
          <button @click="selectedCategory = 'All'" class="btn-reset">View All Products</button>
        </div>
      </div>
    </section>

    <!-- Quality Assurance Section -->
    <section class="quality-section">
      <div class="container">
        <div class="quality-grid">
          <div class="quality-content">
            <span class="section-badge">Quality Guaranteed</span>
            <h2>Committed to Excellence</h2>
            <p>Every product that bears the Mount Kenya Milk name undergoes rigorous quality testing at every stage of production.</p>
            
            <div class="quality-features">
              <div class="quality-feature">
                <div class="quality-icon">🔬</div>
                <div>
                  <strong>Laboratory Tested</strong>
                  <p>Each batch tested for quality and safety</p>
                </div>
              </div>
              <div class="quality-feature">
                <div class="quality-icon">🌿</div>
                <div>
                  <strong>Pure & Natural</strong>
                  <p>No artificial preservatives or additives</p>
                </div>
              </div>
              <div class="quality-feature">
                <div class="quality-icon">🏭</div>
                <div>
                  <strong>Modern Processing</strong>
                  <p>State-of-the-art facilities</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="quality-stats glass-card">
            <div class="stat-circle">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#e0e7ff" stroke-width="5"/>
                <circle cx="50" cy="50" r="45" fill="none" stroke="#f59e0b" stroke-width="5" 
                        stroke-dasharray="283" stroke-dashoffset="28" stroke-linecap="round"
                        transform="rotate(-90 50 50)"/>
              </svg>
              <div class="stat-circle-content">
                <span class="stat-value">99.9%</span>
                <span class="stat-label">Quality Score</span>
              </div>
            </div>
            <div class="stat-badge">
              <span>⭐ ISO 22000 Certified</span>
              <span>⭐ HACCP Compliant</span>
              <span>⭐ KEBS Approved</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Why Choose Us Section -->
    <section class="why-choose-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Why Choose Us</span>
          <h2 class="section-title">The Mount Kenya Milk Difference</h2>
          <p class="section-subtitle">
            What sets our products apart from the rest
          </p>
        </div>
        
        <div class="benefits-grid">
          <div class="benefit-card glass-card animate-on-scroll">
            <div class="benefit-icon">🥛</div>
            <h3>100% Pure</h3>
            <p>No mixing, no adulteration - just pure, fresh milk from healthy cows</p>
          </div>
          <div class="benefit-card glass-card animate-on-scroll delay-1">
            <div class="benefit-icon">👨‍🌾</div>
            <h3>Farmer Owned</h3>
            <p>Direct from our cooperative members, ensuring fair prices and quality</p>
          </div>
          <div class="benefit-card glass-card animate-on-scroll delay-2">
            <div class="benefit-icon">🔒</div>
            <h3>Traceable Source</h3>
            <p>Complete transparency from farm to packaging</p>
          </div>
          <div class="benefit-card glass-card animate-on-scroll delay-3">
            <div class="benefit-icon">🚚</div>
            <h3>Fresh Delivery</h3>
            <p>Cold chain maintained throughout delivery</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card glass-card">
          <div class="cta-content">
            <h2>Ready to experience the difference?</h2>
            <p>Visit our online shop or contact our sales team for bulk orders</p>
            <div class="cta-buttons">
              <router-link to="/shop" class="btn btn-primary">
                Shop Online
                <span class="btn-icon">→</span>
              </router-link>
              <router-link to="/contact" class="btn btn-secondary">
                Contact Sales
              </router-link>
            </div>
          </div>
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
        const response = await axios.get('/api/products', {
          params: { cacheBust: Date.now() }
        })
        const data = response.data
        this.products = Array.isArray(data)
          ? data
          : (data?.items || [])
        this.$nextTick(() => {
          this.setupScrollAnimation()
        })
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
    },
    setupScrollAnimation() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible')
          }
        })
      }, { threshold: 0.1 })
      
      document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el)
      })
    }
  }
}
</script>

<style scoped>
/* Hero Section */
.products-hero {
  position: relative;
  min-height: 70vh;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" opacity="0.05"><path fill="white" d="M50,30 L60,50 L50,70 L40,50 Z"/><circle cx="70" cy="30" r="10"/><circle cx="30" cy="70" r="10"/></svg>') repeat;
}

.hero-pattern {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(to top, #f8fafc, transparent);
}

.hero-content {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 80px 0;
}

.hero-text {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.hero-badge {
  display: inline-block;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.85rem;
  color: white;
  margin-bottom: 20px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  line-height: 1.2;
  margin-bottom: 20px;
}

.hero-title .highlight {
  color: #f59e0b;
  position: relative;
  display: inline-block;
}

.hero-description {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.9);
  margin-bottom: 40px;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.category-pills {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.category-pill {
  padding: 8px 20px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 50px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.category-pill:hover,
.category-pill.active {
  background: #f59e0b;
  border-color: #f59e0b;
  transform: translateY(-2px);
}

.scroll-indicator {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  color: white;
  z-index: 1;
}

.scroll-indicator span {
  display: block;
  font-size: 0.8rem;
  margin-bottom: 10px;
  opacity: 0.7;
}

.scroll-mouse {
  width: 26px;
  height: 40px;
  border: 2px solid white;
  border-radius: 20px;
  position: relative;
  margin: 0 auto;
}

.scroll-mouse::after {
  content: '';
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 8px;
  background: white;
  border-radius: 2px;
  animation: scroll 2s infinite;
}

@keyframes scroll {
  0% { transform: translate(-50%, 0); opacity: 1; }
  100% { transform: translate(-50%, 15px); opacity: 0; }
}

/* Products Section */
.products-section {
  padding: 80px 0;
  background: #f8fafc;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-badge {
  display: inline-block;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.section-title {
  font-size: 2.5rem;
  color: #1e3a8a;
  margin-bottom: 20px;
}

.section-subtitle {
  color: #666;
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 30px;
}

.product-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.product-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.product-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.product-image {
  position: relative;
  height: 260px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.product-card:hover .product-image img {
  transform: scale(1.1);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  font-size: 4rem;
}

.product-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(30,58,138,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .product-overlay {
  opacity: 1;
}

.view-details {
  color: white;
  text-decoration: none;
  font-weight: 600;
  padding: 12px 24px;
  border: 2px solid white;
  border-radius: 50px;
  transition: all 0.3s;
}

.view-details:hover {
  background: white;
  color: #1e3a8a;
}

.view-details .arrow {
  display: inline-block;
  transition: transform 0.3s;
}

.view-details:hover .arrow {
  transform: translateX(5px);
}

.product-info {
  padding: 25px;
}

.product-category {
  display: inline-block;
  background: #e0e7ff;
  color: #1e3a8a;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.product-info h3 {
  font-size: 1.3rem;
  color: #1e3a8a;
  margin-bottom: 10px;
}

.product-info p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 15px;
}

.product-features {
  margin-bottom: 15px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #555;
  margin-bottom: 5px;
}

.feature-icon {
  color: #10b981;
  font-weight: bold;
}

.product-packaging {
  margin-bottom: 20px;
}

.packaging-label {
  font-size: 0.8rem;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.packaging-sizes {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.size-badge {
  background: #f3f4f6;
  color: #1e3a8a;
  padding: 4px 10px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 500;
}

.product-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #f59e0b;
  font-weight: 600;
  text-decoration: none;
}

.product-link .arrow {
  transition: transform 0.3s;
}

.product-link:hover .arrow {
  transform: translateX(5px);
}

/* No Results */
.no-results {
  text-align: center;
  padding: 60px;
  background: white;
}

.no-results-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.no-results h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

.no-results p {
  color: #666;
  margin-bottom: 20px;
}

.btn-reset {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-reset:hover {
  background: #3b82f6;
  transform: translateY(-2px);
}

/* Quality Section */
.quality-section {
  padding: 80px 0;
  background: white;
}

.quality-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: center;
}

.quality-content h2 {
  font-size: 2rem;
  color: #1e3a8a;
  margin: 20px 0;
}

.quality-content p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 30px;
}

.quality-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quality-feature {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.quality-icon {
  font-size: 2rem;
}

.quality-feature strong {
  display: block;
  color: #1e3a8a;
  margin-bottom: 5px;
}

.quality-feature p {
  margin: 0;
  font-size: 0.9rem;
}

.quality-stats {
  padding: 40px;
  text-align: center;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
}

.stat-circle {
  position: relative;
  width: 180px;
  height: 180px;
  margin: 0 auto 30px;
}

.stat-circle svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.stat-circle-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.stat-circle-content .stat-value {
  font-size: 2rem;
  font-weight: 800;
  display: block;
}

.stat-circle-content .stat-label {
  font-size: 0.8rem;
  opacity: 0.9;
}

.stat-badge {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-badge span {
  background: rgba(255,255,255,0.15);
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.85rem;
}

/* Why Choose Section */
.why-choose-section {
  padding: 80px 0;
  background: #f8fafc;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.benefit-card {
  padding: 40px 30px;
  text-align: center;
  background: white;
  transition: transform 0.3s;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.benefit-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.benefit-card:hover {
  transform: translateY(-10px);
}

.benefit-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.benefit-card h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

.benefit-card p {
  color: #666;
  line-height: 1.6;
}

/* CTA Section */
.cta-section {
  padding: 80px 0;
  background: white;
}

.cta-card {
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  padding: 60px;
  text-align: center;
  color: white;
}

.cta-content h2 {
  font-size: 2rem;
  margin-bottom: 15px;
}

.cta-content p {
  margin-bottom: 30px;
  opacity: 0.9;
}

.cta-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
  padding: 12px 30px;
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: white;
  color: #1e3a8a;
  transform: translateY(-2px);
}

/* Animations */
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Glass Card Effect */
.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

/* Responsive */
@media (max-width: 968px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .quality-grid {
    grid-template-columns: 1fr;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  .category-pills {
    gap: 8px;
  }
  
  .category-pill {
    padding: 6px 14px;
    font-size: 0.8rem;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .cta-card {
    padding: 40px 20px;
  }
  
  .cta-content h2 {
    font-size: 1.5rem;
  }
  
  .benefits-grid {
    grid-template-columns: 1fr;
  }
}
</style>