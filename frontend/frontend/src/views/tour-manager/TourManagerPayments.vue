<template>
  <div class="tour-manager-payments">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1><i class="fas fa-money-bill-wave"></i> Payment Management</h1>
        <p class="subtitle">Process and track tour booking payments</p>
      </div>
      <div class="header-actions">
        <button @click="exportPayments" class="btn-export">
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
      <div class="stat-chip">
        <span class="chip-label">Total Revenue</span>
        <span class="chip-value total">KES {{ formatPrice(totalRevenue) }}</span>
      </div>
      <div class="stat-chip">
        <span class="chip-label">Commitment Paid</span>
        <span class="chip-value commitment">KES {{ formatPrice(commitmentPaid) }}</span>
      </div>
      <div class="stat-chip">
        <span class="chip-label">Fully Paid</span>
        <span class="chip-value paid">{{ fullyPaidCount }}</span>
      </div>
      <div class="stat-chip">
        <span class="chip-label">Pending</span>
        <span class="chip-value pending">{{ pendingPayments }}</span>
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
            placeholder="Search by reference or customer..."
            @input="applyFilters"
          >
        </div>
      </div>
      <div class="filter-group">
        <select v-model="filters.payment_status" class="filter-select" @change="applyFilters">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="commitment_paid">Commitment Paid</option>
          <option value="fully_paid">Fully Paid</option>
        </select>
      </div>
      <div class="filter-group">
        <select v-model="filters.booking_status" class="filter-select" @change="applyFilters">
          <option value="">All Booking Status</option>
          <option value="pending">Pending</option>
          <option value="confirmed">Confirmed</option>
          <option value="commitment_pending">Commitment Pending</option>
          <option value="cleared">Cleared</option>
          <option value="completed">Completed</option>
          <option value="rejected">Rejected</option>
          <option value="cancelled">Cancelled</option>
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

    <!-- Payments Table -->
    <div class="table-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading payments...</p>
      </div>

      <div v-else-if="filteredPayments.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <h3>No Payments Found</h3>
        <p>Try adjusting your filters or check back later</p>
        <button @click="clearFilters" class="btn-primary small">Clear Filters</button>
      </div>

      <div v-else class="table-wrapper">
        <table class="payments-table">
          <thead>
            <tr>
              <th>Booking</th>
              <th>Customer</th>
              <th>Total Amount</th>
              <th>Paid</th>
              <th>Balance</th>
              <th>Payment Status</th>
              <th>Booking Status</th>
              <th style="width: 120px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in paginatedPayments" :key="booking.id">
              <td>
                <span class="ref-code">{{ booking.reference }}</span>
              </td>
              <td>
                <div class="customer-info">
                  <span class="customer-name">{{ booking.customer_name }}</span>
                  <span class="customer-email">{{ booking.customer_email }}</span>
                </div>
              </td>
              <td class="amount">KES {{ formatPrice(booking.total_amount) }}</td>
              <td class="amount paid">
                KES {{ formatPrice(booking.commitment_paid ? booking.commitment_amount : 0) }}
              </td>
              <td class="amount balance">
                KES {{ formatPrice(booking.total_amount - (booking.commitment_paid ? booking.commitment_amount : 0)) }}
              </td>
              <td>
                <span class="payment-badge" :class="booking.payment_status">
                  {{ formatPaymentStatus(booking.payment_status) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="booking.status">
                  {{ formatStatus(booking.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="viewBooking(booking)" class="btn-action view" title="View Details">
                    <i class="fas fa-eye"></i>
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
      <div v-if="filteredPayments.length > 0" class="pagination">
        <div class="pagination-info">
          Showing {{ (currentPage - 1) * perPage + 1 }} to 
          {{ Math.min(currentPage * perPage, filteredPayments.length) }} of 
          {{ filteredPayments.length }} payments
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

    <!-- Payment Detail Modal -->
    <div v-if="selectedBooking" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-container payment-detail-modal">
        <button class="modal-close" @click="closeDetailModal">
          <i class="fas fa-times"></i>
        </button>
        <div class="payment-detail-content">
          <div class="detail-header">
            <h2><i class="fas fa-receipt"></i> Payment Details</h2>
            <span class="booking-ref">{{ selectedBooking.reference }}</span>
          </div>

          <div class="detail-grid">
            <div class="detail-section">
              <h4><i class="fas fa-user"></i> Customer</h4>
              <p><strong>{{ selectedBooking.customer_name }}</strong></p>
              <p>{{ selectedBooking.customer_email }}</p>
              <p>{{ selectedBooking.customer_phone }}</p>
            </div>
            <div class="detail-section">
              <h4><i class="fas fa-info-circle"></i> Tour Details</h4>
              <p><strong>Package:</strong> {{ selectedBooking.package?.name || 'N/A' }}</p>
              <p><strong>Date:</strong> {{ formatDate(selectedBooking.tour_date) }}</p>
              <p><strong>People:</strong> {{ selectedBooking.people_count }}</p>
            </div>
          </div>

          <div class="payment-breakdown">
            <h4><i class="fas fa-calculator"></i> Payment Breakdown</h4>
            <div class="breakdown-row">
              <span>Total Amount</span>
              <span class="amount">KES {{ formatPrice(selectedBooking.total_amount) }}</span>
            </div>
            <div class="breakdown-row">
              <span>Commitment Deposit ({{ getCommitmentPercentage(selectedBooking) }}%)</span>
              <span class="amount">KES {{ formatPrice(selectedBooking.commitment_amount) }}</span>
            </div>
            <div class="breakdown-row paid">
              <span>Amount Paid</span>
              <span class="amount">
                KES {{ formatPrice(selectedBooking.commitment_paid ? selectedBooking.commitment_amount : 0) }}
              </span>
            </div>
            <div class="breakdown-row balance">
              <span>Remaining Balance</span>
              <span class="amount">
                KES {{ formatPrice(selectedBooking.total_amount - (selectedBooking.commitment_paid ? selectedBooking.commitment_amount : 0)) }}
              </span>
            </div>
            <div class="breakdown-row status">
              <span>Payment Status</span>
              <span class="payment-badge" :class="selectedBooking.payment_status">
                {{ formatPaymentStatus(selectedBooking.payment_status) }}
              </span>
            </div>
          </div>

          <div class="payment-actions">
            <button 
              v-if="canProcessPayment(selectedBooking)" 
              @click="openPaymentModal(selectedBooking)" 
              class="btn-process-payment"
            >
              <i class="fas fa-money-bill-wave"></i> Process Payment
            </button>
            <button @click="closeDetailModal" class="btn-close-detail">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Form Modal -->
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
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import PaymentForm from '@/components/tours/PaymentForm.vue'

// ============================================================
// STATE
// ============================================================
const bookings = ref([])
const loading = ref(false)
const currentPage = ref(1)
const perPage = ref(10)
const selectedBooking = ref(null)
const paymentBooking = ref(null)

// Filters
const filters = ref({
  search: '',
  payment_status: '',
  booking_status: '',
  date_from: '',
  date_to: ''
})

// ============================================================
// COMPUTED
// ============================================================
const filteredPayments = computed(() => {
  let result = bookings.value
  
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    result = result.filter(b => 
      b.reference?.toLowerCase().includes(query) ||
      b.customer_name?.toLowerCase().includes(query) ||
      b.customer_email?.toLowerCase().includes(query)
    )
  }
  
  if (filters.value.payment_status) {
    result = result.filter(b => b.payment_status === filters.value.payment_status)
  }
  
  if (filters.value.booking_status) {
    result = result.filter(b => b.status === filters.value.booking_status)
  }
  
  if (filters.value.date_from) {
    result = result.filter(b => b.created_at && new Date(b.created_at) >= new Date(filters.value.date_from))
  }
  if (filters.value.date_to) {
    result = result.filter(b => b.created_at && new Date(b.created_at) <= new Date(filters.value.date_to))
  }
  
  return result
})

const paginatedPayments = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredPayments.value.slice(start, start + perPage.value)
})

const totalPages = computed(() => {
  return Math.ceil(filteredPayments.value.length / perPage.value)
})

const totalRevenue = computed(() => {
  return bookings.value
    .filter(b => b.payment_status === 'fully_paid' || b.status === 'completed')
    .reduce((sum, b) => sum + b.total_amount, 0)
})

const commitmentPaid = computed(() => {
  return bookings.value
    .filter(b => b.commitment_paid)
    .reduce((sum, b) => sum + b.commitment_amount, 0)
})

const fullyPaidCount = computed(() => {
  return bookings.value.filter(b => b.payment_status === 'fully_paid').length
})

const pendingPayments = computed(() => {
  return bookings.value.filter(b => b.payment_status === 'pending' && b.status !== 'rejected' && b.status !== 'cancelled').length
})

// ============================================================
// METHODS
// ============================================================
const canProcessPayment = (booking) => {
  if (booking.status === 'rejected' || booking.status === 'cancelled') {
    return false
  }
  return booking.status === 'confirmed' || 
         booking.status === 'commitment_pending' ||
         booking.status === 'cleared'
}

const getCommitmentPercentage = (booking) => {
  if (booking.package && booking.package.commitment_percentage) {
    return booking.package.commitment_percentage
  }
  if (booking.commitment_amount && booking.total_amount) {
    return Math.round((booking.commitment_amount / booking.total_amount) * 100)
  }
  return 30
}

const loadPayments = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/tour/admin/bookings')
    bookings.value = response.data.bookings || []
  } catch (error) {
    console.error('Error loading payments:', error)
    alert('Failed to load payments')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadPayments()
}

const applyFilters = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  filters.value = {
    search: '',
    payment_status: '',
    booking_status: '',
    date_from: '',
    date_to: ''
  }
  applyFilters()
}

