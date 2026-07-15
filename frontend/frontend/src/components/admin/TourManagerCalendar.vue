<template>
  <div class="tour-manager-calendar">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1><i class="fas fa-calendar-alt"></i> Tour Calendar</h1>
        <p class="subtitle">Manage blocked dates and view tour schedules</p>
      </div>
      <div class="header-actions">
        <div class="package-selector">
          <label>Package:</label>
          <select v-model="selectedPackageId" @change="handlePackageChange">
            <option v-for="pkg in packages" :key="pkg.id" :value="pkg.id">
              {{ pkg.name }}
            </option>
          </select>
        </div>
        <button @click="refreshCalendar" class="btn-refresh" :disabled="loading">
          <i :class="loading ? 'fas fa-spinner fa-spin' : 'fas fa-sync-alt'"></i>
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Legend -->
    <div class="calendar-legend">
      <div class="legend-item">
        <span class="legend-dot available"></span>
        Available
      </div>
      <div class="legend-item">
        <span class="legend-dot blocked"></span>
        Blocked
      </div>
      <div class="legend-item">
        <span class="legend-dot has-bookings"></span>
        Has Bookings
      </div>
      <div class="legend-item">
        <span class="legend-dot today"></span>
        Today
      </div>
    </div>

    <!-- Calendar -->
    <div class="calendar-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading calendar...</p>
      </div>
      <div ref="calendarEl" class="calendar-wrapper"></div>
    </div>

    <!-- Date Details Modal -->
    <div v-if="selectedDate" class="modal-overlay" @click.self="closeDateDetails">
      <div class="modal-container date-detail-modal">
        <button class="modal-close" @click="closeDateDetails">
          <i class="fas fa-times"></i>
        </button>
        <div class="date-detail-content">
          <div class="date-header">
            <h2><i class="fas fa-calendar-day"></i> {{ formatFullDate(selectedDate.date) }}</h2>
            <span class="date-status" :class="selectedDate.is_blocked ? 'blocked' : 'available'">
              {{ selectedDate.is_blocked ? '🚫 Blocked' : '✅ Available' }}
            </span>
            <span class="booking-count" v-if="selectedDate.bookings && selectedDate.bookings.length > 0">
              <i class="fas fa-ticket-alt"></i> {{ selectedDate.bookings.length }} booking(s)
            </span>
          </div>

          <div class="date-actions">
            <button 
              v-if="selectedDate.is_blocked" 
              @click="unblockDate" 
              class="btn-unblock"
            >
              <i class="fas fa-unlock"></i> Unblock Date
            </button>
            <button 
              v-else 
              @click="openBlockModal" 
              class="btn-block"
            >
              <i class="fas fa-lock"></i> Block Date
            </button>
          </div>

          <!-- ✅ Bookings List -->
          <div v-if="selectedDate.bookings && selectedDate.bookings.length > 0" class="date-bookings">
            <h4><i class="fas fa-ticket-alt"></i> Bookings on this date</h4>
            <div class="booking-list">
              <div 
                v-for="booking in selectedDate.bookings" 
                :key="booking.id"
                class="booking-item"
                :class="booking.status"
              >
                <span class="booking-ref">{{ booking.reference }}</span>
                <span class="booking-people"><i class="fas fa-users"></i> {{ booking.people_count }}</span>
                <span class="booking-status" :class="booking.status">{{ booking.status }}</span>
                <button @click="viewBooking(booking)" class="btn-view-booking">
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="no-bookings">
            <i class="fas fa-calendar-check"></i>
            <p>No bookings on this date</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Block Modal -->
    <div v-if="showBlockModal" class="modal-overlay" @click.self="showBlockModal = false">
      <div class="modal-container block-modal">
        <div class="modal-header">
          <h3><i class="fas fa-lock"></i> Block Date</h3>
          <button class="modal-close" @click="showBlockModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Block <strong>{{ formatFullDate(selectedDate?.date) }}</strong></p>
          <div class="form-group">
            <label>Reason for blocking *</label>
            <textarea v-model="blockReason" rows="3" placeholder="Please provide a reason..."></textarea>
          </div>
          <div class="form-actions">
            <button @click="showBlockModal = false" class="btn-cancel">Cancel</button>
            <button @click="confirmBlock" class="btn-danger" :disabled="!blockReason.trim()">
              <i class="fas fa-lock"></i> Block Date
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Detail Modal -->
    <div v-if="selectedBooking" class="modal-overlay" @click.self="selectedBooking = null">
      <div class="modal-container booking-detail-modal">
        <button class="modal-close" @click="selectedBooking = null">
          <i class="fas fa-times"></i>
        </button>
        <BookingDetail 
          :booking="selectedBooking" 
          @close="selectedBooking = null"
          @updated="refreshCalendar"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { Calendar } from '@fullcalendar/core'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import axios from 'axios'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay } from 'date-fns'
