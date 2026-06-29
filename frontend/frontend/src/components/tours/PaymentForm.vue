<template>
  <div class="payment-form">
    <h2><i class="fas fa-money-bill-wave"></i> Process Payment</h2>
    <p class="subtitle">Booking: <strong>{{ booking.reference }}</strong></p>

    <form @submit.prevent="submitPayment" class="form">
      <!-- Payment Status -->
      <div class="payment-status" v-if="booking.commitment_paid || booking.payment_status === 'fully_paid'">
        <div v-if="booking.payment_status === 'fully_paid'" class="status-badge paid">
          <i class="fas fa-check-circle"></i> Fully Paid
        </div>
        <div v-else-if="booking.commitment_paid" class="status-badge partial">
          <i class="fas fa-clock"></i> Commitment Paid ({{ commitmentPercentage }}%)
        </div>
      </div>

      <div class="form-group">
        <label>Payment Type</label>
        <select v-model="paymentData.payment_type" required>
          <option value="">Select payment type...</option>
          <option value="commitment">Commitment Deposit ({{ commitmentPercentage }}%)</option>
          <option v-if="booking.commitment_paid" value="balance">Balance Payment</option>
          <option value="full">Full Payment</option>
        </select>
        <small class="hint" v-if="!booking.commitment_paid">
          Commitment deposit is {{ commitmentPercentage }}% of total (KES {{ formatPrice(commitmentAmount) }})
        </small>
        <small class="hint" v-else>
          Remaining balance: KES {{ formatPrice(remainingBalance) }}
        </small>
      </div>

      <div class="form-group">
        <label>Amount (KES)</label>
        <input 
          type="number" 
          v-model="paymentData.amount" 
          required
          :placeholder="`Enter amount (max: ${formatPrice(maxAmount)})`"
          :max="maxAmount"
          min="1"
          step="1"
          @input="validateAmount"
        >
        <small class="hint">Maximum: KES {{ formatPrice(maxAmount) }}</small>
        <small v-if="paymentData.payment_type === 'commitment'" class="hint highlight">
          Commitment amount: KES {{ formatPrice(commitmentAmount) }}
        </small>
      </div>

      <div class="form-group">
        <label>Payment Method</label>
        <select v-model="paymentData.payment_method" required>
          <option value="manual">Manual (Cash/Bank Transfer)</option>
          <option value="mpesa">M-Pesa</option>
          <option value="bank_transfer">Bank Transfer</option>
        </select>
      </div>

      <div class="form-group">
        <label>Reference Number</label>
        <input 
          type="text" 
          v-model="paymentData.reference_number" 
          placeholder="e.g., M-Pesa confirmation code or bank reference"
        >
      </div>

      <div class="form-group">
        <label>Notes (Optional)</label>
        <textarea v-model="paymentData.notes" rows="2" placeholder="Any additional notes..."></textarea>
      </div>

      <!-- Payment Breakdown -->
      <div class="payment-summary">
        <div class="summary-row">
          <span>Booking Total</span>
          <span>KES {{ formatPrice(booking.total_amount) }}</span>
        </div>
        <div class="summary-row" v-if="booking.commitment_paid">
          <span>Commitment Paid ({{ commitmentPercentage }}%)</span>
          <span class="paid-amount">KES {{ formatPrice(booking.commitment_amount) }}</span>
        </div>
        <div class="summary-row total">
          <span>Remaining Balance</span>
          <span>KES {{ formatPrice(remainingBalance) }}</span>
        </div>
        <div class="summary-row" v-if="paymentData.payment_type === 'commitment'">
          <span>Commitment Amount</span>
          <span class="commitment-amount">KES {{ formatPrice(commitmentAmount) }}</span>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" @click="$emit('close')" class="btn-cancel">
          Cancel
        </button>
        <button type="submit" :disabled="submitting || !isValidAmount" class="btn-submit">
          <span v-if="!submitting">
            <i class="fas fa-check"></i> Confirm Payment
          </span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> Processing...
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PaymentForm',
  props: {
    booking: {
      type: Object,
      required: true
    }
  },
  emits: ['confirmed', 'close'],
  data() {
    return {
      paymentData: {
        payment_type: '',
        amount: '',
        payment_method: 'manual',
        reference_number: '',
        notes: ''
      },
      submitting: false
      // ❌ Remove: commitmentPercentage: 30 (This is now a computed property)
    }
  },
  computed: {
    // ✅ Only define commitmentPercentage as a computed property
    commitmentPercentage() {
      // Try to get from booking.package, or fallback to 30
      if (this.booking.package && this.booking.package.commitment_percentage) {
        return this.booking.package.commitment_percentage
      }
      // If package data is not loaded, try to get from the commitment_amount
      if (this.booking.commitment_amount && this.booking.total_amount) {
        return Math.round((this.booking.commitment_amount / this.booking.total_amount) * 100)
      }
      return 30
    },
    commitmentAmount() {
      return (this.booking.total_amount * this.commitmentPercentage) / 100
    },
    remainingBalance() {
      const paid = this.booking.commitment_paid ? this.booking.commitment_amount : 0
      return this.booking.total_amount - paid
    },
    maxAmount() {
      if (this.paymentData.payment_type === 'commitment') {
        if (this.booking.commitment_paid) return 0
        return this.commitmentAmount
      }
      return this.remainingBalance
    },
    isValidAmount() {
      const amount = parseFloat(this.paymentData.amount)
      if (!amount || amount <= 0) return false
      if (amount > this.maxAmount) return false
      return true
    }
  },
  watch: {
    'paymentData.payment_type'(newVal) {
      if (newVal === 'commitment' && !this.booking.commitment_paid) {
        this.paymentData.amount = this.commitmentAmount
      } else if (newVal === 'full') {
        this.paymentData.amount = this.remainingBalance
      } else if (newVal === 'balance') {
        this.paymentData.amount = this.remainingBalance
      }
    }
  },
  methods: {
    formatPrice(amount) {
      return (amount || 0).toLocaleString('en-KE', { 
        minimumFractionDigits: 0, 
        maximumFractionDigits: 0 
      })
    },
    validateAmount() {
      const amount = parseFloat(this.paymentData.amount)
      if (amount > this.maxAmount) {
        this.paymentData.amount = this.maxAmount
      }
      if (amount && amount > 0) {
        this.paymentData.amount = Math.round(amount * 100) / 100
      }
    },
    async submitPayment() {
      if (!this.paymentData.payment_type) {
        alert('Please select a payment type')
        return
      }
      
      const amount = parseFloat(this.paymentData.amount)
      if (!amount || amount <= 0) {
        alert('Please enter a valid amount')
        return
      }
      
      if (amount > this.maxAmount) {
        alert(`Amount cannot exceed KES ${this.formatPrice(this.maxAmount)}`)
        return
      }

      if (this.paymentData.payment_type === 'commitment') {
        if (this.booking.commitment_paid) {
          alert('Commitment deposit has already been paid')
          return
        }
        if (amount > this.commitmentAmount) {
          if (!confirm(`The commitment deposit is KES ${this.formatPrice(this.commitmentAmount)}. Continue with KES ${this.formatPrice(amount)}?`)) {
            return
          }
        }
      }

      this.submitting = true
      try {
        const payload = {
          amount: amount,
          payment_type: this.paymentData.payment_type,
          payment_method: this.paymentData.payment_method,
          reference_number: this.paymentData.reference_number || null,
          notes: this.paymentData.notes || null
        }

        const response = await axios.put(
          `/api/tour/admin/bookings/${this.booking.id}/payment`,
          payload
        )
        
        if (response.data.success) {
          this.$emit('confirmed', response.data.booking)
          this.$emit('close')
        }
      } catch (error) {
        console.error('Error processing payment:', error)
        alert(error.response?.data?.error || 'Failed to process payment. Please try again.')
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.payment-form {
  padding: 24px;
  max-width: 500px;
  margin: 0 auto;
}

.payment-form h2 {
  color: #1e3a8a;
  margin: 0 0 4px;
}

.payment-form h2 i {
  color: #f59e0b;
  margin-right: 8px;
}

.subtitle {
  color: #6b7280;
  margin: 0 0 20px;
}

.payment-status {
  margin-bottom: 16px;
}

.status-badge {
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge.paid {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.partial {
  background: #fef3c7;
  color: #92400e;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.form-group select,
.form-group input,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-group select:focus,
.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.hint {
  font-size: 12px;
  color: #6b7280;
}

.hint.highlight {
  color: #f59e0b;
  font-weight: 600;
}

.payment-summary {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-top: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 14px;
  color: #4b5563;
}

.summary-row .paid-amount {
  color: #10b981;
  font-weight: 600;
}

.summary-row .commitment-amount {
  color: #f59e0b;
  font-weight: 600;
}

.summary-row.total {
  font-weight: 700;
  color: #1f2937;
  border-top: 1px solid #e5e7eb;
  padding-top: 8px;
  margin-top: 4px;
}

.summary-row.total span:last-child {
  color: #f59e0b;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn-cancel {
  flex: 1;
  padding: 10px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #4b5563;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-submit {
  flex: 2;
  padding: 10px;
  background: #10b981;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-submit:hover:not(:disabled) {
  background: #059669;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .form-actions {
    flex-direction: column;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>