const viewBooking = (booking) => {
  selectedBooking.value = booking
}

const closeDetailModal = () => {
  selectedBooking.value = null
}

const openPaymentModal = (booking) => {
  if (!canProcessPayment(booking)) {
    alert('Cannot process payment for this booking. Booking may be rejected or cancelled.')
    return
  }
  paymentBooking.value = booking
}

const handlePaymentConfirmed = () => {
  paymentBooking.value = null
  loadPayments()
}

const exportPayments = () => {
  if (filteredPayments.value.length === 0) {
    alert('No payments to export')
    return
  }
  
  const headers = ['Reference', 'Customer', 'Email', 'Total Amount', 'Paid', 'Balance', 'Payment Status', 'Booking Status']
  const rows = filteredPayments.value.map(b => [
    b.reference,
    b.customer_name,
    b.customer_email,
    b.total_amount,
    b.commitment_paid ? b.commitment_amount : 0,
    b.total_amount - (b.commitment_paid ? b.commitment_amount : 0),
    b.payment_status,
    b.status
  ])
  
  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `payments_${new Date().toISOString().split('T')[0]}.csv`
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
// LIFECYCLE
// ============================================================
onMounted(() => {
  loadPayments()
})
</script>


<style scoped>
.tour-manager-payments {
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

.chip-value.total { color: #1e3a8a; }
.chip-value.commitment { color: #f59e0b; }
.chip-value.paid { color: #10b981; }
.chip-value.pending { color: #ef4444; }

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

.payments-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.payments-table thead {
  background: #f8fafc;
}

.payments-table th {
  text-align: left;
  padding: 12px 16px;
  color: #4b5563;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
  white-space: nowrap;
}

.payments-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.payments-table tbody tr:hover td {
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

/* Amounts */
.amount {
  font-weight: 600;
  color: #1f2937;
}

.amount.paid {
  color: #10b981;
}

.amount.balance {
  color: #f59e0b;
}

/* Payment Badges */
.payment-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
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

/* ============================================
   PAYMENT DETAIL MODAL
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

.payment-detail-content {
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
  font-size: 1.2rem;
}

.detail-header h2 i {
  color: #f59e0b;
  margin-right: 8px;
}

.booking-ref {
  font-weight: 700;
  color: #6b7280;
  font-size: 0.9rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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

/* Payment Breakdown */
.payment-breakdown {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.payment-breakdown h4 {
  color: #1e3a8a;
  margin: 0 0 12px;
  font-size: 0.9rem;
}

.payment-breakdown h4 i {
  color: #f59e0b;
  margin-right: 8px;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.9rem;
}

.breakdown-row:last-child {
  border-bottom: none;
}

.breakdown-row .amount {
  font-weight: 600;
}

.breakdown-row.paid .amount {
  color: #10b981;
}

.breakdown-row.balance .amount {
  color: #f59e0b;
}

.breakdown-row.status {
  padding-top: 8px;
  margin-top: 4px;
  border-top: 2px solid #e5e7eb;
}

/* Payment Actions */
.payment-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 2px solid #e5e7eb;
  flex-wrap: wrap;
}

.btn-process-payment {
  padding: 10px 24px;
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

.btn-process-payment:hover {
  background: #d97706;
}

.btn-close-detail {
  padding: 10px 24px;
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-close-detail:hover {
  background: #e5e7eb;
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
    flex-wrap: wrap;
  }
  
  .stat-chip {
    flex: 1;
    min-width: calc(50% - 6px);
    justify-content: space-between;
  }
  
  .payments-table {
    font-size: 12px;
  }
  
  .payments-table th,
  .payments-table td {
    padding: 8px 10px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
  
  .pagination {
    flex-direction: column;
    align-items: center;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-container {
    max-width: 100%;
    margin: 10px;
  }
  
  .payment-actions {
    flex-direction: column;
  }
  
  .payment-actions button {
    width: 100%;
    justify-content: center;
  }
}
</style>