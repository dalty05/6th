<template>
  <main>
    <!-- Hero Section -->
    <section class="blog-hero">
      <div class="hero-background">
        <div class="hero-overlay"></div>
        <div class="hero-pattern"></div>
      </div>
      
      <div class="container">
        <div class="hero-content">
          <div class="hero-text animate-fade-in-up">
            <span class="hero-badge">Our Blog</span>
            <h1 class="hero-title">Stories & <span class="highlight">Updates</span></h1>
            <p class="hero-description">
              Stay informed about the latest news, farmer success stories, industry insights, 
              and community events from Meru Central Dairy.
            </p>
          </div>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <span>Explore our stories</span>
        <div class="scroll-mouse"></div>
      </div>
    </section>

    <!-- Featured Post Section -->
    <section class="featured-section" v-if="featuredPost">
      <div class="container">
        <div class="featured-card glass-card animate-on-scroll">
          <div class="featured-badge">Featured Article</div>
          <div class="featured-grid">
            <div class="featured-image">
              <img 
                v-if="featuredPost.featured_image" 
                :src="featuredPost.featured_image" 
                :alt="featuredPost.title"
              >
              <div v-else class="image-placeholder">
                <span>📰</span>
              </div>
            </div>
            <div class="featured-content">
              <div class="post-meta">
                <span class="post-date">{{ formatDate(featuredPost.created_at) }}</span>
                <span class="post-read-time">⏱️ {{ getReadTime(featuredPost.content) }} min read</span>
              </div>
              <h2>{{ featuredPost.title }}</h2>
              <p>{{ featuredPost.excerpt || truncateContent(featuredPost.content, 150) }}</p>
              <div class="featured-footer">
                <div class="post-author">
                  <span class="author-avatar">👤</span>
                  <span>By {{ featuredPost.author || 'Admin' }}</span>
                  <span class="post-views">👁️ {{ featuredPost.views }} views</span>
                </div>
                <router-link :to="`/blog/${featuredPost.slug}`" class="read-more-btn">
                  Read Full Article
                  <span class="arrow">→</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Category Filters -->
    <section class="filters-section">
      <div class="container">
        <div class="filters-wrapper glass-card">
          <div class="search-box">
            <span class="search-icon">🔍</span>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search articles..."
              class="search-input"
            >
          </div>
          <div class="category-filters">
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
    </section>

    <!-- Blog Posts Grid -->
    <section class="blog-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Latest Articles</span>
          <h2 class="section-title">Recent Stories & News</h2>
          <p class="section-subtitle">
            Discover the latest updates from our dairy community
          </p>
        </div>
        
        <div class="blog-grid">
  <article
    v-for="post in filteredPosts"
    :key="post.id"
    class="blog-card glass-card animate-on-scroll"
  >
    <!-- Image -->
    <div class="blog-image-wrapper">
      <div class="blog-image">
        <img
          v-if="post.featured_image"
          :src="post.featured_image"
          :alt="post.title"
          @error="handleImageError"
        />

        <div v-else class="image-placeholder">
          <span>📰</span>
        </div>

        <div class="image-overlay">
          <span class="category-tag">
            {{ getCategory(post) }}
          </span>

          <button
            class="save-btn"
            @click="toggleReadLater(post)"
          >
            {{ isInReadLater(post.id) ? '✓ Saved' : '📌 Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="blog-content">
      <!-- Meta -->
      <div class="post-meta">
        <span>{{ formatDate(post.created_at) }}</span>
        <span>•</span>
        <span>{{ getReadTime(post.content) }} min read</span>
      </div>

      <!-- Title -->
      <h3 class="blog-title">
        {{ post.title }}
      </h3>

      <!-- Excerpt -->
      <p class="blog-excerpt">
        {{ post.excerpt || truncateContent(post.content, 130) }}
      </p>

      <!-- Footer -->
      <div class="post-footer">
        <div class="post-author">
          <span class="author-avatar">👤</span>
          <span>{{ post.author || 'Admin' }}</span>
        </div>

        <router-link
          :to="`/blog/${post.slug}`"
          class="read-more"
        >
          Read Article →
        </router-link>
      </div>

      <!-- Stats -->
      <div class="post-bottom">
        <span class="post-views">
          👁️ {{ post.views }} views
        </span>
      </div>
    </div>
  </article>
</div>
        
        <div v-if="filteredPosts.length === 0" class="no-results glass-card">
          <div class="no-results-icon">🔍</div>
          <h3>No articles found</h3>
          <p>Try adjusting your search or category filter</p>
          <button @click="resetFilters" class="btn-reset">Clear Filters</button>
        </div>
        
        <!-- Load More Button -->
        <div v-if="hasMorePosts" class="load-more">
          <button @click="loadMore" class="btn-load-more" :disabled="loadingMore">
            {{ loadingMore ? 'Loading...' : 'Load More Articles' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Newsletter Section -->
    <section class="newsletter-section">
      <div class="container">
        <div class="newsletter-card glass-card">
          <div class="newsletter-icon">📧</div>
          <h3>Subscribe to Our Newsletter</h3>
          <p>Get the latest stories, updates, and dairy industry insights delivered to your inbox</p>
          
          <div class="newsletter-form">
            <input 
              type="email" 
              v-model="newsletterEmail" 
              placeholder="Enter your email address"
              class="newsletter-input"
            >
            <button @click="subscribeNewsletter" :disabled="newsletterLoading" class="btn-subscribe">
              {{ newsletterLoading ? 'Subscribing...' : 'Subscribe' }}
              <span class="arrow">→</span>
            </button>
          </div>
          
          <p class="newsletter-note">No spam, unsubscribe anytime.</p>
        </div>
      </div>
    </section>

    <!-- Categories Section -->
    <section class="categories-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Explore Topics</span>
          <h2 class="section-title">Browse by Category</h2>
          <p class="section-subtitle">
            Find articles that interest you most
          </p>
        </div>
        
        <div class="categories-grid">
          <div class="category-card glass-card animate-on-scroll" v-for="topic in topics" :key="topic.name">
            <div class="category-icon">{{ topic.icon }}</div>
            <h3>{{ topic.name }}</h3>
            <p>{{ topic.description }}</p>
            <span class="category-count">{{ topic.count }} articles</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Blog',
  data() {
    return {
      posts: [],
      featuredPost: null,
      searchQuery: '',
      selectedCategory: 'All',
      readLaterList: [],
      newsletterEmail: '',
      newsletterLoading: false,
      loadingMore: false,
      page: 1,
      pageSize: 6,
      total: 0,
      hasMore: true
    }
  },
  computed: {
    categories() {
      return ['All', 'News', 'Stories', 'Events', 'Tips', 'Community']
    },
    debugBlogCount() {
      return this.posts.length
    },
    topics() {
      return [
        { name: 'Farmer Stories', icon: '👨‍🌾', description: 'Success stories from our cooperative members', count: 12 },
        { name: 'Industry News', icon: '📰', description: 'Latest updates from the dairy industry', count: 8 },
        { name: 'Health & Nutrition', icon: '🥛', description: 'Tips for healthy living with dairy', count: 6 },
        { name: 'Community Events', icon: '🎉', description: 'Upcoming events and initiatives', count: 5 },
        { name: 'Sustainability', icon: '🌱', description: 'Our environmental initiatives', count: 4 },
        { name: 'Product Updates', icon: '🆕', description: 'New products and improvements', count: 7 }
      ]
    },
    filteredPosts() {
      let filtered = this.posts

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(post =>
          post.title.toLowerCase().includes(query) ||
          (post.content && post.content.toLowerCase().includes(query)) ||
          (post.excerpt && post.excerpt.toLowerCase().includes(query))
        )
      }

      if (this.selectedCategory !== 'All') {
        filtered = filtered.filter(post => {
          const category = this.getCategory(post)
          return category === this.selectedCategory
        })
      }

      return filtered
    },
    hasMorePosts() {
      return this.hasMore
    }
  },
  mounted() {
    this.fetchPosts()
    this.loadReadLater()
    this.setupScrollAnimation()
  },
  methods: {
    async fetchPosts() {
  try {

    const featuredRes = await axios.get('/api/blog', {
      params: { mode: 'featured', page: 1, page_size: 1 }
    })

    console.log('FEATURED:', featuredRes.data)

    this.featuredPost =
      featuredRes.data.items &&
      featuredRes.data.items.length
        ? featuredRes.data.items[0]
        : null

    this.page = 1

    const recentRes = await axios.get('/api/blog', {
      params: { mode: 'recent', page: this.page, page_size: this.pageSize }
    })

    console.log('RECENT:', recentRes.data)

    this.posts = recentRes.data.items || []
    this.$nextTick(() => {
      this.setupScrollAnimation()
    })

    console.log('POSTS ARRAY:', this.posts)

    this.total = recentRes.data.total || 0
    this.hasMore = this.posts.length < this.total

  } catch (error) {
    console.error('Error fetching blog posts:', error)
  }
},
    loadSampleData() {
      this.featuredPost = {
        id: 1,
        title: 'Meru Dairy Wins Industry Excellence Award 2024',
        slug: 'meru-dairy-wins-award-2024',
        excerpt: 'We are proud to announce that Meru Central Dairy has been recognized as the best dairy cooperative in Kenya.',
        content: 'Full article content here...',
        featured_image: null,
        views: 1250,
        created_at: new Date().toISOString(),
        author: 'Communications Team'
      }

      this.posts = [
        {
          id: 2,
          title: 'Empowering Farmers: New Training Program Launched',
          slug: 'empowering-farmers-training-program',
          excerpt: 'Our latest initiative aims to equip farmers with modern dairy farming techniques.',
          content: 'Full article content here...',
          featured_image: null,
          views: 890,
          created_at: new Date().toISOString(),
          author: 'Farmer Support Team'
        }
      ]

      this.total = this.posts.length
      this.hasMore = false
    },
    getCategory(post) {
      if (!post || !post.title) return 'News'

      const t = post.title.toLowerCase()
      if (t.includes('farmer') || t.includes('success')) return 'Stories'
      if (t.includes('event') || t.includes('launch')) return 'Events'
      if (t.includes('tip') || t.includes('guide')) return 'Tips'
      if (t.includes('community') || t.includes('csr')) return 'Community'
      return 'News'
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    },
    truncateContent(content, length) {
      if (!content) return ''
      if (content.length <= length) return content
      return content.substring(0, length) + '...'
    },
    getReadTime(content) {
      if (!content) return 1
      const wordsPerMinute = 200
      const words = content.split(/\s+/).filter(Boolean).length
      return Math.max(1, Math.ceil(words / wordsPerMinute))
    },
    handleImageError(e) {
      e.target.style.display = 'none'
    },
    loadReadLater() {
      const saved = localStorage.getItem('readLater')
      if (saved) this.readLaterList = JSON.parse(saved)
    },
    toggleReadLater(post) {
      const index = this.readLaterList.findIndex(p => p.id === post.id)
      if (index === -1) {
        this.readLaterList.push({ id: post.id, title: post.title, slug: post.slug })
        alert('Article added to Read Later list!')
      } else {
        this.readLaterList.splice(index, 1)
        alert('Article removed from Read Later list')
      }
      localStorage.setItem('readLater', JSON.stringify(this.readLaterList))
    },
    isInReadLater(postId) {
      return this.readLaterList.some(p => p.id === postId)
    },
    async loadMore() {
      if (!this.hasMore || this.loadingMore) return

      this.loadingMore = true
      try {
        this.page += 1
        const recentRes = await axios.get('/api/blog', {
          params: { mode: 'recent', page: this.page, page_size: this.pageSize }
        })

        const newItems = recentRes.data.items || []
        this.posts = this.posts.concat(newItems)
        this.total = recentRes.data.total || this.total
        this.hasMore = this.posts.length < this.total
      } catch (e) {
        console.error('Error loading more blog posts:', e)
      } finally {
        this.loadingMore = false
      }
    },
    resetFilters() {
      this.searchQuery = ''
      this.selectedCategory = 'All'
    },
    subscribeNewsletter() {
      if (!this.newsletterEmail) {
        alert('Please enter your email address')
        return
      }
      this.newsletterLoading = true
      setTimeout(() => {
        alert(`Thank you for subscribing! We'll send updates to ${this.newsletterEmail}`)
        this.newsletterEmail = ''
        this.newsletterLoading = false
      }, 1000)
    },
    setupScrollAnimation() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      }, { threshold: 0.1 })

      document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el))
    }
  }
}
</script>

