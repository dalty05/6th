<template>
  <div class="tour-manager-bookings">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1><i class="fas fa-ticket-alt"></i> Tour Bookings</h1>
        <p class="subtitle">Manage all factory tour bookings</p>
      </div>
      <div class="header-actions">
        <button @click="exportBookings" class="btn-export">
          <i class="fas fa-file-export"></i> Export
        </button>
        <button @click="refreshData" class="btn-refresh" :disabled="loading">
          <i :class="loading ? 'fas fa-spinner fa-spin' : 'fas fa-sync-alt'"></i>
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Stats Summary -->
    <div class="stats-summary">
      <div class="stat-chip" v-for="stat in statusStats" :key="stat.status">
        <span class="chip-label">{{ stat.label }}</span>
        <span class="chip-value" :class="stat.status">{{ stat.count }}</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <div class="filter-input">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="Search by reference, customer, email..."
            @input="applyFilters"
          >
        </div>
      </div>
      <div class="filter-group">
        <select v-model="filters.status" class="filter-select" @change="applyFilters">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="confirmed">Confirmed</option>
          <option value="commitment_pending">Commitment Pending</option>
          <option value="cleared">Cleared</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>
      <div class="filter-group">
        <select v-model="filters.package_id" class="filter-select" @change="applyFilters">
          <option value="">All Packages</option>
          <option v-for="pkg in packages" :key="pkg.id" :value="pkg.id">
            {{ pkg.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <input type="date" v-model="filters.date_from" class="filter-date" @change="applyFilters" placeholder="From">
      </div>
      <div class="filter-group">
        <input type="date" v-model="filters.date_to" class="filter-date" @change="applyFilters" placeholder="To">
      </div>
      <button @click="clearFilters" class="btn-clear-filters">
        <i class="fas fa-undo"></i> Clear
      </button>
    </div>

    <!-- Bookings Table -->
    <div class="table-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading bookings...</p>
      </div>

      <div v-else-if="bookings.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <h3>No Bookings Found</h3>
        <p>Try adjusting your filters or check back later</p>
        <button @click="clearFilters" class="btn-primary small">Clear Filters</button>
      </div>

      <div v-else class="table-wrapper">
        <table class="bookings-table">
          <thead>
            <tr>
              <th style="width: 40px;">
                <input type="checkbox" v-model="selectAll" @change="toggleSelectAll">
              </th>
              <th>Reference</th>
              <th>Customer</th>
              <th>Package</th>
              <th>Date</th>
              <th>People</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Payment</th>
              <th style="width: 140px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in paginatedBookings" :key="booking.id">
              <td>
                <input type="checkbox" v-model="selectedBookings" :value="booking.id">
              </td>
              <td>
                <span class="ref-code">{{ booking.reference }}</span>
              </td>
              <td>
                <div class="customer-info">
                  <span class="customer-name">{{ booking.customer_name }}</span>
                  <span class="customer-email">{{ booking.customer_email }}</span>
                </div>
              </td>
              <td>{{ booking.package?.name || 'N/A' }}</td>
              <td>{{ formatDate(booking.tour_date) }}</td>
              <td>{{ booking.people_count }}</td>
              <td class="amount">KES {{ formatPrice(booking.total_amount) }}</td>
              <td>
                <span class="status-badge" :class="booking.status">
                  {{ formatStatus(booking.status) }}
                </span>
              </td>
              <td>
                <span class="payment-badge" :class="booking.payment_status">
                  {{ formatPaymentStatus(booking.payment_status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="viewBooking(booking)" class="btn-action view" title="View Details">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    v-if="booking.status === 'pending'" 
                    @click="approveBooking(booking)" 
                    class="btn-action approve"
                    title="Approve"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  <button 
                    v-if="booking.status === 'pending'" 
                    @click="rejectBooking(booking)" 
                    class="btn-action reject"
                    title="Reject"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                  <button 
                    v-if="canProcessPayment(booking)" 
                    @click="openPaymentModal(booking)" 
                    class="btn-action payment"
                    title="Process Payment"
                  >
                    <i class="fas fa-money-bill-wave"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="bookings.length > 0" class="pagination">
        <div class="pagination-info">
          Showing {{ (currentPage - 1) * perPage + 1 }} to 
          {{ Math.min(currentPage * perPage, filteredBookings.length) }} of 
          {{ filteredBookings.length }} bookings
        </div>
        <div class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Booking Detail Modal -->
    <div v-if="selectedBooking" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-container booking-detail-modal">
        <button class="modal-close" @click="closeDetailModal">
          <i class="fas fa-times"></i>
        </button>
        <BookingDetail 
          :booking="selectedBooking" 
          @close="closeDetailModal"
          @updated="handleBookingUpdated"
          @payment="openPaymentModal"
        />
      </div>
    </div>

    <!-- Payment Modal -->
    <div v-if="paymentBooking" class="modal-overlay" @click.self="paymentBooking = null">
      <div class="modal-container payment-modal">
        <button class="modal-close" @click="paymentBooking = null">
          <i class="fas fa-times"></i>
        </button>
        <PaymentForm 
          :booking="paymentBooking" 
          @confirmed="handlePaymentConfirmed"
          @close="paymentBooking = null"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import BookingDetail from '@/components/tours/BookingDetail.vue'
import PaymentForm from '@/components/tours/PaymentForm.vue'

// ============================================================
// STATE - INITIALIZE ALL REACTIVE REFS
// ============================================================
const bookings = ref([])
const packages = ref([])
const loading = ref(false)
const currentPage = ref(1)
const perPage = ref(10)
const selectedBookings = ref([])
const selectAll = ref(false)
const selectedBooking = ref(null)
const paymentBooking = ref(null)

// ✅ Initialize filters with default values
const filters = ref({
  search: '',
  status: '',
  package_id: '',
  date_from: '',
  date_to: ''
})

// ============================================================
// COMPUTED
// ============================================================
const filteredBookings = computed(() => {
  let result = bookings.value || []
  
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    result = result.filter(b => 
      b.reference?.toLowerCase().includes(query) ||
      b.customer_name?.toLowerCase().includes(query) ||
      b.customer_email?.toLowerCase().includes(query)
    )
  }
  
  if (filters.value.status) {
    result = result.filter(b => b.status === filters.value.status)
  }
  
  if (filters.value.package_id) {
    result = result.filter(b => b.package_id === parseInt(filters.value.package_id))
  }
  
  if (filters.value.date_from) {
    result = result.filter(b => b.tour_date && new Date(b.tour_date) >= new Date(filters.value.date_from))
  }
  if (filters.value.date_to) {
    result = result.filter(b => b.tour_date && new Date(b.tour_date) <= new Date(filters.value.date_to))
  }
  
  return result
})

const paginatedBookings = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredBookings.value.slice(start, start + perPage.value)
})

const totalPages = computed(() => {
  return Math.ceil(filteredBookings.value.length / perPage.value)
})

const statusStats = computed(() => {
  const stats = [
    { status: 'all', label: 'All', count: bookings.value.length },
    { status: 'pending', label: 'Pending', count: bookings.value.filter(b => b.status === 'pending').length },
    { status: 'confirmed', label: 'Confirmed', count: bookings.value.filter(b => b.status === 'confirmed').length },
    { status: 'completed', label: 'Completed', count: bookings.value.filter(b => b.status === 'completed').length },
    { status: 'rejected', label: 'Rejected', count: bookings.value.filter(b => b.status === 'rejected').length }
  ]
  return stats
})

// ============================================================
// METHODS
// ============================================================
const canProcessPayment = (booking) => {
  if (!booking) return false
  if (booking.status === 'rejected' || booking.status === 'cancelled') {
    return false
  }
  return booking.status === 'confirmed' || 
         booking.status === 'commitment_pending' ||
         booking.status === 'cleared'
}

const loadBookings = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.package_id) params.package_id = filters.value.package_id
    
    const response = await axios.get('/api/tour/admin/bookings', { params })
    bookings.value = response.data.bookings || []
  } catch (error) {
    console.error('Error loading bookings:', error)
    bookings.value = []
    alert('Failed to load bookings')
  } finally {
    loading.value = false
  }
}

