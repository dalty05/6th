<!-- frontend/src/components/modals/CareersContent.vue -->
<template>
  <div class="careers-content">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading opportunities...</p>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="jobs.length === 0" class="empty-state">
      <i class="fas fa-briefcase"></i>
      <h4>No Current Openings</h4>
      <p>Check back later for job opportunities at Meru Dairy.</p>
      <p class="email-note">You can also send your CV to <strong>careers@merudairy.co.ke</strong></p>
    </div>
    
    <!-- Jobs List -->
    <div v-else class="jobs-list">
      <div v-for="job in jobs" :key="job.id" class="job-card">
        <div class="job-header">
          <div class="job-title-section">
            <h3>{{ job.title }}</h3>
            <span class="job-type" :class="getJobTypeClass(job.type)">
              {{ job.type || 'Full-time' }}
            </span>
          </div>
          <div class="job-deadline" v-if="job.application_deadline">
            <i class="fas fa-calendar-alt"></i> Deadline: {{ formatDate(job.application_deadline) }}
          </div>
        </div>
        
        <div class="job-meta">
          <span v-if="job.location">
            <i class="fas fa-map-marker-alt"></i> {{ job.location }}
          </span>
          <span v-if="job.experience_level">
            <i class="fas fa-chart-line"></i> {{ job.experience_level }}
          </span>
          <span v-if="job.salary_range">
            <i class="fas fa-money-bill-wave"></i> {{ job.salary_range }}
          </span>
        </div>
        
        <p class="job-description">{{ truncate(job.description, 200) }}</p>
        
        <div class="job-footer">
          <button @click="openApplicationForm(job)" class="btn-apply">
            <i class="fas fa-paper-plane"></i> Apply Now
          </button>
          <button @click="viewJobDetails(job)" class="btn-details">
            <i class="fas fa-info-circle"></i> View Details
          </button>
        </div>
      </div>
    </div>
    
    <!-- Job Detail Modal -->
    <div class="modal-overlay" v-if="showJobDetail" @click.self="closeDetailModal">
      <div class="modal-container modal-detail">
        <div class="modal-header">
          <div class="modal-header-content">
            <h2>{{ selectedJob?.title }}</h2>
            <div class="modal-job-meta">
              <span class="job-type" :class="getJobTypeClass(selectedJob?.type)">
                {{ selectedJob?.type || 'Full-time' }}
              </span>
              <span v-if="selectedJob?.location">
                <i class="fas fa-map-marker-alt"></i> {{ selectedJob.location }}
              </span>
              <span v-if="selectedJob?.experience_level">
                <i class="fas fa-chart-line"></i> {{ selectedJob.experience_level }}
              </span>
            </div>
          </div>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedJob">
          <div class="detail-grid">
            <!-- Left Column - Main Content -->
            <div class="detail-main">
              <!-- Description -->
              <div class="detail-section" v-if="selectedJob.description">
                <h4><i class="fas fa-align-left"></i> Job Description</h4>
                <div class="detail-content description-text" v-html="formatText(selectedJob.description)"></div>
              </div>
              
              <!-- Responsibilities -->
              <div class="detail-section" v-if="selectedJob.responsibilities">
                <h4><i class="fas fa-tasks"></i> Key Responsibilities</h4>
                <div class="detail-content" v-html="formatText(selectedJob.responsibilities)"></div>
              </div>
            </div>
            
            <!-- Right Column - Sidebar -->
            <div class="detail-sidebar">
              <!-- Requirements -->
              <div class="detail-section" v-if="selectedJob.requirements">
                <h4><i class="fas fa-check-circle"></i> Requirements</h4>
                <div class="detail-content requirements-list" v-html="formatText(selectedJob.requirements)"></div>
              </div>
              
              <!-- Benefits -->
              <div class="detail-section" v-if="selectedJob.benefits">
                <h4><i class="fas fa-gift"></i> Benefits</h4>
                <div class="detail-content" v-html="formatText(selectedJob.benefits)"></div>
              </div>
              
              <!-- Quick Info -->
              <div class="detail-section quick-info">
                <h4><i class="fas fa-info-circle"></i> Quick Info</h4>
                <div class="detail-content">
                  <div class="info-row" v-if="selectedJob.location">
                    <span class="info-label">Location:</span>
                    <span class="info-value">{{ selectedJob.location }}</span>
                  </div>
                  <div class="info-row" v-if="selectedJob.experience_level">
                    <span class="info-label">Experience:</span>
                    <span class="info-value">{{ selectedJob.experience_level }}</span>
                  </div>
                  <div class="info-row" v-if="selectedJob.salary_range">
                    <span class="info-label">Salary:</span>
                    <span class="info-value">{{ selectedJob.salary_range }}</span>
                  </div>
                  <div class="info-row" v-if="selectedJob.application_deadline">
                    <span class="info-label">Deadline:</span>
                    <span class="info-value">{{ formatDate(selectedJob.application_deadline) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="apply-actions">
            <button @click="closeDetailModal; openApplicationForm(selectedJob)" class="btn-apply-large">
              <i class="fas fa-paper-plane"></i> Apply for this Position
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Job Application Form Modal -->
    <div class="modal-overlay" v-if="showApplicationForm" @click.self="closeApplicationForm">
      <div class="modal-container modal-application">
        <div class="modal-header">
          <h2>Apply for {{ selectedJob?.title }}</h2>
          <button class="close-btn" @click="closeApplicationForm">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="application-info">
            <i class="fas fa-info-circle"></i>
            <p>Please fill out the form below to apply for this position. All fields marked with <span class="required">*</span> are required.</p>
          </div>
          
          <form @submit.prevent="submitApplication" class="application-form">
            <div class="form-row">
              <div class="form-group">
                <label>First Name <span class="required">*</span></label>
                <input type="text" v-model="application.first_name" placeholder="Enter your first name" required>
              </div>
              <div class="form-group">
                <label>Last Name <span class="required">*</span></label>
                <input type="text" v-model="application.last_name" placeholder="Enter your last name" required>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Email Address <span class="required">*</span></label>
                <input type="email" v-model="application.email" placeholder="your@email.com" required>
              </div>
              <div class="form-group">
                <label>Phone Number</label>
                <input type="tel" v-model="application.phone" placeholder="e.g., 0712 345 678">
              </div>
            </div>
            
            <div class="form-group">
              <label>Cover Letter <span class="required">*</span></label>
              <textarea v-model="application.cover_letter" rows="6" required 
                placeholder="Tell us why you're the ideal candidate for this position..."></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Upload CV/Resume <span class="required">*</span></label>
                <div class="file-upload-area" :class="{ 'has-file': cvFile }" @click="$refs.cvInput.click()">
                  <input type="file" ref="cvInput" @change="handleCVUpload" accept=".pdf,.doc,.docx" style="display: none">
                  <i class="fas fa-cloud-upload-alt"></i>
                  <p v-if="!cvFile">Click to upload or drag and drop</p>
                  <p v-else><i class="fas fa-file-pdf"></i> {{ cvFile.name }}</p>
                  <small>Accepted formats: PDF, DOC, DOCX (Max 5MB)</small>
                </div>
                <div v-if="cvError" class="error-text">{{ cvError }}</div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Portfolio URL (Optional)</label>
                <input type="url" v-model="application.portfolio_url" placeholder="https://yourportfolio.com">
              </div>
              <div class="form-group">
                <label>LinkedIn Profile (Optional)</label>
                <input type="url" v-model="application.linkedin_url" placeholder="https://linkedin.com/in/username">
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeApplicationForm" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit" :disabled="submitting">
                <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-paper-plane"></i>
                {{ submitting ? 'Submitting...' : 'Submit Application' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Success Modal -->
    <div class="modal-overlay" v-if="showSuccess" @click.self="showSuccess = false">
      <div class="modal-container modal-success">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h2>Application Submitted!</h2>
        <p>Thank you for applying to <strong>{{ successJobTitle }}</strong>.</p>
        <p>We have sent a confirmation email to your inbox. Our HR team will review your application and get back to you within 5-7 business days.</p>
        <button @click="showSuccess = false; closeApplicationForm()" class="btn-success">Done</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

const jobs = ref([])
const loading = ref(false)
const showJobDetail = ref(false)
const showApplicationForm = ref(false)
const showSuccess = ref(false)
const selectedJob = ref(null)
const submitting = ref(false)
const cvFile = ref(null)
const cvError = ref('')
const successJobTitle = ref('')

const application = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  cover_letter: '',
  portfolio_url: '',
  linkedin_url: ''
})

const loadJobs = async () => {
  loading.value = true
  try {
    const response = await api.get('/jobs', { params: { per_page: 20 } })
    jobs.value = response.data.data || []
  } catch (error) {
    console.error('Error loading jobs:', error)
    toast.error('Failed to load job opportunities')
  } finally {
    loading.value = false
  }
}

const viewJobDetails = (job) => {
  selectedJob.value = job
  showJobDetail.value = true
  document.body.style.overflow = 'hidden'
}

const closeDetailModal = () => {
  showJobDetail.value = false
  document.body.style.overflow = 'auto'
}

const openApplicationForm = (job) => {
  selectedJob.value = job
  closeDetailModal()
  showApplicationForm.value = true
  application.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    cover_letter: '',
    portfolio_url: '',
    linkedin_url: ''
  }
  cvFile.value = null
  cvError.value = ''
  document.body.style.overflow = 'hidden'
}

const closeApplicationForm = () => {
  showApplicationForm.value = false
  selectedJob.value = null
  cvFile.value = null
  document.body.style.overflow = 'auto'
}

const handleCVUpload = (event) => {
  const file = event.target.files[0]
  cvError.value = ''
  
  if (!file) return
  
  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  if (!allowedTypes.includes(file.type)) {
    cvError.value = 'Invalid file type. Please upload PDF, DOC, or DOCX'
    cvFile.value = null
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    cvError.value = 'File size must be less than 5MB'
    cvFile.value = null
    return
  }
  
  cvFile.value = file
}

const submitApplication = async () => {
  // Validate CV
  if (!cvFile.value) {
    cvError.value = 'Please upload your CV'
    return
  }
  
  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(application.value.email)) {
    toast.error('Please enter a valid email address')
    return
  }
  
  submitting.value = true
  
  const formData = new FormData()
  formData.append('first_name', application.value.first_name)
  formData.append('last_name', application.value.last_name)
  formData.append('email', application.value.email)
  formData.append('phone', application.value.phone || '')
  formData.append('cover_letter', application.value.cover_letter)
  formData.append('portfolio_url', application.value.portfolio_url || '')
  formData.append('linkedin_url', application.value.linkedin_url || '')
  formData.append('cv', cvFile.value)
  
  try {
    await api.post(`/jobs/${selectedJob.value.id}/apply`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    successJobTitle.value = selectedJob.value.title
    showApplicationForm.value = false
    showSuccess.value = true
  } catch (error) {
    console.error('Application error:', error)
    toast.error(error.response?.data?.error || 'Failed to submit application. Please try again.')
  } finally {
    submitting.value = false
  }
}

const getJobTypeClass = (type) => {
  const classes = {
    'Full-time': 'type-fulltime',
    'Part-time': 'type-parttime',
    'Remote': 'type-remote',
    'Contract': 'type-contract',
    'Internship': 'type-internship'
  }
  return classes[type] || 'type-fulltime'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not specified'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const truncate = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const formatText = (text) => {
  if (!text) return ''
  return text.replace(/\n/g, '<br>')
}

onMounted(() => {
  loadJobs()
})
</script>

<style scoped>
.careers-content {
  padding: 0;
}

/* Loading & Empty States */
.loading-state, .empty-state {
  text-align: center;
  padding: 3rem 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state i {
  font-size: 4rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.empty-state h4 {
  font-size: 1.25rem;
  margin: 0 0 0.5rem;
  color: #1e3a8a;
}

.empty-state p {
  color: #6b7280;
  margin: 0;
}

.email-note {
  margin-top: 1rem !important;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

/* Jobs List */
.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.job-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  border-color: #f59e0b;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.job-title-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.job-title-section h3 {
  color: #1e3a8a;
  margin: 0;
  font-size: 1.25rem;
}

.job-type {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.type-fulltime {
  background: #d1fae5;
  color: #065f46;
}
.type-parttime {
  background: #fef3c7;
  color: #92400e;
}
.type-remote {
  background: #dbeafe;
  color: #1e40af;
}
.type-contract {
  background: #fed7aa;
  color: #9a3412;
}
.type-internship {
  background: #e0e7ff;
  color: #3730a3;
}

.job-deadline {
  font-size: 0.75rem;
  color: #ef4444;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.job-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.job-meta i {
  margin-right: 0.25rem;
  width: 14px;
}

.job-description {
  color: #4b5563;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.job-footer {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-apply, .btn-details {
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-apply {
  background: #1e3a8a;
  color: white;
  border: none;
}

.btn-apply:hover {
  background: #f59e0b;
  transform: translateY(-2px);
}

.btn-details {
  background: white;
  color: #1e3a8a;
  border: 1px solid #1e3a8a;
}

.btn-details:hover {
  background: #1e3a8a;
  color: white;
}

/* ========================================
   MODAL OVERLAY & CONTAINER - FIXED HEIGHT
   ======================================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1.5rem;
  animation: fadeIn 0.25s ease;
}

.modal-container {
  background: white;
  border-radius: 20px;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
  box-shadow: 0 25px 50px rgba(0,0,0,0.25);
  overflow: hidden;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ========================================
   JOB DETAIL MODAL - FIXED HEIGHT
   ======================================== */
.modal-detail {
  max-width: 1000px;
  width: 100%;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #e5e7eb;
  flex-shrink: 0;
  background: white;
}

.modal-header-content h2 {
  color: #1e3a8a;
  margin: 0 0 0.5rem;
  font-size: 1.6rem;
}

.modal-job-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #6b7280;
}

.modal-job-meta i {
  margin-right: 0.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #9ca3af;
  transition: all 0.3s;
  line-height: 1;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  flex-shrink: 0;
}

.close-btn:hover {
  color: #ef4444;
  background: #fee2e2;
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Detail Grid - Two Column */
.detail-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 2rem;
  align-items: start;
}

.detail-main {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 0;
}

.detail-section {
  background: #f8fafc;
  border-radius: 14px;
  padding: 1.25rem;
  border: 1px solid #e5e7eb;
}

.detail-section h4 {
  color: #1e3a8a;
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-section h4 i {
  color: #f59e0b;
}

.detail-content {
  color: #4b5563;
  line-height: 1.7;
  font-size: 0.9rem;
}

.description-text {
  font-size: 0.95rem;
  line-height: 1.8;
}

.requirements-list {
  padding-left: 0.5rem;
}

.requirements-list p {
  margin-bottom: 0.5rem;
}

/* Quick Info */
.quick-info .detail-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #1e3a8a;
}

.info-value {
  color: #4b5563;
  text-align: right;
}

/* Apply Actions */
.apply-actions {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e5e7eb;
  text-align: center;
  flex-shrink: 0;
}

.btn-apply-large {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.8rem 2.5rem;
  border-radius: 40px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.btn-apply-large:hover {
  background: #f59e0b;
  transform: scale(1.02);
}

/* ========================================
   APPLICATION FORM MODAL - FIXED HEIGHT
   ======================================== */
.modal-application {
  max-width: 750px;
  width: 100%;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}

.modal-application .modal-header {
  flex-shrink: 0;
}

.modal-application .modal-body {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.application-info {
  background: #e0e7ff;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.application-info i {
  color: #1e3a8a;
  font-size: 1.2rem;
  margin-top: 0.1rem;
}

.application-info p {
  margin: 0;
  color: #1e3a8a;
  font-size: 0.9rem;
}

.required {
  color: #ef4444;
}

.application-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 0.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
  color: #374151;
  font-size: 0.85rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.9rem;
  transition: all 0.3s;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.file-upload-area {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f8fafc;
}

.file-upload-area:hover {
  border-color: #f59e0b;
  background: #fef3c7;
}

.file-upload-area.has-file {
  border-color: #10b981;
  background: #d1fae5;
}

.file-upload-area i {
  font-size: 2rem;
  color: #9ca3af;
  margin-bottom: 0.5rem;
}

.file-upload-area p {
  margin: 0;
  font-size: 0.9rem;
  color: #6b7280;
}

.file-upload-area small {
  font-size: 0.7rem;
  color: #9ca3af;
  display: block;
  margin-top: 0.25rem;
}

.error-text {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.btn-cancel {
  background: #e5e7eb;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: #d1d5db;
}

.btn-submit {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.btn-submit:hover:not(:disabled) {
  background: #f59e0b;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ========================================
   SUCCESS MODAL
   ======================================== */
.modal-success {
  max-width: 450px;
  width: 100%;
  text-align: center;
  padding: 2.5rem;
  max-height: 92vh;
  overflow-y: auto;
}

.success-icon {
  font-size: 4rem;
  color: #10b981;
  margin-bottom: 1rem;
}

.modal-success h2 {
  color: #1e3a8a;
  margin: 0 0 0.5rem;
  font-size: 1.4rem;
}

.modal-success p {
  color: #6b7280;
  margin: 0.5rem 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

.btn-success {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.7rem 2rem;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 600;
  margin-top: 1rem;
  transition: all 0.3s;
}

.btn-success:hover {
  background: #059669;
}

/* ========================================
   RESPONSIVE
   ======================================== */
@media (max-width: 968px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .detail-sidebar {
    position: static;
  }
  
  .modal-detail {
    max-width: 95%;
  }
  
  .modal-header {
    padding: 1rem 1.25rem;
  }
  
  .modal-header-content h2 {
    font-size: 1.3rem;
  }
  
  .modal-body {
    padding: 1.25rem;
  }
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .modal-application {
    max-width: 98%;
  }
  
  .job-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .job-footer {
    flex-direction: column;
  }
  
  .btn-apply, .btn-details {
    width: 100%;
    justify-content: center;
  }
  
  .modal-job-meta {
    flex-wrap: wrap;
  }
  
  .modal-success {
    padding: 1.5rem;
  }
  
  .modal-success h2 {
    font-size: 1.2rem;
  }
  
  .file-upload-area {
    padding: 1rem;
  }
  
  .modal-container {
    max-height: 95vh;
  }
  
  .modal-detail {
    max-height: 95vh;
  }
  
  .modal-application {
    max-height: 95vh;
  }
}

@media (max-width: 480px) {
  .modal-detail {
    max-width: 100%;
    border-radius: 12px;
  }
  
  .modal-header {
    padding: 0.75rem 1rem;
  }
  
  .modal-header-content h2 {
    font-size: 1.1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .detail-section {
    padding: 0.75rem;
  }
  
  .job-card {
    padding: 1rem;
  }
  
  .modal-overlay {
    padding: 0.5rem;
  }
}
</style>