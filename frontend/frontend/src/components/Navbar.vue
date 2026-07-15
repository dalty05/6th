<template>
  <nav class="navbar" :class="{ scrolled: isScrolled, 'menu-open': mobileMenuOpen }">
    <div class="container">
      <div class="navbar-brand" @click="scrollToHome">
        <img src="/logo.png" alt="Mount Kenya Milk" class="logo" @error="handleImageError">
        <span class="brand-name">Mount Kenya Milk</span>
      </div>
      
      <button 
        class="mobile-toggle" 
        @click.stop="toggleMobileMenu"
        :aria-label="mobileMenuOpen ? 'Close menu' : 'Open menu'"
        :aria-expanded="mobileMenuOpen"
        type="button"
      >
        <span :class="{ active: mobileMenuOpen }"></span>
        <span :class="{ active: mobileMenuOpen }"></span>
        <span :class="{ active: mobileMenuOpen }"></span>
      </button>
      
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
        
        <div class="dropdown" ref="dropdownRef">
          <button class="dropdown-btn" @click.stop="toggleDropdown">
            <i class="fas fa-ellipsis-h"></i> 
            <span class="dropdown-label">More</span> 
            <span class="dropdown-arrow">▼</span>
          </button>
          <div class="dropdown-content" v-show="dropdownOpen">
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
              <!-- ✅ Changed to router-link to existing login page -->
              <router-link to="/admin/login" @click="closeMenu" class="dropdown-item">
                <i class="fas fa-lock"></i> Admin Login
              </router-link>
            </template>
          </div>
        </div>
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
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
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
    const dropdownRef = ref(null)
    const mobileMenuOpen = ref(false)
    const dropdownOpen = ref(false)
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
      const navbar = document.querySelector('.navbar')
      if (navbar && !navbar.contains(event.target) && mobileMenuOpen.value) {
        mobileMenuOpen.value = false
      }
      
      if (dropdownRef.value && !dropdownRef.value.contains(event.target) && dropdownOpen.value) {
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
    
    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value
      
      if (dropdownOpen.value) {
        dropdownOpen.value = false
      }
      
      if (mobileMenuOpen.value) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
    
    const toggleDropdown = (event) => {
      event?.stopPropagation()
      dropdownOpen.value = !dropdownOpen.value
    }
    
    const closeMenu = () => {
      mobileMenuOpen.value = false
      dropdownOpen.value = false
      document.body.style.overflow = ''
    }
    
    const handleLogout = async () => {
      try {
        await authService.logout()
        closeMenu()
        router.push('/')
      } catch (error) {
        authService.clearUser()
        closeMenu()
        router.push('/')
      }
    }
    
    const handleImageError = (e) => {
      e.target.style.display = 'none'
    }
    
    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
      document.addEventListener('click', handleClickOutside)
      handleInitialHash()
      
      const handleResize = () => {
        if (window.innerWidth > 768 && mobileMenuOpen.value) {
          mobileMenuOpen.value = false
          document.body.style.overflow = ''
        }
      }
      window.addEventListener('resize', handleResize)
      
      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
      })
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
      document.removeEventListener('click', handleClickOutside)
      document.body.style.overflow = ''
    })
    
    return {
      dropdownRef,
      mobileMenuOpen,
      dropdownOpen,
      isScrolled,
      activeSection,
      isAuthenticated,
      showCareersModal,
      showCSRModal,
      openCareersModal,
      openCSRModal,
      scrollTo,
      scrollToHome,
      toggleMobileMenu,
      toggleDropdown,
      closeMenu,
      handleLogout,
      handleImageError
    }
  }
}
</script>

<style scoped>
/* ========== MOBILE TOGGLE FIXES ========== */
.mobile-toggle {
  display: none;
  flex-direction: column;
  cursor: pointer;
  gap: 5px;
  flex-shrink: 0;
  z-index: 1001;
  padding: 5px;
  background: none;
  border: none;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.mobile-toggle:hover,
.mobile-toggle:focus {
  opacity: 0.8;
}

.mobile-toggle span {
  display: block;
  width: 28px;
  height: 3px;
  background: #1e3a8a;
  transition: all 0.3s ease;
  border-radius: 3px;
  transform-origin: center;
  pointer-events: none;
}

.mobile-toggle span.active:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.mobile-toggle span.active:nth-child(2) {
  opacity: 0;
  transform: scaleX(0);
}

.mobile-toggle span.active:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

/* ========== RESPONSIVE ========== */
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
    padding: 1.5rem 1.5rem 2rem;
    gap: 0.75rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    max-height: calc(100vh - 70px);
    overflow-y: auto;
    justify-content: flex-start;
    margin: 0;
    flex: none;
    border-top: 1px solid rgba(0,0,0,0.05);
  }
  
  .navbar-menu.is-active {
    display: flex;
    animation: slideDown 0.3s ease;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  body.menu-open {
    overflow: hidden;
  }
}

