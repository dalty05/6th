<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <img src="/logo.png" alt="Meru Dairy" class="register-logo">
        <h2>Admin Registration</h2>
        <p>Register for administrator access</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label>Full Name</label>
          <input 
            type="text" 
            v-model="form.fullName" 
            placeholder="John Doe"
            required
          >
        </div>

        <div class="form-group">
          <label>Email Address</label>
          <input 
            type="email" 
            v-model="form.email" 
            placeholder="email@merudairy.co.ke"
            required
          >
        </div>

        <div class="form-group">
          <label>Password</label>
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="form.password" 
            placeholder="Create a strong password"
            required
          >
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? '👁️' : '👁️‍🗨️' }}
          </button>
        </div>

        <div class="password-hints">
          <p>Password must contain:</p>
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
            placeholder="Confirm your password"
            required
          >
        </div>

        <button type="submit" class="btn-register" :disabled="loading || !isFormValid">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>

        <div class="login-link">
          Already have an account? <router-link to="/admin/login">Login here</router-link>
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
  name: 'AdminRegister',
  data() {
    return {
      form: {
        fullName: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      loading: false,
      successMessage: '',
      errorMessage: '',
      showPassword: false
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
      return this.form.fullName && 
             this.form.email && 
             this.hasMinLength && 
             this.hasUpperCase && 
             this.hasLowerCase && 
             this.hasNumber &&
             this.form.password === this.form.confirmPassword
    }
  },
  methods: {
    async handleRegister() {
      this.loading = true
      this.errorMessage = ''
      this.successMessage = ''
      
      try {
        const response = await authService.register(
          this.form.email,
          this.form.fullName,
          this.form.password
        )
        
        if (response.role === 'super_admin') {
          this.successMessage = 'Registration successful! You are the super admin. Please check your email to verify.'
        } else {
          this.successMessage = 'Registration successful! Please check your email to verify. A super admin will approve your account.'
        }
        
        setTimeout(() => {
          this.$router.push('/admin/login')
        }, 3000)
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  padding: 1rem;
}

.register-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-logo {
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
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-blue);
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
  margin-top: 0.25rem;
}

.password-hints li {
  padding: 0.15rem 0;
}

.password-hints li.valid {
  color: #10b981;
}

.btn-register {
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

.btn-register:hover:not(:disabled) {
  background: var(--primary-light);
}

.btn-register:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
}

.login-link a {
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