<style scoped>
/* Hero Section */
.blog-hero {
  position: relative;
  min-height: 60vh;
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
}

.hero-description {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.9);
  line-height: 1.6;
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

/* Featured Section */
.featured-section {
  padding: 60px 0 40px;
  background: #f8fafc;
}

.featured-card {
  overflow: hidden;
  background: white;
}

.featured-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  background: #f59e0b;
  color: white;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  z-index: 1;
}

.featured-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}

.featured-image {
  height: 400px;
  overflow: hidden;
}

.featured-image img {
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
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  font-size: 4rem;
}

.featured-content {
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.featured-content h2 {
  font-size: 1.8rem;
  color: #1e3a8a;
  margin: 15px 0;
  line-height: 1.3;
}

.featured-content p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.featured-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.post-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 0.85rem;
  color: #666;
}

.read-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #f59e0b;
  font-weight: 600;
  text-decoration: none;
}

.read-more-btn .arrow {
  transition: transform 0.3s;
}

.read-more-btn:hover .arrow {
  transform: translateX(5px);
}

/* Filters Section */
.filters-section {
  padding: 40px 0;
  background: #f8fafc;
}

.filters-wrapper {
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  background: white;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8fafc;
  padding: 8px 16px;
  border-radius: 50px;
  flex: 1;
  max-width: 300px;
}

