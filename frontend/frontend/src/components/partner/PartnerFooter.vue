<template>
  <footer class="partner-footer">
    <div class="footer-container">
      <div class="footer-copyright">
        <i class="fas fa-tint"></i>
        <span>Meru Dairy Partner Portal</span>
      </div>
      <div class="footer-links">
        <a href="#" @click.prevent="showHelp" class="footer-link">
          <i class="fas fa-question-circle"></i> Help
        </a>
        <a href="#" @click.prevent="showSupport" class="footer-link">
          <i class="fas fa-headset"></i> Support
        </a>
        <a href="#" @click.prevent="showFeedback" class="footer-link">
          <i class="fas fa-comment"></i> Feedback
        </a>
      </div>
      <div class="footer-contact">
        <a href="tel:+254710901376">
          <i class="fas fa-phone-alt"></i> +254 710 901 376
        </a>
        <a href="mailto:partners@merudairy.co.ke">
          <i class="fas fa-envelope"></i> partners@merudairy.co.ke
        </a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { toast } from 'vue3-toastify'

const currentYear = computed(() => new Date().getFullYear())

const showHelp = () => {
  toast.info('📚 Partner help documentation available on request', { autoClose: 3000 })
}

const showSupport = () => {
  toast.success('📞 Partner support: +254 710 901 376', { autoClose: 4000 })
}

const showFeedback = () => {
  toast.info('✉️ Send feedback to partners@merudairy.co.ke', { autoClose: 3000 })
}
</script>

<style scoped>
.partner-footer {
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 0.75rem 1.5rem;
  margin-top: 1.5rem;
}

.footer-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

.footer-copyright {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.7rem;
  color: #9ca3af;
}

.footer-copyright i {
  color: #f59e0b;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.3s;
  cursor: pointer;
}

.footer-link i {
  font-size: 0.65rem;
}

.footer-link:hover {
  color: #f59e0b;
}

.footer-contact {
  display: flex;
  gap: 1.5rem;
}

.footer-contact a {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-contact a:hover {
  color: #f59e0b;
}

@media (max-width: 768px) {
  .partner-footer {
    padding: 0.75rem 1rem;
  }
  
  .footer-container {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }
  
  .footer-links, .footer-contact {
    justify-content: center;
  }
}
</style>