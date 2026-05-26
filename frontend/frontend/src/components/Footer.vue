<template>
  <footer class="footer">
    <!-- Main Footer Content -->
    <div class="footer-main">
      <div class="container">
        <div class="footer-grid">
          <!-- Brand Section -->
          <div class="footer-brand">
            <div class="brand-logo">
              <img src="/logo.png" alt="Mount Kenya Milk" class="logo-img" @error="handleImageError">
              <span class="brand-name">Mount Kenya Milk</span>
            </div>
            <p class="brand-description">
              Kenya's biggest dairy co-operative, providing quality dairy products 
              from the pristine slopes of Mount Kenya.
            </p>
            <div class="certification-badges">
              <span class="cert-badge">⭐ ISO 22000</span>
              <span class="cert-badge">✓ HACCP</span>
              <span class="cert-badge">🏆 KEBS</span>
            </div>
          </div>

          <!-- Quick Links -->
          <div class="footer-section">
            <h3 class="footer-title">Quick Links</h3>
            <ul class="footer-links">
              <li><router-link to="/">Home</router-link></li>
              <li><router-link to="/about">About Us</router-link></li>
              <li><router-link to="/products">Products</router-link></li>
              <li><router-link to="/shop">Shop Online</router-link></li>
              <li><router-link to="/blog">Blog</router-link></li>
            </ul>
          </div>

          <!-- Important Links -->
          <div class="footer-section">
            <h3 class="footer-title">Important Links</h3>
            <ul class="footer-links">
              <li><router-link to="/contact">Contact Us</router-link></li>
              <li><router-link to="/careers">Careers</router-link></li>
              <li><router-link to="/csr">CSR Initiatives</router-link></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Terms & Conditions</a></li>
            </ul>
          </div>

          <!-- Contact Info -->
          <div class="footer-section">
            <h3 class="footer-title">Contact Info</h3>
            <div class="contact-info">
              <div class="contact-item">
                <span class="contact-icon">📍</span>
                <span>Meru Town, Kenya</span>
              </div>
              <div class="contact-item">
                <span class="contact-icon">📞</span>
                <div>
                  <a href="tel:+254710901376">+254 710 901 376</a><br>
                  <a href="tel:+254719111444">+254 719 111 444</a>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">✉️</span>
                <div>
                  <a href="mailto:maziwa@merudairy.co.ke">maziwa@merudairy.co.ke</a><br>
                  <a href="mailto:sales@merudairy.co.ke">sales@merudairy.co.ke</a>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">🕒</span>
                <span>Mon-Fri: 8AM - 5PM<br>Sat: 9AM - 1PM</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Newsletter Section -->
    <div class="footer-newsletter">
      <div class="container">
        <div class="newsletter-wrapper glass-card">
          <div class="newsletter-content">
            <div class="newsletter-icon">📧</div>
            <div>
              <h3>Subscribe to Our Newsletter</h3>
              <p>Get updates on products, promotions, and dairy industry news</p>
            </div>
          </div>
          <div class="newsletter-form">
            <input 
              type="email" 
              v-model="newsletterEmail" 
              placeholder="Enter your email address"
              class="newsletter-input"
            >
            <button @click="subscribeNewsletter" :disabled="newsletterLoading" class="newsletter-btn">
              {{ newsletterLoading ? 'Subscribing...' : 'Subscribe' }}
              <span class="btn-icon">→</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Bottom -->
    <div class="footer-bottom">
      <div class="container">
        <div class="bottom-content">
          <div class="copyright">
            <p>&copy; {{ currentYear }} Meru Central Dairy Co-operative Union Ltd. All rights reserved.</p>
          </div>
          
          <div class="social-links">
            <a href="#" class="social-icon" aria-label="Facebook">
              <span>📘</span>
            </a>
            <a href="#" class="social-icon" aria-label="Twitter">
              <span>🐦</span>
            </a>
            <a href="#" class="social-icon" aria-label="Instagram">
              <span>📸</span>
            </a>
            <a href="#" class="social-icon" aria-label="LinkedIn">
              <span>💼</span>
            </a>
            <a href="#" class="social-icon" aria-label="YouTube">
              <span>▶️</span>
            </a>
          </div>
          
          <div class="payment-methods">
            <span class="payment-icon">💳 Visa</span>
            <span class="payment-icon">💳 Mastercard</span>
            <span class="payment-icon">📱 M-Pesa</span>
            <span class="payment-icon">💵 Cash</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Back to Top Button -->
    <button 
      v-show="showBackToTop" 
      @click="scrollToTop" 
      class="back-to-top glass-card"
      aria-label="Back to top"
    >
      <span>↑</span>
    </button>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  data() {
    return {
      newsletterEmail: '',
      newsletterLoading: false,
      showBackToTop: false,
      currentYear: new Date().getFullYear()
    }
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    handleImageError(e) {
      e.target.style.display = 'none'
    },
    handleScroll() {
      this.showBackToTop = window.scrollY > 300
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    async subscribeNewsletter() {
      if (!this.newsletterEmail) {
        alert('Please enter your email address')
        return
      }
      
      if (!this.newsletterEmail.includes('@')) {
        alert('Please enter a valid email address')
        return
      }
      
      this.newsletterLoading = true
      
      // Simulate API call - replace with actual endpoint
      setTimeout(() => {
        alert(`Thank you for subscribing! We'll send updates to ${this.newsletterEmail}`)
        this.newsletterEmail = ''
        this.newsletterLoading = false
      }, 1000)
    }
  }
}
</script>