const loadPackages = async () => {
  try {
    const response = await axios.get('/api/tour/admin/packages')
    packages.value = response.data.packages || []
  } catch (error) {
    console.error('Error loading packages:', error)
    packages.value = []
  }
}

const refreshData = () => {
  loadBookings()
}

const applyFilters = () => {
  currentPage.value = 1
  loadBookings()
}

const clearFilters = () => {
  filters.value = {
    search: '',
    status: '',
    package_id: '',
    date_from: '',
    date_to: ''
  }
  selectedBookings.value = []
  selectAll.value = false
  applyFilters()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedBookings.value = paginatedBookings.value.map(b => b.id)
  } else {
    selectedBookings.value = []
  }
}

const viewBooking = (booking) => {
  selectedBooking.value = booking
}

const closeDetailModal = () => {
  selectedBooking.value = null
}

const handleBookingUpdated = () => {
  loadBookings()
}

const approveBooking = async (booking) => {
  if (!confirm(`Approve booking ${booking.reference}?`)) return
  try {
    await axios.put(`/api/tour/admin/bookings/${booking.id}/status`, {
      status: 'confirmed',
      notes: 'Approved by manager'
    })
    await loadBookings()
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
    await loadBookings()
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
  paymentBooking.value = booking
}

const handlePaymentConfirmed = () => {
  paymentBooking.value = null
  loadBookings()
}

const exportBookings = () => {
  if (filteredBookings.value.length === 0) {
    alert('No bookings to export')
    return
  }
  
  const headers = ['Reference', 'Customer', 'Email', 'Phone', 'Package', 'Date', 'People', 'Amount', 'Status', 'Payment Status']
  const rows = filteredBookings.value.map(b => [
    b.reference,
    b.customer_name,
    b.customer_email,
    b.customer_phone,
    b.package?.name || 'N/A',
    formatDate(b.tour_date),
    b.people_count,
    b.total_amount,
    b.status,
    b.payment_status
  ])
  
  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `bookings_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-KE', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPrice = (amount) => {
  return (amount || 0).toLocaleString('en-KE', { 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  })
}

const formatStatus = (status) => {
  const map = {
    pending: 'Pending',
    confirmed: 'Confirmed',
    commitment_pending: 'Commitment Pending',
    cleared: 'Cleared',
    completed: 'Completed',
    cancelled: 'Cancelled',
    rejected: 'Rejected'
  }
  return map[status] || status
}

const formatPaymentStatus = (status) => {
  const map = {
    pending: 'Pending',
    commitment_paid: 'Commitment Paid',
    fully_paid: 'Fully Paid'
  }
  return map[status] || status
}

// ============================================================
// WATCHERS
// ============================================================
watch(() => filters.value, () => {
  applyFilters()
}, { deep: true })

// ============================================================
// LIFECYCLE
// ============================================================
onMounted(() => {
  loadBookings()
  loadPackages()
})
</script>




<style scoped>
.tour-manager-bookings {
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
  margin-bottom: 20px;
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

.btn-export {
  padding: 10px 20px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-export:hover {
  background: #059669;
  transform: translateY(-2px);
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

/* ============================================
   STATS SUMMARY
   ============================================ */
.stats-summary {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-chip {
  background: white;
  border-radius: 8px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  border: 1px solid #e5e7eb;
}

.chip-label {
  font-size: 13px;
  color: #6b7280;
}

.chip-value {
  font-weight: 700;
  font-size: 16px;
}

.chip-value.pending { color: #f59e0b; }
.chip-value.confirmed { color: #10b981; }
.chip-value.completed { color: #3b82f6; }

/* ============================================
   FILTERS
   ============================================ */
.filters-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  align-items: center;
}

.filter-group {
  flex: 1;
  min-width: 140px;
}

.filter-input {
  position: relative;
}

.filter-input i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.filter-input input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.filter-input input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.filter-select,
.filter-date {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: all 0.3s;
}

.filter-select:focus,
.filter-date:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.btn-clear-filters {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #4b5563;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-clear-filters:hover {
  background: #e5e7eb;
}

/* ============================================
   TABLE
   ============================================ */
.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.bookings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.bookings-table thead {
  background: #f8fafc;
}

.bookings-table th {
  text-align: left;
  padding: 12px 16px;
  color: #4b5563;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
  white-space: nowrap;
}

.bookings-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.bookings-table tbody tr:hover td {
  background: #f8fafc;
}

/* Customer Info */
.customer-info {
  display: flex;
  flex-direction: column;
}

.customer-name {
  font-weight: 500;
  color: #1f2937;
}

.customer-email {
  font-size: 12px;
  color: #6b7280;
}

/* Reference Code */
.ref-code {
  font-weight: 600;
  color: #1e3a8a;
  font-size: 13px;
}

/* Amount */
.amount {
  font-weight: 600;
  color: #1f2937;
}

/* Status Badges */
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

.status-badge.commitment_pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.cleared {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
}

/* Payment Badges */
.payment-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  text-transform: capitalize;
  display: inline-block;
}

.payment-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.payment-badge.commitment_paid {
  background: #dbeafe;
  color: #1e40af;
}

.payment-badge.fully_paid {
  background: #d1fae5;
  color: #065f46;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 4px;
}

.btn-action {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action:hover {
  transform: scale(1.1);
}

.btn-action.view {
  background: #dbeafe;
  color: #1e40af;
}

.btn-action.approve {
  background: #d1fae5;
  color: #065f46;
}

.btn-action.reject {
  background: #fee2e2;
  color: #991b1b;
}

.btn-action.payment {
  background: #fef3c7;
  color: #92400e;
}

/* ============================================
   PAGINATION
   ============================================ */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  flex-wrap: wrap;
  gap: 12px;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #f59e0b;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #4b5563;
}

/* ============================================
   LOADING & EMPTY STATES
   ============================================ */
.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-state i {
  font-size: 48px;
  opacity: 0.3;
  display: block;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #1f2937;
  margin: 0 0 8px;
}

.empty-state p {
  margin: 0 0 16px;
}

.btn-primary.small {
  padding: 8px 20px;
  font-size: 14px;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #d97706;
}

/* ============================================
   MODALS
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
  max-width: 800px;
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

.booking-detail-modal,
.payment-modal {
  padding: 0;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .filters-section {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: 100%;
  }
  
  .btn-clear-filters {
    width: 100%;
    justify-content: center;
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
  
  .stats-summary {
    gap: 8px;
  }
  
  .stat-chip {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  .bookings-table {
    font-size: 12px;
  }
  
  .bookings-table th,
  .bookings-table td {
    padding: 8px 10px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
  
  .pagination {
    flex-direction: column;
    align-items: center;
  }
  
  .modal-container {
    max-width: 100%;
    margin: 10px;
  }
}

@media (max-width: 480px) {
  .stat-chip {
    flex: 1;
    justify-content: center;
  }
  
  .bookings-table {
    font-size: 11px;
  }
  
  .bookings-table th,
  .bookings-table td {
    padding: 6px 8px;
  }
}
</style>