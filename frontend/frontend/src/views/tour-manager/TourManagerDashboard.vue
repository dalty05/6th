<template>
  <div class="tour-manager-dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1><i class="fas fa-chart-pie"></i> Dashboard</h1>
        <p class="subtitle">Welcome back, {{ user?.full_name || 'Tour Manager' }}!</p>
      </div>
      <div class="header-actions">
        <button @click="refreshData" class="btn-refresh" :disabled="refreshing">
          <i :class="refreshing ? 'fas fa-spinner fa-spin' : 'fas fa-sync-alt'"></i>
          {{ refreshing ? 'Refreshing...' : 'Refresh' }}
        </button>
        <button @click="goToBookings" class="btn-primary">
          <i class="fas fa-plus"></i> New Booking
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.color }">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-info">
          <h3>{{ stat.value }}</h3>
          <p>{{ stat.label }}</p>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h3><i class="fas fa-bolt"></i> Quick Actions</h3>
      <div class="action-grid">
        <div class="action-card" @click="goToBookings">
          <i class="fas fa-ticket-alt"></i>
          <span>View All Bookings</span>
        </div>
        <div class="action-card" @click="goToCalendar">
          <i class="fas fa-calendar-alt"></i>
          <span>Check Calendar</span>
        </div>
        <div v-if="canManage" class="action-card" @click="goToPackages">
          <i class="fas fa-tag"></i>
          <span>Manage Packages</span>
        </div>
        <div class="action-card" @click="goToPayments">
          <i class="fas fa-money-bill-wave"></i>
          <span>Process Payments</span>
        </div>
        <div v-if="pendingCount > 0" class="action-card highlight" @click="goToBookings">
          <i class="fas fa-clock"></i>
          <span>{{ pendingCount }} Pending <br>Approvals</span>
          <span class="pending-badge">{{ pendingCount }}</span>
        </div>
      </div>
    </div>

    <!-- Two Column Layout -->
    <div class="dashboard-grid">
      <!-- Recent Bookings -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3><i class="fas fa-history"></i> Recent Bookings</h3>
          <button @click="goToBookings" class="view-all-btn">View All</button>
        </div>
        <div class="card-body">
          <div v-if="recentBookingsLoading" class="loading-state">
            <div class="loading-spinner small"></div>
            <p>Loading recent bookings...</p>
          </div>
          <div v-else-if="!recentBookings || recentBookings.length === 0" class="empty-state">
            <i class="fas fa-inbox"></i>
            <p>No recent bookings</p>
          </div>
          <div v-else class="booking-list">
            <div v-for="booking in recentBookings" :key="booking.id" class="booking-item">
              <div class="booking-info">
                <span class="booking-ref">{{ booking.reference }}</span>
                <span class="booking-customer">{{ booking.customer_name }}</span>
                <span class="booking-date">{{ formatDate(booking.tour_date) }}</span>
              </div>
              <div class="booking-status-group">
                <span class="status-badge" :class="booking.status">
                  {{ booking.status }}
                </span>
                <button @click="viewBooking(booking)" class="btn-view">
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Tours -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3><i class="fas fa-calendar-check"></i> Upcoming Tours</h3>
          <button @click="goToCalendar" class="view-all-btn">View Calendar</button>
        </div>
        <div class="card-body">
          <div v-if="upcomingToursLoading" class="loading-state">
            <div class="loading-spinner small"></div>
            <p>Loading upcoming tours...</p>
          </div>
          <div v-else-if="!upcomingTours || upcomingTours.length === 0" class="empty-state">
            <i class="fas fa-calendar"></i>
            <p>No upcoming tours</p>
          </div>
          <div v-else class="tour-list">
            <div v-for="tour in upcomingTours" :key="tour.id" class="tour-item">
              <div class="tour-date">
                <span class="day">{{ formatDay(tour.tour_date) }}</span>
                <span class="month">{{ formatMonth(tour.tour_date) }}</span>
              </div>
              <div class="tour-info">
                <span class="tour-ref">{{ tour.reference }}</span>
                <span class="tour-package">{{ tour.package?.name || 'N/A' }}</span>
                <span class="tour-people"><i class="fas fa-users"></i> {{ tour.people_count }}</span>
              </div>
              <span class="status-badge" :class="tour.status">
                {{ tour.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Detail Modal -->
    <div v-if="selectedBooking" class="modal-overlay" @click.self="closeBookingDetail">
      <div class="modal-container booking-detail-modal">
        <button class="modal-close" @click="closeBookingDetail">
          <i class="fas fa-times"></i>
        </button>
        <div class="booking-detail-content">
          <div class="detail-header">
            <h2><i class="fas fa-ticket-alt"></i> Booking Details</h2>
            <span class="booking-ref-large">{{ selectedBooking.reference }}</span>
          </div>
          <div class="detail-grid">
            <div class="detail-section">
              <h4><i class="fas fa-user"></i> Customer</h4>
              <p><strong>{{ selectedBooking.customer_name }}</strong></p>
              <p>{{ selectedBooking.customer_email }}</p>
              <p>{{ selectedBooking.customer_phone }}</p>
              <p v-if="selectedBooking.group_name" class="group-name">
                <i class="fas fa-users"></i> {{ selectedBooking.group_name }}
              </p>
            </div>
            <div class="detail-section">
              <h4><i class="fas fa-info-circle"></i> Tour Details</h4>
              <p><strong>Package:</strong> {{ selectedBooking.package?.name || 'N/A' }}</p>
              <p><strong>Date:</strong> {{ formatFullDate(selectedBooking.tour_date) }}</p>
              <p><strong>People:</strong> {{ selectedBooking.people_count }}</p>
              <p><strong>Total:</strong> KES {{ formatPrice(selectedBooking.total_amount) }}</p>
              <p><strong>Status:</strong> 
                <span class="status-badge" :class="selectedBooking.status">
                  {{ selectedBooking.status }}
                </span>
              </p>
            </div>
          </div>
          <div class="detail-actions">
            <button v-if="selectedBooking.status === 'pending'" @click="approveBooking(selectedBooking)" class="btn-approve">
              <i class="fas fa-check"></i> Approve
            </button>
            <button v-if="selectedBooking.status === 'pending'" @click="rejectBooking(selectedBooking)" class="btn-reject">
              <i class="fas fa-times"></i> Reject
            </button>
            <button 
              v-if="canProcessPayment(selectedBooking)" 
              @click="openPaymentModal(selectedBooking)" 
              class="btn-payment"
            >
              <i class="fas fa-money-bill-wave"></i> Process Payment
            </button>
            <button @click="closeBookingDetail" class="btn-close-detail">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import axios from 'axios'
import { format } from 'date-fns'

const router = useRouter()
const user = ref(null)

// State
const stats = ref([
  { label: 'Total Bookings', value: '0', icon: 'fas fa-calendar-check', color: '#3b82f6' },
  { label: 'Pending', value: '0', icon: 'fas fa-clock', color: '#f59e0b' },
  { label: 'Confirmed', value: '0', icon: 'fas fa-check-circle', color: '#10b981' },
  { label: 'Revenue', value: 'KES 0', icon: 'fas fa-money-bill-wave', color: '#8b5cf6' }
])
const recentBookings = ref([])  // ✅ Initialize as empty array
const upcomingTours = ref([])   // ✅ Initialize as empty array
const pendingCount = ref(0)
const refreshing = ref(false)
const recentBookingsLoading = ref(false)
const upcomingToursLoading = ref(false)
const selectedBooking = ref(null)

const canManage = computed(() => {
  const userData = authService.getUser()
  return userData?.is_tour_manager || userData?.role === 'admin' || userData?.role === 'super_admin'
})

const canProcessPayment = (booking) => {
  if (!booking) return false
  if (booking.status === 'rejected' || booking.status === 'cancelled') {
    return false
  }
  return booking.status === 'confirmed' || 
         booking.status === 'commitment_pending' ||
         booking.status === 'cleared'
}

const loadStats = async () => {
  try {
    const response = await axios.get('/api/tour/admin/dashboard/stats')
    const data = response.data
    stats.value = [
      { 
        label: 'Total Bookings', 
        value: data.total_bookings || 0, 
        icon: 'fas fa-calendar-check',
        color: '#3b82f6'
      },
      { 
        label: 'Pending', 
        value: data.pending_bookings || 0, 
        icon: 'fas fa-clock',
        color: '#f59e0b'
      },
      { 
        label: 'Confirmed', 
        value: data.confirmed_bookings || 0, 
        icon: 'fas fa-check-circle',
        color: '#10b981'
      },
      { 
        label: 'Revenue', 
        value: `KES ${(data.total_revenue || 0).toLocaleString()}`, 
        icon: 'fas fa-money-bill-wave',
        color: '#8b5cf6'
      }
    ]
    pendingCount.value = data.pending_bookings || 0
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadRecentBookings = async () => {
  recentBookingsLoading.value = true
  try {
    const response = await axios.get('/api/tour/admin/bookings?per_page=5')
    recentBookings.value = response.data.bookings || []
  } catch (error) {
    console.error('Error loading recent bookings:', error)
    recentBookings.value = []  // ✅ Set to empty array on error
  } finally {
    recentBookingsLoading.value = false
  }
}

const loadUpcomingTours = async () => {
  upcomingToursLoading.value = true
  try {
    const response = await axios.get('/api/tour/admin/bookings?status=confirmed&per_page=5')
    upcomingTours.value = response.data.bookings || []
  } catch (error) {
    console.error('Error loading upcoming tours:', error)
    upcomingTours.value = []  // ✅ Set to empty array on error
  } finally {
    upcomingToursLoading.value = false
  }
}

const refreshData = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      loadStats(),
      loadRecentBookings(),
      loadUpcomingTours()
    ])
  } catch (error) {
    console.error('Error refreshing data:', error)
  } finally {
    refreshing.value = false
  }
}

