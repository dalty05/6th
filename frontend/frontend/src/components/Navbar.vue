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
            <router-link to="/careers" @click="closeMenu" class="dropdown-item">
              <i class="fas fa-briefcase"></i> Job Opportunities
            </router-link>
            <router-link to="/csr" @click="closeMenu" class="dropdown-item">
              <i class="fas fa-hand-holding-heart"></i> CSR
            </router-link>
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
      
      <div class="nav-actions">
        <!-- Search Button -->
        <button class="search-btn" @click="toggleSearch" aria-label="Search">
          <i class="fas fa-search"></i>
        </button>
        
        <!-- REMOVED: User Menu Section -->
        
        <!-- Mobile Toggle -->
        <div class="mobile-toggle" @click="toggleMobileMenu">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
    
    <!-- Search Modal -->
    <div class="search-modal" v-if="showSearch" @click.self="toggleSearch">
      <!-- ... search modal content ... -->
    </div>
    
    <!-- Admin Login Modal -->
    <div class="modal" v-if="showAdminLogin" @click.self="closeLoginModal">
      <!-- ... login modal content ... -->
    </div>
  </nav>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { scrollToSection, handleInitialHash } from '@/utils/scroll'
import { useSectionObserver } from '@/composables/useSectionObserver'
import authService from '@/services/auth'

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter()
    const mobileMenuOpen = ref(false)
    const dropdownOpen = ref(false)
    const userMenuOpen = ref(false)
    const showAdminLogin = ref(false)
    const showSearch = ref(false)
    const searchQuery = ref('')
    const searchSuggestions = ref([])
    const cartCount = ref(0) // For future e-commerce
    const loginStep = ref(1)
    const loginForm = ref({ email: '', password: '' })
    const otpCodes = ref(['', '', '', '', '', ''])
    const loading = ref(false)
    const errorMessage = ref('')
    const resendCooldown = ref(false)
    const resendTimer = ref(0)
    const isScrolled = ref(false)
    
    const { activeSection } = useSectionObserver(['home', 'about', 'products', 'blog', 'contact'])
    
    const isAuthenticated = computed(() => authService.isAuthenticated())
    const userName = computed(() => {
      const user = authService.getUser()
      return user?.full_name?.split(' ')[0] || 'Admin'
    })
    
    // Close dropdowns when clicking outside
    const handleClickOutside = (event) => {
      const dropdown = document.querySelector('.dropdown')
      const userMenu = document.querySelector('.user-menu')
      
      if (dropdown && !dropdown.contains(event.target) && dropdownOpen.value) {
        dropdownOpen.value = false
      }
      if (userMenu && !userMenu.contains(event.target) && userMenuOpen.value) {
        userMenuOpen.value = false
      }
    }
    
    const scrollTo = (sectionId) => {
      router.push({ hash: `#${sectionId}` })
      closeMenu()
    }
    
    const scrollToHome = () => {
      scrollToSection('home', 0)
    }
    
    const goToShop = () => {
      router.push('/shop')
    }
    
    const toggleSearch = () => {
      showSearch.value = !showSearch.value
      if (!showSearch.value) {
        searchQuery.value = ''
        searchSuggestions.value = []
      }
    }
    
    const handleSearch = async () => {
      if (!searchQuery.value.trim()) return
      
      // Search products and blog posts
      router.push(`/products?search=${encodeURIComponent(searchQuery.value)}`)
      showSearch.value = false
      searchQuery.value = ''
    }
    
    const handleSuggestionClick = (item) => {
      if (item.type === 'product') {
        router.push(`/product/${item.id}`)
      } else if (item.type === 'blog') {
        router.push(`/blog/${item.slug}`)
      }
      showSearch.value = false
      searchQuery.value = ''
    }
    
    // Watch for search input to show suggestions
    watch(searchQuery, async (newQuery) => {
      if (newQuery.length > 2) {
        try {
          // Fetch product suggestions
          const productRes = await fetch(`/api/products?search=${newQuery}&per_page=3`)
          const productData = await productRes.json()
          
          // Fetch blog suggestions
          const blogRes = await fetch(`/api/blog?simple=true&per_page=3`)
          const blogData = await blogRes.json()
          
          const suggestions = [
            ...(productData.data || []).map(p => ({ ...p, type: 'product' })),
            ...(Array.isArray(blogData) ? blogData.slice(0, 3).map(b => ({ ...b, type: 'blog' })) : [])
          ]
          searchSuggestions.value = suggestions.slice(0, 5)
        } catch (error) {
          console.error('Error fetching suggestions:', error)
        }
      } else {
        searchSuggestions.value = []
      }
    })
    
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
    
    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
      if (mobileMenuOpen.value) {
        dropdownOpen.value = false
        userMenuOpen.value = false
      }
    }
    
    const toggleDropdown = () => {
      dropdownOpen.value = !dropdownOpen.value
      if (dropdownOpen.value) {
        userMenuOpen.value = false
      }
    }
    
    const toggleUserMenu = () => {
      userMenuOpen.value = !userMenuOpen.value
      if (userMenuOpen.value) {
        dropdownOpen.value = false
      }
    }
    
    const closeMenu = () => {
      mobileMenuOpen.value = false
      dropdownOpen.value = false
      userMenuOpen.value = false
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
      userMenuOpen,
      showAdminLogin,
      showSearch,
      searchQuery,
      searchSuggestions,
      cartCount,
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
      userName,
      scrollTo,
      scrollToHome,
      goToShop,
      toggleSearch,
      handleSearch,
      handleSuggestionClick,
      handleStep1,
      handleStep2,
      handleOtpInput,
      handleOtpKeyup,
      resendOtp,
      toggleMobileMenu,
      toggleDropdown,
      toggleUserMenu,
      closeMenu,
      closeLoginModal,
      handleLogout,
      handleImageError
    }
  }
}
</script>

