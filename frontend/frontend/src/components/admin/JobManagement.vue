<!-- frontend/src/components/admin/JobManagement.vue -->
<template>
  <div class="job-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1>Job Management</h1>
        <p>Manage job postings, track applications, and communicate with candidates</p>
      </div>
      <button @click="openCreateModal" class="btn-create">
        <i class="fas fa-plus"></i> Create New Job
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <i class="fas fa-briefcase"></i>
        </div>
        <div class="stat-info">
          <h3>{{ jobs.length }}</h3>
          <p>Total Jobs</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-info">
          <h3>{{ applications.length }}</h3>
          <p>Total Applications</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <i class="fas fa-hourglass-half"></i>
        </div>
        <div class="stat-info">
          <h3>{{ pendingApplications }}</h3>
          <p>Pending Review</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-info">
          <h3>{{ hiredApplications }}</h3>
          <p>Hired</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'jobs' }" 
        @click="activeTab = 'jobs'; loadJobs()"
      >
        <i class="fas fa-briefcase"></i> Jobs
        <span class="badge">{{ jobs.length }}</span>
      </button>
      <button 
        :class="{ active: activeTab === 'applications' }" 
        @click="activeTab = 'applications'; loadApplications()"
      >
        <i class="fas fa-file-alt"></i> Applications
        <span class="badge">{{ applications.length }}</span>
      </button>
      <button 
        :class="{ active: activeTab === 'categories' }" 
        @click="activeTab = 'categories'; loadCategories()"
      >
        <i class="fas fa-tags"></i> Categories
      </button>
    </div>

    <!-- ========== JOBS TAB ========== -->
    <div v-if="activeTab === 'jobs'" class="jobs-tab">
      <div class="jobs-grid">
        <div v-for="job in jobs" :key="job.id" class="job-card">
          <div class="job-card-header">
            <div class="job-title">
              <h3>{{ job.title }}</h3>
              <span :class="['status-badge', job.is_active ? 'active' : 'inactive']">
                {{ job.is_active ? 'Active' : 'Closed' }}
              </span>
            </div>
            <div class="job-actions">
              <button @click="editJob(job)" class="icon-btn edit" title="Edit Job">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="deleteJob(job.id)" class="icon-btn delete" title="Delete Job">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          
          <div class="job-card-body">
            <div class="job-meta">
              <span><i class="fas fa-folder"></i> {{ job.category_name || 'Uncategorized' }}</span>
              <span><i class="fas fa-briefcase"></i> {{ job.type || 'Not specified' }}</span>
              <span><i class="fas fa-map-marker-alt"></i> {{ job.location || 'Remote' }}</span>
            </div>
            <div class="job-stats">
              <span><i class="fas fa-eye"></i> {{ job.views_count || 0 }} views</span>
              <span><i class="fas fa-file-alt"></i> {{ job.applications_count || 0 }} applications</span>
              <span><i class="fas fa-calendar"></i> Deadline: {{ formatDate(job.application_deadline) }}</span>
            </div>
          </div>
          
          <div class="job-card-footer">
            <button @click="viewJobDetails(job)" class="btn-outline">
              <i class="fas fa-info-circle"></i> View Details
            </button>
            <button @click="activeTab = 'applications'; loadApplications(job.id)" class="btn-primary-small">
              <i class="fas fa-users"></i> View Applications
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== APPLICATIONS TAB ========== -->
    <div v-if="activeTab === 'applications'" class="applications-tab">
      <div class="filters-bar">
        <div class="filter-group">
          <i class="fas fa-filter"></i>
          <select v-model="appFilters.status" @change="loadApplications">
            <option value="">All Status</option>
            <option value="pending">📋 Pending</option>
            <option value="reviewed">👁️ Reviewed</option>
            <option value="shortlisted">⭐ Shortlisted</option>
            <option value="rejected">❌ Rejected</option>
            <option value="hired">✅ Hired</option>
          </select>
        </div>
        <div class="filter-group">
          <i class="fas fa-briefcase"></i>
          <select v-model="appFilters.job_id" @change="loadApplications">
            <option value="">All Jobs</option>
            <option v-for="job in jobs" :key="job.id" :value="job.id">
              {{ job.title }}
            </option>
          </select>
        </div>
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input type="text" v-model="appFilters.search" placeholder="Search by name or email..." @input="debouncedSearch">
        </div>
      </div>

      <div class="applications-grid">
        <div v-for="app in paginatedApplications" :key="app.id" class="application-card">
          <div class="application-header">
            <div class="applicant-avatar">
              <span>{{ getInitials(app.applicant_name) }}</span>
            </div>
            <div class="applicant-info">
              <h4>{{ app.applicant_name }}</h4>
              <p><i class="fas fa-envelope"></i> {{ app.email }}</p>
              <p v-if="app.phone"><i class="fas fa-phone"></i> {{ app.phone }}</p>
            </div>
            <div :class="['status-badge', getStatusClass(app.status)]">
              {{ getStatusText(app.status) }}
            </div>
          </div>
          
          <div class="application-body">
            <div class="application-job">
              <i class="fas fa-briefcase"></i> Applied for: <strong>{{ app.job_title }}</strong>
            </div>
            <div class="application-date">
              <i class="fas fa-calendar"></i> {{ formatDate(app.applied_at) }}
            </div>
            <div class="application-cover">
              <i class="fas fa-quote-left"></i> {{ truncate(app.cover_letter, 120) }}
            </div>
          </div>
          
          <div class="application-footer">
            <a :href="'http://localhost:5000' + app.cv_url" target="_blank" class="btn-cv">
              <i class="fas fa-download"></i> Download CV
            </a>
            <button @click="viewApplicationDetails(app)" class="btn-view">
              <i class="fas fa-eye"></i> View Details
            </button>
            <select :value="app.status" @change="updateStatus(app.id, $event.target.value)" class="status-select">
              <option value="pending">📋 Pending</option>
              <option value="reviewed">👁️ Reviewed</option>
              <option value="shortlisted">⭐ Shortlisted</option>
              <option value="rejected">❌ Rejected</option>
              <option value="hired">✅ Hired</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="filteredApplications.length > 10">
        <button @click="currentPage--" :disabled="currentPage === 1" class="page-btn">
          <i class="fas fa-chevron-left"></i>
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="currentPage++" :disabled="currentPage === totalPages" class="page-btn">
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- ========== CATEGORIES TAB ========== -->
    <div v-if="activeTab === 'categories'" class="categories-tab">
      <div class="category-form-card">
        <h3><i class="fas fa-plus-circle"></i> Add New Category</h3>
        <div class="category-form">
          <input type="text" v-model="newCategory.name" placeholder="Category name">
          <input type="text" v-model="newCategory.slug" placeholder="Slug (url-friendly)">
          <input type="text" v-model="newCategory.icon" placeholder="Icon emoji (e.g., 📈)">
          <textarea v-model="newCategory.description" placeholder="Description" rows="2"></textarea>
          <button @click="createCategory" class="btn-create-category">
            <i class="fas fa-plus"></i> Add Category
          </button>
        </div>
      </div>

      <div class="categories-grid">
        <div v-for="cat in categories" :key="cat.id" class="category-card">
          <div class="category-icon">{{ cat.icon || '📁' }}</div>
          <div class="category-info">
            <h4>{{ cat.name }}</h4>
            <p>{{ cat.description || 'No description' }}</p>
            <span class="job-count">{{ cat.job_count }} jobs</span>
          </div>
          <div class="category-actions">
            <span :class="['status-badge', cat.is_active ? 'active' : 'inactive']">
              {{ cat.is_active ? 'Active' : 'Inactive' }}
            </span>
            <button @click="toggleCategoryStatus(cat)" class="icon-btn" :title="cat.is_active ? 'Disable' : 'Enable'">
              <i :class="cat.is_active ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
            <button @click="deleteCategory(cat.id)" class="icon-btn delete" title="Delete">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== JOB DETAIL MODAL ========== -->
    <div class="modal-overlay" v-if="showJobDetailModal" @click.self="closeJobDetailModal">
      <div class="modal-container large">
        <div class="modal-header">
          <h2>{{ selectedJob?.title }}</h2>
          <button class="close-btn" @click="closeJobDetailModal">&times;</button>
        </div>
        <div class="modal-body" v-if="selectedJob">
          <div class="detail-grid">
            <div class="detail-section full-width">
              <h4><i class="fas fa-align-left"></i> Description</h4>
              <p>{{ selectedJob.description }}</p>
            </div>
            <div class="detail-section">
              <h4><i class="fas fa-check-circle"></i> Requirements</h4>
              <p>{{ selectedJob.requirements }}</p>
            </div>
            <div class="detail-section" v-if="selectedJob.responsibilities">
              <h4><i class="fas fa-tasks"></i> Responsibilities</h4>
              <p>{{ selectedJob.responsibilities }}</p>
            </div>
            <div class="detail-section" v-if="selectedJob.benefits">
              <h4><i class="fas fa-gift"></i> Benefits</h4>
              <p>{{ selectedJob.benefits }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeJobDetailModal" class="btn-secondary">Close</button>
            <button @click="editJob(selectedJob); closeJobDetailModal()" class="btn-primary">Edit Job</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== APPLICATION DETAIL MODAL ========== -->
    <div class="modal-overlay" v-if="showApplicationDetailModal" @click.self="closeApplicationDetailModal">
      <div class="modal-container application-detail-modal">
        <div class="modal-header">
          <h2>Application Details</h2>
          <button class="close-btn" @click="closeApplicationDetailModal">&times;</button>
        </div>
        <div class="modal-body" v-if="selectedApplication">
          <!-- Applicant Info -->
          <div class="detail-card">
            <div class="detail-card-header">
              <div class="applicant-large-avatar">
                {{ getInitials(selectedApplication.applicant_name) }}
              </div>
              <div class="applicant-large-info">
                <h3>{{ selectedApplication.applicant_name }}</h3>
                <p><i class="fas fa-envelope"></i> {{ selectedApplication.email }}</p>
                <p v-if="selectedApplication.phone"><i class="fas fa-phone"></i> {{ selectedApplication.phone }}</p>
                <div :class="['status-badge large', getStatusClass(selectedApplication.status)]">
                  {{ getStatusText(selectedApplication.status) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Job Info -->
          <div class="detail-card">
            <h4><i class="fas fa-briefcase"></i> Position Applied</h4>
            <p><strong>{{ selectedApplication.job_title }}</strong></p>
            <p><i class="fas fa-calendar"></i> Applied on {{ formatDate(selectedApplication.applied_at) }}</p>
          </div>

          <!-- Cover Letter -->
          <div class="detail-card">
            <h4><i class="fas fa-envelope-open-text"></i> Cover Letter</h4>
            <div class="cover-letter">
              {{ selectedApplication.cover_letter }}
            </div>
          </div>

          <!-- CV Download -->
          <div class="detail-card">
            <h4><i class="fas fa-file-pdf"></i> CV / Resume</h4>
            <a :href="'http://localhost:5000' + selectedApplication.cv_url" target="_blank" class="btn-download">
              <i class="fas fa-download"></i> Download CV
            </a>
          </div>

          <!-- Portfolio & LinkedIn -->
          <div class="detail-row" v-if="selectedApplication.portfolio_url || selectedApplication.linkedin_url">
            <div class="detail-card half" v-if="selectedApplication.portfolio_url">
              <h4><i class="fas fa-folder-open"></i> Portfolio</h4>
              <a :href="selectedApplication.portfolio_url" target="_blank" class="external-link">
                {{ selectedApplication.portfolio_url }}
              </a>
            </div>
            <div class="detail-card half" v-if="selectedApplication.linkedin_url">
              <h4><i class="fab fa-linkedin"></i> LinkedIn</h4>
              <a :href="selectedApplication.linkedin_url" target="_blank" class="external-link">
                {{ selectedApplication.linkedin_url }}
              </a>
            </div>
          </div>

          <!-- Admin Notes & Rating -->
          <div class="detail-card">
            <h4><i class="fas fa-sticky-note"></i> Admin Notes</h4>
            <textarea v-model="appNotes" rows="3" placeholder="Add internal notes about this candidate..."></textarea>
            <div class="rating-section">
              <label>Rating:</label>
              <div class="stars">
                <i v-for="star in 5" :key="star" 
                   :class="['fas fa-star', star <= (appRating || 0) ? 'filled' : '']"
                   @click="appRating = star"></i>
              </div>
            </div>
            <button @click="saveAppNotes" class="btn-save-notes">
              <i class="fas fa-save"></i> Save Notes
            </button>
          </div>

          <!-- Reply to Applicant -->
          <div class="detail-card">
            <h4><i class="fas fa-reply"></i> Reply to Applicant</h4>
            <textarea v-model="appReply" rows="4" placeholder="Write your reply message here..."></textarea>
            <button @click="sendReply" class="btn-send-reply">
              <i class="fas fa-paper-plane"></i> Send Reply
            </button>
            <div v-if="selectedApplication.admin_reply" class="previous-reply">
              <hr>
              <p><strong>Previous reply sent on {{ formatDate(selectedApplication.replied_at) }}:</strong></p>
              <p>{{ selectedApplication.admin_reply }}</p>
            </div>
          </div>

          <!-- Update Status -->
          <div class="detail-card">
            <h4><i class="fas fa-exchange-alt"></i> Update Status</h4>
            <div class="status-options">
              <button v-for="status in statusOptions" :key="status.value"
                :class="['status-option', { active: selectedApplication.status === status.value }]"
                @click="updateStatus(selectedApplication.id, status.value)">
                <i :class="status.icon"></i> {{ status.label }}
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeApplicationDetailModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- ========== CREATE/EDIT JOB MODAL ========== -->
    <div class="modal-overlay" v-if="showJobModal" @click.self="closeJobModal">
      <div class="modal-container large">
        <div class="modal-header">
          <h2>{{ editingJob ? 'Edit Job' : 'Create New Job' }}</h2>
          <button class="close-btn" @click="closeJobModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveJob" class="job-form">
            <div class="form-row">
              <div class="form-group full">
                <label>Job Title *</label>
                <input type="text" v-model="jobForm.title" required placeholder="e.g., Senior Dairy Technologist">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Slug</label>
                <input type="text" v-model="jobForm.slug" placeholder="auto-generated">
              </div>
              <div class="form-group">
                <label>Category</label>
                <select v-model="jobForm.category_id">
                  <option :value="null">Select Category</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Location</label>
                <input type="text" v-model="jobForm.location" placeholder="e.g., Meru, Kenya">
              </div>
              <div class="form-group">
                <label>Job Type</label>
                <select v-model="jobForm.type">
                  <option value="">Select Type</option>
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Remote">Remote</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Experience Level</label>
                <select v-model="jobForm.experience_level">
                  <option value="">Select Level</option>
                  <option value="Entry">Entry Level</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Senior">Senior Level</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
              <div class="form-group">
                <label>Salary Range</label>
                <input type="text" v-model="jobForm.salary_range" placeholder="e.g., KES 50,000 - 80,000">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Application Deadline</label>
                <input type="datetime-local" v-model="jobForm.application_deadline">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label>Description *</label>
                <textarea v-model="jobForm.description" rows="4" required placeholder="Detailed job description..."></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label>Requirements *</label>
                <textarea v-model="jobForm.requirements" rows="4" required placeholder="List requirements..."></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label>Responsibilities</label>
                <textarea v-model="jobForm.responsibilities" rows="3" placeholder="Key responsibilities..."></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label>Benefits</label>
                <textarea v-model="jobForm.benefits" rows="3" placeholder="Benefits and perks..."></textarea>
              </div>
            </div>
            <div class="form-row checkbox-row">
              <label class="checkbox-label">
                <input type="checkbox" v-model="jobForm.is_active"> Active (visible to applicants)
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="jobForm.is_featured"> Featured (highlighted)
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeJobModal" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ editingJob ? 'Update Job' : 'Create Job' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

// API endpoints
const adminJobApi = {
  getJobs: () => api.get('/admin/jobs'),
  createJob: (data) => api.post('/admin/jobs', data),
  updateJob: (id, data) => api.put(`/admin/jobs/${id}`, data),
  deleteJob: (id) => api.delete(`/admin/jobs/${id}`),
}

const adminJobCategoryApi = {
  getCategories: () => api.get('/admin/job-categories'),
  createCategory: (data) => api.post('/admin/job-categories', data),
  updateCategory: (id, data) => api.put(`/admin/job-categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/admin/job-categories/${id}`),
}

const adminApplicationApi = {
  getApplications: (params) => api.get('/admin/applications', { params }),
  updateStatus: (id, data) => api.put(`/admin/applications/${id}/status`, data),
  replyToApplication: (id, reply) => api.post(`/admin/applications/${id}/reply`, { reply }),
}

// State
const activeTab = ref('jobs')
const jobs = ref([])
const applications = ref([])
const categories = ref([])
const loading = ref(false)

// Modals
const showJobModal = ref(false)
const showJobDetailModal = ref(false)
const showApplicationDetailModal = ref(false)
const editingJob = ref(null)
const selectedJob = ref(null)
const selectedApplication = ref(null)

// Form data
const jobForm = ref({
  title: '', slug: '', category_id: null, location: '', type: '', experience_level: '',
  salary_range: '', description: '', requirements: '', responsibilities: '', benefits: '',
  application_deadline: '', is_active: true, is_featured: false
})

const newCategory = ref({ name: '', slug: '', icon: '', description: '' })
const appNotes = ref('')
const appRating = ref(null)
const appReply = ref('')

// Filters & Pagination
const appFilters = ref({ status: '', job_id: '', search: '' })
const currentPage = ref(1)
const itemsPerPage = 10
let searchTimeout = null

const statusOptions = [
  { value: 'pending', label: 'Pending', icon: 'fas fa-hourglass-half' },
  { value: 'reviewed', label: 'Reviewed', icon: 'fas fa-check-circle' },
  { value: 'shortlisted', label: 'Shortlisted', icon: 'fas fa-star' },
  { value: 'rejected', label: 'Rejected', icon: 'fas fa-times-circle' },
  { value: 'hired', label: 'Hired', icon: 'fas fa-user-check' }
]

// Computed
const pendingApplications = computed(() => applications.value.filter(a => a.status === 'pending').length)
const hiredApplications = computed(() => applications.value.filter(a => a.status === 'hired').length)

const filteredApplications = computed(() => {
  let filtered = [...applications.value]
  if (appFilters.value.search) {
    const search = appFilters.value.search.toLowerCase()
    filtered = filtered.filter(a => 
      a.applicant_name.toLowerCase().includes(search) || 
      a.email.toLowerCase().includes(search)
    )
  }
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredApplications.value.length / itemsPerPage))
const paginatedApplications = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredApplications.value.slice(start, start + itemsPerPage)
})

// Methods
const loadJobs = async () => {
  try {
    const response = await adminJobApi.getJobs()
    jobs.value = response.data
  } catch (error) {
    
  }
}

const loadApplications = async (jobId = null) => {
  try {
    const params = {}
    if (appFilters.value.status) params.status = appFilters.value.status
    if (jobId || appFilters.value.job_id) params.job_id = jobId || appFilters.value.job_id
    const response = await adminApplicationApi.getApplications(params)
    applications.value = response.data
    currentPage.value = 1
  } catch (error) {
    
  }
}

const loadCategories = async () => {
  try {
    const response = await adminJobCategoryApi.getCategories()
    categories.value = response.data
  } catch (error) {
    
  }
}

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 300)
}