const goToBookings = () => {
  router.push('/tour-manager/bookings')
}

const goToCalendar = () => {
  router.push('/tour-manager/calendar')
}

const goToPackages = () => {
  router.push('/tour-manager/packages')
}

const goToPayments = () => {
  router.push('/tour-manager/payments')
}

const viewBooking = (booking) => {
  selectedBooking.value = booking
}

const closeBookingDetail = () => {
  selectedBooking.value = null
}

const approveBooking = async (booking) => {
  if (!confirm(`Approve booking ${booking.reference}?`)) return
  try {
    await axios.put(`/api/tour/admin/bookings/${booking.id}/status`, {
      status: 'confirmed',
      notes: 'Approved by manager'
    })
    await refreshData()
    closeBookingDetail()
  } catch (error) {
    console.error('Error approving booking:', error)
    alert('Failed to approve booking')
  }
}

const rejectBooking = async (booking) => {
  const reason = prompt('Reason for rejection:')
  if (reason === null) return
  try {
    await axios.put(`/api/tour/admin/bookings/${booking.id}/status`, {
      status: 'rejected',
      notes: `Rejected: ${reason}`
    })
    await refreshData()
    closeBookingDetail()
  } catch (error) {
    console.error('Error rejecting booking:', error)
    alert('Failed to reject booking')
  }
}

