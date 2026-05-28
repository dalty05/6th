<template>
  <div class="partner-links">
    <div class="page-header">
      <h1>Referral Links</h1>
      <button class="btn-primary">
        <i class="fas fa-plus"></i> Create New Link
      </button>
    </div>
    
    <div class="coming-soon">
      <i class="fas fa-tools"></i>
      <h2>Coming Soon</h2>
      <p>Referral link management is under development</p>
      <router-link to="/partner/dashboard" class="btn-back">← Back to Dashboard</router-link>
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  name: 'PartnerReferralLinks',
  mounted() {
    if (!authService.isPartner()) {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.partner-links {
  padding: 2rem;
  min-height: 100vh;
  background: #f8fafc;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #1e3a8a;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.coming-soon {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 16px;
}

.coming-soon i {
  font-size: 4rem;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.coming-soon h2 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.coming-soon p {
  color: #666;
  margin-bottom: 1.5rem;
}

.btn-back {
  color: #f59e0b;
  text-decoration: none;
}
</style>