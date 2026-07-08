// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'

// Import existing views
import Home from '../views/Home.vue'

// Admin Views
import AdminLogin from '../views/admin/Login.vue'
import AdminRegister from '../views/admin/Register.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import ForgotPassword from '../views/admin/ForgotPassword.vue'
import ResetPassword from '../views/admin/ResetPassword.vue'

import JobManagement from '../components/admin/JobManagement.vue'

// Partner Views 
import PartnerDashboard from '../views/partner/Dashboard.vue'
import PartnerReferralLinks from '../views/partner/ReferralLinks.vue'
import PartnerAnalytics from '../views/partner/Analytics.vue'
import PartnerProfile from '../views/partner/Profile.vue'

import ReferralRedirect from '../views/ReferralRedirect.vue'


import ProductDetail from '../views/ProductDetail.vue'




// ============================================================
// DYNAMIC COMPONENT REGISTRY
// ============================================================

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
  
  // Administration Components
  'users': () => import('@/components/admin/UserManagement.vue'),
  'permissions': () => import('@/components/admin/PermissionManager.vue'),
  'roles': () => import('@/components/admin/RoleManager.vue'),
  
  // Tour Components
  'tours': () => import('@/views/tour-manager/TourManagerBookings.vue'),
  'tour-packages': () => import('@/views/tour-manager/TourManagerPackages.vue'),
  'tour-calendar': () => import('@/views/tour-manager/TourManagerCalendar.vue'),
  'tour-payments': () => import('@/views/tour-manager/TourManagerPayments.vue'),
  'tour-reports': () => import('@/views/tour-manager/TourManagerReports.vue'),
  'tour-staff': () => import('@/components/admin/TourStaffManagement.vue'),

    // Partner Components
  'partner-dashboard': () => import('@/views/partner/Dashboard.vue'),
  'partner-links': () => import('@/views/partner/ReferralLinks.vue'),
  'partner-analytics': () => import('@/views/partner/Analytics.vue'),
  'profile': () => import('@/components/admin/MyProfile.vue'),
}

// Generate dynamic routes from components
function generateDynamicRoutes() {
  const routes = []
  
  // Admin Dashboard with dynamic tabs
  routes.push({
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: {
      requiresAuth: true,
      title: 'Admin Dashboard | Mount Kenya Milk'
    }
  })
  
  // Role Manager - accessible via dedicated route
  routes.push({
    path: '/admin/roles',
    name: 'RoleManager',
    component: () => import('@/components/admin/RoleManager.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['super_admin'],
      componentKey: 'roles',
      title: 'Role Management | Mount Kenya Milk'
    }
  })
  
  // Permission Manager 
  routes.push({
    path: '/admin/permissions',
    name: 'PermissionManager',
    component: () => import('@/components/admin/PermissionManager.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['super_admin'],
      componentKey: 'permissions',
      title: 'Permission Management | Mount Kenya Milk'
    }
  })
  
  // Tour Staff Management
  routes.push({
    path: '/admin/tour-staff',
    name: 'TourStaffManagement',
    component: () => import('@/components/admin/TourStaffManagement.vue'),
    meta: {
      requiresAuth: true,
      allowedRoles: ['super_admin', 'admin', 'tour_manager'],
      componentKey: 'tour-staff',
      title: 'Tour Staff Management | Mount Kenya Milk'
    }
  })
  
  return routes
}