const openPaymentModal = (booking) => {
  if (!canProcessPayment(booking)) {
    alert('Cannot process payment for this booking.')
    return
  }
  router.push('/tour-manager/payments')
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return format(new Date(dateStr), 'MMM d, yyyy')
}

const formatFullDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return format(new Date(dateStr), 'EEEE, MMMM d, yyyy at h:mm a')
}

const formatDay = (dateStr) => {
  if (!dateStr) return 'N/A'
  return format(new Date(dateStr), 'dd')
}

const formatMonth = (dateStr) => {
  if (!dateStr) return 'N/A'
  return format(new Date(dateStr), 'MMM')
}

const formatPrice = (amount) => {
  return (amount || 0).toLocaleString('en-KE', { 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  })
}

onMounted(() => {
  user.value = authService.getUser()
  refreshData()
})
</script>


<style scoped>
.tour-manager-dashboard {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============================================
   PAGE HEADER
   ============================================ */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  color: #1e3a8a;
  margin: 0 0 4px;
  font-size: 1.8rem;
}

.page-header h1 i {
  color: #f59e0b;
  margin-right: 12px;
}

.subtitle {
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-refresh {
  padding: 10px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #4b5563;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-refresh:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #1e3a8a;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  padding: 10px 20px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* ============================================
   STATS GRID
   ============================================ */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  flex-shrink: 0;
}

.stat-info h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
}

.stat-info p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

/* ============================================
   QUICK ACTIONS
   ============================================ */
.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 24px;
}

.quick-actions h3 {
  margin: 0 0 16px;
  color: #1f2937;
  font-size: 1.1rem;
}

.quick-actions h3 i {
  color: #f59e0b;
  margin-right: 8px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.action-card {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  border: 1px solid #e5e7eb;
  position: relative;
}

.action-card:hover {
  border-color: #f59e0b;
  background: #fef3c7;
  transform: translateY(-2px);
}

.action-card.highlight {
  background: #fef3c7;
  border-color: #f59e0b;
}

.action-card.highlight:hover {
  background: #fde68a;
}

.action-card i {
  font-size: 24px;
  color: #f59e0b;
  display: block;
  margin-bottom: 8px;
}

.action-card span {
  font-size: 14px;
  color: #1f2937;
}

.pending-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
}

/* ============================================
   DASHBOARD GRID
   ============================================ */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.dashboard-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.card-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}

