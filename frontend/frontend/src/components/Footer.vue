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
              <div class="brand-info">
                <h3>Mount Kenya Milk</h3>
                <p>Kenya's biggest dairy co-operative</p>
              </div>
            </div>
            <p class="brand-description">
              Providing quality dairy products from the pristine slopes of Mount Kenya 
              since 1972. Empowering over 120,000 farmers and serving millions of customers nationwide.
            </p>
            <div class="certification-badges">
              <span class="cert-badge">
                <i class="fas fa-check-circle"></i> ISO 22000
              </span>
              <span class="cert-badge">
                <i class="fas fa-check-circle"></i> HACCP
              </span>
              <span class="cert-badge">
                <i class="fas fa-check-circle"></i> KEBS
              </span>
            </div>
          </div>

          <!-- Quick Links -->
          <div class="footer-links">
            <h4>Quick Links</h4>
            <ul>
              <li><a @click.prevent="scrollTo('home')" href="#">Home</a></li>
              <li><a @click.prevent="scrollTo('about')" href="#">About Us</a></li>
              <li><a @click.prevent="scrollTo('products')" href="#">Products</a></li>
              <li><a @click.prevent="scrollTo('shop')" href="#">Shop Online</a></li>
              <li><a @click.prevent="scrollTo('blog')" href="#">Blog</a></li>
              <li><a @click.prevent="scrollTo('contact')" href="#">Contact Us</a></li>
            </ul>
          </div>

          <!-- Important Links -->
          <div class="footer-links">
            <h4>Resources</h4>
            <ul>
              <li><router-link to="/careers">Careers</router-link></li>
              <li><router-link to="/csr">CSR Initiatives</router-link></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Terms & Conditions</a></li>
              <li><a href="#">FAQs</a></li>
              <li><a href="#">Delivery Information</a></li>
            </ul>
          </div>

          <!-- Contact Info -->
          <div class="footer-contact">
            <h4>Contact Us</h4>
            <div class="contact-details">
              <div class="contact-item">
                <i class="fas fa-map-marker-alt"></i>
                <span>Meru Town, Kenya</span>
              </div>
              <div class="contact-item">
                <i class="fas fa-phone-alt"></i>
                <div>
                  <a href="tel:+254710901376">+254 710 901 376</a><br>
                  <a href="tel:+254719111444">+254 719 111 444</a>
                </div>
              </div>
              <div class="contact-item">
                <i class="fas fa-envelope"></i>
                <div>
                  <a href="mailto:info@merudairy.co.ke">info@merudairy.co.ke</a><br>
                  <a href="mailto:sales@merudairy.co.ke">sales@merudairy.co.ke</a>
                </div>
              </div>
              <div class="contact-item">
                <i class="fas fa-clock"></i>
                <div>
                  <span>Mon-Fri: 8AM - 5PM</span><br>
                  <span>Sat: 9AM - 1PM</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Newsletter Subscription Section -->
    <div class="footer-newsletter">
      <div class="container">
        <div class="newsletter-wrapper">
          <div class="newsletter-content">
            <div class="newsletter-icon">
              <i class="fas fa-envelope-open-text"></i>
            </div>
            <div>
              <h3>Subscribe to Our Newsletter</h3>
              <p>Get the latest updates on products, promotions, and dairy industry news</p>
            </div>
          </div>
          <form @submit.prevent="submitNewsletter" class="newsletter-form">
            <div class="input-group">
              <i class="fas fa-user"></i>
              <input 
                type="text" 
                v-model="newsletterForm.name" 
                placeholder="Your Name" 
                required
              >
            </div>
            <div class="input-group">
              <i class="fas fa-envelope"></i>
              <input 
                type="email" 
                v-model="newsletterForm.email" 
                placeholder="Email Address" 
                required
              >
            </div>
            <button type="submit" class="btn-subscribe" :disabled="newsletterLoading">
              <span v-if="!newsletterLoading">Subscribe</span>
              <span v-else><i class="fas fa-spinner fa-spin"></i> Subscribing...</span>
              <i class="fas fa-arrow-right"></i>
            </button>
          </form>
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
              <i class="fab fa-facebook-f"></i>
            </a>
            <a href="#" class="social-icon" aria-label="Twitter">
              <i class="fab fa-twitter"></i>
            </a>
            <a href="#" class="social-icon" aria-label="Instagram">
              <i class="fab fa-instagram"></i>
            </a>
            <a href="#" class="social-icon" aria-label="LinkedIn">
              <i class="fab fa-linkedin-in"></i>
            </a>
            <a href="#" class="social-icon" aria-label="YouTube">
              <i class="fab fa-youtube"></i>
            </a>
          </div>
          
          <!-- <div class="payment-methods">
            <span class="payment-icon">
              <i class="fab fa-cc-visa"></i> Visa
            </span>
            <span class="payment-icon">
              <i class="fab fa-cc-mastercard"></i> Mastercard
            </span>
            <span class="payment-icon">
              <i class="fas fa-mobile-alt"></i> M-Pesa
            </span>
            <span class="payment-icon">
              <i class="fas fa-money-bill-wave"></i> Cash
            </span>
          </div> -->
        </div>
      </div>
    </div>

    <!-- Back to Top Button -->
    <button 
      v-show="showBackToTop" 
      @click="scrollToTop" 
      class="back-to-top"
      aria-label="Back to top"
    >
      <i class="fas fa-arrow-up"></i>
    </button>

    <!-- Newsletter Success Modal -->
    <div v-if="showNewsletterSuccess" class="newsletter-success-modal" @click.self="closeNewsletterSuccess">
      <div class="success-content">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h3>Subscribed Successfully!</h3>
        <p>Thank you for subscribing to our newsletter. You'll receive updates on products, promotions, and dairy industry news.</p>
        <button @click="closeNewsletterSuccess" class="btn-close">Continue</button>
      </div>
    </div>

    <!-- Newsletter Error Modal -->
