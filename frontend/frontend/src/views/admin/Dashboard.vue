<template>
  <div class="admin-dashboard">
    <AdminNavbar @toggleSidebar="toggleMobileSidebar" />
    
    <AdminSidebar 
      :activeTab="activeTab" 
      @navigate="handleNavigate"
      ref="sidebarRef"
    />
    
    <div class="dashboard-content" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'mobile-open': mobileSidebarOpen }">
      <div class="content-wrapper">
        <div class="page-header">
          <h1>{{ pageTitle }}</h1>
          <p>{{ pageSubtitle }}</p>
        </div>

        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="tab-content">
          <!-- Stats Grid -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-boxes"></i>
              </div>
              <div class="stat-info">
                <h3>{{ stats.totalProducts || 0 }}</h3>
                <p>Products</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-newspaper"></i>
              </div>
              <div class="stat-info">
                <h3>{{ stats.totalBlogs || 0 }}</h3>
                <p>Blog Posts</p>
              </div>
            </div>
            <div class="stat-card" v-if="canViewJobs">
              <div class="stat-icon">
                <i class="fas fa-briefcase"></i>
              </div>
              <div class="stat-info">
                <h3>{{ stats.totalJobs || 0 }}</h3>
                <p>Job Openings</p>
              </div>
            </div>
            <div class="stat-card" v-if="canViewOutlets">
              <div class="stat-icon">
                <i class="fas fa-map-marker-alt"></i>
              </div>
              <div class="stat-info">
                <h3>{{ stats.totalOutlets || 0 }}</h3>
                <p>Outlet Locations</p>
              </div>
            </div>


            

              <div v-if="isSuperAdmin" class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-users"></i>
                </div>
                <div class="stat-info">
                  <h3>{{ stats.totalUsers || 0 }}</h3>
                  <p>Users</p>
                </div>
              </div>


            <div class="stat-card" v-if="canViewReferrals">
              <div class="stat-icon">
                <i class="fas fa-link"></i>
              </div>
              <div class="stat-info">
                <h3>{{ stats.totalClicks || 0 }}</h3>
                <p>Referral Clicks</p>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="quick-actions-grid">
            <div class="quick-action-card" v-if="canViewProducts" @click="activeTab = 'products'">
              <i class="fas fa-box-open"></i>
              <h4>Manage Products</h4>
              <p>Add, edit, or remove products</p>
            </div>
            <div class="quick-action-card" v-if="canViewBlog" @click="activeTab = 'blog'">
              <i class="fas fa-newspaper"></i>
              <h4>Manage Blog</h4>
              <p>Create and edit blog posts</p>
            </div>
            <div class="quick-action-card" v-if="canViewJobs" @click="activeTab = 'jobs'">
              <i class="fas fa-briefcase"></i>
              <h4>Manage Jobs</h4>
              <p>Post and manage job openings</p>
            </div>
            <div class="quick-action-card" v-if="canViewOutlets" @click="activeTab = 'outlets'">
              <i class="fas fa-map-marker-alt"></i>
              <h4>Manage Outlets</h4>
              <p>Add and manage physical locations</p>
            </div>
            <div class="quick-action-card" v-if="isSuperAdmin" @click="activeTab = 'users'">
              <i class="fas fa-users-cog"></i>
              <h4>Manage Users</h4>
              <p>Control user access</p>
            </div>
            <div class="quick-action-card" v-if="canViewStatistics" @click="activeTab = 'statistics'">
              <i class="fas fa-chart-line"></i>
              <h4>View Analytics</h4>
              <p>Track performance</p>
            </div>
          </div>
        </div>

        <!-- Products Tab -->
        <div v-else-if="activeTab === 'products'" class="tab-content">
          <ProductsManagement @refresh="loadStats" />
        </div>

        <!-- Blog Tab -->
        <div v-else-if="activeTab === 'blog'" class="tab-content">
          <BlogManagement @refresh="loadStats" />
        </div>

        <!-- Jobs Tab -->
        <div v-else-if="activeTab === 'jobs'" class="tab-content">
          <JobManagement @refresh="loadStats" />
        </div>

        <!-- Outlets Tab -->
        <div v-else-if="activeTab === 'outlets'" class="tab-content">
          <OutletManagement @refresh="loadStats" />
        </div>

        <!-- Users Tab -->
        <div v-else-if="activeTab === 'users'" class="tab-content">
          <UserManagement @refresh="loadStats" />
        </div>

        <!-- Partners Tab -->
        <div v-else-if="activeTab === 'partners'" class="tab-content">
          <PartnerManagement @refresh="loadStats" />
        </div>

       

        <!-- Statistics Tab -->
        <div v-else-if="activeTab === 'statistics'" class="tab-content">
          <AdvancedAnalytics />
        </div>

        <!-- Contacts Tab -->
        <div v-else-if="activeTab === 'contacts'" class="tab-content">
          <ContactManagement />
        </div>


        <!-- Newsletter Tab -->
