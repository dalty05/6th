<template>
  <footer class="admin-footer">
    <div class="footer-container">
      <div class="footer-copyright">
        <span>&copy; {{ currentYear }} Meru Central Dairy Co-operative Union Ltd</span>
      </div>
      
      <div class="footer-links">
        <a href="#" class="footer-link" @click.prevent="showSupport">
          <i class="fas fa-question-circle"></i>
          Support
        </a>
        <a href="#" class="footer-link" @click.prevent="showPrivacy">
          <i class="fas fa-shield-alt"></i>
          Privacy
        </a>
        <a href="#" class="footer-link" @click.prevent="showTerms">
          <i class="fas fa-file-contract"></i>
          Terms
        </a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { toast } from 'vue3-toastify'

const currentYear = computed(() => new Date().getFullYear())

const showSupport = () => {
  toast.info(
    '📞 Support Contact\n\nPhone: +254 710 901 376\nEmail: support@merudairy.co.ke',
    { autoClose: 5000, position: 'top-right' }
  )
}

const showPrivacy = () => {
  toast.info('Privacy policy information coming soon', { autoClose: 3000 })
}

const showTerms = () => {
  toast.info('Terms and conditions information coming soon', { autoClose: 3000 })
}
</script>

<style scoped>
.admin-footer {
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 1rem 0;
  margin-top: auto;
}

.footer-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.footer-copyright {
  font-size: 0.75rem;
  color: #9ca3af;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-link i {
  font-size: 0.7rem;
}

.footer-link:hover {
  color: #f59e0b;
}

@media (max-width: 768px) {
  .footer-container {
    flex-direction: column;
    text-align: center;
    padding: 0 1rem;
  }
  
  .footer-links {
    gap: 1rem;
  }
}
</style>