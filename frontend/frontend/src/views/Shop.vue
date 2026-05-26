<template>
  <main>
    <!-- Hero Section -->
    <section class="shop-hero">
      <div class="hero-background">
        <div class="hero-overlay"></div>
        <div class="hero-pattern"></div>
      </div>
      
      <div class="container">
        <div class="hero-content">
          <div class="hero-text animate-fade-in-up">
            <span class="hero-badge">Coming Soon</span>
            <h1 class="hero-title">Online <span class="highlight">Shopping</span></h1>
            <p class="hero-description">
              Experience the convenience of ordering fresh Mount Kenya Milk products 
              from the comfort of your home. Our online store is launching soon!
            </p>
            <div class="hero-buttons">
              <a href="https://shop.mountkenyamilk.co.ke/" target="_blank" class="btn btn-primary btn-large">
                Visit Our Shop
                <span class="btn-icon">→</span>
              </a>
              <router-link to="/products" class="btn btn-outline-light btn-large">
                Browse Products
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <span>Shop with confidence</span>
        <div class="scroll-mouse"></div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Why Shop With Us</span>
          <h2 class="section-title">A Better Shopping Experience</h2>
          <p class="section-subtitle">
            We're building an online store that puts you first
          </p>
        </div>
        
        <div class="features-grid">
          <div class="feature-card glass-card animate-on-scroll">
            <div class="feature-icon">🚚</div>
            <h3>Fast Delivery</h3>
            <p>Fresh products delivered to your doorstep within 24 hours</p>
          </div>
          <div class="feature-card glass-card animate-on-scroll delay-1">
            <div class="feature-icon">💳</div>
            <h3>Secure Payments</h3>
            <p>Multiple payment options including M-Pesa and cards</p>
          </div>
          <div class="feature-card glass-card animate-on-scroll delay-2">
            <div class="feature-icon">🔄</div>
            <h3>Easy Returns</h3>
            <p>Hassle-free returns within 7 days of delivery</p>
          </div>
          <div class="feature-card glass-card animate-on-scroll delay-3">
            <div class="feature-icon">⭐</div>
            <h3>Quality Guaranteed</h3>
            <p>100% fresh products with quality certification</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Sales Section -->
    <section class="contact-sales-section">
      <div class="container">
        <div class="contact-grid">
          <div class="contact-info glass-card">
            <div class="contact-icon">📞</div>
            <h3>Need Bulk Orders?</h3>
            <p>Contact our dedicated sales team for wholesale inquiries, corporate orders, or special requirements.</p>
            
            <div class="contact-details">
              <div class="contact-item">
                <span class="contact-label">Phone:</span>
                <a href="tel:+254719111444" class="contact-value">+254 719 111 444</a>
              </div>
              <div class="contact-item">
                <span class="contact-label">Email:</span>
                <a href="mailto:sales@merudairy.co.ke" class="contact-value">sales@merudairy.co.ke</a>
              </div>
              <div class="contact-item">
                <span class="contact-label">Hours:</span>
                <span class="contact-value">Mon-Fri: 8AM - 5PM</span>
              </div>
            </div>
            
            <router-link to="/contact" class="btn-contact">
              Message Sales Team
              <span class="arrow">→</span>
            </router-link>
          </div>
          
          <div class="sales-image glass-card">
            <div class="image-placeholder">
              <span>🥛</span>
            </div>
            <div class="floating-badge">
              <span>Bulk Discounts Available</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Updates Section -->
    <section class="updates-section">
      <div class="container">
        <div class="updates-card glass-card">
          <div class="updates-icon">🚀</div>
          <h3>We're Working Hard to Serve You Better</h3>
          <p>Our online shop is currently under development with exciting new features coming soon. Stay tuned for updates and be the first to know when we launch!</p>
          
          <div class="updates-grid">
            <div class="update-item">
              <div class="update-check">✓</div>
              <div>User-friendly interface</div>
            </div>
            <div class="update-item">
              <div class="update-check">✓</div>
              <div>Real-time order tracking</div>
            </div>
            <div class="update-item">
              <div class="update-check">✓</div>
              <div>Subscription options</div>
            </div>
            <div class="update-item">
              <div class="update-check">✓</div>
              <div>Loyalty rewards program</div>
            </div>
          </div>
          
          <div class="notification-banner">
            <p>📧 Get notified when we launch</p>
            <div class="notification-form">
              <input type="email" placeholder="Enter your email" v-model="notificationEmail">
              <button @click="notifyMe" :disabled="notifyLoading">
                {{ notifyLoading ? 'Subscribing...' : 'Notify Me' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Physical Store Locations -->
    <section class="locations-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Visit Us</span>
          <h2 class="section-title">Our Physical Stores</h2>
          <p class="section-subtitle">
            Can't wait for online delivery? Visit our stores nationwide
          </p>
        </div>
        
        <div class="locations-grid">
          <div class="location-card glass-card animate-on-scroll">
            <div class="location-icon">📍</div>
            <h3>Nairobi</h3>
            <p>Kenyatta Avenue, Nairobi CBD</p>
            <p>Mon-Sat: 8AM - 6PM</p>
          </div>
          <div class="location-card glass-card animate-on-scroll delay-1">
            <div class="location-icon">📍</div>
            <h3>Meru</h3>
            <p>Main Branch, Meru Town</p>
            <p>Mon-Sat: 8AM - 6PM</p>
          </div>
          <div class="location-card glass-card animate-on-scroll delay-2">
            <div class="location-icon">📍</div>
            <h3>Mombasa</h3>
            <p>Moi Avenue, Mombasa CBD</p>
            <p>Mon-Sat: 8AM - 6PM</p>
          </div>
          <div class="location-card glass-card animate-on-scroll delay-3">
            <div class="location-icon">📍</div>
            <h3>Kisumu</h3>
            <p>Oginga Odinga Street</p>
            <p>Mon-Sat: 8AM - 6PM</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card glass-card">
          <div class="cta-content">
            <h2>Ready to place a bulk order?</h2>
            <p>Get competitive pricing and dedicated support for wholesale purchases</p>
            <div class="cta-buttons">
              <a href="tel:+254719111444" class="btn btn-primary">
                Call Sales Team
                <span class="btn-icon">📞</span>
              </a>
              <router-link to="/products" class="btn btn-secondary">
                Browse Products
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: 'Shop',
  data() {
    return {
      notificationEmail: '',
      notifyLoading: false
    }
  },
  mounted() {
    this.setupScrollAnimation()
  },
  methods: {
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
    },
    notifyMe() {
      if (!this.notificationEmail) {
        alert('Please enter your email address')
        return
      }
      
      this.notifyLoading = true
      // Simulate API call
      setTimeout(() => {
        alert(`Thank you! We'll notify you at ${this.notificationEmail} when our shop launches.`)
        this.notificationEmail = ''
        this.notifyLoading = false
      }, 1000)
    }
  }
}
</script>