import BookingDetail from '@/components/tours/BookingDetail.vue'

// ============================================================
// STATE
// ============================================================
const calendarEl = ref(null)
let calendarInstance = null
const loading = ref(false)
const packages = ref([])
const selectedPackageId = ref(null)
const availabilityData = ref({})
// ✅ Store all bookings by date
const bookingsByDate = ref({})
const selectedDate = ref(null)
const selectedBooking = ref(null)
const showBlockModal = ref(false)
const blockReason = ref('')

// ============================================================
// COMPUTED
// ============================================================
const availableDays = computed(() => {
  return Object.values(availabilityData.value).filter(d => !d.is_blocked).length
})

const blockedDays = computed(() => {
  return Object.values(availabilityData.value).filter(d => d.is_blocked).length
})

// ============================================================
// METHODS
// ============================================================

const loadPackages = async () => {
  try {
    const response = await axios.get('/api/admin/tour/packages')
    packages.value = response.data.packages || []
    if (packages.value.length > 0) {
      selectedPackageId.value = packages.value[0].id
    }
  } catch (error) {
    packages.value = []
  }
}

const getStatus = (data) => {
  if (data.is_blocked) return 'blocked'
  return 'available'
}

const getStatusLabel = (data) => {
  if (data.is_blocked) return '🚫 Blocked'
  return '✅ Available'
}

const initCalendar = () => {
  if (!calendarEl.value) return
  
  if (calendarInstance) {
    calendarInstance.destroy()
    calendarInstance = null
  }
  
  calendarInstance = new Calendar(calendarEl.value, {
    plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,dayGridWeek'
    },
    events: [],
    eventClick: (info) => {
      const dateStr = info.event.startStr
      // ✅ Get availability data
      const data = availabilityData.value[dateStr] || { is_blocked: false }
      
      // ✅ Get bookings for this date
      const bookings = bookingsByDate.value[dateStr] || []
      
      selectedDate.value = {
        date: new Date(dateStr),
        ...data,
        bookings: bookings
      }
      
    },
    dayMaxEvents: true,
    height: 'auto',
    datesSet: () => {
      if (!loading.value && selectedPackageId.value) {
        loadAvailability()
        // ✅ Also load bookings for the visible month
        loadBookingsForMonth()
      }
    },
    eventClassNames: (arg) => {
      const data = arg.event.extendedProps.availability
      if (data) {
        const status = getStatus(data)
        return [`fc-event-${status}`]
      }
      return []
    },
    dayCellClassNames: (arg) => {
      const dateStr = format(arg.date, 'yyyy-MM-dd')
      const data = availabilityData.value[dateStr]
      const bookings = bookingsByDate.value[dateStr] || []
      
      const classes = []
      if (data) {
        const status = getStatus(data)
        classes.push(`fc-day-${status}`)
      }
      // ✅ Add class if date has bookings
      if (bookings.length > 0) {
        classes.push('fc-day-has-bookings')
      }
      return classes
    },
    eventContent: (arg) => {
      return {
        html: `<span class="event-title">${arg.event.title}</span>`
      }
    }
  })
  
  calendarInstance.render()
  
  setTimeout(() => {
    if (selectedPackageId.value) {
      loadAvailability()
      loadBookingsForMonth()
    }
  }, 300)
}

const updateCalendarEvents = () => {
  if (!calendarInstance) return
  
  const events = []
  Object.entries(availabilityData.value).forEach(([date, data]) => {
    const status = getStatus(data)
    const title = getStatusLabel(data)
    
    // ✅ Check if there are bookings for this date
    const bookings = bookingsByDate.value[date] || []
    const hasBookings = bookings.length > 0
    
    // ✅ Add booking count to title if there are bookings
    const displayTitle = hasBookings ? `${title} (${bookings.length} bookings)` : title
    
    events.push({
      title: displayTitle,
      date: date,
      allDay: true,
      className: `status-${status}`,
      extendedProps: {
        availability: data,
        bookings: bookings
      }
    })
  })
  
  calendarInstance.removeAllEvents()
  calendarInstance.addEventSource(events)
  
}

const loadAvailability = async () => {
  if (!selectedPackageId.value) {
    return
  }
  
  loading.value = true
  
  try {
    const currentDate = calendarInstance ? calendarInstance.getDate() : new Date()
    const monthStart = startOfMonth(currentDate)
    const monthEnd = endOfMonth(currentDate)
    const dateRange = eachDayOfInterval({ start: monthStart, end: monthEnd })
    
    const promises = dateRange.map(date => {
      const dateStr = format(date, 'yyyy-MM-dd')
      return axios.get('/api/tour/availability', {
        params: {
          package_id: selectedPackageId.value,
          date: dateStr
        }
      }).then(res => ({
        date: dateStr,
        data: res.data
      })).catch(() => ({
        date: dateStr,
        data: { is_available: true, is_blocked: false }
      }))
    })
    
    const results = await Promise.all(promises)
    results.forEach(({ date, data }) => {
      availabilityData.value[date] = data
    })
    
    await nextTick()
    updateCalendarEvents()
    
  } catch (error) {
  } finally {
    loading.value = false
  }
}

