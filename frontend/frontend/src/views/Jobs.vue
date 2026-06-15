<template>
  <main class="jobs-page">
    <div class="container">
      <div class="page-header">
        <h1>Career Opportunities</h1>
        <p>Join Meru Dairy and be part of Kenya's biggest dairy cooperative</p>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="Search jobs..."
            @input="debouncedSearch"
          >
        </div>

        <select v-model="filters.category" @change="loadJobs">
          <option value="all">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>

        <select v-model="filters.type" @change="loadJobs">
          <option value="all">All Types</option>
          <option value="Full-time">Full-time</option>
          <option value="Part-time">Part-time</option>
          <option value="Remote">Remote</option>
          <option value="Contract">Contract</option>
          <option value="Internship">Internship</option>
        </select>
      </div>

      <!-- Jobs Grid -->
      <div class="jobs-grid" v-if="!loading">
        <div v-for="job in jobs" :key="job.id" class="job-card">
          <div class="job-badge" v-if="job.is_featured">Featured</div>
          <h3>{{ job.title }}</h3>
          <div class="job-meta">
            <span v-if="job.location"><i class="fas fa-map-marker-alt"></i> {{ job.location }}</span>
            <span v-if="job.type"><i class="fas fa-briefcase"></i> {{ job.type }}</span>
            <span v-if="job.experience_level"><i class="fas fa-chart-line"></i> {{ job.experience_level }}</span>
          </div>
          <p class="job-description">{{ job.description }}</p>
          <div class="job-footer">
            <span class="deadline" v-if="job.application_deadline">
              <i class="fas fa-calendar-alt"></i> Deadline: {{ formatDate(job.application_deadline) }}
            </span>
            <button @click="viewJob(job.slug)" class="btn-apply">View Details</button>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading jobs...</p>
      </div>

      <!-- No Results -->
      <div v-if="!loading && jobs.length === 0" class="no-results">
        <i class="fas fa-search"></i>
        <h3>No jobs found</h3>
        <p>Try adjusting your search or filter criteria</p>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="pagination.total_pages > 1">
        <button @click="changePage(pagination.current_page - 1)" :disabled="pagination.current_page === 1">
          Previous
        </button>
        <span>Page {{ pagination.current_page }} of {{ pagination.total_pages }}</span>
        <button @click="changePage(pagination.current_page + 1)" :disabled="!pagination.has_next">
          Next
        </button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { jobApi, jobCategoryApi } from '@/services/api'

const router = useRouter()
const jobs = ref([])
const categories = ref([])
const loading = ref(false)
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_items: 0,
  has_next: false,
  has_prev: false
})

const filters = ref({
  search: '',
  category: 'all',
  type: 'all'
})

let searchTimeout = null

const loadCategories = async () => {
  try {
    const response = await jobCategoryApi.getCategories()
    categories.value = response.data
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const loadJobs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current_page,
      per_page: 10,
      ...filters.value
    }
    if (params.category === 'all') delete params.category
    if (params.type === 'all') delete params.type
    
    const response = await jobApi.getJobs(params)
    jobs.value = response.data.data
    pagination.value = response.data.pagination
  } catch (error) {
    console.error('Error loading jobs:', error)
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.value.current_page = 1
    loadJobs()
  }, 500)
}

const changePage = (page) => {
  if (page < 1 || page > pagination.value.total_pages) return
  pagination.value.current_page = page
  loadJobs()
}

const viewJob = (slug) => {
  router.push(`/jobs/${slug}`)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadCategories()
  loadJobs()
})
</script>

<style scoped>
.jobs-page {
  padding: 4rem 0;
  background: #f8fafc;
  min-height: 70vh;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #6b7280;
  font-size: 1.1rem;
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
  position: relative;
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
  padding: 12px 12px 12px 40px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
}

.filters-bar select {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  font-size: 1rem;
  cursor: pointer;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.job-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  position: relative;
}

.job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.job-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #f59e0b;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.job-card h3 {
  font-size: 1.25rem;
  color: #1e3a8a;
  margin-bottom: 0.75rem;
  padding-right: 70px;
}

.job-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.job-meta i {
  width: 16px;
  margin-right: 4px;
}

.job-description {
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;


  line-clamp: 3;          /* Standard property */
  -webkit-line-clamp: 3;
  overflow: hidden;
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.deadline {
  font-size: 0.75rem;
  color: #ef4444;
}

.btn-apply {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s;
}

.btn-apply:hover {
  background: #3b82f6;
}

.loading-spinner {
  text-align: center;
  padding: 4rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #1e3a8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-results {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 12px;
}

.no-results i {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.no-results h3 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination button {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .jobs-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-bar {
    flex-direction: column;
  }
  
  .page-header h1 {
    font-size: 1.75rem;
  }
}
</style>