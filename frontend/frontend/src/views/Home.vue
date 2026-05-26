<template>
  <main>
    <!-- Hero Section with Parallax Effect -->
    <section class="hero-section">
      <div class="hero-background">
        <div class="hero-overlay"></div>
        <video autoplay muted loop class="hero-video" poster="/images/hero-bg.jpg">
          <source src="/videos/hero-bg.mp4" type="video/mp4">
        </video>
      </div>
      
      <div class="hero-content">
        <div class="container">
          <div class="hero-text animate-fade-in-up">
            <span class="hero-badge">🇰🇪 Kenya's Biggest Dairy Co-operative</span>
            <h1 class="hero-title">
              Pure <span class="highlight">Mount Kenya</span><br>
              Milk Delivered Fresh
            </h1>
            <p class="hero-description">
              From our farms to your table, experience the richness of nature 
              with Mount Kenya Milk products.
            </p>
            <div class="hero-buttons">
              <router-link to="/products" class="btn btn-primary btn-large">
                Explore Products
                <span class="btn-icon">→</span>
              </router-link>
              <router-link to="/about" class="btn btn-outline-light btn-large">
                Learn More
              </router-link>
            </div>
          </div>
          
          <div class="hero-stats animate-fade-in-up delay-2">
            <div class="stat-card" v-for="stat in statistics.slice(0, 4)" :key="stat.label">
              <div class="stat-number">{{ stat.value }}{{ stat.suffix }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <span>Scroll to explore</span>
        <div class="scroll-mouse"></div>
      </div>
    </section>

    <!-- Floating Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Why Choose Us</span>
          <h2 class="section-title">Excellence in Every Drop</h2>
          <p class="section-subtitle">
            Discover what makes Mount Kenya Milk the preferred choice for millions
          </p>
        </div>
        
        <div class="features-grid">
          <div class="feature-card glass-card" v-for="feature in features" :key="feature.title">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            <div class="feature-link">
              <span>Learn more</span>
              <span class="arrow">→</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Products Showcase with Floating Cards -->
    <section class="products-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Our Collection</span>
          <h2 class="section-title">Premium Dairy Products</h2>
          <p class="section-subtitle">
            Crafted with care for your family's nutrition
          </p>
        </div>
        
        <div class="products-slider">
          <div class="products-grid">
            <div class="product-card glass-card" v-for="product in featuredProducts" :key="product.id">
              <div class="product-image">
                <img v-if="product.image_url" :src="product.image_url" :alt="product.name">
                <div v-else class="image-placeholder">
                  <span>🥛</span>
                </div>
              </div>
              <div class="product-badge" v-if="product.featured">Featured</div>
              <h3>{{ product.name }}</h3>
              <p>{{ truncate(product.description, 80) }}</p>
              <router-link :to="`/products/${product.id}`" class="product-link">
                Discover Product
                <span class="arrow">→</span>
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="view-all">
          <router-link to="/products" class="btn btn-secondary">
            View All Products
            <span class="btn-icon">→</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- About Us with Floating Quote -->
    <section class="about-section">
      <div class="container">
        <div class="about-grid">
          <div class="about-content">
            <span class="section-badge">Our Story</span>
            <h2>Kenya's Largest<br>Dairy Co-operative</h2>
            <p>Meru Central Dairy Co-operative Union Ltd has grown from humble beginnings to become Kenya's biggest dairy processor, empowering over 120,000 farmers and serving millions of customers nationwide.</p>
            <div class="about-stats">
              <div class="about-stat">
                <div class="stat-number">50+</div>
                <div class="stat-label">Years of Excellence</div>
              </div>
              <div class="about-stat">
                <div class="stat-number">120K+</div>
                <div class="stat-label">Happy Farmers</div>
              </div>
              <div class="about-stat">
                <div class="stat-number">10M+</div>
                <div class="stat-label">Customers Served</div>
              </div>
            </div>
            <router-link to="/about" class="btn btn-primary">
              Learn More About Us
            </router-link>
          </div>
          
          <div class="about-image glass-card">
            <img src="/images/about1.jpg" alt="Meru Dairy Farm">
            <div class="floating-quote">
              <div class="quote-icon">"</div>
              <p>Quality milk from happy cows in the pristine slopes of Mount Kenya</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Testimonials</span>
          <h2 class="section-title">What Our Customers Say</h2>
          <p class="section-subtitle">
            Trusted by millions across Kenya
          </p>
        </div>
        
        <div class="testimonials-slider">
          <div class="testimonials-grid">
            <div class="testimonial-card glass-card" v-for="testimonial in testimonials" :key="testimonial.id">
              <div class="quote-mark">"</div>
              <p class="testimonial-text">{{ testimonial.content }}</p>
              <div class="testimonial-author">
                <div class="author-info">
                  <strong>{{ testimonial.name }}</strong>
                  <span>{{ testimonial.role }}</span>
                </div>
                <div class="rating">
                  <span v-for="i in 5" :key="i" class="star">★</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Blog Section -->
    <section class="blog-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Latest Updates</span>
          <h2 class="section-title">From Our Blog</h2>
          <p class="section-subtitle">
            Stay updated with the latest news and stories
          </p>
        </div>
        
        <div class="blog-grid">
          <div class="blog-card glass-card" v-for="post in latestBlogs" :key="post.id">
            <div class="blog-image">
              <img v-if="post.featured_image" :src="post.featured_image" :alt="post.title">
              <div v-else class="image-placeholder">📝</div>
            </div>
            <div class="blog-content">
              <div class="blog-meta">
                <span class="blog-date">{{ formatDate(post.created_at) }}</span>
                <span class="blog-views">👁️ {{ post.views }}</span>
              </div>
              <h3>{{ post.title }}</h3>
              <p>{{ truncate(post.excerpt || post.content, 100) }}</p>
              <router-link :to="`/blog/${post.slug}`" class="read-more">
                Read Article
                <span class="arrow">→</span>
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="view-all">
          <router-link to="/blog" class="btn btn-secondary">
            View All Articles
            <span class="btn-icon">→</span>
          </router-link>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
  data() {
    return {
      currentSlide: 0,
      features: [
        {
          icon: '🥛',
          title: '100% Pure & Fresh',
          description: 'Pasteurized and packed fresh daily from the slopes of Mount Kenya'
        },
        {
          icon: '👨‍🌾',
          title: 'Farmer Owned',
          description: 'Supporting over 120,000 local farmers through fair trade practices'
        },
        {
          icon: '🔬',
          title: 'Quality Assured',
          description: 'Rigorous quality testing at every stage of production'
        },
        {
          icon: '🚚',
          title: 'Nationwide Delivery',
          description: 'Reaching millions of customers across Kenya every day'
        }
      ],
      featuredProducts: [],
      statistics: [],
      testimonials: [],
      latestBlogs: []
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const [productsRes, statsRes, testimonialsRes, blogsRes] = await Promise.all([
          axios.get('/api/products'),
          axios.get('/api/statistics'),
          axios.get('/api/testimonials'),
          axios.get('/api/blog')
        ])
        
        this.featuredProducts = productsRes.data.filter(p => p.featured).slice(0, 6)
        this.statistics = statsRes.data
        this.testimonials = testimonialsRes.data
        this.latestBlogs = blogsRes.data.slice(0, 3)
      } catch (error) {
        console.error('Error fetching data:', error)
        // Fallback statistics
        this.statistics = [
          { label: 'Our Farmers', value: '120,000', suffix: '+' },
          { label: 'Cooperative Societies', value: '120', suffix: '+' },
          { label: 'Litres Processed', value: '600,000', suffix: '+' },
          { label: 'Customers Served', value: '10,000,000', suffix: '+' }
        ]
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    truncate(text, length) {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    }
  }
}
</script>

<style scoped>
/* Global Styles */
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Hero Section */
.hero-section {
  position: relative;
  min-height: 100vh;
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
  z-index: 0;
}

.hero-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(30,58,138,0.9) 0%, rgba(59,130,246,0.8) 100%);
}

