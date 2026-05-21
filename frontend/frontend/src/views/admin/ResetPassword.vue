<template>
  <div class="reset-container">
    <div class="reset-card">
      <div class="reset-header">
        <img src="/logo.png" alt="Meru Dairy" class="reset-logo">
        <h2>Create New Password</h2>
        <p>Enter your new password below</p>
      </div>

      <form @submit.prevent="handleReset" class="reset-form">
        <div class="form-group">
          <label>New Password</label>
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="form.password" 
            placeholder="Enter new password"
            required
          >
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? '👁️' : '👁️‍🗨️' }}
          </button>
        </div>

        <div class="password-hints">
          <ul>
            <li :class="{ valid: hasMinLength }">✓ At least 8 characters</li>
            <li :class="{ valid: hasUpperCase }">✓ Uppercase letter</li>
            <li :class="{ valid: hasLowerCase }">✓ Lowercase letter</li>
            <li :class="{ valid: hasNumber }">✓ Number</li>
          </ul>
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <input 
            type="password" 
            v-model="form.confirmPassword" 
            placeholder="Confirm new password"
            required
          >
        </div>

        <button type="submit" class="btn-reset" :disabled="loading || !isFormValid">
          {{ loading ? 'Resetting...' : 'Reset Password' }}
        </button>

        <div class="back-link">
          <router-link to="/admin/login">← Back to Login</router-link>
        </div>
      </form>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  name: 'ResetPassword',
  data() {
    return {
      form: {
        password: '',
        confirmPassword: ''
      },
      loading: false,
      errorMessage: '',
      showPassword: false,
      token: null
    }
  },
  computed: {
    hasMinLength() {
      return this.form.password.length >= 8
    },
    hasUpperCase() {
      return /[A-Z]/.test(this.form.password)
    },
    hasLowerCase() {
      return /[a-z]/.test(this.form.password)
    },
    hasNumber() {
      return /\d/.test(this.form.password)
    },
    isFormValid() {
      return this.hasMinLength && 
             this.hasUpperCase && 
             this.hasLowerCase && 
             this.hasNumber &&
             this.form.password === this.form.confirmPassword
    }
  },
  mounted() {
    this.token = this.$route.query.token
    if (!this.token) {
      this.errorMessage = 'Invalid reset link. Please request a new one.'
    }
  },
  methods: {
    async handleReset() {
      if (!this.token) return
      
      this.loading = true
      this.errorMessage = ''
      
      try {
        await authService.resetPassword(this.token, this.form.password)
        this.$router.push('/admin/login?reset=success')
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to reset password. Link may have expired.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.reset-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  padding: 1rem;
}

.reset-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.reset-header {
  text-align: center;
  margin-bottom: 2rem;
}

.reset-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
  position: relative;
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

.toggle-password {
  position: absolute;
  right: 12px;
  bottom: 10px;
  background: none;
  border: none;
  cursor: pointer;
}

.password-hints {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 1rem;
}

.password-hints ul {
  list-style: none;
  padding: 0;
}

.password-hints li {
  padding: 0.15rem 0;
}

.password-hints li.valid {
  color: #10b981;
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
  margin-top: 1rem;
}

.btn-reset:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-link {
  text-align: center;
  margin-top: 1.5rem;
}

.back-link a {
  color: var(--primary-blue);
  text-decoration: none;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fee;
  color: #c00;
  border-radius: 8px;
  font-size: 0.9rem;
  text-align: center;
}
</style>