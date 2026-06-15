<template>
  <div class="partner-analytics">
    <div class="page-header">
      <h1>Analytics</h1>
    </div>
    
    <div class="coming-soon">
      <i class="fas fa-chart-line"></i>
      <h2>Coming Soon</h2>
      <p>Detailed analytics dashboard is under development</p>
      <router-link to="/partner/dashboard" class="btn-back">← Back to Dashboard</router-link>
    </div>
    <PartnerFooter />
  </div>
</template>

<script>
import authService from '@/services/auth'


import PartnerFooter from '@/components/partner/PartnerFooter.vue'

export default {
  name: 'PartnerAnalytics',
  mounted() {
    if (!authService.isPartner()) {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>

.partner-analytics {
  min-height: 100vh;
  background: #f8fafc;
}

.page-content {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 60px);
  padding: 80px 2rem 0;
}

.content-wrapper {
  flex: 1;
}

@media (max-width: 768px) {
  .page-content {
    padding: 70px 1rem 0;
  }
}

.partner-analytics {
  padding: 2rem;
  min-height: 100vh;
  background: #f8fafc;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #1e3a8a;
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