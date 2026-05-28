<template>
  <div class="partner-profile">
    <div class="page-header">
      <h1>My Profile</h1>
    </div>
    
    <div class="coming-soon">
      <i class="fas fa-user-edit"></i>
      <h2>Coming Soon</h2>
      <p>Profile management is under development</p>
      <router-link to="/partner/dashboard" class="btn-back">← Back to Dashboard</router-link>
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  name: 'PartnerProfile',
  mounted() {
    if (!authService.isPartner()) {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.partner-profile {
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