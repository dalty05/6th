<template>
  <nav class="navbar" :class="{ scrolled: isScrolled, 'menu-open': mobileMenuOpen }">
    <div class="container">
      <div class="navbar-brand" @click="scrollToHome">
        <img src="/logo.png" alt="Mount Kenya Milk" class="logo" @error="handleImageError">
        <span class="brand-name">Mount Kenya Milk</span>
      </div>
      
      <div class="navbar-menu" :class="{ 'is-active': mobileMenuOpen }">
        <a 
          @click.prevent="scrollTo('home')" 
          :class="{ active: activeSection === 'home' }"
          class="nav-link"
        >
          <i class="fas fa-home"></i> Home
        </a>
        <a 
          @click.prevent="scrollTo('about')" 
          :class="{ active: activeSection === 'about' }"
          class="nav-link"
        >
          <i class="fas fa-info-circle"></i> About Us
        </a>
        <a 
          @click.prevent="scrollTo('products')" 
          :class="{ active: activeSection === 'products' }"
          class="nav-link"
        >
          <i class="fas fa-box-open"></i> Products
        </a>
        <a 
          @click.prevent="scrollTo('shop')" 
          :class="{ active: activeSection === 'shop' }"
          class="nav-link"
        >
          <i class="fas fa-shopping-cart"></i> Shop Online
        </a>
        <a 
          @click.prevent="scrollTo('blog')" 
          :class="{ active: activeSection === 'blog' }"
          class="nav-link"
        >
          <i class="fas fa-newspaper"></i> Blog
        </a>
        <a 
          @click.prevent="scrollTo('contact')" 
          :class="{ active: activeSection === 'contact' }"
          class="nav-link"
        >
          <i class="fas fa-envelope"></i> Contact Us
        </a>
        
        <div class="dropdown">
          <button class="dropdown-btn" @click="toggleDropdown">
            <i class="fas fa-ellipsis-h"></i> More <span>▼</span>
          </button>
          <div class="dropdown-content" v-show="dropdownOpen" @click.stop>
            <button @click="openCareersModal" class="dropdown-item">
              <i class="fas fa-briefcase"></i> Job Opportunities
            </button>
            <button @click="openCSRModal" class="dropdown-item">
              <i class="fas fa-hand-holding-heart"></i> CSR
            </button>
            <div class="dropdown-divider"></div>
            <template v-if="isAuthenticated">
              <router-link to="/admin/dashboard" @click="closeMenu" class="dropdown-item">
                <i class="fas fa-tachometer-alt"></i> Dashboard
              </router-link>
              <button @click="handleLogout" class="dropdown-item logout-btn">
                <i class="fas fa-sign-out-alt"></i> Logout
              </button>
            </template>
            <template v-else>
              <router-link to="/admin/login" class="dropdown-item" @click="closeLoginModal">
                <i class="fas fa-lock"></i> Admin Login
              </router-link>
            </template> 
          </div>
        </div>
      </div>
    </div>
    
    <!-- Admin Login Modal -->
    <div class="modal" v-if="showAdminLogin" @click.self="closeLoginModal">
      <div class="modal-content">
        <div class="modal-icon">
          <i class="fas fa-lock"></i>
        </div>
        <h3>Admin Login</h3>
        
        <div v-if="loginStep === 1">
          <form @submit.prevent="handleStep1">
            <div class="input-group">
              <i class="fas fa-envelope"></i>
              <input type="email" v-model="loginForm.email" placeholder="Email Address" required>
            </div>
            <div class="input-group">
              <i class="fas fa-lock"></i>
              <input type="password" v-model="loginForm.password" placeholder="Password" required>
            </div>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Verifying...' : 'Continue' }}
            </button>
          </form>
          <div class="modal-footer">
            <router-link to="/admin/forgot-password" @click="closeLoginModal">Forgot Password?</router-link>
            <router-link to="/admin/register" @click="closeLoginModal">Register</router-link>
          </div>
        </div>
        
        <div v-else-if="loginStep === 2">
          <p class="otp-instruction">Enter the 6-digit code sent to your email</p>
          <form @submit.prevent="handleStep2">
            <div class="otp-inputs">
              <input v-for="i in 6" :key="i" type="text" maxlength="1" class="otp-input"
                v-model="otpCodes[i-1]" @input="handleOtpInput(i-1, $event)"
                @keyup="handleOtpKeyup(i-1, $event)" ref="otpInputs" autofocus>
            </div>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Verifying...' : 'Verify & Login' }}
            </button>
          </form>
          <button class="btn-resend" @click="resendOtp" :disabled="resendCooldown">
            {{ resendCooldown ? `Resend in ${resendTimer}s` : 'Resend Code' }}
          </button>
          <button class="btn-back" @click="loginStep = 1">← Back</button>
        </div>
        
        <div v-if="errorMessage" class="error-message">
          <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
        </div>
        <button class="close-btn" @click="closeLoginModal">×</button>
      </div>
    </div>
    
    <!-- Careers Modal -->
    <InfoModal v-model:visible="showCareersModal" title="Job Opportunities">
      <CareersContent />
    </InfoModal>
    
    <!-- CSR Modal -->
    <InfoModal v-model:visible="showCSRModal" title="Corporate Social Responsibility">
      <CSRContent />
    </InfoModal>
  </nav>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { scrollToSection, handleInitialHash } from '@/utils/scroll'
