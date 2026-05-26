<template>
  <main>
    <!-- Hero Section -->
    <section class="about-hero">
      <div class="hero-background">
        <div class="hero-overlay"></div>
        <div class="hero-pattern"></div>
      </div>
      
      <div class="container">
        <div class="hero-content">
          <div class="hero-text animate-fade-in-up">
            <span class="hero-badge">Our Story</span>
            <h1 class="hero-title">Kenya's Pride in<br><span class="highlight">Dairy Excellence</span></h1>
            <p class="hero-description">
              For over five decades, Meru Central Dairy Co-operative Union Ltd has been 
              at the forefront of Kenya's dairy industry, transforming lives and delivering 
              quality nutrition to millions.
            </p>
            <div class="hero-stats">
              <div class="stat-item">
                <div class="stat-number">50+</div>
                <div class="stat-label">Years of Excellence</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">120K+</div>
                <div class="stat-label">Farmers Empowered</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">10M+</div>
                <div class="stat-label">Happy Families</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <span>Discover our journey</span>
        <div class="scroll-mouse"></div>
      </div>
    </section>

    <!-- Mission & Vision Section -->
    <section class="mission-vision">
      <div class="container">
        <div class="mv-grid">
          <div class="mv-card glass-card animate-on-scroll">
            <div class="mv-icon">🎯</div>
            <h3>Our Mission</h3>
            <p>To provide high-quality, safe, and nutritious dairy products while empowering our farmers and contributing to the economic growth of our community.</p>
            <div class="mv-highlight">
              <span>Quality First</span>
              <span>Farmer First</span>
              <span>Community First</span>
            </div>
          </div>
          
          <div class="mv-card glass-card animate-on-scroll delay-1">
            <div class="mv-icon">👁️</div>
            <h3>Our Vision</h3>
            <p>To be the leading dairy cooperative in Africa, setting standards for quality, sustainability, and farmer welfare.</p>
            <div class="mv-highlight">
              <span>African Leader</span>
              <span>Sustainable</span>
              <span>Innovative</span>
            </div>
          </div>
          
          <div class="mv-card glass-card animate-on-scroll delay-2">
            <div class="mv-icon">💎</div>
            <h3>Our Values</h3>
            <p>Integrity, Quality, Sustainability, Innovation, and Community Partnership guide everything we do.</p>
            <div class="mv-highlight">
              <span>Integrity</span>
              <span>Quality</span>
              <span>Innovation</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Our Journey Timeline -->
    <section class="journey-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Our Journey</span>
          <h2 class="section-title">A Legacy of Excellence</h2>
          <p class="section-subtitle">
            From humble beginnings to Kenya's largest dairy cooperative
          </p>
        </div>
        
        <div class="timeline">
          <div class="timeline-item animate-on-scroll" v-for="(milestone, index) in milestones" :key="index">
            <div class="timeline-marker">
              <div class="marker-dot"></div>
              <div class="marker-line" v-if="index < milestones.length - 1"></div>
            </div>
            <div class="timeline-content glass-card">
              <div class="timeline-year">{{ milestone.year }}</div>
              <h3>{{ milestone.title }}</h3>
              <p>{{ milestone.description }}</p>
              <div class="timeline-icon">{{ milestone.icon }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Leadership Section -->
    <section class="leadership-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Leadership</span>
          <h2 class="section-title">Meet Our Leadership Team</h2>
          <p class="section-subtitle">
            Dedicated professionals driving excellence in the dairy industry
          </p>
        </div>
        
        <div class="leadership-grid">
          <div class="leader-card glass-card animate-on-scroll" v-for="leader in leaders" :key="leader.name">
            <div class="leader-image">
              <div class="image-placeholder">{{ leader.avatar }}</div>
            </div>
            <div class="leader-info">
              <h3>{{ leader.name }}</h3>
              <p class="leader-title">{{ leader.title }}</p>
              <p class="leader-bio">{{ leader.bio }}</p>
              <div class="leader-social">
                <a href="#" class="social-link">in</a>
                <a href="#" class="social-link">tw</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Impact Statistics Section -->
    <section class="impact-section">
      <div class="container">
        <div class="impact-grid">
          <div class="impact-content">
            <span class="section-badge">Our Impact</span>
            <h2>Transforming Lives Through Dairy</h2>
            <p>We've grown from a small cooperative to a movement that's changing the agricultural landscape of Kenya.</p>
            <div class="impact-features">
              <div class="impact-feature">
                <div class="impact-icon">👨‍🌾</div>
                <div>
                  <strong>Farmer Training Programs</strong>
                  <p>Free training on modern dairy farming techniques</p>
                </div>
              </div>
              <div class="impact-feature">
                <div class="impact-icon">🏥</div>
                <div>
                  <strong>Community Healthcare</strong>
                  <p>Medical camps and health insurance for farmers</p>
                </div>
              </div>
              <div class="impact-feature">
                <div class="impact-icon">📚</div>
                <div>
                  <strong>Education Support</strong>
                  <p>Scholarships for farmers' children</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="impact-stats glass-card">
            <div class="stat-item-large">
              <div class="stat-number">600K+</div>
              <div class="stat-label">Litres Processed Daily</div>
            </div>
            <div class="stat-item-large">
              <div class="stat-number">120+</div>
              <div class="stat-label">Cooperative Societies</div>
            </div>
            <div class="stat-item-large">
              <div class="stat-number">100%</div>
              <div class="stat-label">Locally Sourced</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Farmer Success Stories -->
    <section class="stories-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Success Stories</span>
          <h2 class="section-title">Voices of Our Farmers</h2>
          <p class="section-subtitle">
            Real stories of transformation from our cooperative members
          </p>
        </div>
        
        <div class="stories-grid">
          <div class="story-card glass-card animate-on-scroll" v-for="story in farmerStories" :key="story.name">
            <div class="story-quote">"</div>
            <p class="story-text">{{ story.story }}</p>
            <div class="story-author">
              <div class="author-avatar">{{ story.avatar }}</div>
              <div class="author-details">
                <strong>{{ story.name }}</strong>
                <span>{{ story.location }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Food Safety Policy -->
    <section class="safety-section">
      <div class="container">
        <div class="safety-card glass-card">
          <div class="safety-icon">🔒</div>
          <div class="safety-content">
            <h3>Food Safety Policy Statement</h3>
            <p>We are committed to producing safe, high-quality dairy products that meet all regulatory standards. Our food safety management system ensures traceability from farm to table, with rigorous testing at every stage of production.</p>
            <div class="safety-badges">
              <span>✓ ISO 22000 Certified</span>
              <span>✓ HACCP Compliant</span>
              <span>✓ KEBS Approved</span>
            </div>
            <button class="btn-download" @click="downloadPolicy">
              <span>Download Policy Statement</span>
              <span class="download-icon">📄</span>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Partners Section -->
    <section class="partners-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Our Partners</span>
          <h2 class="section-title">Trusted by Industry Leaders</h2>
        </div>
        
        <div class="partners-grid">
          <div class="partner-card glass-card" v-for="partner in partners" :key="partner">
            <div class="partner-logo">{{ partner }}</div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: 'About',
  data() {
    return {
      milestones: [
        {
          year: '1972',
          title: 'Humble Beginnings',
          description: 'Meru Central Dairy Co-operative Union Ltd was founded by a small group of dedicated farmers.',
          icon: '🌱'
        },
        {
          year: '1985',
          title: 'First Processing Plant',
          description: 'Opened our first milk processing facility, revolutionizing dairy in the region.',
          icon: '🏭'
        },
        {
          year: '2000',
          title: 'Expansion Era',
          description: 'Expanded operations to serve the entire Mount Kenya region and beyond.',
          icon: '📈'
        },
        {
          year: '2015',
          title: 'Technological Leap',
          description: 'Introduced modern processing technology and quality control systems.',
          icon: '💻'
        },
        {
          year: '2024',
          title: 'Industry Leader',
          description: "Kenya's biggest dairy co-operative, serving millions of customers daily.",
          icon: '👑'
        }
      ],
      leaders: [
        {
          name: 'John Mwangi',
          title: 'Chairman',
          bio: 'Leading the cooperative with over 20 years of experience in agricultural development.',
          avatar: '👨‍💼'
        },
        {
          name: 'Dr. Sarah Wanjiku',
          title: 'CEO',
          bio: 'Visionary leader driving innovation and quality excellence in dairy processing.',
          avatar: '👩‍⚕️'
        },
        {
          name: 'Peter Kimathi',
          title: 'Head of Operations',
          bio: 'Ensuring smooth operations and supply chain excellence across Kenya.',
          avatar: '👨‍🔧'
        },
        {
          name: 'Grace Muthoni',
          title: 'Quality Assurance Director',
          bio: 'Maintaining the highest quality standards from farm to table.',
          avatar: '👩‍🔬'
        }
      ],
      farmerStories: [
        {
          name: 'Joseph Maina',
          location: 'Meru County',
          story: 'Being part of Meru Dairy transformed my life. From 2 cows to 15, I now support my family and send my children to university.',
          avatar: '👨‍🌾'
        },
        {
          name: 'Jane Wambui',
          location: 'Nyeri County',
          story: 'The training programs helped me improve milk quality and increase production by 300%. Meru Dairy changed my business forever.',
          avatar: '👩‍🌾'
        },
        {
          name: 'David Kariuki',
          location: 'Laikipia',
          story: 'Through Meru Dairy, I access better markets and fair prices. My farm has grown beyond what I ever imagined.',
          avatar: '👨‍🌾'
        }
      ],
      partners: [
        'Kenya Dairy Board',
        'Ministry of Agriculture',
        'World Bank',
        'USAID',
        'AGRA',
        'Equity Bank'
      ]
    }
  },
  methods: {
    downloadPolicy() {
      alert('Food Safety Policy PDF will be available for download soon.')
    }
  },
  mounted() {
    // Add scroll animation observer
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
</script>

<style scoped>
/* Hero Section */
.about-hero {
  position: relative;
  min-height: 80vh;
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
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" opacity="0.1"><path fill="white" d="M50,30 L60,50 L50,70 L40,50 Z"/><circle cx="70" cy="30" r="10"/><circle cx="30" cy="70" r="10"/></svg>') repeat;
}

.hero-pattern {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(to top, white, transparent);
}

.hero-content {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 100px 0;
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
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 50px;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #f59e0b;
}

.stat-label {
  color: white;
  font-size: 0.85rem;
  margin-top: 5px;
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

/* Mission Vision Section */
.mission-vision {
  padding: 80px 0;
  background: #f8fafc;
}

.mv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.mv-card {
  padding: 40px 30px;
  text-align: center;
  transition: transform 0.3s;
}

.mv-card:hover {
  transform: translateY(-10px);
}

.mv-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.mv-card h3 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 15px;
}

.mv-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.mv-highlight {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.mv-highlight span {
  background: #e0e7ff;
  color: #1e3a8a;
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
}

/* Timeline Section */
.journey-section {
  padding: 80px 0;
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

.timeline {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
}

.timeline-item {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  position: relative;
}

.timeline-marker {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-dot {
  width: 16px;
  height: 16px;
  background: #f59e0b;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 3px #f59e0b;
  z-index: 1;
}

.marker-line {
  width: 2px;
  height: 100%;
  background: linear-gradient(to bottom, #f59e0b, #e0e7ff);
  margin-top: 8px;
}

.timeline-content {
  flex: 1;
  padding: 25px;
  position: relative;
  transition: transform 0.3s;
}

.timeline-content:hover {
  transform: translateX(10px);
}

.timeline-year {
  display: inline-block;
  background: #f59e0b;
  color: white;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.timeline-content h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

.timeline-content p {
  color: #666;
  line-height: 1.6;
}

.timeline-icon {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 2rem;
  opacity: 0.3;
}

/* Leadership Section */
.leadership-section {
  padding: 80px 0;
  background: #f8fafc;
}

.leadership-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.leader-card {
  padding: 30px;
  text-align: center;
  transition: transform 0.3s;
}

.leader-card:hover {
  transform: translateY(-5px);
}

.leader-image {
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  font-size: 3rem;
}

.leader-card h3 {
  color: #1e3a8a;
  margin-bottom: 5px;
}

.leader-title {
  color: #f59e0b;
  font-weight: 600;
  margin-bottom: 10px;
}

.leader-bio {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 15px;
}

.leader-social {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.social-link {
  width: 30px;
  height: 30px;
  background: #e0e7ff;
  color: #1e3a8a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
}

.social-link:hover {
  background: #1e3a8a;
  color: white;
}

/* Impact Section */
.impact-section {
  padding: 80px 0;
}

.impact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: center;
}

.impact-content h2 {
  font-size: 2rem;
  color: #1e3a8a;
  margin: 20px 0;
}

.impact-content p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 30px;
}

.impact-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.impact-feature {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.impact-icon {
  font-size: 2rem;
}

.impact-feature strong {
  display: block;
  color: #1e3a8a;
  margin-bottom: 5px;
}

.impact-feature p {
  margin: 0;
  font-size: 0.9rem;
}

.impact-stats {
  padding: 40px;
  text-align: center;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
}

.stat-item-large {
  margin-bottom: 30px;
}

.stat-item-large:last-child {
  margin-bottom: 0;
}

.stat-item-large .stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: #f59e0b;
}

/* Stories Section */
.stories-section {
  padding: 80px 0;
  background: #f8fafc;
}

.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.story-card {
  padding: 30px;
  position: relative;
}

.story-quote {
  font-size: 4rem;
  color: #f59e0b;
  opacity: 0.3;
  font-family: serif;
  position: absolute;
  top: 20px;
  left: 20px;
}

.story-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.story-author {
  display: flex;
  gap: 15px;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.author-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.author-details strong {
  display: block;
  color: #1e3a8a;
}

.author-details span {
  font-size: 0.85rem;
  color: #666;
}

/* Food Safety Section */
.safety-section {
  padding: 80px 0;
}

.safety-card {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 30px;
  padding: 40px;
  align-items: center;
  background: linear-gradient(135deg, #f0f4ff, white);
}

.safety-icon {
  font-size: 4rem;
}

.safety-content h3 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 15px;
}

.safety-content p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.safety-badges {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.safety-badges span {
  background: #d1fae5;
  color: #065f46;
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.85rem;
}

.btn-download {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
}

.btn-download:hover {
  background: #3b82f6;
  transform: translateY(-2px);
}

/* Partners Section */
.partners-section {
  padding: 80px 0;
  background: #f8fafc;
}

.partners-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 30px;
}

.partner-card {
  padding: 30px;
  text-align: center;
  transition: transform 0.3s;
}

.partner-card:hover {
  transform: translateY(-5px);
}

.partner-logo {
  font-weight: 600;
  color: #1e3a8a;
}

/* Glass Card Effect */
.glass-card {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

/* Animations */
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

.animate-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.animate-on-scroll.visible {
  opacity: 1;
  transform: translateY(0);
}

.delay-1 {
  transition-delay: 0.2s;
}

.delay-2 {
  transition-delay: 0.4s;
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

/* Responsive */
@media (max-width: 968px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .impact-grid {
    grid-template-columns: 1fr;
  }
  
  .safety-card {
    grid-template-columns: 1fr;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-stats {
    gap: 30px;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  .timeline-item {
    flex-direction: column;
  }
  
  .timeline-marker {
    display: none;
  }
  
  .leadership-grid,
  .stories-grid {
    grid-template-columns: 1fr;
  }
}
</style>