const openCreateModal = () => {
  editingJob.value = null
  jobForm.value = {
    title: '', slug: '', category_id: null, location: '', type: '', experience_level: '',
    salary_range: '', description: '', requirements: '', responsibilities: '', benefits: '',
    application_deadline: '', is_active: true, is_featured: false
  }
  showJobModal.value = true
}

const editJob = (job) => {
  editingJob.value = job
  jobForm.value = { ...job }
  if (job.application_deadline) {
    jobForm.value.application_deadline = job.application_deadline.slice(0, 16)
  }
  showJobModal.value = true
}

const viewJobDetails = (job) => {
  selectedJob.value = job
  showJobDetailModal.value = true
}

const viewApplicationDetails = (app) => {
  selectedApplication.value = app
  appNotes.value = app.admin_notes || ''
  appRating.value = app.rating
  appReply.value = ''
  showApplicationDetailModal.value = true
}

const saveJob = async () => {
  try {
    if (editingJob.value) {
      await adminJobApi.updateJob(editingJob.value.id, jobForm.value)
      toast.success('Job updated successfully')
    } else {
      await adminJobApi.createJob(jobForm.value)
      toast.success('Job created successfully')
    }
    closeJobModal()
    loadJobs()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to save job')
  }
}

const deleteJob = async (id) => {
  if (confirm('Are you sure you want to delete this job?')) {
    try {
      await adminJobApi.deleteJob(id)
      toast.success('Job deleted')
      loadJobs()
    } catch (error) {
      toast.error('Failed to delete job')
    }
  }
}

