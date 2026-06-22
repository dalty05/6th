<template>
  <div class="partner-layout">
    <!-- Sidebar -->
    <PartnerSidebar ref="sidebarRef" />

    <!-- Main Content -->
    <main class="partner-main">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <button class="sidebar-toggle" @click="toggleSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <h1><i class="fas fa-question-circle"></i> Help &amp; Support</h1>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="openContactModal">
            <i class="fas fa-envelope"></i> Contact Support
          </button>
        </div>
      </div>

      <!-- Page Content -->
      <div class="page-content">
        <!-- Quick Help Sections -->
        <div class="help-grid">
          <!-- Getting Started -->
          <div class="help-card">
            <div class="help-icon">
              <i class="fas fa-rocket"></i>
            </div>
            <h3>Getting Started</h3>
            <p>Learn how to create your first referral link and start earning</p>
            <ul class="help-list">
              <li><i class="fas fa-check-circle"></i> Create your first referral link</li>
              <li><i class="fas fa-check-circle"></i> Share your link with customers</li>
              <li><i class="fas fa-check-circle"></i> Track your performance</li>
            </ul>
          </div>

          <!-- Creating Links -->
          <div class="help-card">
            <div class="help-icon">
              <i class="fas fa-link"></i>
            </div>
            <h3>Creating Links</h3>
            <p>Best practices for creating effective referral links</p>
            <ul class="help-list">
              <li><i class="fas fa-check-circle"></i> Use descriptive link names</li>
              <li><i class="fas fa-check-circle"></i> Add campaign tracking</li>
              <li><i class="fas fa-check-circle"></i> Test your links before sharing</li>
            </ul>
          </div>

          <!-- Analytics -->
          <div class="help-card">
            <div class="help-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <h3>Understanding Analytics</h3>
            <p>Make data-driven decisions with your referral analytics</p>
            <ul class="help-list">
              <li><i class="fas fa-check-circle"></i> Track clicks and conversions</li>
              <li><i class="fas fa-check-circle"></i> Identify top-performing links</li>
              <li><i class="fas fa-check-circle"></i> Optimize your campaigns</li>
            </ul>
          </div>

          <!-- FAQ -->
          <div class="help-card">
            <div class="help-icon">
              <i class="fas fa-question"></i>
            </div>
            <h3>Frequently Asked Questions</h3>
            <p>Quick answers to common questions</p>
            <ul class="help-list">
              
              
              <li><i class="fas fa-check-circle"></i> How do I track referrals?</li>
            </ul>
          </div>
        </div>

        <!-- FAQ Accordion -->
        <div class="faq-section glass-card">
          <h3><i class="fas fa-comments"></i> Frequently Asked Questions</h3>
          
          <div class="faq-item" v-for="(faq, index) in faqs" :key="index">
            <div class="faq-question" @click="toggleFaq(index)">
              <h4>{{ faq.question }}</h4>
              <i class="fas" :class="faq.open ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
            <div class="faq-answer" v-show="faq.open">
              <p>{{ faq.answer }}</p>
            </div>
          </div>
        </div>

        <!-- Contact Support Section -->
        <div class="support-section glass-card">
          <div class="support-content">
            <div>
              <h3><i class="fas fa-headset"></i> Need More Help?</h3>
              <p>Our support team is here to assist you with any questions</p>
            </div>
            <div class="support-actions">
              <button @click="openContactModal" class="btn-primary">
                <i class="fas fa-envelope"></i> Contact Support
              </button>
            </div>
          </div>
          <div class="support-hours">
            <i class="fas fa-clock"></i>
            <span>Available Mon-Fri: 8AM - 5PM EAT</span>
          </div>
        </div>
      </div>
    </main>

    <!-- Contact Support Modal -->
    <div v-if="showContactModal" class="modal-overlay" @click.self="closeContactModal">
      <div class="modal-container">
        <!-- Modal Header -->
        <div class="modal-header">
          <div class="header-content">
            <i class="fas fa-headset"></i>
            <div>
              <h2>Contact Support</h2>
              <p>We're here to help you</p>
            </div>
          </div>
          <button class="close-btn" @click="closeContactModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <!-- Contact Options -->
          <div class="contact-grid">
            <!-- Email -->
            <div class="contact-card" @click="copyEmail">
              <div class="contact-icon email">
                <i class="fas fa-envelope"></i>
              </div>
              <div class="contact-info">
                <h4>Email Us</h4>
                <p class="contact-value">{{ supportEmail }}</p>
                <span class="action-hint">Click to copy</span>
              </div>
            </div>

            <!-- Phone -->
            <div class="contact-card" @click="callPhone">
              <div class="contact-icon phone">
                <i class="fas fa-phone"></i>
              </div>
              <div class="contact-info">
                <h4>Call Us</h4>
                <p class="contact-value">{{ supportPhone }}</p>
                <span class="action-hint">Click to call</span>
              </div>
            </div>

            <!-- WhatsApp -->
            <div class="contact-card" @click="openWhatsApp">
              <div class="contact-icon whatsapp">
                <i class="fab fa-whatsapp"></i>
              </div>
              <div class="contact-info">
                <h4>WhatsApp</h4>
                <p class="contact-value">{{ supportPhone }}</p>
                <span class="action-hint">Chat with us</span>
              </div>
            </div>

            <!-- Hours -->
            <div class="contact-card disabled">
              <div class="contact-icon hours">
                <i class="fas fa-clock"></i>
              </div>
              <div class="contact-info">
                <h4>Support Hours</h4>
                <p class="contact-value">Mon-Fri: 8AM - 5PM</p>
                <span class="action-hint">EAT Timezone</span>
              </div>
            </div>
          </div>

          <!-- Quick Message -->
          <div class="quick-message">
            <div class="message-header">
              <i class="fas fa-pen"></i>
              <span>Send a quick message</span>
            </div>
            <!-- <form @submit.prevent="sendQuickMessage" class="message-form">
              <textarea 
                v-model="quickMessage" 
                placeholder="Describe your issue briefly..."
                rows="3"
              ></textarea>
              <button type="submit" class="send-btn" :disabled="!quickMessage.trim()">
                <i class="fas fa-paper-plane"></i>
                Send Message
              </button>
            </form> -->
            <p class="message-note">
              <i class="fas fa-info-circle"></i>
              For urgent issues, please call us directly.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import PartnerSidebar from '@/components/partner/PartnerSidebar.vue'