const routes = [
  // ============================================================
  // PUBLIC ROUTES
  // ============================================================
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Mount Kenya Milk - Kenya\'s Largest Dairy Co-operative' }
  },
  
  // ============================================================
  // PRODUCT DETAILS
  // ============================================================

  {
  path: '/product/:slug',
  name: 'ProductDetail',
  component: ProductDetail,
  meta: { 
    title: 'Product Details | Mount Kenya Milk',
    layout: 'default'
  }
},






  // ============================================================
  // REFERRAL ROUTES
  // ============================================================
  { 
    path: '/r/:code', 
    name: 'ReferralRedirect', 
    component: ReferralRedirect 
  },
  
  // ============================================================
  // AUTH ROUTES
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
  // DYNAMIC ADMIN ROUTES
  // ============================================================
  ...generateDynamicRoutes(),
  
  // ============================================================
  // ADMIN JOBS ROUTE
  // ============================================================
  {
    path: '/jobs',
    name: 'AdminJobs',
    component: JobManagement,
    meta: {
      requiresAuth: true,
      allowedRoles: ['super_admin', 'admin'],
      title: 'Job Management | Mount Kenya Milk'
    }
  },
  
  // ============================================================
  // TOUR MANAGER ROUTES
  // ============================================================
  {
    path: '/tour-manager',
    component: () => import('@/views/tour-manager/TourManagerLayout.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Tour Manager',
      allowedRoles: ['tour_manager', 'tour_assistant', 'admin', 'super_admin']
    },
    children: [
      {
        path: 'dashboard',
        name: 'TourManagerDashboard',
        component: () => import('@/views/tour-manager/TourManagerDashboard.vue'),
        meta: { title: 'Tour Manager Dashboard' }
      },
      {
        path: 'bookings',
        name: 'TourManagerBookings',
        component: () => import('@/views/tour-manager/TourManagerBookings.vue'),
        meta: { title: 'Tour Bookings' }
      },
      {
        path: 'calendar',
        name: 'TourManagerCalendar',
        component: () => import('@/views/tour-manager/TourManagerCalendar.vue'),
        meta: { title: 'Tour Calendar' }
      },
      {
        path: 'packages',
        name: 'TourManagerPackages',
        component: () => import('@/views/tour-manager/TourManagerPackages.vue'),
        meta: { title: 'Tour Packages', requiresManager: true }
      },
      {
        path: 'payments',
        name: 'TourManagerPayments',
        component: () => import('@/views/tour-manager/TourManagerPayments.vue'),
        meta: { title: 'Tour Payments' }
      },
      {
        path: 'reports',
        name: 'TourManagerReports',
        component: () => import('@/views/tour-manager/TourManagerReports.vue'),
        meta: { title: 'Tour Reports', requiresManager: true }
      },
      {
  path: '/tour-manager/profile',
  name: 'TourManagerProfile',
  component: () => import('@/views/tour-manager/TourManagerProfile.vue'),
  meta: {
    requiresAuth: true,
    allowedRoles: ['tour_manager', 'tour_assistant', 'admin', 'super_admin'],
    title: 'My Profile | Tour Manager'
  }
},
      {
        path: '',
        redirect: '/tour-manager/dashboard'
      }
    ]
  },
  
  // ============================================================
  // PARTNER ROUTES
  // ============================================================
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
    // component: PartnerProfile,
    component: () => import('@/views/partner/Profile.vue'),
    meta: { 
      requiresAuth: true, 
      allowedRoles: ['partner'],
      title: 'My Profile | Mount Kenya Milk'
    }
  },
  {
    path: '/partner/help',
    name: 'PartnerHelp',
    component: () => import('@/views/partner/Help.vue'),
    meta: { 
      requiresAuth: true, 
      allowedRoles: ['partner'],
      title: 'Help Center | Mount Kenya Milk'
    }
  },

  // MY PROFILE

  {
  path: '/admin/profile',
  name: 'MyProfile',
  component: () => import('@/components/admin/MyProfile.vue'),
  meta: {
    requiresAuth: true,
    componentKey: 'profile',
    title: 'My Profile | Meru Dairy'
  }
},
  
  
  // ADMIN LAYOUT 
  
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, layout: 'admin' },
    children: [
     
    ]
  },


  // PARTNER MANAGEMENT ROUTE
  {
  path: '/admin/partners',
  name: 'PartnerManagement',
  component: () => import('@/components/admin/PartnerManagement.vue'),
  meta: {
    requiresAuth: true,
    componentKey: 'partners',
    title: 'Partner Management | Meru Dairy'
  }
},








  
  // ============================================================
  // CATCH ALL
  // ============================================================
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

// ============================================================
// NAVIGATION GUARD
//  ============================================================
router.beforeEach(async (to, from, next) => {
  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  const isAuthenticated = authService.isAuthenticated()
  const user = authService.getUser()
  
  // ✅ Check if route is for guests only (login, register, etc.)
  if (to.meta.guestOnly && isAuthenticated) {
    // Redirect authenticated users to their dashboard
    const dashboard = authService.getRoleBasedDashboard()
    if (dashboard !== to.path) {
      next(dashboard)
      return
    }
  }
  
  if (to.meta.requiresAuth) {
    console.debug('Router guard requiresAuth:', to.path)
    // Always verify session with backend (Flask-Login cookie)
    // Avoid relying on localStorage-based token checks.
    const sessionValid = await authService.checkAuth()
    console.debug('Router guard sessionValid:', sessionValid, 'path:', to.path)
    if (!sessionValid) {
      await authService.clearUserAndPermissions()
      console.debug('Router guard redirecting to login from', to.path)
      next('/admin/login')
      return
    }

    // Update user after checkAuth (setUserAndReload)
    const updatedUser = authService.getUser()

    //  Check role-based access
    if (to.meta.allowedRoles && !to.meta.allowedRoles.includes(updatedUser?.role)) {
      const dashboard = authService.getRoleBasedDashboard()
      if (dashboard !== to.path) {
        next(dashboard)
        return
      }
    }
  }
  
  
  if (to.path.startsWith('/admin') && to.meta.requiresAuth && to.path !== '/admin/dashboard' && to.name !== 'AdminDashboard') {
    // Only load permissions for authenticated admin routes
    if (!permissionService.isDashboardLoaded()) {
      await permissionService.loadPermissions()
    }
    
    // Check if user has access to this component
    const componentKey = to.name?.toLowerCase() || ''
    if (componentKey && !permissionService.canViewComponent(componentKey)) {
      // Redirect to dashboard if component not accessible
      next('/admin/dashboard')
      return
    }
  }
  
  next()
})

export default router