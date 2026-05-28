import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ProductDetail from '../views/ProductDetail.vue'
import BlogDetail from '../views/BlogDetail.vue'
import Shop from '../views/Shop.vue'
import Careers from '../views/Careers.vue'
import CSR from '../views/CSR.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import AdminLogin from '../views/admin/Login.vue'
import AdminRegister from '../views/admin/Register.vue'
import ForgotPassword from '../views/admin/ForgotPassword.vue'
import ResetPassword from '../views/admin/ResetPassword.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Mount Kenya Milk - Kenya\'s Largest Dairy Co-operative' }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: ProductDetail,
    meta: { title: 'Product Details | Mount Kenya Milk' }
  },
  {
    path: '/blog/:slug',
    name: 'BlogDetail',
    component: BlogDetail,
    meta: { title: 'Blog Post | Mount Kenya Milk' }
  },
  {
    path: '/shop',
    name: 'Shop',
    component: Shop,
    meta: { title: 'Shop Online | Mount Kenya Milk' }
  },
  {
    path: '/careers',
    name: 'Careers',
    component: Careers,
    meta: { title: 'Careers | Mount Kenya Milk' }
  },
  {
    path: '/csr',
    name: 'CSR',
    component: CSR,
    meta: { title: 'CSR | Mount Kenya Milk' }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    meta: { title: 'Admin Login | Mount Kenya Milk' }
  },
  {
    path: '/admin/register',
    name: 'AdminRegister',
    component: AdminRegister,
    meta: { title: 'Admin Registration | Mount Kenya Milk' }
  },
  {
    path: '/admin/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { title: 'Forgot Password | Mount Kenya Milk' }
  },
  {
    path: '/admin/reset-password',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { title: 'Reset Password | Mount Kenya Milk' }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, title: 'Admin Dashboard | Mount Kenya Milk' }
  },
  {
    // Catch all redirect for unknown routes
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Handle saved position (browser back/forward)
    if (savedPosition) {
      return savedPosition
    }
    
    // Handle hash navigation (e.g., #about, #products)
    if (to.hash) {
      const elementId = to.hash.substring(1) // Remove the # character
      const element = document.getElementById(elementId)
      
      if (element) {
        // Calculate position with navbar offset
        const navbarHeight = 80
        const elementPosition = element.getBoundingClientRect().top
        const offsetPosition = elementPosition + window.pageYOffset - navbarHeight
        
        return {
          top: offsetPosition,
          behavior: 'smooth'
        }
      }
      
      // Fallback - try to find element after a short delay
      return new Promise((resolve) => {
        setTimeout(() => {
          const delayedElement = document.getElementById(elementId)
          if (delayedElement) {
            const navbarHeight = 80
            const elementPosition = delayedElement.getBoundingClientRect().top
            const offsetPosition = elementPosition + window.pageYOffset - navbarHeight
            resolve({
              top: offsetPosition,
              behavior: 'smooth'
            })
          } else {
            resolve({ top: 0, behavior: 'smooth' })
          }
        }, 100)
      })
    }
    
    // Default - scroll to top
    return { top: 0, behavior: 'smooth' }
  }
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // Check authentication for protected routes
  if (to.meta.requiresAuth) {
    const user = localStorage.getItem('user')
    if (!user) {
      next('/admin/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

// After each route navigation, handle hash if present
router.afterEach((to) => {
  if (to.hash) {
    const elementId = to.hash.substring(1)
    setTimeout(() => {
      const element = document.getElementById(elementId)
      if (element) {
        const navbarHeight = 80
        const elementPosition = element.getBoundingClientRect().top
        const offsetPosition = elementPosition + window.pageYOffset - navbarHeight
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        })
      }
    }, 100)
  }
})

export default router