const router = useRouter()
const sidebarRef = ref(null)
const showContactModal = ref(false)
const quickMessage = ref('')

// Contact details
const supportEmail = 'support@merudairy.co.ke'
const supportPhone = '+254 710 901 376'
const whatsappNumber = '254710901376'

// FAQ Data
const faqs = ref([
  {
    question: 'How do I create a referral link?',
    answer: 'Go to the "Referral Links" page and click "Create New Link". Enter a name and description for your link, then click "Create". You will receive a unique link code to share with your customers.',
    open: false
  },
  {
    question: 'How do I track my referrals?',
    answer: 'You can track all your referrals in the "Analytics" section. This shows you total clicks, unique visitors, conversions, and conversion rates for all your links.',
    open: false
  },
  {
    question: 'Can I have multiple referral links?',
    answer: 'Yes! You can create as many referral links as you need. This is useful for tracking different campaigns, channels, or customer segments.',
    open: false
  },
  {
    question: 'How do I know if my link is working?',
    answer: 'Each referral link has a unique tracking code. You can test your link by clicking on it yourself - the click will be recorded in your analytics dashboard.',
    open: false
  }
])

const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleMobile()
  }
}

const toggleFaq = (index) => {
  faqs.value[index].open = !faqs.value[index].open
}

const openContactModal = () => {
  showContactModal.value = true
}

const closeContactModal = () => {
  showContactModal.value = false
  quickMessage.value = ''
}

// Copy email to clipboard
const copyEmail = () => {
  navigator.clipboard.writeText(supportEmail).then(() => {
    toast.success('Email copied to clipboard')
  }).catch(() => {
    // Fallback
    const textArea = document.createElement('textarea')
    textArea.value = supportEmail
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    toast.success('Email copied to clipboard')
  })
}

// Call phone
const callPhone = () => {
  window.location.href = `tel:${supportPhone.replace(/\s/g, '')}`
}

// Open WhatsApp
const openWhatsApp = () => {
  window.open(`https://wa.me/${whatsappNumber}`, '_blank')
}