import { useSectionObserver } from '@/composables/useSectionObserver'
import authService from '@/services/auth'
import InfoModal from '@/components/common/InfoModal.vue'
import CareersContent from '@/components/modals/CareersContent.vue'
import CSRContent from '@/components/modals/CSRContent.vue'

export default {
  name: 'Navbar',
  components: {
    InfoModal,
    CareersContent,
    CSRContent
  },
  setup() {
    const router = useRouter()
    const mobileMenuOpen = ref(false)
    const dropdownOpen = ref(false)
    const showAdminLogin = ref(false)

    const loginStep = ref(1)
    const loginForm = ref({ email: '', password: '' })
    const otpCodes = ref(['', '', '', '', '', ''])
    const loading = ref(false)
    const errorMessage = ref('')
    const resendCooldown = ref(false)
    const resendTimer = ref(0)
    const isScrolled = ref(false)
    const showCareersModal = ref(false)
    const showCSRModal = ref(false)
    
    const { activeSection } = useSectionObserver(['home', 'about', 'products', 'blog', 'contact'])
    
    const isAuthenticated = computed(() => authService.isAuthenticated())
    
    const openCareersModal = () => {
      showCareersModal.value = true
      closeMenu()
    }
    
    const openCSRModal = () => {
      showCSRModal.value = true
      closeMenu()
    }
    
    const handleClickOutside = (event) => {
      const dropdown = document.querySelector('.dropdown')
      
      if (dropdown && !dropdown.contains(event.target) && dropdownOpen.value) {
        dropdownOpen.value = false
      }
    }
    
    const scrollTo = (sectionId) => {
      router.push({ hash: `#${sectionId}` })
      closeMenu()
    }
    
    const scrollToHome = () => {
      scrollToSection('home', 0)
    }
  
    const handleScroll = () => {
      isScrolled.value = window.scrollY > 50
    }
    
    const handleStep1 = async () => {
      loading.value = true
      errorMessage.value = ''
      
      try {
        const response = await authService.loginStep1(
          loginForm.value.email,
          loginForm.value.password
        )
        
        if (response.requires_otp) {
          loginStep.value = 2
        }
      } catch (error) {
        errorMessage.value = error.response?.data?.error || 'Login failed'
      } finally {
        loading.value = false
      }
    }
    
    const handleStep2 = async () => {
      const otpCode = otpCodes.value.join('')
      if (otpCode.length !== 6) {
        errorMessage.value = 'Please enter the 6-digit code'
        return
      }
      
      loading.value = true
      errorMessage.value = ''
      
      try {
        await authService.loginStep2(otpCode)
        closeLoginModal()
        router.push('/admin/dashboard')
      } catch (error) {
        errorMessage.value = error.response?.data?.error || 'Invalid code'
        otpCodes.value = ['', '', '', '', '', '']
      } finally {
        loading.value = false
      }
    }
    
    const handleOtpInput = (index, event) => {
      const value = event.target.value.replace(/[^0-9]/g, '')
      otpCodes.value[index] = value
      if (value && index < 5) {
        const nextInput = document.querySelectorAll('.otp-input')[index + 1]
        nextInput?.focus()
      }
    }
    
    const handleOtpKeyup = (index, event) => {
      if (event.key === 'Backspace' && !otpCodes.value[index] && index > 0) {
        const prevInput = document.querySelectorAll('.otp-input')[index - 1]
        prevInput?.focus()
      }
    }
    
    const resendOtp = async () => {
      if (resendCooldown.value) return
      
      try {
        await authService.loginStep1(loginForm.value.email, loginForm.value.password)
        resendCooldown.value = true
        resendTimer.value = 60
        const interval = setInterval(() => {
          resendTimer.value--
          if (resendTimer.value <= 0) {
            clearInterval(interval)
            resendCooldown.value = false
          }
        }, 1000)
        errorMessage.value = ''
      } catch (error) {
        errorMessage.value = 'Failed to resend code'
      }
    }
    
    const toggleDropdown = () => {
      dropdownOpen.value = !dropdownOpen.value
    }
    
    const closeMenu = () => {
      mobileMenuOpen.value = false
      dropdownOpen.value = false
    }
    
    const closeLoginModal = () => {
      showAdminLogin.value = false
      loginStep.value = 1
      loginForm.value = { email: '', password: '' }
      otpCodes.value = ['', '', '', '', '', '']
      errorMessage.value = ''
    }
    
    const handleLogout = async () => {
      await authService.logout()
      router.push('/')
      closeMenu()
    }
    
    const handleImageError = (e) => {
      e.target.style.display = 'none'
    }
    
    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
      document.addEventListener('click', handleClickOutside)
      handleInitialHash()
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
      document.removeEventListener('click', handleClickOutside)
    })
    
    return {
      mobileMenuOpen,
      dropdownOpen,
      showAdminLogin,
      loginStep,
      loginForm,
      otpCodes,
      loading,
      errorMessage,
      resendCooldown,
      resendTimer,
      isScrolled,
      activeSection,
      isAuthenticated,
      showCareersModal,
      showCSRModal,
      openCareersModal,
      openCSRModal,
      scrollTo,
      scrollToHome,
      handleStep1,
      handleStep2,
      handleOtpInput,
      handleOtpKeyup,
      resendOtp,
      toggleDropdown,
      closeMenu,
      closeLoginModal,
      handleLogout,
      handleImageError
    }
  }
}
</script>