const updateStatus = async (appId, status) => {
  try {
    await adminApplicationApi.updateStatus(appId, { status })
    toast.success(`Application status updated to ${getStatusText(status)}`)
    loadApplications()
    if (selectedApplication.value?.id === appId) {
      selectedApplication.value.status = status
    }
  } catch (error) {
    toast.error('Failed to update status')
  }
}

const saveAppNotes = async () => {
  try {
    await adminApplicationApi.updateStatus(selectedApplication.value.id, {
      admin_notes: appNotes.value,
      rating: appRating.value
    })
    toast.success('Notes saved')
    selectedApplication.value.admin_notes = appNotes.value
    selectedApplication.value.rating = appRating.value
  } catch (error) {
    toast.error('Failed to save notes')
  }
}

const sendReply = async () => {
  if (!appReply.value.trim()) {
    toast.error('Please enter a reply message')
    return
  }
  try {
    await adminApplicationApi.replyToApplication(selectedApplication.value.id, appReply.value)
    toast.success('Reply sent to applicant')
    appReply.value = ''
    loadApplications()
  } catch (error) {
    toast.error('Failed to send reply')
  }
}

const createCategory = async () => {
  if (!newCategory.value.name) {
    toast.error('Category name is required')
    return
  }
  try {
    await adminJobCategoryApi.createCategory(newCategory.value)
    toast.success('Category created')
    newCategory.value = { name: '', slug: '', icon: '', description: '' }
    loadCategories()
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to create category')
  }
}

