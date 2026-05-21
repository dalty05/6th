<template>
  <nav class="navbar">
    <div class="container">
      <div class="navbar-brand">
        <img src="/logo.png" alt="Mount Kenya Milk" class="logo" @error="handleImageError">
        <span class="brand-name">Mount Kenya Milk</span>
      </div>
      
      <div class="navbar-menu" :class="{ 'is-active': mobileMenuOpen }">
        <router-link to="/" @click="closeMenu">Home</router-link>
        <router-link to="/about" @click="closeMenu">About Us</router-link>
        <router-link to="/products" @click="closeMenu">Products</router-link>
        <router-link to="/shop" @click="closeMenu">Shop Online</router-link>
        <router-link to="/blog" @click="closeMenu">Blog</router-link>
        <router-link to="/contact" @click="closeMenu">Contact Us</router-link>
        
        <div class="dropdown">
          <button class="dropdown-btn" @click="toggleDropdown">
            More <span>▼</span>
          </button>
          <div class="dropdown-content" v-show="dropdownOpen">
            <router-link to="/careers" @click="closeMenu">Job Opportunities</router-link>
            <router-link to="/csr" @click="closeMenu">CSR</router-link>
            <template v-if="isAuthenticated">
              <router-link to="/admin/dashboard" @click="closeMenu">Dashboard</router-link>
              <button @click="handleLogout" class="admin-link">Logout</button>
            </template>
            <template v-else>
              <button @click="showAdminLogin = true" class="admin-link">
                Admin Login
              </button>
            </template>
          </div>
        </div>
      </div>
      
      <div class="social-links">
        <a href="#" target="_blank"><i class="fab fa-facebook"></i></a>
        <a href="#" target="_blank"><i class="fab fa-twitter"></i></a>
        <a href="#" target="_blank"><i class="fab fa-instagram"></i></a>
      </div>
      
      <div class="mobile-toggle" @click="toggleMobileMenu">
        <span></span><span></span><span></span>
      </div>
    </div>
    
    <!-- Admin Login Modal -->
    <div class="modal" v-if="showAdminLogin" @click.self="closeLoginModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeLoginModal">×</button>
        
        <!-- Step 1: Email & Password -->
        <div v-if="loginStep === 1">
          <h3>Admin Login</h3>
          <form @submit.prevent="handleStep1">
            <input 
              type="email" 
              v-model="loginForm.email" 
              placeholder="Email Address" 
              required
              autocomplete="email"
            >
            <input 
              type="password" 
              v-model="loginForm.password" 
              placeholder="Password" 
              required
              autocomplete="current-password"
            >
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Verifying...' : 'Continue' }}
            </button>
          </form>
          <div class="modal-footer">
            <router-link to="/admin/forgot-password" @click="closeLoginModal">
              Forgot Password?
            </router-link>
            <router-link to="/admin/register" @click="closeLoginModal">
              Register
            </router-link>
          </div>
        </div>
        
        <!-- Step 2: OTP Verification -->
        <div v-else-if="loginStep === 2">
          <h3>Two-Factor Authentication</h3>
          <p class="otp-instruction">Enter the 6-digit code sent to your email</p>
          <form @submit.prevent="handleStep2">
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
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Verifying...' : 'Verify & Login' }}
            </button>
          </form>
          <button 
            class="btn-resend" 
            @click="resendOtp" 
            :disabled="resendCooldown"
          >
            {{ resendCooldown ? `Resend in ${resendTimer}s` : 'Resend Code' }}
          </button>
          <button class="btn-back" @click="loginStep = 1">
            ← Back
          </button>
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import axios from 'axios'
import authService from '@/services/auth'