<style scoped>
/* ========== BASE NAVBAR STYLES ========== */
.navbar {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: all 0.3s ease;
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

/* ========== NAVIGATION MENU ========== */
.navbar-menu {
  display: flex;
  gap: 1.5rem;
  align-items: center;
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
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.dropdown-btn i {
  font-size: 0.9rem;
}

.dropdown-content {
  position: absolute;
  top: 100%;
  left: 0;
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
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

/* ========== USER MENU ========== */
.user-menu {
  position: relative;
}

.user-menu-btn {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 50px;
  transition: all 0.3s;
  font-weight: 500;
  color: #333;
}

.user-menu-btn:hover {
  background: #f8fafc;
  color: #f59e0b;
}

.user-menu-btn i:first-child {
  font-size: 1.3rem;
  color: #f59e0b;
}

.user-menu-btn i:last-child {
  font-size: 0.8rem;
  transition: transform 0.3s;
}

.user-menu-btn i:last-child.rotated {
  transform: rotate(180deg);
}

.user-menu-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  min-width: 200px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-radius: 12px;
  overflow: hidden;
  z-index: 100;
  margin-top: 10px;
  animation: fadeInDown 0.2s ease;
}

.user-menu-item {
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

.user-menu-item i {
  width: 20px;
  color: #666;
}

.user-menu-item:hover {
  background: #f8fafc;
}

/* ========== NAV ACTIONS ========== */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-btn, .cart-btn {
  background: none;
  border: none;
  color: #333;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  padding: 6px;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover, .cart-btn:hover {
  background: #f8fafc;
  color: #f59e0b;
}

.cart-count {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #f59e0b;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 50px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ========== SOCIAL LINKS ========== */
.social-links {
  display: flex;
  gap: 0.5rem;
}

.social-links a {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 1rem;
  transition: all 0.3s;
  text-decoration: none;
  border-radius: 50%;
}

.social-links a:hover {
  background: #f8fafc;
  color: #f59e0b;
  transform: translateY(-2px);
}

/* ========== SEARCH MODAL ========== */
.search-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.9);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
}

.search-modal-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 60px;
  width: 90%;
  max-width: 600px;
  animation: slideInUp 0.3s ease;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-modal-content i {
  font-size: 1.2rem;
  color: #666;
}

.search-modal-content input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1rem;
  padding: 0.5rem 0;
}

.search-modal-content button {
  background: #f59e0b;
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.search-modal-content button:hover {
  background: #d97706;
  transform: scale(1.05);
}

.search-suggestions {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  margin-top: 1rem;
  overflow: hidden;
  animation: fadeInUp 0.3s ease;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.3s;
  border-bottom: 1px solid #e5e7eb;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: #f8fafc;
}

.suggestion-item i {
  color: #666;
}

/* ========== MODAL STYLES ========== */
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

/* OTP Inputs */
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

/* ========== MOBILE TOGGLE ========== */
.mobile-toggle {
  display: none;
  flex-direction: column;
  cursor: pointer;
  gap: 4px;
}

.mobile-toggle span {
  width: 25px;
  height: 3px;
  background: #1e3a8a;
  transition: 0.3s;
  border-radius: 3px;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 1024px) {
  .navbar-menu {
    gap: 1rem;
  }
  
  .social-links {
    display: none;
  }
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
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    max-height: calc(100vh - 70px);
    overflow-y: auto;
  }
  
  .navbar-menu.is-active {
    display: flex;
  }
  
  .mobile-toggle {
    display: flex;
  }
  
  .dropdown-content {
    position: static;
    box-shadow: none;
    padding-left: 1rem;
    margin-top: 0;
    background: #f8fafc;
  }
  
  .dropdown-btn {
    width: 100%;
    justify-content: space-between;
  }
  
  .user-menu-dropdown {
    position: static;
    box-shadow: none;
    margin-top: 0;
    background: #f8fafc;
  }
  
  .user-menu-btn {
    width: 100%;
    justify-content: space-between;
  }
  
  .nav-actions {
    gap: 0.5rem;
  }
  
  .search-btn, .cart-btn {
    width: 32px;
    height: 32px;
  }
  
  .navbar.scrolled .container {
    padding: 0.5rem 20px;
  }
  
  .brand-name {
    display: none;
  }
}

@media (max-width: 480px) {
  .navbar .container {
    padding: 0.8rem 15px;
  }
  
  .logo {
    height: 40px;
  }
  
  .search-btn, .cart-btn {
    width: 28px;
    height: 28px;
    font-size: 0.9rem;
  }
  
  .modal-content {
    padding: 1.5rem;
  }
  
  .otp-input {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
}
</style>