const toggleCategoryStatus = async (cat) => {
  try {
    await adminJobCategoryApi.updateCategory(cat.id, { is_active: !cat.is_active })
    toast.success(`Category ${cat.is_active ? 'disabled' : 'enabled'}`)
    loadCategories()
  } catch (error) {
    toast.error('Failed to update category')
  }
}

const deleteCategory = async (id) => {
  if (confirm('Are you sure you want to delete this category?')) {
    try {
      await adminJobCategoryApi.deleteCategory(id)
      toast.success('Category deleted')
      loadCategories()
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete category')
    }
  }
}

const closeJobModal = () => {
  showJobModal.value = false
  editingJob.value = null
}

const closeJobDetailModal = () => {
  showJobDetailModal.value = false
  selectedJob.value = null
}

const closeApplicationDetailModal = () => {
  showApplicationDetailModal.value = false
  selectedApplication.value = null
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'status-pending',
    reviewed: 'status-reviewed',
    shortlisted: 'status-shortlisted',
    rejected: 'status-rejected',
    hired: 'status-hired'
  }
  return classes[status] || 'status-pending'
}

const getStatusText = (status) => {
  const texts = {
    pending: 'Pending Review',
    reviewed: 'Reviewed',
    shortlisted: 'Shortlisted',
    rejected: 'Rejected',
    hired: 'Hired'
  }
  return texts[status] || 'Pending'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not specified'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const truncate = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

onMounted(() => {
  loadJobs()
  loadCategories()
})
</script>

<style scoped>
.job-management {
  padding: 1.5rem;
  background: #f8fafc;
  min-height: 100vh;
}

/* ========== HEADER ========== */
.management-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
  font-size: 1.8rem;
}