<div v-else-if="activeTab === 'newsletter'" class="tab-content">
  <NewsletterManagement />
</div>








        <!-- Permissions Tab -->
        <div v-else-if="activeTab === 'permissions'" class="tab-content">
          <PermissionManager />
        </div>

        <div v-else-if="activeTab === 'profile'" class="tab-content">
          <Profile />
        </div>




      </div>
      
      <AdminFooter />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'
import api from '@/services/api'

// Components
import AdminNavbar from '@/components/layout/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import ProductsManagement from '@/components/admin/ProductsManagement.vue'
import BlogManagement from '@/components/admin/BlogManagement.vue'
import JobManagement from '@/components/admin/JobManagement.vue'
import OutletManagement from '@/components/admin/OutletManagement.vue'
import UserManagement from '@/components/admin/UserManagement.vue'
import PartnerManagement from '@/components/admin/PartnerManagement.vue'
import ReferralAnalytics from '@/components/admin/ReferralAnalytics.vue'
import AdvancedAnalytics from '@/components/admin/AdvancedAnalytics.vue'

import AdminFooter from '@/components/layout/AdminFooter.vue'
import ContactManagement from '@/components/admin/ContactManagement.vue'
import PermissionManager from '@/components/admin/PermissionManager.vue'
import Profile from '@/views/admin/Profile.vue'

import NewsletterManagement from '@/components/admin/NewsletterManagement.vue'





const router = useRouter()
const route = useRoute()

// State
const activeTab = ref('overview')
const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)
const sidebarRef = ref(null)
const user = ref(null)
const stats = ref({
  totalProducts: 0,
  totalBlogs: 0,
  totalJobs: 0,
  totalOutlets: 0,
  totalUsers: 0,
  totalClicks: 0
})

// Permission computed properties from permissionService
const canViewProducts = computed(() => permissionService.canViewProducts())
const canViewBlog = computed(() => permissionService.canViewBlog())
const canViewJobs = computed(() => permissionService.canViewJobs())
const canViewOutlets = computed(() => permissionService.canViewOutlets())
const canViewReferrals = computed(() => permissionService.canViewReferrals())
const canViewStatistics = computed(() => permissionService.canViewStatistics())
// const isSuperAdmin = computed(() => permissionService.userRole === 'super_admin')
const isSuperAdmin = computed(() => user.value?.role === 'super_admin')

const pageTitle = computed(() => {
  const titles = {
    overview: 'Dashboard Overview',
    products: 'Products Management',
    blog: 'Blog Management',
    jobs: 'Job Management',
    outlets: 'Outlet Management',
    users: 'User Management',
    partners: 'Partner Management',
    referrals: 'Referral Analytics',
    statistics: 'Advanced Analytics',
    contacts: 'Contact Messages',
    newsletter: 'Newsletter Management',
    permissions: 'Permission Manager',
    profile: 'My Profile'
  }
  return titles[activeTab.value] || 'Dashboard'
})

const pageSubtitle = computed(() => {
  const subtitles = {
    overview: 'Welcome back, ' + (user.value?.full_name?.split(' ')[0] || 'Admin'),
    products: 'Manage your dairy product catalog',
    blog: 'Create and manage blog content',
    jobs: 'Post and manage job openings',
    outlets: 'Manage physical shop and depot locations',
    users: 'Control user access and permissions',
    partners: 'Manage marketing partners',
    statistics: 'Comprehensive analytics and insights',
    contacts: 'View and respond to customer inquiries',
    newsletter: 'Manage subscribers and send email campaigns',
    permissions: 'Manage user permissions and access control',
    profile: 'Manage your account settings and preferences'
  }
  return subtitles[activeTab.value] || ''
})

