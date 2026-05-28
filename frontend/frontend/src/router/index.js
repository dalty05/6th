// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import authService from '@/services/auth'

// Import existing views
import Home from '../views/Home.vue'
import ProductDetail from '../views/ProductDetail.vue'
import BlogDetail from '../views/BlogDetail.vue'
import Shop from '../views/Shop.vue'
import Careers from '../views/Careers.vue'
import CSR from '../views/CSR.vue'

// Admin Views
import AdminLogin from '../views/admin/Login.vue'
import AdminRegister from '../views/admin/Register.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import ForgotPassword from '../views/admin/ForgotPassword.vue'
import ResetPassword from '../views/admin/ResetPassword.vue'

// Partner Views (NEW)
import PartnerDashboard from '../views/partner/Dashboard.vue'
import PartnerReferralLinks from '../views/partner/ReferralLinks.vue'
import PartnerAnalytics from '../views/partner/Analytics.vue'
import PartnerProfile from '../views/partner/Profile.vue'

const routes = [
  // Public routes
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
  
  // Auth routes
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    meta: { title: 'Admin Login | Mount Kenya Milk', guestOnly: true }
  },
  {
    path: '/admin/register',
    name: 'AdminRegister',
    component: AdminRegister,
    meta: { title: 'Admin Registration | Mount Kenya Milk', guestOnly: true }
  },
  {
    path: '/admin/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { title: 'Forgot Password | Mount Kenya Milk', guestOnly: true }
  },
  {
    path: '/admin/reset-password',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { title: 'Reset Password | Mount Kenya Milk', guestOnly: true }
  },
  
  // Admin routes (super_admin and admin)
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { 
      requiresAuth: true, 
      allowedRoles: ['super_admin', 'admin'],
      title: 'Admin Dashboard | Mount Kenya Milk'
    }
  },
  
  // Partner routes (NEW)
  {
    path: '/partner/dashboard',
    name: 'PartnerDashboard',
    component: PartnerDashboard,
    meta: { 
      requiresAuth: true, 
      allowedRoles: ['partner'],
      title: 'Partner Dashboard | Mount Kenya Milk'
    }
  },
  {
    path: '/partner/links',
    name: 'PartnerReferralLinks',
    component: PartnerReferralLinks,
    meta: { 
      requiresAuth: true, 
      allowedRoles: ['partner'],
      title: 'My Referral Links | Mount Kenya Milk'
    }
  },
  {
    path: '/partner/analytics',
    name: 'PartnerAnalytics',
    component: PartnerAnalytics,
    meta: { 
      requiresAuth: true, 
      allowedRoles: ['partner'],
      title: 'Analytics | Mount Kenya Milk'
    }
  },
  {
    path: '/partner/profile',
    name: 'PartnerProfile',
    component: PartnerProfile,
    meta: { 
      requiresAuth: true, 
      allowedRoles: ['partner'],
      title: 'My Profile | Mount Kenya Milk'
    }
  },
  
  // Catch all
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
        top: 80
      }
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// Navigation guard for authentication and role-based access
router.beforeEach((to, from, next) => {
  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  const isAuthenticated = authService.isAuthenticated()
  const user = authService.getUser()
  
  // Check if route is for guests only (login, register, etc.)
  if (to.meta.guestOnly && isAuthenticated) {
    // Redirect authenticated users to their dashboard
    const dashboard = authService.getRoleBasedDashboard()
    next(dashboard)
    return
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next('/admin/login')
      return
    }
    
    // Check role-based access
    if (to.meta.allowedRoles && !to.meta.allowedRoles.includes(user?.role)) {
      // Redirect to appropriate dashboard based on role
      const dashboard = authService.getRoleBasedDashboard()
      next(dashboard)
      return
    }
  }
  
  next()
})

export default router