.search-icon { font-size: 1rem; }

.search-input {
  border: none;
  background: none;
  outline: none;
  font-size: 0.9rem;
  width: 100%;
}

.category-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.category-pill {
  padding: 6px 16px;
  background: #f8fafc;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.85rem;
}

.category-pill:hover,
.category-pill.active {
  background: #1e3a8a;
  color: white;
}

/* Blog Section */
.blog-section {
  padding: 60px 0;
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
/* Improved Blog Layout */
.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 32px;
}



.blog-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 18px 40px rgba(0,0,0,0.12);
}

.blog-image-wrapper {
  position: relative;
}

.blog-image {
  position: relative;
  height: 240px;
  overflow: hidden;
}

.blog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.blog-card:hover .blog-image img {
  transform: scale(1.08);
}

.image-overlay {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-tag {
  background: rgba(30, 58, 138, 0.9);
  color: white;
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 0.75rem;
  font-weight: 600;
}

.save-btn {
  background: rgba(255,255,255,0.9);
  border: none;
  padding: 6px 12px;
  border-radius: 30px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover {
  background: #f59e0b;
  color: white;
}

.blog-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 0.8rem;
  margin-bottom: 14px;
}

.blog-title {
  font-size: 1.3rem;
  line-height: 1.5;
  color: #1e3a8a;
  margin-bottom: 14px;
  transition: color 0.3s ease;
}

.blog-card:hover .blog-title {
  color: #2563eb;
}

.blog-excerpt {
  color: #555;
  line-height: 1.7;
  margin-bottom: 22px;
  flex: 1;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 18px;
  border-top: 1px solid #e5e7eb;
}

.read-more {
  color: #f59e0b;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
}

.read-more:hover {
  transform: translateX(4px);
}

.post-bottom {
  margin-top: 15px;
  color: #6b7280;
  font-size: 0.8rem;
}

/* Responsive */
@media (max-width: 768px) {
  .blog-grid {
    grid-template-columns: 1fr;
  }

  .blog-image {
    height: 220px;
  }

  .blog-title {
    font-size: 1.1rem;
  }

  .post-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 30px;
}

.blog-card {
  background: white;
  overflow: hidden;
  transition: all 0.3s;
  opacity: 1;
  transform: translateY(0);
}

.blog-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.blog-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.blog-image {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.blog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.blog-card:hover .blog-image img { transform: scale(1.1); }

.image-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0;
  transition: opacity 0.3s;
}

.blog-card:hover .image-overlay { opacity: 1; }

.read-later {
  background: #1e3a8a;
  color: white;
  padding: 5px 10px;
  border-radius: 50px;
  font-size: 0.7rem;
  cursor: pointer;
  display: inline-block;
}

.blog-content { padding: 25px; }

.blog-content h3 {
  font-size: 1.2rem;
  color: #1e3a8a;
  margin-bottom: 12px;
  line-height: 1.4;
}

.blog-content p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #666;
}