// Load stats
const loadStats = async () => {
  try {
    // Products - handle paginated response
    let productCount = 0
    try {
      const productsRes = await api.get('/products?per_page=1000')
      const productsData = productsRes.data
      
      if (Array.isArray(productsData)) {
        productCount = productsData.length
      } else if (productsData?.data && Array.isArray(productsData.data)) {
        productCount = productsData.data.length
      } else if (productsData?.pagination) {
        productCount = productsData.pagination.total_items || 0
      } else if (productsData?.items) {
        productCount = productsData.items.length || 0
      }
    } catch (e) {
      console.warn('Could not fetch products:', e)
    }

    // Blog - handle paginated response
    let blogCount = 0
    try {
      const blogRes = await api.get('/blog?simple=true&per_page=100')
      const blogData = blogRes.data
      
      if (Array.isArray(blogData)) {
        blogCount = blogData.length
      } else if (blogData?.data && Array.isArray(blogData.data)) {
        blogCount = blogData.data.length
      } else if (blogData?.pagination) {
        blogCount = blogData.pagination.total_items || 0
      }
    } catch (e) {
      console.warn('Could not fetch blogs:', e)
    }

    // Jobs
    let jobCount = 0
    if (canViewJobs.value) {
      try {
        const jobsRes = await api.get('/admin/jobs')
        jobCount = jobsRes.data?.length || 0
      } catch (e) {
        console.warn('Could not fetch jobs:', e)
      }
    }

    // Outlets
    let outletCount = 0
    if (canViewOutlets.value) {
      try {
        const outletsRes = await api.get('/admin/outlets')
        outletCount = outletsRes.data?.length || 0
      } catch (e) {
        console.warn('Could not fetch outlets:', e)
      }
    }

    // Users
    let userCount = 0
    if (isSuperAdmin.value) {
      try {
        const usersRes = await api.get('/admin/users')
        userCount = usersRes.data?.length || 0
      } catch (e) {
        console.warn('Could not fetch users:', e)
      }
    }

    let clickCount = 0
if (canViewReferrals.value) {
  try {
    const referralsRes = await api.get('/referral/stats')
    clickCount = referralsRes.data?.total_clicks || referralsRes.data?.totalClicks || 0
  } catch (e) {
    console.warn('Could not fetch referrals:', e)
  }
}

   

    stats.value = {
      totalProducts: productCount,
      totalBlogs: blogCount,
      totalJobs: jobCount,
      totalOutlets: outletCount,
      totalUsers: userCount,
      totalClicks: clickCount
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}
// Navigation
const handleNavigate = (tab) => {
  activeTab.value = tab
  router.push({ path: '/admin/dashboard', query: { tab } })
}

const toggleMobileSidebar = () => {
  mobileSidebarOpen.value = !mobileSidebarOpen.value
  if (sidebarRef.value) {
    sidebarRef.value.isOpen = mobileSidebarOpen.value
  }
}

// Check URL params
const checkUrlParams = () => {
  const tab = route.query.tab
  const validTabs = ['overview', 'products', 'blog', 'jobs', 'outlets', 'users', 'partners', 'statistics', 'contacts','permissions','newsletter', 'profile']
  if (tab && validTabs.includes(tab)) {
    activeTab.value = tab
  }
}



onMounted(() => {
  user.value = authService.getUser()

  
  loadStats()
  checkUrlParams()
})
</script>

<style scoped>
/* Your existing styles remain the same */
.admin-dashboard {
  min-height: 100vh;
  background: #f8fafc;
}

.dashboard-content {
  margin-left: 260px;
  padding: 80px 1.5rem 0;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-content.sidebar-collapsed {
  margin-left: 80px;
}

.content-wrapper {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h1 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
  font-size: 1.8rem;
}

.page-header p {
  color: #666;
  margin: 0;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: #e0e7ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon i {
  font-size: 1.5rem;
  color: #f59e0b;
}

.stat-info h3 {
  font-size: 1.5rem;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 0;
  color: #666;
  font-size: 0.8rem;
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.quick-action-card {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.quick-action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  border-color: #f59e0b;
}

.quick-action-card i {
  font-size: 1.5rem;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

.quick-action-card h4 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
  font-size: 1rem;
}

.quick-action-card p {
  color: #666;
  margin: 0;
  font-size: 0.8rem;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-content {
    margin-left: 0;
    padding: 70px 1rem 0;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header h1 {
    font-size: 1.4rem;
  }
}
</style>