// Send quick message
const sendQuickMessage = () => {
  if (!quickMessage.value.trim()) return
  
  // Open email with pre-filled subject and body
  const subject = 'Support Request from Partner'
  const body = `Hello Support Team,\n\n${quickMessage.value}\n\nThank you.`
  window.location.href = `mailto:${supportEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  
  toast.success('Opening email...')
  quickMessage.value = ''
  setTimeout(() => closeContactModal(), 500)
}
</script>

<style scoped>
.partner-layout {
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
}

.partner-main {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-header h1 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-header h1 i {
  color: #f59e0b;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.page-content {
  flex: 1;
  padding: 1.5rem 2rem;
}

.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #0f172a;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.sidebar-toggle:hover {
  background: #f1f5f9;
}

/* Help Grid */
.help-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.help-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.help-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.help-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #fef3c7;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.help-icon i {
  font-size: 1.25rem;
  color: #d97706;
}

.help-card h3 {
  font-size: 1rem;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.help-card p {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0 0 1rem;
}

.help-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-list li {
  font-size: 0.8rem;
  color: #4b5563;
  padding: 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.help-list li i {
  color: #10b981;
  font-size: 0.7rem;
}

/* FAQ Section */
.faq-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
}

.faq-section h3 {
  font-size: 1rem;
  color: #0f172a;
  margin: 0 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.faq-section h3 i {
  color: #f59e0b;
}

.faq-item {
  border-bottom: 1px solid #f1f5f9;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  cursor: pointer;
  transition: all 0.2s;
}

.faq-question:hover {
  color: #f59e0b;
}

.faq-question h4 {
  font-size: 0.9rem;
  margin: 0;
  font-weight: 500;
}

.faq-question i {
  color: #94a3b8;
  font-size: 0.8rem;
}

.faq-answer {
  padding: 0 0 0.75rem;
  color: #6b7280;
  font-size: 0.85rem;
  line-height: 1.6;
}

.faq-answer p {
  margin: 0;
}

/* Support Section */
.support-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}

.support-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.support-content h3 {
  font-size: 1rem;
  color: #0f172a;
  margin: 0 0 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.support-content h3 i {
  color: #f59e0b;
}

.support-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.85rem;
}

.support-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.support-hours {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.support-hours i {
  color: #f59e0b;
}

/* Buttons */
.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-1px);
}

/* ========================================
   CONTACT MODAL STYLES
   ======================================== */

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  z-index: 10000;
  animation: fadeIn 0.2s ease;
}

.modal-container {
  width: 100%;
  max-width: 560px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  animation: slideUp 0.3s ease;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-content i {
  font-size: 1.5rem;
  color: #f59e0b;
}

.header-content h2 {
  margin: 0;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
}

.header-content p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.8rem;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  font-size: 1.1rem;
  transition: 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 1.5rem;
}

/* Contact Grid */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.contact-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.contact-card:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #f59e0b;
}

.contact-card.disabled {
  cursor: default;
  opacity: 0.7;
}

.contact-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.contact-icon.email { background: #dbeafe; color: #2563eb; }
.contact-icon.phone { background: #d1fae5; color: #059669; }
.contact-icon.whatsapp { background: #dcfce7; color: #25d366; }
.contact-icon.hours { background: #fef3c7; color: #d97706; }

.contact-info {
  flex: 1;
  min-width: 0;
}

.contact-info h4 {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: #0f172a;
}

.contact-info .contact-value {
  margin: 0.1rem 0 0;
  font-size: 0.75rem;
  color: #4b5563;
  word-break: break-all;
}

.contact-info .action-hint {
  font-size: 0.6rem;
  color: #9ca3af;
  display: block;
  margin-top: 0.1rem;
}

/* Quick Message */
.quick-message {
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.message-header i {
  color: #f59e0b;
  font-size: 0.9rem;
}

.message-header span {
  font-size: 0.85rem;
  font-weight: 500;
  color: #0f172a;
}

.message-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.message-form textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.85rem;
  resize: vertical;
  transition: 0.2s;
  font-family: inherit;
}

.message-form textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.send-btn {
  align-self: flex-end;
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.message-note {
  font-size: 0.7rem;
  color: #6b7280;
  margin: 0.5rem 0 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.message-note i {
  color: #f59e0b;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .partner-main {
    margin-left: 0;
  }
  
  .sidebar-toggle {
    display: flex;
  }
  
  .page-header {
    padding: 0.75rem 1rem;
  }
  
  .page-content {
    padding: 1rem;
  }
  
  .help-grid {
    grid-template-columns: 1fr;
  }
  
  .support-content {
    flex-direction: column;
    text-align: center;
  }
  
  .support-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .contact-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-container {
    max-width: 100%;
    margin: 0.5rem;
    border-radius: 16px;
  }
  
  .modal-body {
    padding: 1rem;
  }
}
</style>