<style scoped>
.footer {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
  position: relative;
  overflow: hidden;
}

.footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #f59e0b, #3b82f6, #10b981, #f59e0b);
  background-size: 200% 100%;
  animation: gradientMove 3s ease infinite;
}

@keyframes gradientMove {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

/* Main Footer */
.footer-main {
  padding: 60px 0 40px;
  position: relative;
  z-index: 1;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 40px;
}

/* Brand Section */
.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.logo-img {
  width: 50px;
  height: 50px;
  object-fit: contain;
}

.brand-name {
  font-size: 1.3rem;
  font-weight: 700;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.brand-description {
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.certification-badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.cert-badge {
  background: rgba(255,255,255,0.1);
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.7rem;
  color: #cbd5e1;
}

/* Footer Sections */
.footer-section {
  margin-bottom: 30px;
}

.footer-title {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 20px;
  position: relative;
  display: inline-block;
}

.footer-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 30px;
  height: 2px;
  background: #f59e0b;
  border-radius: 2px;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 12px;
}

.footer-links a {
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.footer-links a::before {
  content: '→';
  opacity: 0;
  transition: all 0.3s;
}

.footer-links a:hover {
  color: #f59e0b;
  transform: translateX(5px);
}

.footer-links a:hover::before {
  opacity: 1;
  margin-right: 5px;
}

/* Contact Info */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.contact-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  font-size: 0.85rem;
  color: #94a3b8;
}

.contact-icon {
  font-size: 1.1rem;
  min-width: 24px;
}

.contact-item a {
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.3s;
}

.contact-item a:hover {
  color: #f59e0b;
}

/* Newsletter Section */
.footer-newsletter {
  padding: 0 0 40px;
  position: relative;
  z-index: 1;
}

.newsletter-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 30px;
  padding: 30px 40px;
  background: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.1);
}

.newsletter-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.newsletter-icon {
  font-size: 2.5rem;
}

.newsletter-content h3 {
  color: white;
  font-size: 1.2rem;
  margin-bottom: 5px;
}

.newsletter-content p {
  color: #94a3b8;
  font-size: 0.85rem;
}

.newsletter-form {
  display: flex;
  gap: 12px;
  min-width: 350px;
}

.newsletter-input {
  flex: 1;
  padding: 12px 16px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  color: white;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.newsletter-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}

.newsletter-input::placeholder {
  color: #64748b;
}

.newsletter-btn {
  padding: 12px 24px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.newsletter-btn:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
}

.newsletter-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  transition: transform 0.3s;
}

.newsletter-btn:hover .btn-icon {
  transform: translateX(5px);
}

/* Footer Bottom */
.footer-bottom {
  padding: 20px 0;
  border-top: 1px solid rgba(255,255,255,0.1);
  position: relative;
  z-index: 1;
}

.bottom-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.copyright p {
  font-size: 0.8rem;
  color: #64748b;
}

/* Social Links */
.social-links {
  display: flex;
  gap: 15px;
}

.social-icon {
  width: 36px;
  height: 36px;
  background: #1e293b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.3s;
}

.social-icon:hover {
  background: #f59e0b;
  color: white;
  transform: translateY(-3px);
}

/* Payment Methods */
.payment-methods {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.payment-icon {
  font-size: 0.75rem;
  color: #64748b;
  padding: 4px 10px;
  background: #1e293b;
  border-radius: 50px;
}

/* Back to Top Button */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 100;
}

.back-to-top span {
  font-size: 1.5rem;
  color: #f59e0b;
}

.back-to-top:hover {
  transform: translateY(-5px);
  background: #f59e0b;
  box-shadow: 0 5px 15px rgba(245,158,11,0.3);
}

.back-to-top:hover span {
  color: white;
}

/* Glass Card Effect */
.glass-card {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .footer-grid {
    grid-template-columns: 1.5fr 1fr 1fr;
    gap: 30px;
  }
  
  .footer-section:last-child {
    grid-column: span 3;
  }
  
  .newsletter-wrapper {
    flex-direction: column;
    text-align: center;
  }
  
  .newsletter-content {
    flex-direction: column;
    text-align: center;
  }
  
  .newsletter-form {
    width: 100%;
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .footer-main {
    padding: 40px 0 20px;
  }
  
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .footer-section:last-child {
    grid-column: span 1;
  }
  
  .footer-title::after {
    left: 0;
    transform: none;
  }
  
  .bottom-content {
    flex-direction: column;
    text-align: center;
  }
  
  .social-links {
    justify-content: center;
  }
  
  .payment-methods {
    justify-content: center;
  }
  
  .newsletter-wrapper {
    padding: 25px 20px;
    margin: 0 20px;
  }
  
  .newsletter-form {
    flex-direction: column;
  }
  
  .newsletter-btn {
    justify-content: center;
  }
  
  .back-to-top {
    bottom: 20px;
    right: 20px;
    width: 45px;
    height: 45px;
  }
  
  .back-to-top span {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .brand-logo {
    justify-content: center;
  }
  
  .brand-description {
    text-align: center;
  }
  
  .certification-badges {
    justify-content: center;
  }
  
  .footer-section {
    text-align: center;
  }
  
  .footer-title::after {
    left: 50%;
    transform: translateX(-50%);
  }
  
  .footer-links a {
    justify-content: center;
  }
  
  .contact-item {
    justify-content: center;
  }
  
  .newsletter-content h3 {
    font-size: 1rem;
  }
  
  .newsletter-content p {
    font-size: 0.75rem;
  }
}
</style>