/* ========== DROPDOWN RESPONSIVE ========== */
@media (max-width: 768px) {
  .dropdown {
    width: 100%;
  }
  
  .dropdown-btn {
    width: 100%;
    justify-content: space-between;
    padding: 0.75rem 0;
    font-size: 1rem;
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
    width: 100%;
    animation: none;
  }
}

/* ========== DROPDOWN FIXES ========== */
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
  user-select: none;
}

.dropdown-btn:hover {
  color: #f59e0b;
}

.dropdown-label {
  display: inline;
}

.dropdown-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s;
}

.dropdown-content {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  min-width: 220px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-radius: 12px;
  overflow: hidden;
  z-index: 100;
  margin-top: 10px;
  animation: fadeInDown 0.2s ease;
}

/* Responsive dropdown */
@media (max-width: 768px) {
  .dropdown {
    width: 100%;
  }
  
  .dropdown-btn {
    width: 100%;
    justify-content: space-between;
    padding: 0.75rem 0;
    font-size: 1rem;
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
    width: 100%;
    animation: none;
  }
}

/* ========== BASE NAVBAR ========== */
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
  position: relative;
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
  z-index: 1001;
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

/* ========== NAVIGATION ========== */
.navbar-menu {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  justify-content: center;
  flex: 1;
  margin: 0 2rem;
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
  left: 50%;
  transform: translateX(-50%);
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

/* ========== RESPONSIVE ========== */
@media (max-width: 1024px) {
  .navbar-menu {
    gap: 1rem;
    margin: 0 1rem;
  }
}

@media (max-width: 992px) {
  .navbar-menu {
    gap: 0.8rem;
    margin: 0 0.5rem;
  }
  
  .brand-name {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .navbar {
    height: auto;
    min-height: 70px;
  }
  
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
    padding: 1.5rem 1.5rem 2rem;
    gap: 0.75rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    max-height: calc(100vh - 70px);
    overflow-y: auto;
    justify-content: flex-start;
    margin: 0;
    flex: none;
    border-top: 1px solid rgba(0,0,0,0.05);
  }
  
  .navbar-menu.is-active {
    display: flex;
    animation: slideDown 0.3s ease;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .nav-link {
    width: 100%;
    padding: 0.75rem 0;
    font-size: 1rem;
  }
  
  .nav-link::after {
    bottom: 0;
  }
  
  .dropdown {
    width: 100%;
  }
  
  .dropdown-btn {
    width: 100%;
    justify-content: space-between;
    padding: 0.75rem 0;
    font-size: 1rem;
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
    width: 100%;
  }
  
  .dropdown-item {
    padding: 0.75rem 1rem;
  }
  
  .brand-name {
    display: none;
  }
  
  .logo {
    height: 45px;
  }
  
  .navbar .container {
    padding: 0.8rem 20px;
  }
  
  .navbar.scrolled .container {
    padding: 0.5rem 20px;
  }
}

@media (max-width: 480px) {
  .navbar .container {
    padding: 0.6rem 15px;
  }
  
  .navbar.scrolled .container {
    padding: 0.4rem 15px;
  }
  
  .logo {
    height: 38px;
  }
  
  .mobile-toggle span {
    width: 24px;
    height: 2.5px;
  }
  
  .navbar-menu {
    padding: 1rem 1rem 1.5rem;
  }
  
  .nav-link {
    padding: 0.5rem 0;
    font-size: 0.95rem;
  }
  
  .dropdown-btn {
    padding: 0.5rem 0;
    font-size: 0.95rem;
  }
  
  .dropdown-content {
    padding-left: 0.75rem;
  }
  
  .dropdown-item {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }
}
</style>