.card-header h3 i {
  color: #f59e0b;
  margin-right: 8px;
}

.view-all-btn {
  background: none;
  border: none;
  color: #f59e0b;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.85rem;
  transition: color 0.3s;
}

.view-all-btn:hover {
  color: #d97706;
}

.card-body {
  padding: 16px 20px;
  max-height: 400px;
  overflow-y: auto;
}

.card-body::-webkit-scrollbar {
  width: 6px;
}

.card-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.card-body::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

/* ============================================
   BOOKING LIST
   ============================================ */
.booking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  transition: all 0.3s;
  flex-wrap: wrap;
  gap: 8px;
}

.booking-item:hover {
  background: #f1f5f9;
}

.booking-info {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.booking-ref {
  font-weight: 600;
  color: #1e3a8a;
  font-size: 13px;
}

.booking-customer {
  color: #1f2937;
  font-size: 13px;
}

.booking-date {
  color: #6b7280;
  font-size: 12px;
}

.booking-status-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-view {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-view:hover {
  background: #e5e7eb;
  color: #1e3a8a;
}

/* ============================================
   TOUR LIST
   ============================================ */
.tour-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tour-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  transition: all 0.3s;
}

.tour-item:hover {
  background: #f1f5f9;
}

.tour-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #e0e7ff;
  border-radius: 8px;
  padding: 4px 10px;
  min-width: 44px;
}

.tour-date .day {
  font-size: 18px;
  font-weight: 700;
  color: #1e3a8a;
  line-height: 1.2;
}

.tour-date .month {
  font-size: 10px;
  color: #1e3a8a;
  text-transform: uppercase;
  font-weight: 600;
}

.tour-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tour-ref {
  font-weight: 600;
  color: #1e3a8a;
  font-size: 13px;
}

.tour-package {
  color: #4b5563;
  font-size: 12px;
}

.tour-people {
  color: #6b7280;
  font-size: 12px;
}

.tour-people i {
  margin-right: 4px;
}

/* ============================================
   STATUS BADGES
   ============================================ */
.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
  display: inline-block;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.confirmed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.completed {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.commitment_pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.cleared {
  background: #dbeafe;
  color: #1e40af;
}

/* ============================================
   LOADING & EMPTY STATES
   ============================================ */
.loading-state {
  text-align: center;
  padding: 30px 0;
  color: #6b7280;
}

.loading-spinner.small {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 2px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 30px 0;
  color: #6b7280;
}

.empty-state i {
  font-size: 32px;
  opacity: 0.3;
  display: block;
  margin-bottom: 8px;
}

.empty-state p {
  margin: 0;
}

/* ============================================
   BOOKING DETAIL MODAL
   ============================================ */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 0;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(0,0,0,0.1);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #ef4444;
  color: white;
}

.booking-detail-content {
  padding: 24px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.detail-header h2 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1.3rem;
}

.detail-header h2 i {
  color: #f59e0b;
  margin-right: 8px;
}

.booking-ref-large {
  font-weight: 700;
  color: #6b7280;
  font-size: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.detail-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
}

.detail-section h4 {
  color: #1e3a8a;
  margin: 0 0 12px;
  font-size: 0.9rem;
}

.detail-section h4 i {
  color: #f59e0b;
  margin-right: 8px;
}

.detail-section p {
  margin: 4px 0;
  font-size: 0.9rem;
  color: #4b5563;
}

.detail-section p strong {
  color: #1f2937;
}

.group-name {
  margin-top: 8px !important;
  color: #f59e0b !important;
}

.detail-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 2px solid #e5e7eb;
  flex-wrap: wrap;
}

.detail-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-approve {
  background: #10b981;
  color: white;
}

.btn-approve:hover {
  background: #059669;
}

.btn-reject {
  background: #ef4444;
  color: white;
}

.btn-reject:hover {
  background: #dc2626;
}

.btn-close-detail {
  background: #f3f4f6;
  color: #4b5563;
  margin-left: auto;
}

.btn-close-detail:hover {
  background: #e5e7eb;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .header-actions button {
    flex: 1;
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 12px 16px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .stat-info h3 {
    font-size: 18px;
  }
  
  .action-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .booking-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .booking-info {
    flex-wrap: wrap;
  }
  
  .tour-item {
    flex-wrap: wrap;
  }
  
  .detail-actions {
    flex-direction: column;
  }
  
  .btn-close-detail {
    margin-left: 0;
  }
  
  .modal-container {
    max-width: 100%;
    margin: 10px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-direction: column;
  }
}
</style>