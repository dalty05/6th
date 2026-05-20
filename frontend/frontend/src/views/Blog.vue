<template>
  <main>
    <!-- Achievements & Events Hero Section -->
    <section class="achievements-hero">
      <div class="container">
        <div class="achievements-grid">
          <div class="achievements-content">
            <h1>Our Journey of Excellence</h1>
            <p class="achievements-subtitle">Celebrating milestones and community impact</p>
            
            <div class="achievements-stats">
              <div class="achievement-item">
                <span class="achievement-number">10+</span>
                <span class="achievement-label">Industry Awards</span>
              </div>
              <div class="achievement-item">
                <span class="achievement-number">50K+</span>
                <span class="achievement-label">Farmers Empowered</span>
              </div>
              <div class="achievement-item">
                <span class="achievement-number">5+</span>
                <span class="achievement-label">Countries Exporting</span>
              </div>
            </div>
            
            <div class="achievements-description">
              <p>Meru Central Dairy has grown from a small cooperative to Kenya's largest dairy processor. Through strategic partnerships, farmer training programs, and community initiatives, we've transformed the dairy industry in the Mount Kenya region.</p>
              <p>Our recent achievements include launching sustainable farming practices, expanding our processing capacity to 600,000+ liters daily, and implementing digital solutions for farmers.</p>
            </div>
            
            <div class="upcoming-events">
              <h3>📅 Upcoming Events</h3>
              <ul>
                <li>📍 Annual Farmers' Conference - June 15, 2024</li>
                <li>📍 World Milk Day Celebration - June 1, 2024</li>
                <li>📍 Dairy Industry Expo - July 20-22, 2024</li>
              </ul>
            </div>
          </div>
          
          <div class="achievements-image">
            <img 
              src="/images/achievements/hero-image.jpg" 
              alt="Meru Dairy Achievements"
              @error="handleImageError"
              class="hero-image"
            >
            <div class="image-overlay">
              <div class="year-badge">2024</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Blog Subheading -->
    <section class="blog-header">
      <div class="container">
        <div class="blog-header-content">
          <h2>Latest News & Stories</h2>
          <p>Stay updated with the latest happenings, farmer success stories, and industry insights from Meru Dairy</p>
          <div class="header-decoration"></div>
        </div>
      </div>
    </section>

    <!-- Blog Posts List - Redesigned without cards -->
    <section class="blog-posts">
      <div class="container">
        <div class="blog-list">
          <div v-for="(post, index) in posts" :key="post.id" class="blog-post-item">
            <div :class="['blog-post-layout', index % 2 === 0 ? 'layout-left' : 'layout-right']">
              
              <!-- Image Section -->
              <div class="blog-post-image">
                <img 
                  v-if="post.featured_image" 
                  :src="post.featured_image" 
                  :alt="post.title"
                  @error="handleBlogImageError"
                >
                <div v-else class="image-placeholder">
                  <svg width="100%" height="100%" viewBox="0 0 500 350" fill="none">
                    <rect width="500" height="350" fill="#e0e7ff"/>
                    <text x="250" y="180" text-anchor="middle" fill="#1e3a8a" font-size="18">📝 Blog Image</text>
                  </svg>
                </div>
                <div class="image-date-badge">{{ formatDate(post.created_at) }}</div>
              </div>
              
              <!-- Content Section -->
              <div class="blog-post-content">
                <div class="post-meta">
                  <span class="post-category">📰 News & Updates</span>
                  <span class="post-read-time">⏱️ {{ getReadTime(post.content) }} min read</span>
                </div>
                
                <h2 class="post-title">{{ post.title }}</h2>
                
                <div class="post-excerpt">
                  <p>{{ post.excerpt || truncateContent(post.content, 200) }}</p>
                </div>
                
                <div class="post-footer">
                  <div class="post-author">
                    <span class="author-name">By {{ post.author || 'Admin' }}</span>
                    <span class="post-views">👁️ {{ post.views }} views</span>
                  </div>
                  <router-link :to="`/blo g/${post.slug}`" class="read-more-btn">
                    Read Full Article 
                    <span class="arrow">→</span>
                  </router-link>
                </div>
              </div>
              
            </div>
          </div>
        </div>
        
        <div v-if="posts.length === 0" class="no-posts">
          <div class="no-posts-content">
            <svg width="100" height="100" viewBox="0 0 100 100" fill="none">
              <circle cx="50" cy="50" r="45" stroke="#1e3a8a" stroke-width="2" fill="#f0f4ff"/>
              <text x="50" y="55" text-anchor="middle" fill="#1e3a8a" font-size="40">📝</text>
            </svg>
            <h3>No Blog Posts Yet</h3>
            <p>Check back soon for exciting updates and stories!</p>
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
      posts: []
    }
  },
  mounted() {
    this.fetchPosts()
  },
  methods: {
    async fetchPosts() {
      try {
        const response = await axios.get('/api/blog')
        this.posts = response.data
      } catch (error) {
        console.error('Error fetching blog posts:', error)
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      return date.toLocaleDateString('en-US', options)
    },
    truncateContent(content, length) {
      if (!content) return ''
      if (content.length <= length) return content
      return content.substring(0, length) + '...'
    },
    getReadTime(content) {
      if (!content) return 1
      const wordsPerMinute = 200
      const words = content.split(/\s+/).length
      const minutes = Math.ceil(words / wordsPerMinute)
      return minutes
    },
    handleBlogImageError(e) {
      e.target.style.display = 'none'
      if (e.target.parentElement.querySelector('.image-placeholder')) {
        e.target.parentElement.querySelector('.image-placeholder').style.display = 'flex'
      }
    }
  }
}
</script>