// ✅ New: Load bookings for the current month
const loadBookingsForMonth = async () => {
  try {
    const currentDate = calendarInstance ? calendarInstance.getDate() : new Date()
    const monthStart = startOfMonth(currentDate)
    const monthEnd = endOfMonth(currentDate)
    
    // ✅ Fetch all bookings for the month
    const response = await axios.get('/api/admin/tour/bookings', {
      params: {
        date_from: format(monthStart, 'yyyy-MM-dd'),
        date_to: format(monthEnd, 'yyyy-MM-dd'),
        per_page: 100 // Get all bookings for the month
      }
    })
    
    const bookings = response.data.bookings || []
    
    // ✅ Group bookings by date
    const grouped = {}
    bookings.forEach(booking => {
      if (booking.tour_date) {
        const dateKey = format(new Date(booking.tour_date), 'yyyy-MM-dd')
        if (!grouped[dateKey]) {
          grouped[dateKey] = []
        }
        grouped[dateKey].push(booking)
      }
    })
    
    bookingsByDate.value = grouped
    
    
    // ✅ Update calendar events with booking info
    updateCalendarEvents()
    
  } catch (error) {
  }
}

// ✅ Load bookings for a specific date when clicked
const loadBookingsForDate = async (dateStr) => {
  try {
    const response = await axios.get('/api/admin/tour/bookings', {
      params: {
        date_from: dateStr,
        date_to: dateStr,
        per_page: 50
      }
    })
    const bookings = response.data.bookings || []
    
    // ✅ Update the bookings for this date
    bookingsByDate.value[dateStr] = bookings
    
    // ✅ Update selected date with bookings
    if (selectedDate.value && format(selectedDate.value.date, 'yyyy-MM-dd') === dateStr) {
      selectedDate.value.bookings = bookings
    }
    
    // ✅ Update calendar events
    updateCalendarEvents()
    
    
    return bookings
    
  } catch (error) {
    return []
  }
}

const refreshCalendar = () => {
  availabilityData.value = {}
  bookingsByDate.value = {}
  initCalendar()
}

const closeDateDetails = () => {
  selectedDate.value = null
}

const openBlockModal = () => {
  blockReason.value = ''
  showBlockModal.value = true
}

const confirmBlock = async () => {
  if (!selectedDate.value || !blockReason.value.trim()) return
  
  try {
    await axios.put('/api/tour/admin/availability', {
      package_id: selectedPackageId.value,
      date: format(selectedDate.value.date, 'yyyy-MM-dd'),
      is_blocked: true,
      block_reason: blockReason.value
    })
    showBlockModal.value = false
    blockReason.value = ''
    await loadAvailability()
    closeDateDetails()
  } catch (error) {
    alert('Failed to block date')
  }
}

const unblockDate = async () => {
  if (!selectedDate.value) return
  
  if (!confirm(`Unblock ${formatFullDate(selectedDate.value.date)}?`)) return
  
  try {
    await axios.put('/api/tour/admin/availability', {
      package_id: selectedPackageId.value,
      date: format(selectedDate.value.date, 'yyyy-MM-dd'),
      is_blocked: false
    })
    await loadAvailability()
    closeDateDetails()
  } catch (error) {
    alert('Failed to unblock date')
  }
}

const viewBooking = (booking) => {
  selectedBooking.value = booking
}

const formatFullDate = (date) => {
  if (!date) return 'N/A'
  return format(new Date(date), 'EEEE, MMMM d, yyyy')
}

const handlePackageChange = () => {
  availabilityData.value = {}
  bookingsByDate.value = {}
  if (calendarInstance) {
    calendarInstance.removeAllEvents()
  }
  setTimeout(() => {
    if (selectedPackageId.value) {
      loadAvailability()
      loadBookingsForMonth()
    }
  }, 300)
}

// ============================================================
// WATCHERS
// ============================================================
watch(selectedPackageId, (newVal) => {
  if (newVal) {
    handlePackageChange()
  }
})

// ============================================================
// LIFECYCLE
// ============================================================
onMounted(async () => {
  await loadPackages()
  await nextTick()
  setTimeout(() => {
    initCalendar()
  }, 500)
})
</script>

<style scoped>
/* ... keep all existing styles ... */