.header-left p {
  color: #6b7280;
  margin: 0;
}

.btn-create {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.btn-create:hover {
  background: #f59e0b;
  transform: translateY(-2px);
}

/* ========== STATS GRID ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.blue { background: #e0e7ff; color: #1e3a8a; }
.stat-icon.green { background: #d1fae5; color: #065f46; }
.stat-icon.orange { background: #fed7aa; color: #9a3412; }
.stat-icon.purple { background: #e0e7ff; color: #1e3a8a; }

.stat-info h3 {
  font-size: 1.5rem;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 0;
  color: #6b7280;
  font-size: 0.8rem;
}

/* ========== TABS ========== */
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 12px 12px 0 0;
}

.tabs button:hover {
  color: #1e3a8a;
  background: #f1f5f9;
}

.tabs button.active {
  color: #1e3a8a;
  border-bottom: 3px solid #f59e0b;
  background: white;
}

.tabs .badge {
  background: #e5e7eb;
  color: #4b5563;
  padding: 0.125rem 0.5rem;
  border-radius: 20px;
  font-size: 0.7rem;
}

/* ========== JOBS GRID ========== */
.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.25rem;
}

.job-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
}

.job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
  border-color: #f59e0b;
}

.job-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.25rem;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.job-title {
  flex: 1;
}