<style scoped>
/* Achievements Hero Section */
.achievements-hero {
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  color: white;
  padding: 4rem 0;
  position: relative;
  overflow: hidden;
}

.achievements-hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" opacity="0.1"><path fill="white" d="M50,30 L60,50 L50,70 L40,50 Z"/><circle cx="30" cy="30" r="10"/><circle cx="70" cy="70" r="10"/></svg>') repeat;
  pointer-events: none;
}

.achievements-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
  position: relative;
  z-index: 1;
}

.achievements-content h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.achievements-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.achievements-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.achievement-item {
  text-align: center;
}

.achievement-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.achievement-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.achievements-description {
  margin-bottom: 2rem;
  line-height: 1.6;
}

.achievements-description p {
  margin-bottom: 1rem;
  opacity: 0.95;
}

.upcoming-events {
  background: rgba(255,255,255,0.1);
  padding: 1.5rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.upcoming-events h3 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.upcoming-events ul {
  list-style: none;
  padding: 0;
}

.upcoming-events li {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.achievements-image {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.hero-image {
  width: 100%;
  height: auto;
  display: block;
}

.image-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
}

.year-badge {
  background: #f59e0b;
  color: white;
  padding: 8px 16px;
  border-radius: 50px;
  font-weight: bold;
}

/* Blog Header Section */
.blog-header {
  padding: 3rem 0 2rem;
  background: white;
  text-align: center;
}

.blog-header-content h2 {
  font-size: 2rem;
  color: var(--primary-blue);
  margin-bottom: 1rem;
}

.blog-header-content p {
  font-size: 1.1rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.header-decoration {
  width: 80px;
  height: 4px;
  background: var(--accent-blue);
  margin: 1.5rem auto 0;
  border-radius: 2px;
}

/* Blog Posts List - New Design */
.blog-posts {
  padding: 2rem 0 4rem;
  background: #f8fafc;
}

.blog-list {
  max-width: 1200px;
  margin: 0 auto;
}

.blog-post-item {
  margin-bottom: 3rem;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.blog-post-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

.blog-post-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.layout-left .blog-post-image {
  order: 1;
}

.layout-left .blog-post-content {
  order: 2;
}

.layout-right .blog-post-image {
  order: 2;
}

.layout-right .blog-post-content {
  order: 1;
}

.blog-post-image {
  position: relative;
  height: 100%;
  min-height: 350px;
  overflow: hidden;
}

.blog-post-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.blog-post-item:hover .blog-post-image img {
  transform: scale(1.05);
}

.image-date-badge {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: var(--primary-blue);
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  min-height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.blog-post-content {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.post-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.post-category {
  color: var(--accent-blue);
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.post-read-time {
  color: #888;
  font-size: 0.85rem;
}

.post-title {
  font-size: 1.8rem;
  color: var(--primary-blue);
  margin-bottom: 1rem;
  line-height: 1.3;
}

.post-excerpt {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.post-author {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.author-name {
  font-weight: 600;
  color: var(--primary-blue);
}

.read-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary-blue);
  text-decoration: none;
  font-weight: 600;
  transition: gap 0.3s;
}

.read-more-btn:hover .arrow {
  transform: translateX(5px);
}

.arrow {
  transition: transform 0.3s;
}

/* No Posts State */
.no-posts {
  text-align: center;
  padding: 4rem 2rem;
}

.no-posts-content {
  max-width: 400px;
  margin: 0 auto;
}

.no-posts-content h3 {
  color: var(--primary-blue);
  margin: 1rem 0;
}

.no-posts-content p {
  color: #666;
}

/* Responsive Design */
@media (max-width: 968px) {
  .achievements-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .achievements-image {
    order: -1;
    max-width: 500px;
    margin: 0 auto;
  }
  
  .blog-post-layout {
    grid-template-columns: 1fr;
  }
  
  .layout-left .blog-post-image,
  .layout-right .blog-post-image {
    order: 1;
  }
  
  .layout-left .blog-post-content,
  .layout-right .blog-post-content {
    order: 2;
  }
  
  .blog-post-image {
    min-height: 250px;
  }
  
  .post-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 768px) {
  .achievements-hero {
    padding: 2rem 0;
  }
  
  .achievements-content h1 {
    font-size: 1.8rem;
  }
  
  .achievements-stats {
    gap: 1rem;
  }
  
  .achievement-number {
    font-size: 1.5rem;
  }
  
  .blog-header-content h2 {
    font-size: 1.5rem;
  }
  
  .blog-post-content {
    padding: 1.5rem;
  }
  
  .post-meta {
    gap: 1rem;
  }
  
  .post-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>