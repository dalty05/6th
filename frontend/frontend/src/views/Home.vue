<template>
  <main>
    <!-- Hero Carousel -->
    <section class="hero">
      <div class="carousel">
        <div class="carousel-slide" v-for="(slide, index) in slides" :key="index" v-show="currentSlide === index">
          <div class="slide-bg" :style="{ backgroundImage: `url(${slide.image})` }">
            <div class="carousel-caption">
              <h1>{{ slide.title }}</h1>
              <p>{{ slide.subtitle }}</p>
              <router-link to="/products" class="btn btn-primary">View Products</router-link>
            </div>
          </div>
        </div>
        <button class="carousel-prev" @click="prevSlide">❮</button>
        <button class="carousel-next" @click="nextSlide">❯</button>
      </div>
    </section>
    
    <section class="intro">
      <div class="container">
        <h2 class="section-title">Welcome to Meru Dairy</h2>
        <div class="intro-content">
          <p>Meru Central Dairy Co-operative Union Ltd is Kenya's biggest dairy co-operative, proudly serving millions of customers with high-quality Mount Kenya Milk products. Our commitment to excellence and farmer-first approach has made us a trusted name in the Kenyan dairy industry.</p>
        </div>
      </div>
    </section>
    
    <section class="featured-products">
      <div class="container">
        <h2 class="section-title">Our Products</h2>
        <div class="products-grid">
          <div class="product-card" v-for="product in featuredProducts" :key="product.id">
            <div class="product-image-wrapper">
              <img 
                v-if="product.image_url" 
                :src="product.image_url" 
                :alt="product.name"
                class="product-image"
                @error="handleProductImageError"
              >
              <div v-else class="product-image-placeholder">
                <svg width="100%" height="200" viewBox="0 0 300 200" fill="none">
                  <rect width="300" height="200" fill="#dbeafe"/>
                  <text x="150" y="110" text-anchor="middle" fill="#1e3a8a" font-size="14">{{ product.name }}</text>
                </svg>
              </div>
            </div>
            <h3>{{ product.name }}</h3>
            <p>{{ truncate(product.description, 100) }}</p>
            <router-link :to="`/products/${product.id}`" class="btn btn-outline">Learn More</router-link>
          </div>
        </div>
        <div class="text-center">
          <router-link to="/products" class="btn btn-primary">View All Products</router-link>
        </div>
      </div>
    </section>
    
    <section class="statistics">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in statistics" :key="stat.label">
            <div class="stat-value">{{ stat.value }}{{ stat.suffix }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>
    
    <section class="testimonials">
      <div class="container">
        <h2 class="section-title">What Our Customers Say</h2>
        <div class="testimonials-grid">
          <div class="testimonial-card" v-for="testimonial in testimonials" :key="testimonial.id">
            <div class="rating">★ {{ testimonial.rating }}</div>
            <p>"{{ testimonial.content }}"</p>
            <h4>{{ testimonial.name }}</h4>
            <small>{{ testimonial.role }}</small>
          </div>
        </div>
      </div>
    </section>
    
    <section class="latest-blog">
      <div class="container">
        <h2 class="section-title">Latest from Our Blog</h2>
        <div class="blog-grid">
          <div class="blog-card" v-for="post in latestBlogs" :key="post.id">
            <div class="blog-image-wrapper">
              <img 
                v-if="post.featured_image" 
                :src="post.featured_image" 
                :alt="post.title"
                class="blog-image"
                @error="handleBlogImageError"
              >
              <div v-else class="blog-image-placeholder">
                <svg width="100%" height="200" viewBox="0 0 300 200" fill="none">
                  <rect width="300" height="200" fill="#f3f4f6"/>
                  <text x="150" y="110" text-anchor="middle" fill="#6b7280" font-size="12">Blog Image</text>
                </svg>
              </div>
            </div>
            <div class="blog-content">
              <h3>{{ post.title }}</h3>
              <p>{{ post.excerpt || truncate(post.content, 100) }}</p>
              <router-link :to="`/blog/${post.slug}`" class="read-more">Read More →</router-link>
            </div>
          </div>
        </div>
        <div class="text-center">
          <router-link to="/blog" class="btn btn-primary">View All Posts</router-link>
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
      slides: [
        { 
          image: '/images/carousel/slide1.jpg', 
          title: 'Pure Fresh Milk', 
          subtitle: 'From our farms to your table' 
        },
        { 
          image: '/images/carousel/slide2.jpg', 
          title: 'Mount Kenya Yoghurt', 
          subtitle: 'Creamy, delicious, and nutritious' 
        },
        { 
          image: '/images/carousel/slide3.jpg', 
          title: 'Quality You Can Trust', 
          subtitle: 'Kenya\'s biggest dairy co-operative' 
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
    this.startCarousel()
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
        
        this.featuredProducts = productsRes.data.filter(p => p.featured).slice(0, 4)
        this.statistics = statsRes.data
        this.testimonials = testimonialsRes.data
        this.latestBlogs = blogsRes.data.slice(0, 3)
      } catch (error) {
        console.error('Error fetching data:', error)
        // Load fallback data
        this.statistics = [
          { label: 'Our Farmers', value: '120,000', suffix: '+' },
          { label: 'Cooperative Societies', value: '120', suffix: '+' },
          { label: 'Litres of Milk Processed per day', value: '600,000', suffix: '+' },
          { label: 'Customers Served', value: '10,000,000', suffix: '+' }
        ]
      }
    },
    startCarousel() {
      setInterval(() => {
        this.nextSlide()
      }, 5000)
    },
    nextSlide() {
      this.currentSlide = (this.currentSlide + 1) % this.slides.length
    },
    prevSlide() {
      this.currentSlide = (this.currentSlide - 1 + this.slides.length) % this.slides.length
    },
    truncate(text, length) {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    },
    handleProductImageError(e) {
      e.target.style.display = 'none'
      if (e.target.parentElement.querySelector('.product-image-placeholder')) {
        e.target.parentElement.querySelector('.product-image-placeholder').style.display = 'flex'
      }
    },
    handleBlogImageError(e) {
      e.target.style.display = 'none'
      if (e.target.parentElement.querySelector('.blog-image-placeholder')) {
        e.target.parentElement.querySelector('.blog-image-placeholder').style.display = 'flex'
      }
    }
  }
}
</script>