<div v-if="showNewsletterError" class="newsletter-success-modal" @click.self="showNewsletterError = false">
  <div class="success-content" style="border-top: 4px solid #ef4444;">
    <div class="success-icon" style="background: #fee2e2;">
      <i class="fas fa-exclamation-circle" style="color: #ef4444;"></i>
    </div>
    <h3 style="color: #991b1b;">Subscription Failed</h3>
    <p>{{ newsletterErrorMessage }}</p>
    <button @click="showNewsletterError = false" class="btn-close">Try Again</button>
  </div>
</div>



  </footer>
</template>

<script>
import { scrollToSection } from '@/utils/scroll'
import api from '@/services/api'

export default {
  name: 'Footer',
  data() {
    return {
      newsletterForm: {
        name: '',
        email: ''
      },
      newsletterLoading: false,
      showBackToTop: false,
      showNewsletterSuccess: false,
      currentYear: new Date().getFullYear(),
        showNewsletterError: false,
        newsletterErrorMessage: ''
    }
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    handleScroll() {
      this.showBackToTop = window.scrollY > 300
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    scrollTo(sectionId) {
      scrollToSection(sectionId, 80)
    },
    handleImageError(e) {
      e.target.style.display = 'none'
    },


    async submitNewsletter() {
  if (!this.newsletterForm.email.includes('@')) {
    this.newsletterErrorMessage = 'Please enter a valid email address'
    this.showNewsletterError = true
    return
  }

  this.newsletterLoading = true
  
  try {
    const response = await api.post('/newsletter/subscribe', {
      name: this.newsletterForm.name,
      email: this.newsletterForm.email
    })
    
    this.showNewsletterSuccess = true
    this.newsletterForm = { name: '', email: '' }
    
    setTimeout(() => {
      this.showNewsletterSuccess = false
    }, 5000)
    
  } catch (error) {
    this.newsletterErrorMessage = error.response?.data?.error || 'Failed to subscribe. Please try again.'
    this.showNewsletterError = true
    
    // Auto hide error after 5 seconds
    setTimeout(() => {
      this.showNewsletterError = false
    }, 5000)
  } finally {
    this.newsletterLoading = false
  }
},

    closeNewsletterSuccess() {
      this.showNewsletterSuccess = false
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
  height: 3px;
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

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 40px;
}

/* Brand Section */
.footer-brand {
  margin-bottom: 20px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.logo-img {
  width: 60px;
  height: 60px;
  object-fit: contain;
}

.brand-info h3 {
  color: white;
  font-size: 1.3rem;
  margin: 0 0 5px;
}

.brand-info p {
  color: #94a3b8;
  font-size: 0.85rem;
  margin: 0;
}

.brand-description {
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.certification-badges {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.cert-badge {
  background: rgba(255,255,255,0.1);
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.7rem;
  color: #cbd5e1;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.cert-badge i {
  color: #10b981;
  font-size: 0.6rem;
}

/* Footer Links */
.footer-links h4,
.footer-contact h4 {
  color: white;
  font-size: 1.1rem;
  margin-bottom: 20px;
  position: relative;
  display: inline-block;
}

.footer-links h4::after,
.footer-contact h4::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 40px;
  height: 2px;
  background: #f59e0b;
  border-radius: 2px;
}

.footer-links ul {
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
  font-size: 0.9rem;
  cursor: pointer;
  display: inline-block;
}

.footer-links a:hover {
  color: #f59e0b;
  transform: translateX(5px);
}

/* Contact Section */
.contact-details {
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

.contact-item i {
  color: #f59e0b;
  margin-top: 3px;
  width: 18px;
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
  padding: 40px 0;
  background: rgba(255,255,255,0.05);
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.newsletter-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
  flex-wrap: wrap;
}

.newsletter-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.newsletter-icon {
  width: 60px;
  height: 60px;
  background: rgba(245,158,11,0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.newsletter-icon i {
  font-size: 1.8rem;
  color: #f59e0b;
}

.newsletter-content h3 {
  color: white;
  margin: 0 0 5px;
  font-size: 1.2rem;
}

.newsletter-content p {
  color: #94a3b8;
  margin: 0;
  font-size: 0.85rem;
}

.newsletter-form {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-group i {
  position: absolute;
  left: 14px;
  color: #64748b;
}

.input-group input {
  padding: 12px 16px 12px 42px;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  background: #1e293b;
  color: white;
  font-size: 0.9rem;
  width: 250px;
  transition: all 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}

.input-group input::placeholder {
  color: #64748b;
}

.btn-subscribe {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
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

/* Footer Bottom */
.footer-bottom {
  padding: 25px 0;
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
  margin: 0;
}

/* Social Links */
.social-links {
  display: flex;
  gap: 12px;
}

.social-icon {
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.1);
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
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.payment-icon i {
  font-size: 1rem;
}

/* Back to Top Button */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 45px;
  height: 45px;
  background: #f59e0b;
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  z-index: 999;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.back-to-top:hover {
  background: #d97706;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(245,158,11,0.3);
}

/* Newsletter Success Modal */
.newsletter-success-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.success-content {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  max-width: 400px;
  width: 90%;
  animation: fadeInUp 0.3s ease;
}

.success-icon {
  width: 70px;
  height: 70px;
  background: #d1fae5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.success-icon i {
  font-size: 2.5rem;
  color: #10b981;
}

.success-content h3 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.success-content p {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.btn-close {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
  }
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 30px;
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
    justify-content: center;
  }
  
  .input-group input {
    width: 200px;
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
  
  .footer-links h4::after,
  .footer-contact h4::after {
    left: 50%;
    transform: translateX(-50%);
  }
  
  .footer-links ul {
    text-align: center;
  }
  
  .footer-links a:hover {
    transform: translateX(0);
  }
  
  .contact-item {
    justify-content: center;
  }
  
  .brand-logo {
    justify-content: center;
  }
  
  .brand-info {
    text-align: center;
  }
  
  .brand-description {
    text-align: center;
  }
  
  .certification-badges {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .newsletter-form {
    flex-direction: column;
    width: 100%;
  }
  
  .input-group input {
    width: 100%;
  }
  
  .btn-subscribe {
    width: 100%;
    justify-content: center;
  }
  
  .back-to-top {
    bottom: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
  }
}
</style>