<style scoped>
/* ========== BASE NAVBAR ========== */
.navbar {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  /* position: fixed; */
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: all 0.3s ease;
  height: 80px;
}

.navbar.scrolled {
  padding: 0.5rem 0;
  background: rgba(255,255,255,0.98);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 20px;
  transition: padding 0.3s ease;
  max-width: 1400px;
  margin: 0 auto;
}

.navbar.scrolled .container {
  padding: 0.5rem 20px;
}

/* ========== BRAND ========== */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;
}

.logo {
  height: 50px;
  width: auto;
  transition: height 0.3s ease;
}

.navbar.scrolled .logo {
  height: 40px;
}

.brand-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1e3a8a;
  transition: font-size 0.3s ease;
}

.navbar.scrolled .brand-name {
  font-size: 1rem;
}

/* ========== NAVIGATION - CENTERED ========== */
.navbar-menu {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  justify-content: center;  /* ✅ Centering the menu */
  flex: 1;  /* ✅ Takes available space */
  margin: 0 2rem;  /* ✅ Spacing from brand and edges */
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.25rem 0;
  white-space: nowrap;
}

.nav-link i {
  font-size: 0.9rem;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background: #f59e0b;
  transition: width 0.3s;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

.nav-link:hover,
.nav-link.active {
  color: #f59e0b;
}

/* ========== DROPDOWN ========== */
.dropdown {
  position: relative;
}

.dropdown-btn {
  background: none;
  border: none;
  font-weight: 500;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #333;
  transition: color 0.3s;
}

.dropdown-btn:hover {
  color: #f59e0b;
}

.dropdown-content {
  position: absolute;
  top: 100%;
  left: 50%;  /* ✅ Center the dropdown under the button */
  transform: translateX(-50%);  /* ✅ Align center */
  background: white;
  min-width: 220px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-radius: 12px;
  overflow: hidden;
  z-index: 100;
  margin-top: 10px;
  animation: fadeInDown 0.2s ease;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  text-decoration: none;
  color: #333;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 0.9rem;
}

.dropdown-item i {
  width: 20px;
  color: #666;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 4px 0;
}

.logout-btn {
  color: #dc2626 !important;
}

.logout-btn i {
  color: #dc2626;
}

/* ========== MOBILE TOGGLE ========== */
.mobile-toggle {
  display: none;
  flex-direction: column;
  cursor: pointer;
  gap: 4px;
  flex-shrink: 0;
}

.mobile-toggle span {
  width: 25px;
  height: 3px;
  background: #1e3a8a;
  transition: 0.3s;
  border-radius: 3px;
}

/* ========== MODAL ========== */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  width: 90%;
  max-width: 420px;
  position: relative;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-icon {
  text-align: center;
  font-size: 3rem;
  margin-bottom: 1rem;
}

.modal-icon i {
  color: #f59e0b;
}

.modal-content h3 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #1e3a8a;
}

