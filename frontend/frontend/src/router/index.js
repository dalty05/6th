// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'

// ============================================================
// LAYOUTS
// ============================================================

import AdminLayout from '@/layouts/AdminLayout.vue'
import PublicLayout from '@/layouts/PublicLayout.vue'

// ============================================================
// PUBLIC VIEWS
// ============================================================

import Home from '../views/Home.vue'
import ProductDetail from '../views/ProductDetail.vue'
import ReferralRedirect from '../views/ReferralRedirect.vue'

// ============================================================
// AUTH VIEWS
// ============================================================

import AdminLogin from '../views/admin/Login.vue'
import AdminRegister from '../views/admin/Register.vue'
import ForgotPassword from '../views/admin/ForgotPassword.vue'
import ResetPassword from '../views/admin/ResetPassword.vue'

// ============================================================
// ADMIN DASHBOARD
// ============================================================

import AdminDashboard from '../views/admin/Dashboard.vue'

// ============================================================
// DYNAMIC COMPONENT REGISTRY
// ============================================================

// This maps database component keys to actual Vue components
// The keys must match the 'key' field in dashboard_components table
const componentRegistry = {
  // Core Components
  'overview': () => import('@/components/admin/Overview.vue'),
  'products': () => import('@/components/admin/ProductsManagement.vue'),
  'blog': () => import('@/components/admin/BlogManagement.vue'),
  'jobs': () => import('@/components/admin/JobManagement.vue'),
  'outlets': () => import('@/components/admin/OutletManagement.vue'),
  'statistics': () => import('@/components/admin/AdvancedAnalytics.vue'),
  'contacts': () => import('@/components/admin/ContactManagement.vue'),
  'newsletter': () => import('@/components/admin/NewsletterManagement.vue'),
  'activities': () => import('@/components/admin/Activities.vue'),
  
  // Administration
  'users': () => import('@/components/admin/UserManagement.vue'),
  'permissions': () => import('@/components/admin/PermissionManager.vue'),
  'roles': () => import('@/components/admin/RoleManager.vue'),
  
  // Tour Management
  'tours': () => import('@/components/admin/TourManagerBookings.vue'),
  'tour-packages': () => import('@/components/admin/TourManagerPackages.vue'),
  'tour-calendar': () => import('@/components/admin/TourManagerCalendar.vue'),
  'tour-payments': () => import('@/components/admin/TourManagerPayments.vue'),
  'tour-reports': () => import('@/components/admin/TourManagerReports.vue'),
  'tour-staff': () => import('@/components/admin/TourStaffManagement.vue'),
  
  // Partner Management
  'partners': () => import('@/components/admin/PartnerManagement.vue'),
  'partner-links': () => import('@/components/admin/PartnerReferralLinks.vue'),
  'partner-analytics': () => import('@/components/admin/PartnerAnalytics.vue'),
  
  // Profile
  'profile': () => import('@/components/admin/MyProfile.vue'),
}

// ============================================================
// ROUTES
// ============================================================

const routes = [
  // ============================================================
  // PUBLIC ROUTES (PublicLayout)
  // ============================================================
  {
    path: '/',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home,
        meta: { title: 'Mount Kenya Milk - Kenya\'s Largest Dairy Co-operative' }
      },
      {
        path: 'product/:slug',
        name: 'ProductDetail',
        component: ProductDetail,
        meta: { title: 'Product Details | Mount Kenya Milk' }
      }
    ]
  },
  
  // ============================================================
  // REFERRAL REDIRECT
  // ============================================================
  { 
    path: '/r/:code', 
    name: 'ReferralRedirect', 
    component: ReferralRedirect 
  },
  
  // ============================================================
  // AUTH ROUTES (No Layout)
  // ============================================================
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
  
  // ============================================================
  // ADMIN ROUTES (AdminLayout)
  // ============================================================
  {
    path: '/admin',
    component: AdminLayout,
    meta: { 
      requiresAuth: true,
      title: 'Admin Dashboard | Mount Kenya Milk'
    },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { 
          requiresAuth: true,
          title: 'Dashboard | Mount Kenya Milk'
        }
      },


      {
      path: 'roles',
      name: 'RoleManager',
      component: () => import('@/components/admin/RoleManager.vue'),
      meta: {
        requiresAuth: true,
        componentKey: 'roles',
        title: 'Role Management | Mount Kenya Milk'
      }
    },
    // ✅ Add Permission Manager Route
    {
      path: 'permissions',
      name: 'PermissionManager',
      component: () => import('@/components/admin/PermissionManager.vue'),
      meta: {
        requiresAuth: true,
        componentKey: 'permissions',
        title: 'Permission Management | Mount Kenya Milk'
      }
    },
    // ✅ Add User Management Route
    {
      path: 'users',
      name: 'UserManagement',
      component: () => import('@/components/admin/UserManagement.vue'),
      meta: {
        requiresAuth: true,
        componentKey: 'users',
        title: 'User Management | Mount Kenya Milk'
      }
    },




      // Fallback: redirect to dashboard
      {
        path: '',
        redirect: '/admin/dashboard'
      }
    ]
  },
  
  // ============================================================
  // LEGACY REDIRECTS (for backward compatibility)
  // ============================================================
  {
    path: '/tour-manager',
    redirect: '/admin/dashboard?tab=tours'
  },
  {
    path: '/tour-manager/:pathMatch(.*)*',
    redirect: '/admin/dashboard?tab=tours'
  },
  {
    path: '/partner',
    redirect: '/admin/dashboard?tab=partners'
  },
  {
    path: '/partner/:pathMatch(.*)*',
    redirect: '/admin/dashboard?tab=partners'
  },
  {
    path: '/admin/partners',
    redirect: '/admin/dashboard?tab=partners'
  },
  {
    path: '/admin/tour-staff',
    redirect: '/admin/dashboard?tab=tour-staff'
  },
  
  // ============================================================
  // CATCH ALL
  // ============================================================
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

// ============================================================
// ROUTER INSTANCE
// ============================================================

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
      return { top: 0 }
    }
  }
})

// ============================================================
// NAVIGATION GUARD
// ============================================================

router.beforeEach(async (to, from, next) => {
  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  const isAuthenticated = authService.isAuthenticated()
  const user = authService.getUser()
  
  // ✅ Guest-only routes (login, register, etc.)
  if (to.meta.guestOnly && isAuthenticated) {
    const dashboard = authService.getRoleBasedDashboard()
    if (dashboard !== to.path) {
      next(dashboard)
      return
    }
  }
  
  // ✅ Routes requiring authentication
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next('/admin/login')
      return
    }
    
    // ✅ Verify session with backend
    const sessionValid = await authService.checkAuth()
    if (!sessionValid) {
      await authService.clearUserAndPermissions()
      next('/admin/login')
      return
    }
    
    // ✅ Load permissions if not loaded
    if (!permissionService.isDashboardLoaded()) {
      await permissionService.loadPermissions()
    }
    
    // ✅ Check if user has access to the requested component
    const componentKey = to.query.tab
    if (componentKey) {
      const hasAccess = permissionService.canViewComponent(componentKey)
      if (!hasAccess) {
        // Redirect to dashboard with first available component
        const components = permissionService.getDashboardComponents() || []
        if (components.length > 0) {
          next({ 
            path: '/admin/dashboard', 
            query: { tab: components[0].key }
          })
          return
        } else {
          // No components available - redirect to login
          await authService.logout()
          next('/admin/login')
          return
        }
      }
    }
  }
  
  next()
})

export default router