/*   Has Bookings Dot */
.legend-dot.has-bookings {
  background: #3b82f6;
}

:deep(.fc-day-has-bookings .fc-daygrid-day-number) {
  color: #3b82f6 !important;
  font-weight: 700;
}

:deep(.fc-day-has-bookings) {
  position: relative;
}

:deep(.fc-day-has-bookings)::after {
  content: '';
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
}

.booking-count {
  font-size: 12px;
  color: #3b82f6;
  font-weight: 500;
  margin-left: 8px;
}

.booking-count i {
  margin-right: 4px;
}




.tour-manager-calendar {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Page Header */
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
  align-items: center;
  flex-wrap: wrap;
}

.package-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.package-selector label {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.package-selector select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  min-width: 180px;
}

.btn-refresh {
  padding: 8px 16px;
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

/* Legend */
.calendar-legend {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  background: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4b5563;
}

.legend-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.available { background: #10b981; }
.legend-dot.blocked { background: #6b7280; }
.legend-dot.today { background: #f59e0b; border: 2px solid #d97706; }

/* Calendar Container */
.calendar-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  min-height: 400px;
}

.calendar-wrapper {
  min-height: 400px;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
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

/* FullCalendar Custom Styles */
:deep(.fc) {
  font-family: inherit;
}

:deep(.fc-daygrid-day) {
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
  background: white;
}

:deep(.fc-daygrid-day:hover) {
  background: #f8fafc;
}

:deep(.fc-day-available .fc-daygrid-day-number) {
  color: #10b981;
}

:deep(.fc-day-blocked .fc-daygrid-day) {
  background: #f3f4f6 !important;
  opacity: 0.6;
}

:deep(.fc-day-blocked .fc-daygrid-day-number) {
  color: #9ca3af;
}

:deep(.fc-event) {
  border: none;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
}

:deep(.fc-event-available .fc-event) {
  background: #d1fae5 !important;
  color: #065f46 !important;
}

:deep(.fc-event-blocked .fc-event) {
  background: #e5e7eb !important;
  color: #6b7280 !important;
}

:deep(.fc-day-today) {
  background: #fef3c7 !important;
}

:deep(.fc-day-today .fc-daygrid-day-number) {
  color: #f59e0b !important;
  font-weight: 700;
}

:deep(.fc-daygrid-day-number) {
  font-size: 14px;
  font-weight: 500;
}

.event-title {
  font-size: 11px;
}

/* Modal */
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
  max-width: 600px;
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

.date-detail-content {
  padding: 24px;
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.date-header h2 {
  margin: 0;
  color: #1e3a8a;
  font-size: 1.2rem;
}

.date-header h2 i {
  color: #f59e0b;
  margin-right: 8px;
}

.date-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.date-status.available {
  background: #d1fae5;
  color: #065f46;
}

.date-status.blocked {
  background: #e5e7eb;
  color: #6b7280;
}

.date-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.date-actions button {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  min-width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-block {
  background: #ef4444;
  color: white;
}

.btn-block:hover {
  background: #dc2626;
}

.btn-unblock {
  background: #10b981;
  color: white;
}

.btn-unblock:hover {
  background: #059669;
}

.date-bookings {
  margin-top: 16px;
}

.date-bookings h4 {
  color: #1f2937;
  margin: 0 0 12px;
}

.booking-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 13px;
}

.booking-ref {
  font-weight: 600;
  color: #1e3a8a;
}

.booking-status {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: capitalize;
}

.booking-status.pending {
  background: #fef3c7;
  color: #92400e;
}

.booking-status.confirmed {
  background: #d1fae5;
  color: #065f46;
}

.booking-status.completed {
  background: #dbeafe;
  color: #1e40af;
}

.booking-status.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.booking-status.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.no-bookings {
  text-align: center;
  padding: 20px;
  color: #6b7280;
}

.no-bookings i {
  font-size: 32px;
  opacity: 0.3;
  display: block;
  margin-bottom: 8px;
}

/* Block Modal */
.block-modal .modal-body {
  padding: 20px 24px 24px;
}

.block-modal p {
  margin: 0 0 16px;
  color: #4b5563;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
  margin-bottom: 6px;
}

.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
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

.btn-danger {
  flex: 2;
  padding: 10px;
  background: #ef4444;
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

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .package-selector {
    width: 100%;
  }
  
  .package-selector select {
    flex: 1;
  }
  
  .btn-refresh {
    width: 100%;
    justify-content: center;
  }
  
  .calendar-legend {
    gap: 10px;
  }
  
  .legend-item {
    font-size: 12px;
  }
  
  .date-actions {
    flex-direction: column;
  }
  
  .date-actions button {
    width: 100%;
  }
  
  .modal-container {
    max-width: 100%;
    margin: 10px;
  }
}
</style>