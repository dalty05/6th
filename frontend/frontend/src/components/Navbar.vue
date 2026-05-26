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
              

              <router-link to="/admin/login" @click="closeLoginModal">
              Admin Login
            </router-link>
                
              
            
            </template>
          </div>
        </div>
      </div>
      
      <div class="social-links">
        <a href="#" target="_blank"><i class="fab fa-facebook "><img src="/facebook.png" alt="Mount Kenya Milk" class="logo2" @error="handleImageError"></i></a>
        <a href="#" target="_blank"><i class="fab fa-twitter"><img src="/x.png" alt="Mount Kenya Milk" class="logo2" @error="handleImageError"></i></a>
        <a href="#" target="_blank"><i class="fab fab-instagram"><img src="/instagram.jpg" alt="Mount Kenya Milk" class="logo2" @error="handleImageError"></i></a>
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

  mounted() {
  document.addEventListener('click', this.handleOutsideClick)
},

beforeUnmount() {
  document.removeEventListener('click', this.handleOutsideClick)
},




  methods: {
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen
    },

    




    handleOutsideClick(event) {
      const dropdown = this.$el.querySelector('.dropdown')

      if (dropdown && !dropdown.contains(event.target)) {
        this.dropdownOpen = false
      }
    },








    

    closeMenu() {
      this.mobileMenuOpen = false
      this.dropdownOpen = false
      this.showAdminLogin = false
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
:root {
  --nav-bg: rgba(255,255,255,0.95);
}

/* NAVBAR */
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(12px);
  background: var(--nav-bg);
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border-bottom: 1px solid rgba(255,255,255,0.2);
  transition: all 0.3s ease;
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.9rem 24px;
}

/* BRAND */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  height: 52px;
  width: auto;
  transition: transform 0.3s ease;
}
.logo2 {
  max-height: 40px;
  width: auto;
  transition: transform 0.3s ease;
  border-radius: 15px;
  position: relative;
  margin-right: 20px;
}


.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}


.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background: white;
  text-decoration: none;
  color: #1e3a8a;
  font-weight: 500;
  transition: all 0.3s;
  border-radius: 12px;
}





.logo:hover {
  transform: scale(1.05);
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--primary-blue);
  letter-spacing: 0.4px;
}

/* MENU */
.navbar-menu {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.navbar-menu a,
.dropdown-btn {
  position: relative;
  text-decoration: none;
  color: #333;
  font-weight: 600;
  font-size: 0.96rem;
  transition: all 0.3s ease;
}

.navbar-menu a::after,
.dropdown-btn::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 0%;
  height: 2px;
  background: var(--primary-blue);
  transition: width 0.3s ease;
}

.navbar-menu a:hover::after,
.dropdown-btn:hover::after,
.router-link-active::after {
  width: 100%;
}

.navbar-menu a:hover,
.dropdown-btn:hover,
.router-link-active {
  color: var(--primary-blue);
}

/* DROPDOWN */
.dropdown {
  position: relative;
}

.dropdown-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dropdown-btn span {
  font-size: 0.7rem;
  transition: transform 0.3s ease;
}

.dropdown:hover .dropdown-btn span {
  transform: rotate(180deg);
}

.dropdown-content {
  position: absolute;
  top: 130%;
  left: 0;
  min-width: 220px;
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  animation: fadeDropdown 0.25s ease;
  border: 1px solid rgba(255,255,255,0.3);
}

@keyframes fadeDropdown {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-content a,
.dropdown-content button {
  display: block;
  width: 100%;
  padding: 14px 18px;
  border: none;
  background: transparent;
  text-align: left;
  font-size: 0.92rem;
  font-weight: 500;
  cursor: pointer;
  color: #333;
  transition: all 0.25s ease;
}

.dropdown-content a:hover,
.dropdown-content button:hover {
  background: rgba(0, 102, 255, 0.08);
  color: var(--primary-blue);
  padding-left: 24px;
}

.admin-link {
  color: var(--primary-blue);
  font-weight: 700;
}

/* SOCIAL */
.social-links {
  display: flex;
  gap: 1rem;
  padding-right: 10px;
  
}


.social-links a {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: rgba(0,0,0,0.04);
  color: var(--primary-blue);
  transition: all 0.3s ease;
}

.social-links a:hover {
  transform: translateY(-3px);
  background: var(--primary-blue);
  color: white;
}

/* MOBILE TOGGLE */
.mobile-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  cursor: pointer;
}

.mobile-toggle span {
  width: 26px;
  height: 3px;
  border-radius: 10px;
  background: var(--primary-blue);
  transition: all 0.3s ease;
}

/* MODAL */
.modal {
  position: relative;
  inset: 0;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 22px;
  padding: 2rem;
  width: 90%;
  max-width: 420px;
  position: relative;
  animation: modalFade 0.3s ease;
}

@keyframes modalFade {
  from {
    opacity: 0;
    transform: scale(0.92);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-content h3 {
  text-align: center;
  margin-bottom: 1rem;
  color: #222;
}

.modal-content input {
  width: 100%;
  padding: 14px;
  margin: 10px 0;
  border-radius: 12px;
  border: 1px solid #ddd;
  transition: all 0.25s ease;
}

.modal-content input:focus {
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 4px rgba(0,102,255,0.08);
  outline: none;
}

.btn {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  opacity: 0.95;
}

/* OTP */
.modal .otp-inputs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 1.2rem 0;
}

.modal .otp-input {
  width: 52px;
  height: 55px;
  font-size: 1.4rem;
  font-weight: bold;
  text-align: center;
  border-radius: 12px;
}

/* ERROR */
.error-message {
  margin-top: 1rem;
  background: #ffe5e5;
  color: #d60000;
  padding: 12px;
  border-radius: 10px;
  text-align: center;
  font-size: 0.9rem;
}

/* MOBILE */
@media (max-width: 768px) {
  .navbar .container {
    padding: 1rem 18px;
  }

  .navbar-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    display: none;
    flex-direction: column;
    align-items: flex-start;
    padding: 1.5rem;
    background: rgba(255,255,255,0.98);
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    animation: fadeDropdown 0.25s ease;
  }

  .navbar-menu.is-active {
    display: flex;
  }

  .navbar-menu a,
  .dropdown-btn {
    width: 100%;
    padding: 10px 0;
  }

  .dropdown-content {
    position: static;
    width: 100%;
    margin-top: 10px;
    box-shadow: none;
    border-radius: 12px;
    background: rgba(0,0,0,0.03);
  }

  .mobile-toggle {
    display: flex;
  }

  .social-links {
    display: none;
  }

  .brand-name {
    font-size: 1rem;
  }

  .logo {
    height: 45px;
  }
}
</style>