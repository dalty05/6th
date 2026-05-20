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
            <button @click="showAdminLogin = true" class="admin-link">
              Admin Login
            </button>
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
    <div class="modal" v-if="showAdminLogin" @click.self="showAdminLogin = false">
      <div class="modal-content">
        <h3>Admin Login</h3>
        <form @submit.prevent="handleLogin">
          <input type="text" v-model="loginForm.username" placeholder="Username" required>
          <input type="password" v-model="loginForm.password" placeholder="Password" required>
          <button type="submit" class="btn btn-primary">Login</button>
        </form>
        <button class="close-btn" @click="showAdminLogin = false">×</button>
      </div>
    </div>
  </nav>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Navbar',
  data() {
    return {
      mobileMenuOpen: false,
      dropdownOpen: false,
      showAdminLogin: false,
      loginForm: {
        username: '',
        password: ''
      }
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
      // If logo fails to load, show a text-based logo
      e.target.style.display = 'none'
    },
    async handleLogin() {
      try {
        const response = await axios.post('/api/admin/login', this.loginForm)
        if (response.data.is_admin) {
          localStorage.setItem('isAdmin', 'true')
          this.showAdminLogin = false
          this.$router.push('/admin/dashboard')
          this.loginForm = { username: '', password: '' }
        }
      } catch (error) {
        alert('Invalid credentials')
      }
    }
  }
}
</script>

<style scoped>
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

/* If logo fails to load, show a fallback */
.navbar-brand::before {
  content: '🥛';
  font-size: 2rem;
  display: none;
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
  color:  rgb(177, 177, 244);
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
  background: rgb(174, 174, 229);
  color: black;
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

.social-links a:hover {
  transform: translateY(-2px);
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
  transition: 0.3s;
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
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  position: relative;
}

.modal-content h3 {
  margin-bottom: 1rem;
  color: var(--primary-blue);
}

.modal-content input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
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