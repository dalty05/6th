<template>
  <div v-if="isOpen" class="tour-modal-overlay" @click.self="closeModal">
    <div class="tour-modal">
      <!-- Close Button -->
      <button class="modal-close" @click="closeModal">
        <i class="fas fa-times"></i>
      </button>

      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-icon">
          <i class="fas fa-factory"></i>
        </div>
        <h2>Book a Factory Tour</h2>
        <p>Experience the magic of dairy production at Mount Kenya Milk</p>
      </div>

      <!-- Step Indicator -->
      <div class="step-indicator">
        <div 
          v-for="step in steps" 
          :key="step.number"
          class="step"
          :class="{
            'active': currentStep === step.number,
            'completed': currentStep > step.number
          }"
        >
          <div class="step-number">
            <span v-if="currentStep > step.number">✓</span>
            <span v-else>{{ step.number }}</span>
          </div>
          <span class="step-label">{{ step.label }}</span>
        </div>
      </div>

      <!-- Step Content -->
      <div class="step-content">
        <!-- Step 1: Select Package -->
        <div v-if="currentStep === 1" class="step-panel">
          <h3>Select Your Tour Package</h3>
          <p class="step-description">Choose from our curated factory tour experiences</p>
          
          <div class="package-grid">
            <div 
              v-for="pkg in packages" 
              :key="pkg.id"
              class="package-card"
              :class="{ 'selected': selectedPackage === pkg.id }"
              @click="selectPackage(pkg.id)"
            >
              <div class="package-image">
                <img :src="pkg.image_url || '/images/tour-placeholder.jpg'" :alt="pkg.name" @error="setImagePlaceholder">
                <span v-if="pkg.is_featured" class="featured-badge">Featured</span>
              </div>
              <div class="package-info">
                <h4>{{ pkg.name }}</h4>
                <p class="package-description">{{ pkg.short_description || truncate(pkg.description, 80) }}</p>
                <div class="package-details">
                  <span class="duration">
                    <i class="far fa-clock"></i> {{ pkg.duration_hours }} hours
                  </span>
                  <span class="price">KES {{ formatPrice(pkg.base_price) }}/person</span>
                </div>
                <div class="package-includes">
                  <span v-for="item in pkg.includes?.slice(0, 3) || []" :key="item" class="include-tag">
                    <i class="fas fa-check-circle"></i> {{ item }}
                  </span>
                  <span v-if="(pkg.includes?.length || 0) > 3" class="include-tag more">+{{ pkg.includes.length - 3 }} more</span>
                </div>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button 
              class="btn-next" 
              :disabled="!selectedPackage"
              @click="nextStep"
            >
              Next: Select Date <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <!-- Step 2: Select Date -->
        <div v-if="currentStep === 2" class="step-panel">
          <h3>Select Your Tour Date</h3>
          <p class="step-description">Choose a date that works best for your group</p>

          <div class="date-selection">
            <div class="calendar-container">
              <!-- Month Navigation -->
              <div class="calendar-nav">
                <button @click="prevMonth" class="nav-btn">
                  <i class="fas fa-chevron-left"></i>
                </button>
                <span class="month-label">{{ currentMonthLabel }}</span>
                <button @click="nextMonth" class="nav-btn">
                  <i class="fas fa-chevron-right"></i>
                </button>
              </div>

              <!-- Calendar Grid -->
              <div class="calendar-grid">
                <div class="calendar-header">
                  <span v-for="day in weekDays" :key="day" class="day-header">{{ day }}</span>
                </div>
                <div class="calendar-body">
                  <!-- ✅ FIX: Check if date exists before accessing properties -->
                  <div 
                    v-for="(date, index) in calendarDays" 
                    :key="index"
                    class="calendar-day"
                    :class="{
                      'other-month': date && !date.isCurrentMonth,
                      'available': date && date.isAvailable && date.isCurrentMonth,
                      'unavailable': date && !date.isAvailable && date.isCurrentMonth,
                      'selected': date && date.isSelected,
                      'today': date && date.isToday
                    }"
                    @click="date && date.isCurrentMonth && date.isAvailable ? selectDate(date) : null"
                  >
                    <span class="day-number">{{ date ? date.day : '' }}</span>
                    <span v-if="date && date.isAvailable && date.isCurrentMonth" class="availability-dot"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="btn-back" @click="prevStep">
              <i class="fas fa-arrow-left"></i> Back
            </button>
            <button 
              class="btn-next" 
              :disabled="!selectedDate"
              @click="nextStep"
            >
              Next: Your Details <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <!-- Step 3: Enter Details -->
        <div v-if="currentStep === 3" class="step-panel">
          <h3>Your Details</h3>
          <p class="step-description">Provide your contact information for the booking</p>

          <form @submit.prevent="submitBooking" class="booking-form">
            <div class="form-row">
              <div class="form-group">
                <label for="customer_name">Full Name *</label>
                <input 
                  type="text" 
                  id="customer_name" 
                  v-model="bookingForm.customer_name" 
                  required
                  placeholder="Enter your full name"
                >
              </div>
              <div class="form-group">
                <label for="customer_email">Email Address *</label>
                <input 
                  type="email" 
                  id="customer_email" 
                  v-model="bookingForm.customer_email" 
                  required
                  placeholder="your@email.com"
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="customer_phone">Phone Number *</label>
                <input 
                  type="tel" 
                  id="customer_phone" 
                  v-model="bookingForm.customer_phone" 
                  required
                  placeholder="+254 7XX XXX XXX"
                >
              </div>
              <div class="form-group">
                <label for="people_count">Number of People *</label>
                <input 
                  type="number" 
                  id="people_count" 
                  v-model="bookingForm.people_count" 
                  required
                  min="1"
                  :max="selectedPackageData?.max_people || 300"
                  @input="calculatePrice"
                >
                <small class="input-hint">Min: 1, Max: {{ selectedPackageData?.max_people || 300 }}</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="group_name">Group/Organization Name (Optional)</label>
                <input 
                  type="text" 
                  id="group_name" 
                  v-model="bookingForm.group_name" 
                  placeholder="e.g., ABC School, XYZ Company"
                >
              </div>
            </div>

            <div class="form-group full-width">
              <label for="special_requirements">Special Requirements (Optional)</label>
              <textarea 
                id="special_requirements" 
                v-model="bookingForm.special_requirements" 
                rows="3"
                placeholder="Any special requests, accessibility needs, or dietary requirements..."
              ></textarea>
            </div>

            <!-- Price Preview -->
            <div v-if="priceBreakdown" class="price-preview">
              <h4>Price Breakdown</h4>
              <div class="price-details">
                <div class="price-row">
                  <span>Base Price</span>
                  <span>KES {{ formatPrice(selectedPackageData?.base_price || 0) }} × {{ bookingForm.people_count || 0 }}</span>
                </div>
                <div class="price-row">
                  <span>Subtotal</span>
                  <span>KES {{ formatPrice(priceBreakdown.subtotal) }}</span>
                </div>
                <div v-if="priceBreakdown.discount_percentage > 0" class="price-row discount">
                  <span>Discount ({{ priceBreakdown.discount_percentage }}%)</span>
                  <span class="discount-amount">- KES {{ formatPrice(priceBreakdown.discount_amount) }}</span>
                </div>
                <div class="price-row total">
                  <span>Total</span>
                  <span>KES {{ formatPrice(priceBreakdown.total) }}</span>
                </div>
                <div class="price-row commitment">
                  <span>Commitment Deposit ({{ selectedPackageData?.commitment_percentage || 30 }}%)</span>
                  <span>KES {{ formatPrice(priceBreakdown.total * ((selectedPackageData?.commitment_percentage || 30) / 100)) }}</span>
                </div>
                <div class="price-row balance">
                  <span>Balance Due</span>
                  <span>KES {{ formatPrice(priceBreakdown.total * (1 - ((selectedPackageData?.commitment_percentage || 30) / 100))) }}</span>
                </div>
              </div>
              <div class="price-note">
                <i class="fas fa-info-circle"></i>
                <span>Once approved, pay the {{ selectedPackageData?.commitment_percentage || 30 }}% deposit to confirm your booking. Balance due before tour.</span>
              </div>
            </div>

            <div class="step-actions">
              <button type="button" class="btn-back" @click="prevStep">
                <i class="fas fa-arrow-left"></i> Back
              </button>
              <button 
                type="submit" 
                class="btn-submit" 
                :disabled="isSubmitting || !bookingForm.customer_name || !bookingForm.customer_email || !bookingForm.customer_phone || !bookingForm.people_count"
              >
                <span v-if="!isSubmitting">
                  <i class="fas fa-check-circle"></i> Submit for Approval
                </span>
                <span v-else>
                  <i class="fas fa-spinner fa-spin"></i> Processing...
                </span>
              </button>
            </div>
          </form>
        </div>

        <!-- Step 4: Confirmation -->
        <div v-if="currentStep === 4" class="step-panel success-panel">
          <div class="success-animation">
            <i class="fas fa-check-circle"></i>
          </div>
          <h3>Booking Submitted! 🎉</h3>
          <p class="success-message">
            Your factory tour booking has been submitted for approval.
          </p>
          
          <div class="booking-reference">
            <span class="ref-label">Booking Reference</span>
            <span class="ref-number">{{ bookingReference }}</span>
          </div>

          <div class="booking-summary">
            <div class="summary-item">
              <i class="fas fa-user"></i>
              <div>
                <strong>{{ bookingForm.customer_name }}</strong>
                <span>{{ bookingForm.customer_email }}</span>
              </div>
            </div>
            <div class="summary-item">
              <i class="fas fa-calendar-check"></i>
              <div>
                <strong>{{ formatDate(selectedDate) }}</strong>
              </div>
            </div>
            <div class="summary-item">
              <i class="fas fa-users"></i>
              <div>
                <strong>{{ bookingForm.people_count }} people</strong>
                <span>{{ selectedPackageData?.name }}</span>
              </div>
            </div>
          </div>

          <div class="next-steps">
            <h4>What happens next?</h4>
            <ul>
              <li>
                <i class="fas fa-envelope"></i>
                <span>You'll receive a confirmation email with all details</span>
              </li>
              <li>
                <i class="fas fa-clock"></i>
                <span>Our team will review and confirm within 24 hours</span>
              </li>
              <li>
                <i class="fas fa-money-bill-wave"></i>
                <span>Once approved, pay the {{ selectedPackageData?.commitment_percentage || 30 }}% deposit to secure your booking</span>
              </li>
            </ul>
          </div>

          <button class="btn-done" @click="closeModal">
            <i class="fas fa-thumbs-up"></i> Done
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isToday } from 'date-fns'