<style scoped>
/* Hero Section */
.shop-hero {
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
}

.hero-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
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
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
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
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
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

/* Features Section */
.features-section {
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

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  padding: 40px 30px;
  text-align: center;
  background: white;
  transition: all 0.3s;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.feature-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* Contact Sales Section */
.contact-sales-section {
  padding: 80px 0;
  background: white;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}

.contact-info {
  padding: 40px;
  text-align: center;
  background: white;
}

.contact-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.contact-info h3 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 15px;
}

.contact-info p {
  color: #666;
  margin-bottom: 25px;
  line-height: 1.6;
}

.contact-details {
  text-align: left;
  margin: 25px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.contact-item {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.contact-label {
  font-weight: 600;
  color: #1e3a8a;
}

.contact-value {
  color: #f59e0b;
  text-decoration: none;
}

.btn-contact {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #1e3a8a;
  color: white;
  padding: 12px 24px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-contact:hover {
  background: #3b82f6;
  transform: translateY(-2px);
}

.btn-contact .arrow {
  transition: transform 0.3s;
}

.btn-contact:hover .arrow {
  transform: translateX(5px);
}

.sales-image {
  position: relative;
  padding: 40px;
  text-align: center;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
}

.image-placeholder {
  font-size: 8rem;
}

.floating-badge {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #f59e0b;
  color: white;
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.85rem;
  white-space: nowrap;
}

/* Updates Section */
.updates-section {
  padding: 80px 0;
  background: #f8fafc;
}

.updates-card {
  padding: 50px;
  text-align: center;
  background: white;
}

.updates-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.updates-card h3 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 15px;
}

.updates-card > p {
  color: #666;
  max-width: 600px;
  margin: 0 auto 30px;
  line-height: 1.6;
}

.updates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.update-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.update-check {
  width: 24px;
  height: 24px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.notification-banner {
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  padding: 30px;
  border-radius: 16px;
  color: white;
}

.notification-banner p {
  margin-bottom: 15px;
  font-size: 1rem;
}

.notification-form {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.notification-form input {
  padding: 12px 20px;
  border: none;
  border-radius: 50px;
  width: 250px;
  font-size: 0.9rem;
}

.notification-form button {
  padding: 12px 24px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.notification-form button:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
}

.notification-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Locations Section */
.locations-section {
  padding: 80px 0;
  background: white;
}

.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.location-card {
  padding: 30px;
  text-align: center;
  background: white;
  transition: all 0.3s;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.location-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.location-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
}

.location-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.location-card h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

.location-card p {
  color: #666;
  margin-bottom: 5px;
  font-size: 0.9rem;
}

/* CTA Section */
.cta-section {
  padding: 80px 0;
  background: #f8fafc;
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

/* Glass Card Effect */
.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
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

.delay-1 { transition-delay: 0.15s; }
.delay-2 { transition-delay: 0.3s; }
.delay-3 { transition-delay: 0.45s; }

/* Responsive */
@media (max-width: 968px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .contact-grid {
    grid-template-columns: 1fr;
  }
  
  .updates-card {
    padding: 30px;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .features-grid,
  .locations-grid {
    grid-template-columns: 1fr;
  }
  
  .updates-grid {
    grid-template-columns: 1fr;
  }
  
  .notification-form {
    flex-direction: column;
    align-items: center;
  }
  
  .notification-form input {
    width: 100%;
    max-width: 300px;
  }
  
  .cta-card {
    padding: 40px 20px;
  }
  
  .cta-content h2 {
    font-size: 1.5rem;
  }
  
  .contact-item {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
  
  .floating-badge {
    white-space: normal;
    font-size: 0.7rem;
    width: 90%;
  }
}
</style>