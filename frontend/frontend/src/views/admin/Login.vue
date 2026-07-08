<template>
  <div class="login-container">
    <div class="login-card glass-card">
      <div class="login-header">
        <img src="/logo.png" alt="Meru Dairy" class="login-logo" @error="setImagePlaceholder">
        <h2>Admin Portal</h2>
        <p>Secure access to Meru Dairy management system</p>
      </div>

      <!-- Step 1: Email & Password -->
      <form v-if="step === 1" @submit.prevent="handleStep1" class="login-form">
        <div class="form-group">
          <label>Email Address</label>
          <div class="input-wrapper">
            <i class="fas fa-envelope input-icon"></i>
            <input 
              type="email" 
              v-model="loginForm.email" 
              placeholder="admin@merudairy.co.ke"
              required
              autocomplete="email"
              :disabled="loading"
            >
          </div>
        </div>

        <div class="form-group">
          <label>Password</label>
          <div class="input-wrapper">
            <i class="fas fa-lock input-icon"></i>
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="loginForm.password" 
              placeholder="Enter your password"
              required
              autocomplete="current-password"
              :disabled="loading"
            >
            <button type="button" class="toggle-password" @click="showPassword = !showPassword" tabindex="-1">
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
        </div>

        <div class="form-options">
          <label class="checkbox-label">
            <input type="checkbox" v-model="loginForm.remember">
            <span>Remember me</span>
          </label>
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          <span v-if="!loading">
            Continue <i class="fas fa-arrow-right"></i>
          </span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> Verifying...
          </span>
        </button>

        <div class="login-links">
          <router-link to="/admin/forgot-password" class="forgot-link">
            <i class="fas fa-key"></i> Forgot Password?
          </router-link>
          <router-link to="/admin/register" class="register-link">
            <i class="fas fa-user-plus"></i> Register
          </router-link>
        </div>
      </form>

      <!-- Step 2: OTP Verification -->
      <form v-else-if="step === 2" @submit.prevent="handleStep2" class="login-form">
        <div class="otp-header">
          <div class="otp-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <h3>Two-Factor Authentication</h3>
          <p>Enter the 6-digit code sent to your email</p>
          <p class="otp-email">
            <i class="fas fa-envelope"></i> {{ loginForm.email }}
          </p>
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
              @focus="$event.target.select()"
              ref="otpInputs"
              autofocus
              :disabled="loading"
            >
          </div>
        </div>

        <div class="otp-actions">
          <button type="submit" class="btn-login" :disabled="loading">
            <span v-if="!loading">
              <i class="fas fa-sign-in-alt"></i> Verify & Login
            </span>
            <span v-else>
              <i class="fas fa-spinner fa-spin"></i> Verifying...
            </span>
          </button>

          <div class="otp-footer">
            <button type="button" class="btn-resend" @click="resendOtp" :disabled="resendCooldown || loading">
              <i class="fas fa-redo"></i>
              {{ resendCooldown ? `Resend in ${resendTimer}s` : 'Resend Code' }}
            </button>

            <button type="button" class="btn-back" @click="goBack" :disabled="loading">
              <i class="fas fa-arrow-left"></i> Back
            </button>
          </div>
        </div>
      </form>

      <!-- Error/Success Messages -->
      <div v-if="errorMessage" class="alert-error">
        <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert-success">
        <i class="fas fa-check-circle"></i> {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'

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
      successMessage: '',
      showPassword: false,
      resendCooldown: false,
      resendTimer: 0,
      resendInterval: null
    }
  },

  mounted() {
    // ✅ Check if already authenticated
    if (authService.isAuthenticated()) {
      this.redirectToDashboard()
    }

    // ✅ Load saved email if exists
    const savedEmail = localStorage.getItem('saved_email')
    if (savedEmail) {
      this.loginForm.email = savedEmail
      this.loginForm.remember = true
    }

    // ✅ Focus email input
    this.$nextTick(() => {
      const emailInput = document.querySelector('input[type="email"]')
      if (emailInput) emailInput.focus()
    })
  },

  beforeUnmount() {
    if (this.resendInterval) {
      clearInterval(this.resendInterval)
    }
  },

  methods: {
    async handleStep1() {
      this.errorMessage = ''
      this.successMessage = ''
      this.loading = true

      try {
        // ✅ Validate email
        if (!this.loginForm.email || !this.loginForm.email.includes('@')) {
          throw new Error('Please enter a valid email address')
        }

        // ✅ Validate password
        if (!this.loginForm.password || this.loginForm.password.length < 6) {
          throw new Error('Password must be at least 6 characters')
        }

        // ✅ Call login step 1
        const response = await authService.loginStep1(
          this.loginForm.email,
          this.loginForm.password
        )

        // ✅ Save email if remember is checked
        if (this.loginForm.remember) {
          localStorage.setItem('saved_email', this.loginForm.email)
        } else {
          localStorage.removeItem('saved_email')
        }

        // ✅ Move to OTP step
        this.step = 2
        this.otpCodes = ['', '', '', '', '', '']
        this.successMessage = 'OTP sent to your email. Please check your inbox.'

        // ✅ Focus first OTP input
        this.$nextTick(() => {
          if (this.$refs.otpInputs && this.$refs.otpInputs[0]) {
            this.$refs.otpInputs[0].focus()
          }
        })

      } catch (error) {
        this.errorMessage = error.response?.data?.error || error.message || 'Login failed. Please try again.'
        console.error('Login step 1 error:', error)
      } finally {
        this.loading = false
      }
    },

    async handleStep2() {
      const otpCode = this.otpCodes.join('')
      
      // ✅ Validate OTP
      if (otpCode.length !== 6) {
        this.errorMessage = 'Please enter the complete 6-digit verification code'
        return
      }

      this.errorMessage = ''
      this.successMessage = ''
      this.loading = true

      try {
        // ✅ Call login step 2 with remember flag
        const response = await authService.loginStep2(
          otpCode,
          this.loginForm.remember
        )

        if (response.user) {
          // ✅ Load permissions
          await permissionService.init()
          
          this.successMessage = 'Login successful! Redirecting...'
          
          // ✅ Redirect after short delay
          setTimeout(() => {
            this.redirectToDashboard()
          }, 800)
        }

      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Invalid verification code. Please try again.'
        console.error('Login step 2 error:', error)
        
        // ✅ Clear OTP on error
        this.otpCodes = ['', '', '', '', '', '']
        this.$nextTick(() => {
          if (this.$refs.otpInputs && this.$refs.otpInputs[0]) {
            this.$refs.otpInputs[0].focus()
          }
        })
      } finally {
        this.loading = false
      }
    },

    handleOtpInput(index, event) {
      // ✅ Only allow numbers
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
      if (this.resendCooldown || this.loading) return

      this.errorMessage = ''
      this.successMessage = ''

      try {
        // ✅ Resend OTP
        await authService.loginStep1(
          this.loginForm.email,
          this.loginForm.password
        )

        this.successMessage = 'OTP resent to your email.'
        this.startResendTimer()

      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to resend code. Please try again.'
      }
    },

    startResendTimer() {
      this.resendCooldown = true
      this.resendTimer = 60

      if (this.resendInterval) {
        clearInterval(this.resendInterval)
      }

      this.resendInterval = setInterval(() => {
        this.resendTimer--
        if (this.resendTimer <= 0) {
          clearInterval(this.resendInterval)
          this.resendInterval = null
          this.resendCooldown = false
        }
      }, 1000)
    },

    goBack() {
      this.step = 1
      this.errorMessage = ''
      this.successMessage = ''
      this.otpCodes = ['', '', '', '', '', '']

      if (this.resendInterval) {
        clearInterval(this.resendInterval)
        this.resendInterval = null
        this.resendCooldown = false
        this.resendTimer = 0
      }
    },

    redirectToDashboard() {
      const redirect = authService.getLoginRedirect()
      this.$router.push(redirect)
    },

    setImagePlaceholder(event) {
      event.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100%" height="100%" fill="%23eeeeee"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="10" fill="%23999999">Logo</text></svg>'
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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  padding: 40px 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 16px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #999;
  font-size: 16px;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #2563eb;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input-wrapper input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-password {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
}

.toggle-password:hover {
  color: #333;
}

.form-options {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #555;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #2563eb;
  cursor: pointer;
}

.btn-login {
  padding: 14px 24px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.login-links {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  margin-top: 4px;
}

.forgot-link,
.register-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.forgot-link:hover,
.register-link:hover {
  text-decoration: underline;
}

/* OTP Styles */
.otp-header {
  text-align: center;
  margin-bottom: 8px;
}

.otp-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-size: 28px;
  color: white;
}

.otp-header h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
  color: #1a1a2e;
}

.otp-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.otp-email {
  margin-top: 8px;
  color: #2563eb;
  font-weight: 500;
  font-size: 14px;
}

.otp-inputs {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.otp-input {
  width: 48px;
  height: 56px;
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.otp-input:focus {
  outline: none;
  border-color: #2563eb;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.otp-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.otp-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.otp-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-resend {
  background: none;
  border: none;
  color: #2563eb;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-resend:hover:not(:disabled) {
  text-decoration: underline;
}

.btn-resend:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-back {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 8px 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-back:hover:not(:disabled) {
  color: #333;
}

.btn-back:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Alert Messages */
.alert-error {
  margin-top: 16px;
  padding: 12px 16px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 10px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-success {
  margin-top: 16px;
  padding: 12px 16px;
  background: #dcfce7;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  border-radius: 10px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Responsive */
@media (max-width: 480px) {
  .login-card {
    padding: 24px 20px;
  }

  .login-header h2 {
    font-size: 24px;
  }

  .otp-input {
    width: 40px;
    height: 48px;
    font-size: 20px;
  }

  .otp-inputs {
    gap: 8px;
  }

  .login-links {
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
}
</style>