.post-stats { display: flex; align-items: center; gap: 15px; }
.post-views { font-size: 0.8rem; color: #666; }

.read-more {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.read-more .arrow { transition: transform 0.3s; }
.read-more:hover .arrow { transform: translateX(5px); }

/* No Results */
.no-results {
  text-align: center;
  padding: 60px;
  background: white;
  margin-top: 40px;
}

.no-results-icon { font-size: 4rem; margin-bottom: 20px; }

.no-results h3 { color: #1e3a8a; margin-bottom: 10px; }
.no-results p { color: #666; margin-bottom: 20px; }

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

/* Load More */
.load-more { text-align: center; margin-top: 50px; }

.btn-load-more {
  background: transparent;
  border: 2px solid #1e3a8a;
  color: #1e3a8a;
  padding: 12px 32px;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-load-more:hover:not(:disabled) {
  background: #1e3a8a;
  color: white;
  transform: translateY(-2px);
}

.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Newsletter Section */
.newsletter-section {
  padding: 60px 0;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
}

.newsletter-card {
  padding: 50px;
  text-align: center;
  background: rgba(255,255,255,0.95);
  max-width: 600px;
  margin: 0 auto;
}

.newsletter-icon { font-size: 3rem; margin-bottom: 20px; }

.newsletter-card h3 { font-size: 1.5rem; color: #1e3a8a; margin-bottom: 15px; }
.newsletter-card p { color: #666; margin-bottom: 25px; }

.newsletter-form { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
.newsletter-input {
  padding: 12px 20px;
  border: 1px solid #ddd;
  border-radius: 50px;
  width: 280px;
  font-size: 0.9rem;
}

.btn-subscribe {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-subscribe:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
}

.btn-subscribe:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.newsletter-note { font-size: 0.75rem; color: #999; margin-top: 15px; }

/* Categories Section */
.categories-section {
  padding: 60px 0;
  background: #f8fafc;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.category-card {
  padding: 30px;
  text-align: center;
  background: white;
  transition: all 0.3s;
  opacity: 1;
  transform: translateY(0);
  
  transform: translateY(30px);
  
}





.category-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
}

.category-icon { font-size: 2.5rem; margin-bottom: 15px; }

.category-card h3 { color: #1e3a8a; margin-bottom: 10px; }
.category-card p { color: #666; font-size: 0.85rem; margin-bottom: 15px; line-height: 1.5; }
.category-count { display: inline-block; background: #e0e7ff; color: #1e3a8a; padding: 4px 12px; border-radius: 50px; font-size: 0.75rem; }

/* Glass Card Effect */
.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

/* Animations */
.animate-fade-in-up { animation: fadeInUp 0.8s ease-out; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 968px) {
  .hero-title { font-size: 2.5rem; }
  .featured-grid { grid-template-columns: 1fr; }
  .featured-image { height: 300px; }
  .blog-grid { grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
  .filters-wrapper { flex-direction: column; }
  .search-box { max-width: none; width: 100%; }
}

@media (max-width: 768px) {
  .hero-title { font-size: 2rem; }
  .section-title { font-size: 1.8rem; }
  .featured-content { padding: 25px; }
  .featured-content h2 { font-size: 1.3rem; }
  .blog-grid { grid-template-columns: 1fr; }
  .newsletter-card { padding: 30px; }
  .categories-grid { grid-template-columns: 1fr; }
  .category-filters { justify-content: center; }
}
</style>