export default {
  name: 'TourBookingModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  data() {
    return {
      currentStep: 1,
      steps: [
        { number: 1, label: 'Package' },
        { number: 2, label: 'Date' },
        { number: 3, label: 'Details' },
        { number: 4, label: 'Confirm' }
      ],
      
      // Packages
      packages: [],
      selectedPackage: null,
      selectedPackageData: null,
      
      // Date
      currentDate: new Date(),
      selectedDate: null,
      availabilityCache: {},
      
      // Booking Form
      bookingForm: {
        customer_name: '',
        customer_email: '',
        customer_phone: '',
        people_count: 1,
        group_name: '',
        special_requirements: ''
      },
      
      // Price
      priceBreakdown: null,
      
      // Status
      isSubmitting: false,
      bookingReference: '',
      
      // Error
      error: null
    }
  },
  computed: {
    weekDays() {
      return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    },
    currentMonthLabel() {
      return format(this.currentDate, 'MMMM yyyy')
    },
    calendarDays() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const firstDay = new Date(year, month, 1).getDay()
      const daysInMonth = new Date(year, month + 1, 0).getDate()
      const daysInPrevMonth = new Date(year, month, 0).getDate()
      
      const days = []
      
      // Previous month days
      const startOffset = firstDay
      for (let i = startOffset - 1; i >= 0; i--) {
        const day = daysInPrevMonth - i
        const date = new Date(year, month - 1, day)
        const dateKey = format(date, 'yyyy-MM-dd')
        const cacheData = this.availabilityCache[dateKey] || { is_available: true, is_blocked: false }
        
        days.push({
          day: day,
          date: date,
          isCurrentMonth: false,
          isToday: false,
          isAvailable: false,
          isSelected: false,
          isBlocked: false
        })
      }
      
      // Current month days
      for (let i = 1; i <= daysInMonth; i++) {
        const date = new Date(year, month, i)
        const dateKey = format(date, 'yyyy-MM-dd')
        const cacheData = this.availabilityCache[dateKey] || { is_available: true, is_blocked: false }
        const isTodayDate = isToday(date)
        const isSelectedDate = this.selectedDate && isSameDay(date, this.selectedDate)
        
        days.push({
          day: i,
          date: date,
          isCurrentMonth: true,
          isToday: isTodayDate,
          isAvailable: cacheData.is_available !== false && !cacheData.is_blocked,
          isSelected: isSelectedDate,
          isBlocked: cacheData.is_blocked || false
        })
      }
      
      // Next month days to fill grid
      const totalDays = days.length
      const remainingDays = 42 - totalDays
      for (let i = 1; i <= remainingDays; i++) {
        const date = new Date(year, month + 1, i)
        days.push({
          day: i,
          date: date,
          isCurrentMonth: false,
          isToday: false,
          isAvailable: false,
          isSelected: false,
          isBlocked: false
        })
      }
      
      return days
    }
  },
  watch: {
    async isOpen(newVal) {
      if (newVal) {
        await this.fetchPackages()
        this.resetForm()
      }
    }
  },
  methods: {
    formatPrice(amount) {
      return amount.toLocaleString('en-KE', { 
        minimumFractionDigits: 0, 
        maximumFractionDigits: 0 
      })
    },
    formatDate(date) {
      return date ? format(date, 'EEE, MMM d, yyyy') : ''
    },
    truncate(text, length) {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    },
    setImagePlaceholder(event) {
      event.target.src = '/images/tour-placeholder.jpg'
    },
    async fetchPackages() {
      try {
        const response = await axios.get('/api/tour/packages')
        this.packages = response.data.packages || []
        if (this.packages.length > 0) {
          this.selectedPackage = this.packages[0].id
          this.selectedPackageData = this.packages[0]
        }
      } catch (error) {
        console.error('Failed to fetch packages:', error)
        // Fallback packages
        this.packages = [
          {
            id: 1,
            name: 'Standard Factory Tour',
            description: 'Experience the complete dairy production process',
            short_description: '2-hour guided tour',
            base_price: 1500,
            duration_hours: 2,
            includes: ['Factory tour guide', 'Product tasting', 'Safety gear', 'Certificate'],
            is_featured: true,
            image_url: '/images/tour-placeholder.jpg',
            commitment_percentage: 30
          },
          {
            id: 2,
            name: 'Premium Farm-to-Table Experience',
            description: 'Full day experience with farm visit and gourmet lunch',
            short_description: '6-hour complete experience',
            base_price: 3500,
            duration_hours: 6,
            includes: ['Farm visit', 'Factory tour', 'Gourmet lunch', 'Certificate'],
            is_featured: true,
            image_url: '/images/tour-placeholder.jpg',
            commitment_percentage: 30
          }
        ]
        this.selectedPackage = this.packages[0].id
        this.selectedPackageData = this.packages[0]
      }
    },
    async fetchAvailability(date) {
      if (!date) return
      
      const dateKey = format(date, 'yyyy-MM-dd')
      if (this.availabilityCache[dateKey]) return
      
      try {
        const response = await axios.get('/api/tour/availability', {
          params: {
            package_id: this.selectedPackage,
            date: dateKey
          }
        })
        this.availabilityCache[dateKey] = response.data
        this.$forceUpdate()
      } catch (error) {
        console.error('Failed to fetch availability:', error)
        this.availabilityCache[dateKey] = { is_available: true, is_blocked: false }
      }
    },
    async loadMonthAvailability() {
      if (!this.selectedPackage) return
      
      const days = this.calendarDays.filter(d => d.isCurrentMonth)
      for (const day of days) {
        await this.fetchAvailability(day.date)
      }
    },
    selectPackage(packageId) {
      this.selectedPackage = packageId
      this.selectedPackageData = this.packages.find(p => p.id === packageId)
      this.selectedDate = null
      this.priceBreakdown = null
      this.availabilityCache = {}
      // Load availability for current month
      this.loadMonthAvailability()
    },
    selectDate(date) {
      if (!date || !date.isCurrentMonth || !date.isAvailable) return
      this.selectedDate = date.date
    },
    async prevMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1)
      this.availabilityCache = {}
      await this.loadMonthAvailability()
    },
    async nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1)
      this.availabilityCache = {}
      await this.loadMonthAvailability()
    },
    calculatePrice() {
      if (!this.selectedPackageData || !this.bookingForm.people_count) {
        this.priceBreakdown = null
        return
      }
      
      const people = parseInt(this.bookingForm.people_count) || 0
      if (people < 1 || people > this.selectedPackageData.max_people) {
        return
      }
      
      const basePrice = this.selectedPackageData.base_price
      let discount = 0
      
      if (people <= 50) discount = 0.05
      else if (people <= 100) discount = 0.10
      else if (people <= 150) discount = 0.15
      else if (people <= 200) discount = 0.20
      else discount = 0.25
      
      const subtotal = basePrice * people
      const discountAmount = subtotal * discount
      const total = subtotal - discountAmount
      
      this.priceBreakdown = {
        subtotal,
        discount_percentage: discount * 100,
        discount_amount: discountAmount,
        total,
        tier_applied: this.getTierLabel(people)
      }
    },
    getTierLabel(people) {
      if (people <= 50) return '1-50 people (5%)'
      if (people <= 100) return '51-100 people (10%)'
      if (people <= 150) return '101-150 people (15%)'
      if (people <= 200) return '151-200 people (20%)'
      return '201+ people (25%)'
    },
    nextStep() {
      if (this.currentStep === 1 && !this.selectedPackage) return
      if (this.currentStep === 2 && !this.selectedDate) return
      
      if (this.currentStep < 4) {
        this.currentStep++
      }
    },
    prevStep() {
      if (this.currentStep > 1) {
        this.currentStep--
      }
    },
    async submitBooking() {
      if (!this.validateForm()) return
      
      this.isSubmitting = true
      this.error = null
      
      try {
        const dateStr = format(this.selectedDate, 'yyyy-MM-dd')
        const fullDateTime = `${dateStr} 10:00:00`
        
        const payload = {
          package_id: parseInt(this.selectedPackage),
          tour_date: fullDateTime,
          people_count: parseInt(this.bookingForm.people_count) || 1,
          customer_name: this.bookingForm.customer_name.trim(),
          customer_email: this.bookingForm.customer_email.trim(),
          customer_phone: this.bookingForm.customer_phone.trim(),
          group_name: this.bookingForm.group_name?.trim() || null,
          special_requirements: this.bookingForm.special_requirements?.trim() || null
        }
        
        console.log('📤 Sending booking payload:', payload)
        
        const response = await axios.post('/api/tour/booking', payload)
        
        if (response.data.success) {
          this.bookingReference = response.data.booking.reference
          this.currentStep = 4
          this.priceBreakdown = response.data.price_breakdown
        }
      } catch (error) {
        console.error('❌ Booking error:', error)
        console.error('❌ Error response:', error.response?.data)
        this.error = error.response?.data?.error || 'Failed to submit booking. Please try again.'
        alert(this.error)
      } finally {
        this.isSubmitting = false
      }
    },
    validateForm() {
      const form = this.bookingForm
      if (!form.customer_name) {
        alert('Please enter your full name')
        return false
      }
      if (!form.customer_email || !form.customer_email.includes('@')) {
        alert('Please enter a valid email address')
        return false
      }
      if (!form.customer_phone || form.customer_phone.length < 10) {
        alert('Please enter a valid phone number')
        return false
      }
      if (!form.people_count || form.people_count < 1) {
        alert('Please enter the number of people')
        return false
      }
      return true
    },
    resetForm() {
      this.currentStep = 1
      this.selectedDate = null
      this.bookingForm = {
        customer_name: '',
        customer_email: '',
        customer_phone: '',
        people_count: 1,
        group_name: '',
        special_requirements: ''
      }
      this.priceBreakdown = null
      this.isSubmitting = false
      this.bookingReference = ''
      this.error = null
      this.availabilityCache = {}
    },
    closeModal() {
      this.$emit('close')
    }
  }
}
</script>