.job-title h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #1e3a8a;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  display: inline-block;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.job-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s;
  color: #6b7280;
}

.icon-btn:hover {
  background: #e5e7eb;
}

.icon-btn.edit:hover {
  color: #3b82f6;
  background: #dbeafe;
}

.icon-btn.delete:hover {
  color: #ef4444;
  background: #fee2e2;
}

.job-card-body {
  padding: 1.25rem;
}

.job-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.job-meta i {
  margin-right: 0.25rem;
  width: 14px;
}

.job-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.75rem;
  color: #9ca3af;
}

.job-card-footer {
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-outline {
  background: white;
  border: 1px solid #1e3a8a;
  color: #1e3a8a;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: #1e3a8a;
  color: white;
}

.btn-primary-small {
  background: #1e3a8a;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
}

.btn-primary-small:hover {
  background: #f59e0b;
}

/* ========== APPLICATIONS TAB ========== */
.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-group i {
  position: absolute;
  left: 12px;
  color: #9ca3af;
}

.filter-group select {
  padding: 0.6rem 0.75rem 0.6rem 2.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  font-size: 0.85rem;
  cursor: pointer;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-box input {
  width: 100%;
  padding: 0.6rem 0.75rem 0.6rem 2.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.85rem;
}

.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.application-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.application-card:hover {
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.application-header {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  position: relative;
}

.applicant-avatar {
  width: 50px;
  height: 50px;
  background: #1e3a8a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.applicant-info {
  flex: 1;
}

.applicant-info h4 {
  margin: 0 0 0.25rem;
  color: #1e3a8a;
}

.applicant-info p {
  margin: 0;
  font-size: 0.75rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-badge.status-pending { background: #fef3c7; color: #92400e; }
.status-badge.status-reviewed { background: #dbeafe; color: #1e40af; }
.status-badge.status-shortlisted { background: #d1fae5; color: #065f46; }
.status-badge.status-rejected { background: #fee2e2; color: #991b1b; }
.status-badge.status-hired { background: #d1fae5; color: #065f46; }

.application-body {
  padding: 1.25rem;
}

.application-job, .application-date {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.application-job i, .application-date i {
  margin-right: 0.25rem;
  width: 16px;
}

.application-cover {
  font-size: 0.85rem;
  color: #4b5563;
  line-height: 1.5;
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 10px;
  margin-top: 0.5rem;
}

.application-footer {
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.btn-cv, .btn-view {
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  font-size: 0.75rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-cv {
  background: #10b981;
  color: white;
  border: none;
}

.btn-view {
  background: #3b82f6;
  color: white;
  border: none;
}

.status-select {
  padding: 0.4rem 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.75rem;
  cursor: pointer;
  margin-left: auto;
}

/* ========== CATEGORIES TAB ========== */
.category-form-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
}

.category-form-card h3 {
  color: #1e3a8a;
  margin: 0 0 1rem;
  font-size: 1rem;
}

.category-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.category-form input, .category-form textarea {
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.85rem;
}

.category-form input { flex: 1; min-width: 150px; }
.category-form textarea { width: 100%; }

.btn-create-category {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  cursor: pointer;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.category-card {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
  transition: all 0.3s;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.category-icon {
  font-size: 2rem;
}

.category-info {
  flex: 1;
}

.category-info h4 {
  margin: 0 0 0.25rem;
  color: #1e3a8a;
}

.category-info p {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.job-count {
  font-size: 0.7rem;
  color: #9ca3af;
}

.category-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ========== MODALS ========== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-container {
  background: white;
  border-radius: 24px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  animation: fadeInUp 0.3s ease;
}

.modal-container.large {
  max-width: 800px;
}

.application-detail-modal {
  max-width: 750px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #9ca3af;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #ef4444;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Application Detail Modal */
.detail-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.detail-card-header {
  display: flex;
  gap: 1.25rem;
  align-items: center;
}

.applicant-large-avatar {
  width: 70px;
  height: 70px;
  background: #1e3a8a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
}

.applicant-large-info h3 {
  margin: 0 0 0.25rem;
  color: #1e3a8a;
}

.detail-card h4 {
  color: #1e3a8a;
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cover-letter {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 0.85rem;
  white-space: pre-wrap;
}

.btn-download {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #10b981;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.3s;
}

.btn-download:hover {
  background: #059669;
}

.detail-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.detail-card.half {
  margin-bottom: 0;
}

.external-link {
  color: #3b82f6;
  text-decoration: none;
  word-break: break-all;
  font-size: 0.8rem;
}

.stars {
  display: inline-flex;
  gap: 0.25rem;
  margin-left: 0.5rem;
}

.stars i {
  color: #d1d5db;
  cursor: pointer;
  transition: color 0.2s;
}

.stars i.filled {
  color: #f59e0b;
}

.status-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.status-option {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-option:hover {
  border-color: #f59e0b;
}

.status-option.active {
  background: #1e3a8a;
  color: white;
  border-color: #1e3a8a;
}

.btn-save-notes, .btn-send-reply {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-save-notes {
  background: #6b7280;
  color: white;
  border: none;
}

.btn-send-reply {
  background: #f59e0b;
  color: white;
  border: none;
}

.previous-reply {
  margin-top: 1rem;
}

.previous-reply hr {
  margin: 0.75rem 0;
}

/* Job Form */
.job-form .form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.job-form .form-group {
  flex: 1;
  min-width: 200px;
}

.job-form .form-group.full {
  flex: 100%;
}

.job-form label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 0.8rem;
  color: #374151;
}

.job-form input, .job-form select, .job-form textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.85rem;
}

.job-form input:focus, .job-form select:focus, .job-form textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245,158,11,0.1);
}

.checkbox-row {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.85rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel {
  background: #e5e7eb;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  cursor: pointer;
}

.btn-submit {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  cursor: pointer;
}

.btn-secondary {
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
}

.btn-primary {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.page-btn {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.85rem;
  color: #6b7280;
}

/* Responsive */
@media (max-width: 768px) {
  .job-management {
    padding: 1rem;
  }
  
  .jobs-grid {
    grid-template-columns: 1fr;
  }
  
  .applications-grid {
    grid-template-columns: 1fr;
  }
  
  .management-header {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .modal-container {
    width: 95%;
  }
  
  .detail-row {
    grid-template-columns: 1fr;
  }
  
  .filters-bar {
    flex-direction: column;
  }
  
  .filter-group, .search-box {
    width: 100%;
  }
  
  .filter-group select {
    width: 100%;
  }
}
</style>