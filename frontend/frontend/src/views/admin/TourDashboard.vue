<template>
  <div class="tour-dashboard">
    <div class="page-header">
      <div>
        <h1><i class="fas fa-factory"></i> Tour Management</h1>
        <p class="subtitle">Manage factory tour bookings, packages, and availability</p>
      </div>
      <div class="header-actions">
        <button @click="showBookingModal = true" class="btn-primary">
          <i class="fas fa-plus"></i> New Booking
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
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

    <!-- ✅ Tabs - Using the prop to determine active tab -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-btn"
        :class="{ active: internalActiveTab === tab.key }"
        @click="switchTab(tab.key)"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
        <span v-if="tab.badge" class="badge">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Bookings Tab -->
      <div v-if="internalActiveTab === 'tours'" class="bookings-tab">
        <div class="filters">
          <div class="filter-group">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search by reference or customer..."
              class="search-input"
              @input="applyFilters"
            >
          </div>
          <div class="filter-group">
            <select v-model="statusFilter" class="filter-select" @change="applyFilters">
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
            <select v-model="packageFilter" class="filter-select" @change="applyFilters">
              <option value="">All Packages</option>
              <option v-for="pkg in packages" :key="pkg.id" :value="pkg.id">
                {{ pkg.name }}
              </option>
            </select>
          </div>
          <button @click="loadBookings" class="btn-filter">
            <i class="fas fa-search"></i> Filter
          </button>
          <button @click="resetFilters" class="btn-reset">
            <i class="fas fa-undo"></i>
          </button>
        </div>

        <div class="bookings-table-wrapper">
          <table class="bookings-table">
            <thead>
              <tr>
                <th>Reference</th>
                <th>Customer</th>
                <th>Package</th>
                <th>Date</th>
                <th>People</th>
                <th>Total</th>
                <th>Status</th>
                <th>Payment</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="bookingsLoading">
                <td colspan="9" class="text-center">
                  <div class="loading-spinner"></div>
                </td>
              </tr>
              <tr v-else-if="filteredBookings.length === 0">
                <td colspan="9" class="text-center no-data">
                  <i class="fas fa-inbox"></i>
                  <p>No bookings found</p>
                </td>
              </tr>
              <tr v-for="booking in paginatedBookings" :key="booking.id">
                <td><span class="ref-code">{{ booking.reference }}</span></td>
                <td>
                  <div class="customer-info">
                    <strong>{{ booking.customer_name }}</strong>
                    <span>{{ booking.customer_email }}</span>
                  </div>
                </td>
                <td>{{ booking.package?.name || 'N/A' }}</td>
                <td>{{ formatDate(booking.tour_date) }}</td>
                <td>{{ booking.people_count }}</td>
                <td>KES {{ formatPrice(booking.total_amount) }}</td>
                <td>
                  <span class="status-badge" :class="booking.status">
                    {{ booking.status }}
                  </span>
                </td>
                <td>
                  <span class="payment-badge" :class="booking.payment_status">
                    {{ booking.payment_status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="viewBooking(booking)" class="btn-action view" title="View">
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
        <div class="pagination" v-if="totalPages > 1">
          <button @click="currentPage--" :disabled="currentPage === 1">
            <i class="fas fa-chevron-left"></i>
          </button>
          <span>Page {{ currentPage }} of {{ totalPages }}</span>
          <button @click="currentPage++" :disabled="currentPage === totalPages">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <!-- Calendar Tab -->
      <div v-if="internalActiveTab === 'tour-calendar'" class="calendar-tab">
        <div class="calendar-placeholder">
          <i class="fas fa-calendar-alt"></i>
          <h3>Calendar View</h3>
          <p>Interactive calendar for tour availability</p>
          <p style="font-size: 13px; color: #6b7280; margin-top: 8px;">
            Select a package from the Packages tab first
          </p>
        </div>
      </div>

      <!-- Packages Tab -->
      <div v-if="internalActiveTab === 'tour-packages'" class="packages-tab">
        <div class="packages-header">
          <h3>Tour Packages</h3>
          <button @click="showPackageModal = true" class="btn-primary">
            <i class="fas fa-plus"></i> New Package
          </button>
        </div>
        <div class="packages-grid">
          <div v-for="pkg in packages" :key="pkg.id" class="package-card">
            <div class="package-image">
              <img :src="pkg.image_url || '/images/tour-placeholder.jpg'" :alt="pkg.name">
              <div class="package-status" :class="{ active: pkg.is_active }">
                {{ pkg.is_active ? 'Active' : 'Inactive' }}
              </div>
            </div>
            <div class="package-info">
              <h4>{{ pkg.name }}</h4>
              <p>{{ pkg.short_description || pkg.description?.substring(0, 60) + '...' }}</p>
              <div class="package-meta">
                <span><i class="fas fa-users"></i> {{ pkg.min_people }}-{{ pkg.max_people }}</span>
                <span><i class="fas fa-clock"></i> {{ pkg.duration_hours }}h</span>
                <span><i class="fas fa-tag"></i> KES {{ formatPrice(pkg.base_price) }}</span>
              </div>
              <div class="package-actions">
                <button @click="editPackage(pkg)" class="btn-edit">
                  <i class="fas fa-edit"></i>
                </button>
                <button @click="togglePackageStatus(pkg)" class="btn-toggle">
                  <i :class="pkg.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
                <button @click="deletePackage(pkg)" class="btn-delete">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Detail Modal -->
    <div v-if="selectedBooking" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container booking-detail-modal">
        <button class="modal-close" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
        <div class="booking-detail-content">
          <div class="detail-header">
            <h2><i class="fas fa-ticket-alt"></i> Booking Details</h2>
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
              <p><strong>Total:</strong> KES {{ formatPrice(selectedBooking.total_amount) }}</p>
            </div>
          </div>
          <div class="detail-actions">
            <button v-if="selectedBooking.status === 'pending'" @click="approveBooking(selectedBooking)" class="btn-approve">
              <i class="fas fa-check"></i> Approve
            </button>
            <button v-if="selectedBooking.status === 'pending'" @click="rejectBooking(selectedBooking)" class="btn-reject">
              <i class="fas fa-times"></i> Reject
            </button>
            <button @click="closeModal" class="btn-close-detail">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <div v-if="paymentBooking" class="modal-overlay" @click.self="paymentBooking = null">
      <div class="modal-container payment-modal">
        <button class="modal-close" @click="paymentBooking = null">
          <i class="fas fa-times"></i>
        </button>
        <div class="payment-content">
          <h3>Process Payment</h3>
          <p>Booking: <strong>{{ paymentBooking.reference }}</strong></p>
          <p>Total: KES {{ formatPrice(paymentBooking.total_amount) }}</p>
          <p>Commitment: KES {{ formatPrice(paymentBooking.commitment_amount) }}</p>
          <div class="payment-actions">
            <button @click="confirmPayment('commitment')" class="btn-payment-commitment">
              Pay Commitment (30%)
            </button>
            <button @click="confirmPayment('full')" class="btn-payment-full">
              Pay Full Amount
            </button>
            <button @click="paymentBooking = null" class="btn-cancel">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TourDashboard',
  props: {
    activeTab: {
      type: String,
      default: 'tours'
    }
  },
  emits: ['update:activeTab'],
  data() {
    return {
      // ✅ Use the prop to initialize internal tab
      internalActiveTab: this.activeTab,
      bookings: [],
      packages: [],
      loading: false,
      bookingsLoading: false,
      currentPage: 1,
      perPage: 10,
      searchQuery: '',
      statusFilter: '',
      packageFilter: '',
      selectedBooking: null,
      paymentBooking: null,
      showBookingModal: false,
      showPackageModal: false,
      editingPackage: null,
      tabs: [
        { key: 'tours', label: 'Bookings', icon: 'fas fa-list' },
        { key: 'tour-calendar', label: 'Calendar', icon: 'fas fa-calendar-alt' },
        { key: 'tour-packages', label: 'Packages', icon: 'fas fa-tag' }
      ]
    }
  },
  computed: {
    filteredBookings() {
      let result = this.bookings
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(b => 
          b.reference?.toLowerCase().includes(query) ||
          b.customer_name?.toLowerCase().includes(query) ||
          b.customer_email?.toLowerCase().includes(query)
        )
      }
      
      if (this.statusFilter) {
        result = result.filter(b => b.status === this.statusFilter)
      }
      
      if (this.packageFilter) {
        result = result.filter(b => b.package_id === parseInt(this.packageFilter))
      }
      
      return result
    },
    paginatedBookings() {
      const start = (this.currentPage - 1) * this.perPage
      return this.filteredBookings.slice(start, start + this.perPage)
    },
    totalPages() {
      return Math.ceil(this.filteredBookings.length / this.perPage)
    },
    stats() {
      const total = this.bookings.length
      const pending = this.bookings.filter(b => b.status === 'pending').length
      const confirmed = this.bookings.filter(b => b.status === 'confirmed').length
      const completed = this.bookings.filter(b => b.status === 'completed').length
      const revenue = this.bookings
        .filter(b => b.status === 'completed')
        .reduce((sum, b) => sum + b.total_amount, 0)
      
      return [
        { label: 'Total Bookings', value: total, icon: 'fas fa-calendar-check', color: '#3b82f6' },
        { label: 'Pending', value: pending, icon: 'fas fa-clock', color: '#f59e0b' },
        { label: 'Confirmed', value: confirmed, icon: 'fas fa-check-circle', color: '#10b981' },
        { label: 'Revenue', value: `KES ${revenue.toLocaleString()}`, icon: 'fas fa-money-bill-wave', color: '#8b5cf6' }
      ]
    }
  },
  watch: {
    // ✅ Watch for prop changes from parent
    activeTab(newVal) {
      this.internalActiveTab = newVal
      // Refresh data when switching tabs
      if (newVal === 'tours') {
        this.loadBookings()
      }
    }
  },
  methods: {
    canProcessPayment(booking) {
      if (!booking) return false
      if (booking.status === 'rejected' || booking.status === 'cancelled') return false
      return booking.status === 'confirmed' || 
             booking.status === 'commitment_pending' ||
             booking.status === 'cleared'
    },
    switchTab(tab) {
      this.internalActiveTab = tab
      // ✅ Emit to parent so URL updates
      this.$emit('update:activeTab', tab)
      
      // Load data based on tab
      if (tab === 'tours') {
        this.loadBookings()
      } else if (tab === 'tour-packages') {
        this.loadPackages()
      }
    },
    applyFilters() {
      this.currentPage = 1
      this.loadBookings()
    },
    async loadBookings() {
      this.bookingsLoading = true
      try {
        const params = {}
        if (this.statusFilter) params.status = this.statusFilter
        if (this.packageFilter) params.package_id = this.packageFilter
        
        const response = await axios.get('/api/tour/admin/bookings', { params })
        this.bookings = response.data.bookings || []
      } catch (error) {
        console.error('Error loading bookings:', error)
      } finally {
        this.bookingsLoading = false
      }
    },
    async loadPackages() {
      try {
        const response = await axios.get('/api/tour/admin/packages')
        this.packages = response.data.packages || []
      } catch (error) {
        console.error('Error loading packages:', error)
      }
    },
    resetFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.packageFilter = ''
      this.currentPage = 1
      this.loadBookings()
    },
    viewBooking(booking) {
      this.selectedBooking = booking
    },
    closeModal() {
      this.selectedBooking = null
      this.paymentBooking = null
    },
    async approveBooking(booking) {
      if (!confirm(`Approve booking ${booking.reference}?`)) return
      try {
        await axios.put(`/api/tour/admin/bookings/${booking.id}/status`, {
          status: 'confirmed',
          notes: 'Approved by admin'
        })
        await this.loadBookings()
        this.closeModal()
      } catch (error) {
        console.error('Error approving booking:', error)
        alert('Failed to approve booking')
      }
    },
    async rejectBooking(booking) {
      const reason = prompt('Reason for rejection:')
      if (reason === null) return
      try {
        await axios.put(`/api/tour/admin/bookings/${booking.id}/status`, {
          status: 'rejected',
          notes: `Rejected: ${reason}`
        })
        await this.loadBookings()
        this.closeModal()
      } catch (error) {
        console.error('Error rejecting booking:', error)
        alert('Failed to reject booking')
      }
    },
    openPaymentModal(booking) {
      if (!this.canProcessPayment(booking)) {
        alert('Cannot process payment for this booking.')
        return
      }
      this.paymentBooking = booking
    },
    async confirmPayment(type) {
      if (!this.paymentBooking) return
      
      const amount = type === 'commitment' 
        ? this.paymentBooking.commitment_amount 
        : this.paymentBooking.total_amount
      
      if (!confirm(`Confirm ${type} payment of KES ${this.formatPrice(amount)} for ${this.paymentBooking.reference}?`)) return
      
      try {
        await axios.put(`/api/tour/admin/bookings/${this.paymentBooking.id}/payment`, {
          amount: amount,
          payment_type: type,
          payment_method: 'manual'
        })
        await this.loadBookings()
        this.closeModal()
        alert('Payment confirmed successfully!')
      } catch (error) {
        console.error('Error processing payment:', error)
        alert('Failed to process payment')
      }
    },
    editPackage(pkg) {
      alert(`📦 Edit Package: ${pkg.name}\n\nPrice: KES ${this.formatPrice(pkg.base_price)}\nCommitment: ${pkg.commitment_percentage || 30}%\nMin People: ${pkg.min_people}\nMax People: ${pkg.max_people}`)
    },
    async togglePackageStatus(pkg) {
      try {
        await axios.put(`/api/tour/admin/packages/${pkg.id}`, {
          is_active: !pkg.is_active
        })
        await this.loadPackages()
      } catch (error) {
        console.error('Error toggling package status:', error)
        alert('Failed to update package status')
      }
    },
    async deletePackage(pkg) {
      if (!confirm(`Delete package "${pkg.name}"?`)) return
      try {
        await axios.delete(`/api/tour/admin/packages/${pkg.id}`)
        await this.loadPackages()
      } catch (error) {
        console.error('Error deleting package:', error)
        alert('Failed to delete package')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-KE', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatPrice(amount) {
      return (amount || 0).toLocaleString('en-KE', { 
        minimumFractionDigits: 0, 
        maximumFractionDigits: 0 
      })
    }
  },
  mounted() {
    // ✅ Load data based on initial tab
    if (this.activeTab === 'tours') {
      this.loadBookings()
    }
    this.loadPackages()
  }
}
</script>



