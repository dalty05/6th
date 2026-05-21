<template>
  <div class="verify-container">
    <div class="verify-card">
      <div class="verify-header">
        <img src="/logo.png" alt="Meru Dairy" class="verify-logo">
        <h2>Verify Email</h2>
        <p>Verifying your email address...</p>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Please wait while we verify your email...</p>
      </div>

      <div v-if="successMessage" class="success-message">
        <div class="success-icon">✓</div>
        <h3>Email Verified Successfully!</h3>
        <p>{{ successMessage }}</p>
        <p style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
          Redirecting to login page...
        </p>
      </div>

      <div v-if="errorMessage" class="error-message">
        <div class="error-icon">✕</div>
        <h3>Verification Failed</h3>
        <p>{{ errorMessage }}</p>
        <router-link to="/admin/register" class="btn-back">
          Back to Registration
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  name: 'VerifyEmail',
  data() {
    return {
      loading: true,
      successMessage: '',
      errorMessage: '',
      token: null
    }
  },
  mounted() {
    this.token = this.$route.query.token
    if (!this.token) {
      this.errorMessage = 'Invalid verification link. No token provided.'
      this.loading = false
      return
    }
    this.verifyEmail()
  },
  methods: {
    async verifyEmail() {
      this.loading = true
      this.errorMessage = ''
      this.successMessage = ''

      try {
        const response = await fetch('/api/auth/verify-email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token: this.token })
        })

        const data = await response.json()

        if (!response.ok) {
          this.errorMessage = data.error || 'Email verification failed'
          this.loading = false
          return
        }

        this.successMessage = data.message || 'Your email has been verified successfully. Your account is pending approval from a super administrator.'
        
        setTimeout(() => {
          this.$router.push('/admin/login')
        }, 3000)
      } catch (error) {
        this.errorMessage = error.message || 'An error occurred during verification'
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.verify-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  padding: 1rem;
}

.verify-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  text-align: center;
}

.verify-header {
  margin-bottom: 2rem;
}

.verify-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 1rem;
}

.verify-header h2 {
  color: #333;
  margin-bottom: 0.5rem;
}

.verify-header p {
  color: #666;
  font-size: 0.95rem;
}

.loading {
  padding: 2rem 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid var(--primary-blue);
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-message {
  padding: 2rem 0;
}

.success-icon {
  width: 60px;
  height: 60px;
  background: #d1fae5;
  color: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  margin: 0 auto 1rem;
}

.success-message h3 {
  color: #10b981;
  margin-bottom: 0.5rem;
}

.success-message p {
  color: #666;
  font-size: 0.95rem;
}

.error-message {
  padding: 2rem 0;
}

.error-icon {
  width: 60px;
  height: 60px;
  background: #fee;
  color: #dc2626;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  margin: 0 auto 1rem;
}

.error-message h3 {
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-message p {
  color: #666;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.btn-back {
  display: inline-block;
  padding: 10px 20px;
  background: var(--primary-blue);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-back:hover {
  background: var(--primary-light);
  transform: translateY(-2px);
}
</style>