<style scoped>
.hero {
  position: relative;
  height: 70vh;
  overflow: hidden;
}

.carousel {
  position: relative;
  height: 100%;
}

.carousel-slide {
  /* position: absolute; */
  width: 100%;
  height: 600px;
  transition: opacity 4s;

  margin: auto;

}

.slide-bg {
  width: 100%;
  height: 700px;
  background-size: cover;
  background-position: center;
  /* position: relative; */
  margin: auto;
}

.carousel-caption {
  position: absolute;
  bottom: 60%;
  left: 20%;
  background: transparent;
  color: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  color: black;
}

.carousel-prev,
.carousel-next {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0,0,0,0.5);
  color: white;
  border: none;
  padding: 1rem;
  cursor: pointer;
  font-size: 1.5rem;
  z-index: 10;
}

.carousel-prev { left: 10px; }
.carousel-next { right: 10px; }

.carousel-prev:hover,
.carousel-next:hover {
  background: rgba(0,0,0,0.8);
}

.intro {
  padding: 4rem 0;
  background: var(--gray-light);
}

.intro-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  font-size: 1.2rem;
}

.featured-products,
.latest-blog {
  padding: 4rem 0;
}

.products-grid,
.testimonials-grid,
.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.product-card,
.testimonial-card,
.blog-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.product-card:hover,
.blog-card:hover {
  transform: translateY(-5px);
}

.product-image-wrapper,
.blog-image-wrapper {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f5f5f5;
}

.product-image,
.blog-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image,
.blog-card:hover .blog-image {
  transform: scale(1.05);
}

.product-image-placeholder,
.blog-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-card h3,
.blog-content h3 {
  padding: 1rem 1rem 0.5rem;
  color: var(--primary-blue);
}

.product-card p,
.blog-content p {
  padding: 0 1rem;
  color: var(--gray);
}

.product-card .btn,
.blog-content .read-more {
  margin: 1rem;
}

.statistics {
  background: var(--primary-blue);
  color: white;
  padding: 4rem 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
}

.stat-label {
  font-size: 1rem;
  margin-top: 0.5rem;
  opacity: 0.9;
}

.testimonials {
  padding: 4rem 0;
  background: var(--gray-light);
}

.testimonial-card {
  padding: 2rem;
}

.rating {
  color: gold;
  margin-bottom: 1rem;
}

.blog-content {
  padding: 1.5rem;
}

.read-more {
  color: var(--primary-blue);
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
}

.text-center {
  text-align: center;
}

@media (max-width: 768px) {
  .carousel-caption {
    bottom: 10%;
    left: 5%;
    right: 5%;
    padding: 1rem;
  }
  
  .carousel-caption h1 {
    font-size: 1.5rem;
  }
  
  .hero {
    height: 50vh;
  }
  
  .product-image-wrapper,
  .blog-image-wrapper {
    height: 180px;
  }
}
</style>