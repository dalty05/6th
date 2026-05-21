<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <img src="/logo.png" alt="Meru Dairy" class="login-logo">
        <h2>Admin Portal</h2>
        <p>Secure access to Meru Dairy management system</p>
      </div>

      <!-- Step 1: Email & Password -->
      <form v-if="step === 1" @submit.prevent="handleStep1" class="login-form">
        <div class="form-group">
          <label>Email Address</label>
          <input 
            type="email" 
            v-model="loginForm.email" 
            placeholder="admin@merudairy.co.ke"
            required
            autocomplete="email"
          >
        </div>

        <div class="form-group">
          <label>Password</label>
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="loginForm.password" 
            placeholder="Enter your password"
            required
            autocomplete="current-password"
          >
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? '👁️' : '👁️‍🗨️' }}
          </button>
        </div>

        <div class="form-options">
          <label class="checkbox">
            <input type="checkbox" v-model="loginForm.remember"> Remember me
          </label>
          <router-link to="/admin/forgot-password" class="forgot-link">Forgot Password?</router-link>
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? 'Verifying...' : 'Continue' }}
        </button>

        <div class="register-link">
          Don't have an account? <router-link to="/admin/register">Register here</router-link>
        </div>
      </form>

      <!-- Step 2: OTP Verification -->
      <form v-else-if="step === 2" @submit.prevent="handleStep2" class="login-form">
        <div class="otp-header">
          <div class="otp-icon">🔐</div>
          <h3>Two-Factor Authentication</h3>
          <p>Enter the 6-digit code sent to your email</p>
        </div>

        <div class="form-group">
          <label>Verification Code</label>
          <div class="otp-inputs">
            <input 
              v-for="i in 6" 
              :key="i"
              type="text"
              maxlength="1"
              class="otp-input"
              v-model="otpCodes[i-1]"
              @input="handleOtpInput(i-1, $event)"
              @keyup="handleOtpKeyup(i-1, $event)"
              ref="otpInputs"
              autofocus
            >
          </div>
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? 'Verifying...' : 'Verify & Login' }}
        </button>

        <button type="button" class="btn-resend" @click="resendOtp" :disabled="resendCooldown">
          {{ resendCooldown ? `Resend in ${resendTimer}s` : 'Resend Code' }}
        </button>

        <button type="button" class="btn-back" @click="step = 1">
          ← Back to login
        </button>
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
  name: 'AdminLogin',
  data() {
    return {
      step: 1,
      loginForm: {
        email: '',
        password: '',
        remember: false
      },
      otpCodes: ['', '', '', '', '', ''],
      loading: false,
      errorMessage: '',
      showPassword: false,
      resendCooldown: false,
      resendTimer: 0,
      loginEmail: null
    }
  },
  mounted() {
    // Check if already logged in
    if (authService.isAuthenticated()) {
      this.$router.push('/admin/dashboard')
    }
  },
  methods: {
    async handleStep1() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await authService.loginStep1(
          this.loginForm.email,
          this.loginForm.password
        )
        
        if (response.requires_otp) {
          this.loginEmail = this.loginForm.email
          this.step = 2
          this.$nextTick(() => {
            if (this.$refs.otpInputs && this.$refs.otpInputs[0]) {
              this.$refs.otpInputs[0].focus()
            }
          })
        }
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    async handleStep2() {
      const otpCode = this.otpCodes.join('')
      if (otpCode.length !== 6) {
        this.errorMessage = 'Please enter the 6-digit verification code'
        return
      }
      
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await authService.loginStep2(otpCode, this.loginForm.remember)
        this.$router.push('/admin/dashboard')
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Invalid verification code'
        this.otpCodes = ['', '', '', '', '', '']
        this.$refs.otpInputs[0].focus()
      } finally {
        this.loading = false
      }
    },
    
    handleOtpInput(index, event) {
      const value = event.target.value.replace(/[^0-9]/g, '')
      this.otpCodes[index] = value
      
      if (value && index < 5) {
        this.$refs.otpInputs[index + 1].focus()
      }
      
      if (this.otpCodes.join('').length === 6) {
        this.handleStep2()
      }
    },
    
    handleOtpKeyup(index, event) {
      if (event.key === 'Backspace' && !this.otpCodes[index] && index > 0) {
        this.$refs.otpInputs[index - 1].focus()
      }
    },
    
    async resendOtp() {
      if (this.resendCooldown) return
      
      try {
        await authService.loginStep1(this.loginEmail, this.loginForm.password)
        this.resendCooldown = true
        this.resendTimer = 60
        const interval = setInterval(() => {
          this.resendTimer--
          if (this.resendTimer <= 0) {
            clearInterval(interval)
            this.resendCooldown = false
          }
        }, 1000)
        this.errorMessage = ''
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to resend code'
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  padding: 1rem;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 1rem;
}

.login-header h2 {
  color: var(--primary-blue);
  margin-bottom: 0.5rem;
}

.login-header p {
  color: #666;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
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
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(30,58,138,0.1);
}

.toggle-password {
  position: absolute;
  right: 12px;
  bottom: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.forgot-link {
  font-size: 0.9rem;
  color: var(--primary-blue);
  text-decoration: none;
}

.btn-login {
  width: 100%;
  padding: 12px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-login:hover:not(:disabled) {
  background: var(--primary-light);
  transform: translateY(-2px);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.otp-header {
  text-align: center;
  margin-bottom: 2rem;
}

.otp-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.otp-inputs {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.otp-input {
  width: 50px;
  height: 50px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  border: 2px solid #ddd;
  border-radius: 8px;
}

.otp-input:focus {
  border-color: var(--primary-blue);
  outline: none;
}

.btn-resend, .btn-back {
  width: 100%;
  padding: 10px;
  margin-top: 1rem;
  background: none;
  border: none;
  color: var(--primary-blue);
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-resend:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: #666;
}

.register-link a {
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