.hero-content {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 100px 0;
}

.hero-text {
  max-width: 700px;
  margin-bottom: 60px;
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
  font-size: 4rem;
  font-weight: 800;
  color: white;
  line-height: 1.2;
  margin-bottom: 20px;
}

.hero-title .highlight {
  position: relative;
  display: inline-block;
}

.hero-title .highlight::after {
  content: '';
  position: absolute;
  bottom: 5px;
  left: 0;
  width: 100%;
  height: 12px;
  background: #f59e0b;
  opacity: 0.4;
  z-index: -1;
}

.hero-description {
  font-size: 1.2rem;
  color: rgba(255,255,255,0.9);
  margin-bottom: 30px;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.btn-large {
  padding: 14px 32px;
  font-size: 1rem;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.btn-outline-light {
  background: transparent;
  color: white;
  border: 2px solid white;
  border-radius: 50px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-outline-light:hover {
  background: white;
  color: #1e3a8a;
  transform: translateY(-2px);
}

.btn-icon {
  transition: transform 0.3s;
}

.btn-large:hover .btn-icon {
  transform: translateX(5px);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255,255,255,0.2);
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #f59e0b;
  margin-bottom: 5px;
}

.stat-label {
  color: white;
  font-size: 0.9rem;
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

/* Animations */
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

.delay-2 {
  animation-delay: 0.2s;
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

/* Section Styles */
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

/* Features Section */
.features-section {
  padding: 80px 0;
  background: #f8fafc;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.feature-card {
  padding: 30px;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.3rem;
  color: #1e3a8a;
  margin-bottom: 15px;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.feature-link {
  color: #f59e0b;
  font-weight: 600;
  cursor: pointer;
}

.feature-link .arrow {
  transition: transform 0.3s;
  display: inline-block;
}

.feature-link:hover .arrow {
  transform: translateX(5px);
}

/* Products Section */
.products-section {
  padding: 80px 0;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.product-card {
  padding: 0;
  overflow: hidden;
  position: relative;
  transition: all 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.product-image {
  height: 250px;
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

.product-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #f59e0b;
  color: white;
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
}

.product-card h3 {
  padding: 20px 20px 10px;
  font-size: 1.2rem;
  color: #1e3a8a;
}

.product-card p {
  padding: 0 20px;
  color: #666;
  margin-bottom: 20px;
}

.product-link {
  display: inline-block;
  margin: 0 20px 20px;
  color: #f59e0b;
  font-weight: 600;
  text-decoration: none;
}

.product-link .arrow {
  transition: transform 0.3s;
  display: inline-block;
}

.product-link:hover .arrow {
  transform: translateX(5px);
}

/* Glass Card Effect */
.glass-card {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

/* About Section */
.about-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
}

.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: center;
}

.about-content h2 {
  font-size: 2.5rem;
  color: #1e3a8a;
  margin-bottom: 20px;
}

.about-content p {
  color: #666;
  line-height: 1.8;
  margin-bottom: 30px;
}

.about-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.about-stat .stat-number {
  font-size: 1.8rem;
  color: #f59e0b;
}

.about-stat .stat-label {
  color: #666;
  font-size: 0.85rem;
}

.about-image {
  position: relative;
  padding: 20px;
  background: white;
}

.about-image img {
  width: 100%;
  border-radius: 15px;
}

.floating-quote {
  position: absolute;
  bottom: -20px;
  right: -20px;
  background: white;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 250px;
  border-left: 4px solid #f59e0b;
}

.quote-icon {
  font-size: 2rem;
  color: #f59e0b;
  font-family: serif;
  margin-bottom: 5px;
}

.floating-quote p {
  font-size: 0.85rem;
  color: #333;
  margin: 0;
}

/* Testimonials Section */
.testimonials-section {
  padding: 80px 0;
  background: #f8fafc;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.testimonial-card {
  padding: 30px;
  position: relative;
}

.quote-mark {
  font-size: 4rem;
  color: #f59e0b;
  opacity: 0.3;
  font-family: serif;
  position: absolute;
  top: 20px;
  left: 20px;
}

.testimonial-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.testimonial-author {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.author-info strong {
  display: block;
  color: #1e3a8a;
  margin-bottom: 5px;
}

.author-info span {
  font-size: 0.85rem;
  color: #666;
}

.rating .star {
  color: #fbbf24;
  font-size: 0.9rem;
}

/* Blog Section */
.blog-section {
  padding: 80px 0;
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.blog-card {
  overflow: hidden;
  transition: transform 0.3s;
}

.blog-card:hover {
  transform: translateY(-5px);
}

.blog-image {
  height: 220px;
  overflow: hidden;
}

.blog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.blog-card:hover .blog-image img {
  transform: scale(1.1);
}

.blog-content {
  padding: 25px;
}

.blog-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-size: 0.85rem;
  color: #666;
}

.blog-card h3 {
  font-size: 1.2rem;
  color: #1e3a8a;
  margin-bottom: 10px;
  line-height: 1.4;
}

.blog-card p {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.6;
}

.read-more {
  color: #f59e0b;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.read-more .arrow {
  transition: transform 0.3s;
}

.read-more:hover .arrow {
  transform: translateX(5px);
}

.view-all {
  text-align: center;
}

.btn-secondary {
  background: transparent;
  color: #1e3a8a;
  border: 2px solid #1e3a8a;
  border-radius: 50px;
  padding: 12px 30px;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary:hover {
  background: #1e3a8a;
  color: white;
  transform: translateY(-2px);
}

.btn-secondary:hover .btn-icon {
  transform: translateX(5px);
}

/* Responsive */
@media (max-width: 968px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .about-grid {
    grid-template-columns: 1fr;
  }
  
  .floating-quote {
    position: static;
    margin-top: 20px;
  }
  
  .section-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-buttons {
    flex-direction: column;
  }
  
  .features-grid,
  .products-grid,
  .testimonials-grid,
  .blog-grid {
    grid-template-columns: 1fr;
  }
  
  .about-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .hero-stats {
    grid-template-columns: 1fr 1fr;
  }
}
</style>