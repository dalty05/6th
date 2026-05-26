<template>
  <main>
    <!-- Hero Section -->
    <section class="contact-hero">
      <div class="hero-background">
        <div class="hero-overlay"></div>
        <div class="hero-pattern"></div>
      </div>
      
      <div class="container">
        <div class="hero-content">
          <div class="hero-text animate-fade-in-up">
            <span class="hero-badge">Get in Touch</span>
            <h1 class="hero-title">We'd Love to <span class="highlight">Hear From You</span></h1>
            <p class="hero-description">
              Have questions about our products, partnerships, or services? 
              Our team is ready to assist you.
            </p>
          </div>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <span>Reach out to us</span>
        <div class="scroll-mouse"></div>
      </div>
    </section>

    <!-- Contact Grid Section -->
    <section class="contact-section">
      <div class="container">
        <div class="contact-grid">
          <!-- Contact Information Cards -->
          <div class="contact-info-wrapper">
            <div class="section-header-left">
              <span class="section-badge">Contact Information</span>
              <h2>Get in Touch</h2>
              <p>We're here to answer your questions and assist with your needs</p>
            </div>
            
            <div class="info-cards">
              <div class="info-card glass-card animate-on-scroll">
                <div class="info-icon">📍</div>
                <div class="info-content">
                  <h3>Address</h3>
                  <p>Meru Central Dairy Co-operative Union Ltd<br>Meru Town, Kenya</p>
                </div>
              </div>
              
              <div class="info-card glass-card animate-on-scroll delay-1">
                <div class="info-icon">📞</div>
                <div class="info-content">
                  <h3>Phone</h3>
                  <p>
                    <a href="tel:+254710901376">+254 710 901 376</a><br>
                    <a href="tel:+254719111444">+254 719 111 444</a>
                  </p>
                </div>
              </div>
              
              <div class="info-card glass-card animate-on-scroll delay-2">
                <div class="info-icon">✉️</div>
                <div class="info-content">
                  <h3>Email</h3>
                  <p>
                    <a href="mailto:maziwa@merudairy.co.ke">maziwa@merudairy.co.ke</a><br>
                    <a href="mailto:sales@merudairy.co.ke">sales@merudairy.co.ke</a>
                  </p>
                </div>
              </div>
              
              <div class="info-card glass-card animate-on-scroll delay-3">
                <div class="info-icon">🕒</div>
                <div class="info-content">
                  <h3>Working Hours</h3>
                  <p>
                    Monday - Friday: 8:00 AM - 5:00 PM<br>
                    Saturday: 9:00 AM - 1:00 PM
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Social Links -->
            <div class="social-links-section">
              <h3>Connect With Us</h3>
              <div class="social-links-grid">
                <a href="#" class="social-link glass-card">
                  <span>📘</span>
                  <span>Facebook</span>
                </a>
                <a href="#" class="social-link glass-card">
                  <span>🐦</span>
                  <span>Twitter</span>
                </a>
                <a href="#" class="social-link glass-card">
                  <span>📸</span>
                  <span>Instagram</span>
                </a>
                <a href="#" class="social-link glass-card">
                  <span>💼</span>
                  <span>LinkedIn</span>
                </a>
              </div>
            </div>
          </div>
          
          <!-- Contact Form -->
          <div class="contact-form-wrapper">
            <div class="form-card glass-card animate-on-scroll">
              <div class="form-header">
                <div class="form-icon">📨</div>
                <h3>Send us a Message</h3>
                <p>We'll get back to you within 24 hours</p>
              </div>
              
              <form @submit.prevent="submitForm" class="contact-form">
                <div class="form-group">
                  <label>Your Name</label>
                  <div class="input-wrapper">
                    <span class="input-icon">👤</span>
                    <input 
                      type="text" 
                      v-model="form.name" 
                      placeholder="John Doe" 
                      required
                    >
                  </div>
                </div>
                
                <div class="form-group">
                  <label>Email Address</label>
                  <div class="input-wrapper">
                    <span class="input-icon">✉️</span>
                    <input 
                      type="email" 
                      v-model="form.email" 
                      placeholder="john@example.com" 
                      required
                    >
                  </div>
                </div>
                
                <div class="form-group">
                  <label>Subject</label>
                  <div class="input-wrapper">
                    <span class="input-icon">📌</span>
                    <input 
                      type="text" 
                      v-model="form.subject" 
                      placeholder="How can we help you?" 
                      required
                    >
                  </div>
                </div>
                
                <div class="form-group">
                  <label>Message</label>
                  <div class="input-wrapper">
                    <span class="input-icon">💬</span>
                    <textarea 
                      v-model="form.message" 
                      placeholder="Tell us more about your inquiry..." 
                      rows="5" 
                      required
                    ></textarea>
                  </div>
                </div>
                
                <button type="submit" class="btn-submit" :disabled="isSubmitting">
                  <span v-if="!isSubmitting">Send Message</span>
                  <span v-else>Sending...</span>
                  <span class="btn-icon">→</span>
                </button>
              </form>
              
              <div class="form-note">
                <span>🔒</span>
                <p>Your information is safe with us. We never share your data.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Map Section -->
    <section class="map-section">
      <div class="container">
        <div class="map-card glass-card">
          <div class="map-header">
            <span class="section-badge">Find Us</span>
            <h2>Visit Our Headquarters</h2>
            <p>Located in the heart of Meru Town</p>
          </div>
          
          <div class="map-container">
            <iframe 
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d15959.123456789!2d37.6497!3d0.0500!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMMKwMDMnMDAuMCJTIDM3wrAzOScwMC4wIkU!5e0!3m2!1sen!2ske!4v1234567890123!5m2!1sen!2ske" 
              width="100%" 
              height="400" 
              style="border:0;" 
              allowfullscreen="" 
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
            ></iframe>
          </div>
          
          <div class="map-badges">
            <div class="map-badge">
              <span>🚗</span>
              <span>Free Parking Available</span>
            </div>
            <div class="map-badge">
              <span>♿</span>
              <span>Wheelchair Accessible</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="faq-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">FAQs</span>
          <h2 class="section-title">Frequently Asked Questions</h2>
          <p class="section-subtitle">
            Quick answers to common questions
          </p>
        </div>
        
        <div class="faq-grid">
          <div class="faq-card glass-card animate-on-scroll" v-for="(faq, index) in faqs" :key="index">
            <div class="faq-question">
              <span class="faq-icon">❓</span>
              <h3>{{ faq.question }}</h3>
            </div>
            <p>{{ faq.answer }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Success Message Modal -->
    <div v-if="showSuccess" class="success-modal" @click.self="showSuccess = false">
      <div class="success-content glass-card">
        <div class="success-icon">✓</div>
        <h3>Message Sent Successfully!</h3>
        <p>Thank you for reaching out. Our team will get back to you within 24 hours.</p>
        <button @click="showSuccess = false" class="btn-close">Close</button>
      </div>
    </div>
  </main>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Contact',
  data() {
    return {
      form: {
        name: '',
        email: '',
        subject: '',
        message: ''
      },
      isSubmitting: false,
      showSuccess: false,
      faqs: [
        {
          question: 'How can I become a supplier?',
          answer: 'Contact our procurement team through sales@merudairy.co.ke with your proposal and certifications.'
        },
        {
          question: 'Do you offer bulk purchase discounts?',
          answer: 'Yes, we offer competitive pricing for bulk orders. Please contact our sales team for a quote.'
        },
        {
          question: 'What is your delivery area?',
          answer: 'We deliver across Kenya. Delivery times vary by location.'
        },
        {
          question: 'How do I report a quality issue?',
          answer: 'Contact our customer service immediately with your product details and batch number.'
        }
      ]
    }
  },
  mounted() {
    this.setupScrollAnimation()
  },
  methods: {
    async submitForm() {
      this.isSubmitting = true
      
      try {
        // Commented out until backend endpoint is ready
        // const response = await axios.post('/api/contact', this.form)
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        this.showSuccess = true
        this.form = { name: '', email: '', subject: '', message: '' }
        
        // Auto hide after 5 seconds
        setTimeout(() => {
          this.showSuccess = false
        }, 5000)
      } catch (error) {
        alert('Failed to send message. Please try again later.')
      } finally {
        this.isSubmitting = false
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
.contact-hero {
  position: relative;
  min-height: 50vh;
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
  padding: 60px 0;
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
  font-size: 3rem;
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

/* Contact Section */
.contact-section {
  padding: 80px 0;
  background: #f8fafc;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
}

/* Contact Info Side */
.contact-info-wrapper {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.section-header-left {
  margin-bottom: 10px;
}

.section-header-left .section-badge {
  display: inline-block;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 15px;
}

.section-header-left h2 {
  font-size: 2rem;
  color: #1e3a8a;
  margin-bottom: 10px;
}

.section-header-left p {
  color: #666;
}

.info-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: white;
  transition: all 0.3s;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.info-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.info-card:hover {
  transform: translateX(5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.info-icon {
  font-size: 2rem;
}

.info-content h3 {
  color: #1e3a8a;
  margin-bottom: 8px;
  font-size: 1.1rem;
}

.info-content p {
  color: #666;
  line-height: 1.5;
}

.info-content a {
  color: #f59e0b;
  text-decoration: none;
  transition: color 0.3s;
}

.info-content a:hover {
  color: #d97706;
}

/* Social Links */
.social-links-section h3 {
  color: #1e3a8a;
  margin-bottom: 15px;
}

.social-links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 15px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background: white;
  text-decoration: none;
  color: #1e3a8a;
  font-weight: 500;
  transition: all 0.3s;
  border-radius: 12px;
}

.social-link:hover {
  background: #1e3a8a;
  color: white;
  transform: translateY(-3px);
}

/* Form Side */
.contact-form-wrapper {
  position: sticky;
  top: 100px;
}

.form-card {
  padding: 40px;
  background: white;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.form-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.form-header h3 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 8px;
}

.form-header p {
  color: #666;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
}

.input-wrapper textarea ~ .input-icon {
  top: 20px;
  transform: none;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-family: inherit;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.form-group textarea {
  resize: vertical;
  padding-top: 12px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1e3a8a;
  box-shadow: 0 0 0 3px rgba(30,58,138,0.1);
}

.btn-submit {
  width: 100%;
  padding: 14px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-submit:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  transition: transform 0.3s;
}

.btn-submit:hover .btn-icon {
  transform: translateX(5px);
}

.form-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 0.8rem;
  color: #666;
}

/* Map Section */
.map-section {
  padding: 80px 0;
  background: white;
}

.map-card {
  padding: 40px;
  background: white;
}

.map-header {
  text-align: center;
  margin-bottom: 30px;
}

.map-header .section-badge {
  display: inline-block;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 15px;
}

.map-header h2 {
  font-size: 1.8rem;
  color: #1e3a8a;
  margin-bottom: 10px;
}

.map-header p {
  color: #666;
}

.map-container {
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 20px;
}

.map-container iframe {
  display: block;
}

.map-badges {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.map-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8fafc;
  border-radius: 50px;
  font-size: 0.85rem;
  color: #1e3a8a;
}

/* FAQ Section */
.faq-section {
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

.faq-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.faq-card {
  padding: 25px;
  background: white;
  transition: all 0.3s;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.faq-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.faq-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
}

.faq-question {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.faq-icon {
  font-size: 1.5rem;
}

.faq-question h3 {
  font-size: 1.1rem;
  color: #1e3a8a;
}

.faq-card p {
  color: #666;
  line-height: 1.6;
  padding-left: 40px;
}

/* Success Modal */
.success-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.success-content {
  text-align: center;
  padding: 40px;
  max-width: 400px;
  background: white;
}

.success-icon {
  width: 70px;
  height: 70px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 20px;
}

.success-content h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

.success-content p {
  color: #666;
  margin-bottom: 20px;
}

.btn-close {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
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

.delay-1 { transition-delay: 0.1s; }
.delay-2 { transition-delay: 0.2s; }
.delay-3 { transition-delay: 0.3s; }

/* Responsive */
@media (max-width: 968px) {
  .contact-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  
  .contact-form-wrapper {
    position: static;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  .form-card {
    padding: 25px;
  }
  
  .faq-grid {
    grid-template-columns: 1fr;
  }
  
  .social-links-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .map-card {
    padding: 25px;
  }
  
  .map-container iframe {
    height: 250px;
  }
}
</style>