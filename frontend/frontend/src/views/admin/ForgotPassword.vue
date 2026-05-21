<template>
  <div class="forgot-container">
    <div class="forgot-card">
      <div class="forgot-header">
        <img src="/logo.png" alt="Meru Dairy" class="forgot-logo">
        <h2>Reset Password</h2>
        <p>Enter your email to receive a password reset link</p>
      </div>

      <form @submit.prevent="handleForgot" class="forgot-form">
        <div class="form-group">
          <label>Email Address</label>
          <input 
            type="email" 
            v-model="email" 
            placeholder="admin@merudairy.co.ke"
            required
            autofocus
          >
        </div>

        <button type="submit" class="btn-reset" :disabled="loading">
          {{ loading ? 'Sending...' : 'Send Reset Link' }}
        </button>

        <div class="back-link">
          <router-link to="/admin/login">← Back to Login</router-link>
        </div>
      </form>

      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: '',
      loading: false,
      successMessage: '',
      errorMessage: ''
    }
  },
  methods: {
    async handleForgot() {
      this.loading = true
      this.errorMessage = ''
      this.successMessage = ''
      
      try {
        await authService.forgotPassword(this.email)
        this.successMessage = 'If an account exists with this email, you will receive a password reset link.'
        this.email = ''
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to send reset link'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.forgot-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  padding: 1rem;
}

.forgot-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.forgot-header {
  text-align: center;
  margin-bottom: 2rem;
}

.forgot-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.btn-reset {
  width: 100%;
  padding: 12px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.back-link {
  text-align: center;
  margin-top: 1.5rem;
}

.back-link a {
  color: var(--primary-blue);
  text-decoration: none;
}

.success-message, .error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.9rem;
  text-align: center;
}

.success-message {
  background: #d1fae5;
  color: #065f46;
}

.error-message {
  background: #fee;
  color: #c00;
}
</style>