<style scoped>







.tour-dashboard {
  padding: 0;
}

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
  margin: 0;
}

.page-header h1 i {
  color: #f59e0b;
  margin-right: 12px;
}

.subtitle {
  color: #6b7280;
  margin: 4px 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 10px 20px;
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
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
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
  font-size: 20px;
  color: #1f2937;
}

.stat-info p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.tabs {
  display: flex;
  gap: 4px;
  background: #f3f4f6;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 24px;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  background: transparent;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-btn:hover {
  background: rgba(255,255,255,0.5);
}

.tab-btn.active {
  background: white;
  color: #1e3a8a;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 150px;
}

.search-input,
.filter-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.btn-filter {
  padding: 8px 16px;
  background: #1e3a8a;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-filter:hover {
  background: #1e40af;
}

.btn-reset {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: #6b7280;
}

.btn-reset:hover {
  background: #e5e7eb;
}

.bookings-table-wrapper {
  overflow-x: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.bookings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.bookings-table th {
  text-align: left;
  padding: 12px 16px;
  background: #f8fafc;
  color: #4b5563;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}

.bookings-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.bookings-table tr:hover td {
  background: #f8fafc;
}

.ref-code {
  font-weight: 600;
  color: #1e3a8a;
  font-size: 13px;
}

.customer-info {
  display: flex;
  flex-direction: column;
}

.customer-info strong {
  font-size: 13px;
}

.customer-info span {
  font-size: 12px;
  color: #6b7280;
}

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

.btn-action:hover {
  transform: scale(1.1);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:hover:not(:disabled) {
  background: #f3f4f6;
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.package-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.package-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.package-image {
  height: 160px;
  position: relative;
  overflow: hidden;
}

.package-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.package-status {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.package-status.active {
  background: #d1fae5;
  color: #065f46;
}

.package-status:not(.active) {
  background: #fee2e2;
  color: #991b1b;
}

.package-info {
  padding: 16px;
}

.package-info h4 {
  margin: 0 0 4px;
  color: #1e3a8a;
}

.package-info p {
  color: #6b7280;
  font-size: 13px;
  margin: 0 0 12px;
}

.package-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #4b5563;
  margin-bottom: 12px;
}

.package-meta i {
  color: #f59e0b;
}

.package-actions {
  display: flex;
  gap: 8px;
}

.btn-edit {
  background: #dbeafe;
  color: #1e40af;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-toggle {
  background: #fef3c7;
  color: #92400e;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-delete {
  background: #fee2e2;
  color: #991b1b;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit:hover,
.btn-toggle:hover,
.btn-delete:hover {
  transform: scale(1.05);
}

.calendar-placeholder {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.calendar-placeholder i {
  font-size: 48px;
  color: #f59e0b;
  margin-bottom: 16px;
}

.calendar-placeholder h3 {
  color: #1f2937;
  margin-bottom: 8px;
}

.no-data {
  text-align: center;
  padding: 40px 0 !important;
  color: #6b7280;
}

.no-data i {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.3;
}

.text-center {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.packages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .bookings-table {
    font-size: 12px;
  }
  
  .bookings-table th,
  .bookings-table td {
    padding: 8px 10px;
  }
}
</style>