.input-group {
  position: relative;
  margin-bottom: 1rem;
}

.input-group i {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.input-group input {
  width: 100%;
  padding: 12px 12px 12px 42px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #ef4444;
}

.otp-instruction {
  text-align: center;
  color: #666;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.otp-inputs {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin: 1.5rem 0;
}

.otp-input {
  width: 50px;
  height: 50px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.3s;
}

.otp-input:focus {
  border-color: #f59e0b;
  outline: none;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #f59e0b;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #d97706;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-resend, .btn-back {
  width: 100%;
  padding: 10px;
  margin-top: 0.5rem;
  background: none;
  border: none;
  color: #f59e0b;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-resend:hover, .btn-back:hover {
  color: #d97706;
}

.btn-resend:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.modal-footer a {
  color: #666;
  text-decoration: none;
  transition: color 0.3s;
}

.modal-footer a:hover {
  color: #f59e0b;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 12px;
  font-size: 0.85rem;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 1024px) {
  .navbar-menu {
    gap: 1rem;
    margin: 0 1rem;
  }
}

@media (max-width: 768px) {
  .mobile-toggle {
    display: flex;
  }
  
  .navbar-menu {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    flex-direction: column;
    padding: 1rem;
    gap: 0.75rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    max-height: calc(100vh - 70px);
    overflow-y: auto;
    justify-content: flex-start;  /* ✅ Left align on mobile */
    margin: 0;
    flex: none;
  }
  
  .navbar-menu.is-active {
    display: flex;
  }
  
  .nav-link {
    width: 100%;
    padding: 0.5rem 0;
  }
  
  .dropdown {
    width: 100%;
  }
  
  .dropdown-btn {
    width: 100%;
    justify-content: space-between;
    padding: 0.5rem 0;
  }
  
  .dropdown-content {
    position: static;
    left: 0;
    transform: none;
    box-shadow: none;
    padding-left: 1rem;
    margin-top: 0.25rem;
    background: #f8fafc;
    border-radius: 8px;
  }
  
  @keyframes fadeInDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .brand-name {
    display: none;
  }
  
  .modal-content {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .navbar .container {
    padding: 0.8rem 15px;
  }
  
  .logo {
    height: 40px;
  }
  
  .navbar.scrolled .container {
    padding: 0.5rem 15px;
  }
  
  .otp-input {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
  
  .modal-content {
    padding: 1.25rem;
  }

}
</style>