<style scoped>
.tour-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.tour-modal {
  background: white;
  border-radius: 24px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 40px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: #f3f4f6;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s;
  color: #4b5563;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #e5e7eb;
  transform: rotate(90deg);
}

/* Modal Header */
.modal-header {
  text-align: center;
  margin-bottom: 30px;
}

.header-icon {
  width: 70px;
  height: 70px;
  background: #fef3c7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.header-icon i {
  font-size: 32px;
  color: #f59e0b;
}

.modal-header h2 {
  color: #1f2937;
  font-size: 28px;
  margin: 0 0 8px;
}

.modal-header p {
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

/* Step Indicator */
.step-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 0 20px;
  position: relative;
}

.step-indicator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 40px;
  right: 40px;
  height: 2px;
  background: #e5e7eb;
  transform: translateY(-50%);
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  z-index: 1;
  cursor: pointer;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
}

.step.active .step-number {
  background: #f59e0b;
  color: white;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.step.completed .step-number {
  background: #10b981;
  color: white;
}

.step-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.step.active .step-label {
  color: #f59e0b;
}

.step.completed .step-label {
  color: #10b981;
}

/* Step Content */
.step-content {
  min-height: 400px;
}

.step-panel {
  animation: fadeIn 0.3s ease;
}

.step-panel h3 {
  color: #1f2937;
  font-size: 20px;
  margin: 0 0 8px;
}

.step-description {
  color: #6b7280;
  margin: 0 0 24px;
}

/* Package Grid */
.package-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.package-card {
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.package-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.package-card.selected {
  border-color: #f59e0b;
  box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.1);
}

.package-image {
  position: relative;
  height: 140px;
  overflow: hidden;
}

.package-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #f59e0b;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.package-info {
  padding: 16px;
}