export default {
  name: 'Navbar',
  data() {
    return {
      mobileMenuOpen: false,
      dropdownOpen: false,
      showAdminLogin: false,
      loginStep: 1,
      loginForm: {
        email: '',
        password: ''
      },
      otpCodes: ['', '', '', '', '', ''],
      loading: false,
      errorMessage: '',
      resendCooldown: false,
      resendTimer: 0,
      loginEmail: null
    }
  },
  computed: {
    isAuthenticated() {
      return authService.isAuthenticated()
    }
  },
  methods: {
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen
    },
    closeMenu() {
      this.mobileMenuOpen = false
      this.dropdownOpen = false
    },
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen
    },
    handleImageError(e) {
      e.target.style.display = 'none'
    },
    closeLoginModal() {
      this.showAdminLogin = false
      this.loginStep = 1
      this.loginForm = { email: '', password: '' }
      this.otpCodes = ['', '', '', '', '', '']
      this.errorMessage = ''
    },
    
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
          this.loginStep = 2
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
        const response = await authService.loginStep2(otpCode)
        this.closeLoginModal()
        this.$router.push('/admin/dashboard')
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Invalid verification code'
        this.otpCodes = ['', '', '', '', '', '']
        if (this.$refs.otpInputs && this.$refs.otpInputs[0]) {
          this.$refs.otpInputs[0].focus()
        }
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
        await authService.loginStep1(this.loginForm.email, this.loginForm.password)
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
    },
    
    async handleLogout() {
      await authService.logout()
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
/* Add OTP styles */
.modal .otp-inputs {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin: 1rem 0;
}

.modal .otp-input {
  width: 50px;
  height: 50px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  border: 2px solid #ddd;
  border-radius: 8px;
}

.modal .otp-input:focus {
  border-color: var(--primary-blue);
  outline: none;
}

.modal .otp-instruction {
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  margin: 0.5rem 0;
}

.modal .btn-resend,
.modal .btn-back {
  width: 100%;
  padding: 8px;
  margin-top: 0.5rem;
  background: none;
  border: none;
  color: var(--primary-blue);
  cursor: pointer;
  font-size: 0.85rem;
}

.modal .btn-resend:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal .modal-footer {
  margin-top: 1rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.modal .modal-footer a {
  color: var(--primary-blue);
  text-decoration: none;
}

/* Keep your existing navbar styles */
.navbar {
  background: var(--white);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 20px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  height: 50px;
  width: auto;
}

.brand-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary-blue);
}

.navbar-menu {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.navbar-menu a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: color 0.3s;
}

.navbar-menu a:hover,
.navbar-menu .router-link-active {
  color: var(--primary-blue);
}

.dropdown {
  position: relative;
}

.dropdown-btn {
  background: none;
  border: none;
  font-weight: 500;
  cursor: pointer;
  font-size: 1rem;
  padding: 0;
}

.dropdown-content {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 180px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  border-radius: 8px;
  overflow: hidden;
  z-index: 100;
}

.dropdown-content a,
.dropdown-content button {
  display: block;
  padding: 12px 16px;
  text-decoration: none;
  color: #333;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
}

.dropdown-content a:hover,
.dropdown-content button:hover {
  background: var(--gray-light);
}

.admin-link {
  color: var(--primary-blue);
  font-weight: 600;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-links a {
  color: var(--primary-blue);
  font-size: 1.2rem;
  transition: transform 0.3s;
}

.mobile-toggle {
  display: none;
  flex-direction: column;
  cursor: pointer;
}

.mobile-toggle span {
  width: 25px;
  height: 3px;
  background: var(--primary-blue);
  margin: 3px 0;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 400px;
  position: relative;
}

.modal-content input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-content h3 {
  margin-bottom: 1rem;
  text-align: center;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.error-message {
  margin-top: 1rem;
  padding: 0.5rem;
  background: #fee;
  color: #c00;
  border-radius: 4px;
  font-size: 0.85rem;
  text-align: center;
}

@media (max-width: 768px) {
  .navbar-menu {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    flex-direction: column;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }
  
  .navbar-menu.is-active {
    display: flex;
  }
  
  .mobile-toggle {
    display: flex;
  }
  
  .social-links {
    display: none;
  }
  
  .dropdown-content {
    position: static;
    box-shadow: none;
    padding-left: 1rem;
  }
}
</style>