<template>
  <main class="job-detail-page">
    <div class="container" v-if="job">
      <div class="job-header">
        <button class="back-btn" @click="$router.back()">
          <i class="fas fa-arrow-left"></i> Back to Jobs
        </button>
        <div class="job-title-section">
          <h1>{{ job.title }}</h1>
          <div class="job-meta">
            <span v-if="job.location"><i class="fas fa-map-marker-alt"></i> {{ job.location }}</span>
            <span v-if="job.type"><i class="fas fa-briefcase"></i> {{ job.type }}</span>
            <span v-if="job.experience_level"><i class="fas fa-chart-line"></i> {{ job.experience_level }}</span>
            <span v-if="job.salary_range"><i class="fas fa-money-bill-wave"></i> {{ job.salary_range }}</span>
          </div>
        </div>
      </div>

      <div class="job-content">
        <div class="main-content">
          <section class="job-section">
            <h2>Job Description</h2>
            <div class="job-description" v-html="job.description"></div>
          </section>

          <section class="job-section" v-if="job.responsibilities">
            <h2>Key Responsibilities</h2>
            <div class="job-responsibilities" v-html="job.responsibilities"></div>
          </section>

          <section class="job-section">
            <h2>Requirements</h2>
            <div class="job-requirements" v-html="job.requirements"></div>
          </section>

          <section class="job-section" v-if="job.benefits">
            <h2>Benefits</h2>
            <div class="job-benefits" v-html="job.benefits"></div>
          </section>
        </div>

        <div class="sidebar">
          <div class="apply-card">
            <h3>Apply for this position</h3>
            <p>Deadline: <strong>{{ formatDate(job.application_deadline) }}</strong></p>
            <button @click="openApplicationModal" class="btn-apply">Apply Now</button>
          </div>

          <div class="info-card">
            <h4>Job Summary</h4>
            <ul>
              <li><strong>Job Type:</strong> {{ job.type || 'Not specified' }}</li>
              <li><strong>Location:</strong> {{ job.location || 'Not specified' }}</li>
              <li><strong>Experience:</strong> {{ job.experience_level || 'Not specified' }}</li>
              <li><strong>Posted:</strong> {{ formatDate(job.created_at) }}</li>
              <li><strong>Views:</strong> {{ job.views_count }} views</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Application Modal -->
    <div class="modal" v-if="showModal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Apply for {{ job?.title }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>

        <form @submit.prevent="submitApplication" class="application-form">
          <div class="form-row">
            <div class="form-group">
              <label>First Name *</label>
              <input type="text" v-model="application.first_name" required>
            </div>
            <div class="form-group">
              <label>Last Name *</label>
              <input type="text" v-model="application.last_name" required>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Email *</label>
              <input type="email" v-model="application.email" required>
            </div>
            <div class="form-group">
              <label>Phone</label>
              <input type="tel" v-model="application.phone">
            </div>
          </div>

          <div class="form-group">
            <label>Cover Letter *</label>
            <textarea v-model="application.cover_letter" rows="5" required placeholder="Tell us why you're the right candidate for this position..."></textarea>
          </div>

          <div class="form-group">
            <label>CV / Resume * (PDF, DOC, DOCX only)</label>
            <input type="file" @change="handleFileUpload" accept=".pdf,.doc,.docx" required>
            <small v-if="cvFile">{{ cvFile.name }}</small>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Portfolio URL (Optional)</label>
              <input type="url" v-model="application.portfolio_url" placeholder="https://...">
            </div>
            <div class="form-group">
              <label>LinkedIn URL (Optional)</label>
              <input type="url" v-model="application.linkedin_url" placeholder="https://...">
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="submitting">
              {{ submitting ? 'Submitting...' : 'Submit Application' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import { jobApi } from '@/services/api'

const route = useRoute()
const router = useRouter()
const job = ref(null)
const showModal = ref(false)
const submitting = ref(false)
const cvFile = ref(null)

const application = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  cover_letter: '',
  portfolio_url: '',
  linkedin_url: ''
})

const loadJob = async () => {
  try {
    const slug = route.params.slug
    const response = await jobApi.getJob(slug)
    job.value = response.data
  } catch (error) {
    console.error('Error loading job:', error)
    router.push('/jobs')
  }
}

const openApplicationModal = () => {
  if (job.value.application_deadline && new Date(job.value.application_deadline) < new Date()) {
    toast.error('The application deadline has passed')
    return
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
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
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      toast.error('Invalid file type. Please upload PDF, DOC, or DOCX')
      event.target.value = ''
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB')
      event.target.value = ''
      return
    }
    cvFile.value = file
  }
}

const submitApplication = async () => {
  if (!cvFile.value) {
    toast.error('Please upload your CV')
    return
  }

  submitting.value = true

  const formData = new FormData()
  formData.append('first_name', application.value.first_name)
  formData.append('last_name', application.value.last_name)
  formData.append('email', application.value.email)
  formData.append('phone', application.value.phone)
  formData.append('cover_letter', application.value.cover_letter)
  formData.append('portfolio_url', application.value.portfolio_url)
  formData.append('linkedin_url', application.value.linkedin_url)
  formData.append('cv', cvFile.value)

  try {
    await jobApi.applyForJob(job.value.id, formData)
    toast.success('Application submitted successfully! You will receive a confirmation email.')
    closeModal()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to submit application')
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not specified'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(() => {
  loadJob()
})
</script>

<style scoped>
.job-detail-page {
  padding: 4rem 0;
  background: #f8fafc;
  min-height: 70vh;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

.back-btn {
  background: none;
  border: none;
  color: #1e3a8a;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.back-btn:hover {
  color: #3b82f6;
}

.job-title-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.job-title-section h1 {
  font-size: 2rem;
  color: #1e3a8a;
  margin-bottom: 1rem;
}

.job-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  color: #6b7280;
}

.job-meta i {
  margin-right: 0.5rem;
}

.job-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.main-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.job-section {
  margin-bottom: 2rem;
}

.job-section h2 {
  color: #1e3a8a;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.job-description,
.job-requirements,
.job-responsibilities,
.job-benefits {
  line-height: 1.6;
  color: #4b5563;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.apply-card, .info-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.apply-card h3 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.apply-card p {
  margin-bottom: 1rem;
  color: #ef4444;
}

.btn-apply {
  width: 100%;
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
}

.btn-apply:hover {
  background: #3b82f6;
}

.info-card h4 {
  color: #1e3a8a;
  margin-bottom: 1rem;
}

.info-card ul {
  list-style: none;
  padding: 0;
}

.info-card li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

/* Modal Styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  color: #1e3a8a;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.application-form {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1e3a8a;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-cancel {
  background: #e5e7eb;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-submit {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .job-content {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .job-title-section h1 {
    font-size: 1.5rem;
  }
  
  .job-meta {
    font-size: 0.875rem;
    gap: 1rem;
  }
}
</style>