.package-info h4 {
  color: #1f2937;
  margin: 0 0 6px;
  font-size: 16px;
}

.package-description {
  color: #6b7280;
  font-size: 14px;
  margin: 0 0 12px;
  line-height: 1.4;
}

.package-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  margin-bottom: 10px;
}

.duration {
  color: #6b7280;
}

.price {
  font-weight: 600;
  color: #f59e0b;
}

.package-includes {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.include-tag {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.include-tag i {
  color: #10b981;
  font-size: 10px;
}

.include-tag.more {
  background: #e5e7eb;
}

/* Calendar */
.calendar-container {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
}

.calendar-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.nav-btn {
  background: #f3f4f6;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-btn:hover {
  background: #e5e7eb;
}

.month-label {
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
}

.calendar-grid {
  display: grid;
  gap: 4px;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.day-header {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  padding: 4px;
}

.calendar-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  padding: 4px;
  background: #f9fafb;
}

.calendar-day:hover {
  background: #f3f4f6;
}

.calendar-day.other-month {
  opacity: 0.3;
  cursor: default;
}

.calendar-day.available {
  background: #f0fdf4;
}

.calendar-day.available:hover {
  background: #d1fae5;
}

.calendar-day.unavailable {
  background: #fef2f2;
  cursor: not-allowed;
  opacity: 0.5;
}

.calendar-day.selected {
  background: #f59e0b;
  color: white;
}

.calendar-day.selected .day-number {
  color: white;
}

.calendar-day.today {
  border: 2px solid #f59e0b;
}

.day-number {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.availability-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  position: absolute;
  bottom: 4px;
}

.spots-available {
  font-size: 8px;
  color: #6b7280;
  position: absolute;
  bottom: 2px;
}

/* Time Slots */
.time-selection {
  background: #f9fafb;
  border-radius: 16px;
  padding: 20px;
}

.time-selection h4 {
  color: #1f2937;
  margin: 0 0 12px;
}

.time-slots {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.time-slot {
  padding: 10px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.time-slot:hover {
  border-color: #f59e0b;
}

.time-slot.selected {
  border-color: #f59e0b;
  background: #fef3c7;
}

/* Form */
.booking-form {
  margin-top: 10px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.form-group input,
.form-group textarea {
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.input-hint {
  font-size: 12px;
  color: #6b7280;
}

/* Price Preview */
.price-preview {
  background: #f9fafb;
  border-radius: 16px;
  padding: 20px;
  margin: 20px 0;
}

.price-preview h4 {
  color: #1f2937;
  margin: 0 0 16px;
}

.price-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #6b7280;
}

.price-row.discount {
  color: #10b981;
}

.price-row.total {
  font-weight: 700;
  color: #1f2937;
  font-size: 18px;
  padding-top: 8px;
  border-top: 1px solid #e5e7eb;
}

.price-row.commitment {
  color: #f59e0b;
  font-weight: 600;
}

.price-row.balance {
  color: #6b7280;
  font-weight: 500;
}

.discount-amount {
  color: #10b981;
}

.price-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: #fef3c7;
  border-radius: 8px;
  font-size: 13px;
  color: #92400e;
}

.price-note i {
  margin-top: 2px;
}

/* Step Actions */
.step-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  gap: 12px;
}

.btn-back {
  padding: 10px 24px;
  background: #f3f4f6;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 500;
  color: #4b5563;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #e5e7eb;
}

.btn-next {
  padding: 10px 32px;
  background: #f59e0b;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.btn-next:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-next:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-submit {
  padding: 12px 40px;
  background: #10b981;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-submit:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Success Panel */
.success-panel {
  text-align: center;
}

.success-animation {
  width: 80px;
  height: 80px;
  background: #d1fae5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.success-animation i {
  font-size: 40px;
  color: #10b981;
}

.booking-reference {
  background: #f3f4f6;
  border-radius: 12px;
  padding: 16px;
  margin: 20px 0;
}

.ref-label {
  font-size: 14px;
  color: #6b7280;
}

.ref-number {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  display: block;
  margin-top: 4px;
}

.booking-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 20px 0;
  text-align: left;
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 12px;
}

.summary-item i {
  color: #f59e0b;
  font-size: 20px;
  margin-top: 2px;
}

.summary-item div {
  display: flex;
  flex-direction: column;
}

.summary-item strong {
  color: #1f2937;
}

.summary-item span {
  font-size: 14px;
  color: #6b7280;
}

.next-steps {
  text-align: left;
  background: #f9fafb;
  border-radius: 16px;
  padding: 20px;
  margin: 20px 0;
}

.next-steps h4 {
  color: #1f2937;
  margin: 0 0 12px;
}

.next-steps ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.next-steps li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  color: #4b5563;
  font-size: 14px;
}

.next-steps li i {
  color: #f59e0b;
  font-size: 16px;
}

.btn-done {
  padding: 12px 48px;
  background: #f59e0b;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  color: white;
  transition: all 0.3s;
  margin-top: 16px;
}

.btn-done:hover {
  background: #d97706;
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 768px) {
  .tour-modal {
    padding: 24px 16px;
  }
  
  .package-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .step-indicator {
    padding: 0 10px;
  }
  
  .step-label {
    font-size: 10px;
  }
  
  .step-actions {
    flex-wrap: wrap;
  }
  
  .btn-next {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }
  
  .btn-back {
    width: 100%;
    justify-content: center;
  }
  
  .booking-summary {
    grid-template-columns: 1fr;
  }
}
</style>