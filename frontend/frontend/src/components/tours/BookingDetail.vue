<template>
  <div class="booking-detail">
    <div class="detail-header">
      <div class="header-left">
        <h2><i class="fas fa-ticket-alt"></i> Booking Details</h2>
        <span class="booking-ref">{{ booking.reference }}</span>
      </div>
      <span class="status-badge" :class="booking.status">
        {{ formatStatus(booking.status) }}
      </span>
    </div>

    <div class="detail-grid">
      <!-- Customer Info -->
      <div class="detail-section">
        <h3><i class="fas fa-user"></i> Customer Information</h3>
        <div class="info-row">
          <span class="label">Name</span>
          <span class="value">{{ booking.customer_name }}</span>
        </div>
        <div class="info-row">
          <span class="label">Email</span>
          <span class="value">{{ booking.customer_email }}</span>
        </div>
        <div class="info-row">
          <span class="label">Phone</span>
          <span class="value">{{ booking.customer_phone }}</span>
        </div>
        <div class="info-row" v-if="booking.group_name">
          <span class="label">Group</span>
          <span class="value">{{ booking.group_name }}</span>
        </div>
      </div>

      <!-- Tour Info -->
      <div class="detail-section">
        <h3><i class="fas fa-info-circle"></i> Tour Information</h3>
        <div class="info-row">
          <span class="label">Package</span>
          <span class="value">{{ booking.package?.name || 'N/A' }}</span>
        </div>
        <div class="info-row">
          <span class="label">Date</span>
          <span class="value">{{ formatDate(booking.tour_date) }}</span>
        </div>
        <div class="info-row">
          <span class="label">People</span>
          <span class="value">{{ booking.people_count }}</span>
        </div>
        <div class="info-row" v-if="booking.special_requirements">
          <span class="label">Special Requirements</span>
          <span class="value">{{ booking.special_requirements }}</span>
        </div>
      </div>

      <!-- Pricing -->
      <div class="detail-section">
        <h3><i class="fas fa-money-bill-wave"></i> Pricing</h3>
        <div class="info-row">
          <span class="label">Price per Person</span>
          <span class="value">KES {{ formatPrice(booking.price_per_person) }}</span>
        </div>
        <div class="info-row">
          <span class="label">Subtotal</span>
          <span class="value">KES {{ formatPrice(booking.subtotal) }}</span>
        </div>
        <div class="info-row" v-if="booking.discount_applied > 0">
          <span class="label">Discount</span>
          <span class="value discount">- KES {{ formatPrice(booking.discount_applied) }}</span>
        </div>
        <div class="info-row total">
          <span class="label">Total</span>
          <span class="value">KES {{ formatPrice(booking.total_amount) }}</span>
        </div>
        <div class="info-row">
          <span class="label">Payment Status</span>
          <span class="payment-badge" :class="booking.payment_status">
            {{ formatPaymentStatus(booking.payment_status) }}
          </span>
        </div>
        <div class="info-row" v-if="booking.status === 'rejected'">
          <span class="label">Rejection Reason</span>
          <span class="value rejected-text">{{ booking.notes || 'No reason provided' }}</span>
        </div>
      </div>

      <!-- Notes -->
      <div class="detail-section" v-if="booking.notes && booking.status !== 'rejected'">
        <h3><i class="fas fa-sticky-note"></i> Notes</h3>
        <p class="notes-text">{{ booking.notes }}</p>
      </div>
    </div>

    <!-- Actions -->
    <div class="detail-actions">
      <button v-if="canApprove" @click="approveBooking" class="btn-approve">
        <i class="fas fa-check"></i> Approve
      </button>
      <button v-if="canReject" @click="rejectBooking" class="btn-reject">
        <i class="fas fa-times"></i> Reject
      </button>
      <button 
        v-if="canProcessPayment" 
        @click="processPayment" 
        class="btn-payment"
      >
        <i class="fas fa-money-bill-wave"></i> Process Payment
      </button>
      <button @click="closeDetail" class="btn-close-detail">
        <i class="fas fa-times"></i> Close
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'BookingDetail',
  props: {
    booking: {
      type: Object,
      required: true
    }
  },
  emits: ['updated', 'close', 'payment'],
  computed: {
    canApprove() {
      return this.booking.status === 'pending'
    },
    canReject() {
      return this.booking.status === 'pending'
    },
    canProcessPayment() {
      if (this.booking.status === 'rejected' || this.booking.status === 'cancelled') {
        return false
      }
      return this.booking.status === 'confirmed' || 
             this.booking.status === 'commitment_pending' ||
             this.booking.status === 'cleared'
    }
  },
  methods: {
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
    },
    formatStatus(status) {
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
    },
    formatPaymentStatus(status) {
      const map = {
        pending: 'Pending',
        commitment_paid: 'Commitment Paid',
        fully_paid: 'Fully Paid'
      }
      return map[status] || status
    },
    approveBooking() {
      this.$emit('payment', this.booking)
    },
    rejectBooking() {
      this.$emit('close')
    },
    processPayment() {
      this.$emit('payment', this.booking)
    },
    closeDetail() {
      this.$emit('close')
    }
  }
}
</script>


<style scoped>
.booking-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1.3rem;
}

.booking-ref {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.9rem;
}

.status-badge {
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
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

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.detail-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}

.detail-section h3 {
  margin: 0 0 12px;
  font-size: 0.9rem;
  color: #1e3a8a;
}

.detail-section h3 i {
  margin-right: 8px;
  color: #f59e0b;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #e5e7eb;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: #6b7280;
  font-size: 0.85rem;
}

.info-row .value {
  font-weight: 500;
  color: #1f2937;
  text-align: right;
}

.info-row.total {
  font-weight: 700;
  font-size: 1.1rem;
}

.info-row.total .value {
  color: #f59e0b;
}

.discount {
  color: #10b981 !important;
}

.notes-text {
  color: #4b5563;
  line-height: 1.6;
  margin: 0;
}

.payment-badge {
  padding: 2px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: capitalize;
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

.btn-payment {
  background: #f59e0b;
  color: white;
}

.btn-payment:hover {
  background: #d97706;
}

.btn-close-detail {
  background: #f3f4f6;
  color: #4b5563;
  margin-left: auto;
}

.btn-close-detail:hover {
  background: #e5e7eb;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .detail-actions {
    flex-direction: column;
  }
  
  .btn-close-detail {
    margin-left: 0;
  }
}
</style>