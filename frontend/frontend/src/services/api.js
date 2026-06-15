// src/services/api.js
import axios from 'axios'
import { toast } from 'vue3-toastify'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('user')
      window.location.href = '/admin/login'
    }
    
    const message = error.response?.data?.error || error.message || 'An error occurred'
    toast.error(message, {
      autoClose: 3000,
      position: 'top-right'
    })
    
    return Promise.reject(error)
  }




)


// Referral Links
export const referralApi = {
  // Get all referral links
  getLinks: () => api.get('/referral/links'),
  
  // Create new link
  createLink: (data) => api.post('/referral/links', data),
  
  // Update link
  updateLink: (id, data) => api.put(`/referral/links/${id}`, data),
  
  // Delete link
  deleteLink: (id) => api.delete(`/referral/links/${id}`),
  
  // Get analytics for a link
  getAnalytics: (id, days = 30) => api.get(`/referral/links/${id}/clicks?days=${days}`),
  
  // Record conversion
  recordConversion: (id) => api.post(`/referral/links/${id}/convert`),
}



// Job Categories
// Job Categories (Public)
export const jobCategoryApi = {
  getCategories: () => api.get('/job-categories'),
}

// Jobs (Public)
export const jobApi = {
  getJobs: (params) => api.get('/jobs', { params }),
  getJob: (slug) => api.get(`/jobs/${slug}`),
  applyForJob: (jobId, formData) => api.post(`/jobs/${jobId}/apply`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// Admin Jobs
export const adminJobApi = {
  getJobs: () => api.get('/admin/jobs'),
  getJob: (id) => api.get(`/admin/jobs/${id}`),
  createJob: (data) => api.post('/admin/jobs', data),
  updateJob: (id, data) => api.put(`/admin/jobs/${id}`, data),
  deleteJob: (id) => api.delete(`/admin/jobs/${id}`),
}

// Admin Job Categories
export const adminJobCategoryApi = {
  getCategories: () => api.get('/admin/job-categories'),
  createCategory: (data) => api.post('/admin/job-categories', data),
  updateCategory: (id, data) => api.put(`/admin/job-categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/admin/job-categories/${id}`),
}

// Admin Applications
export const adminApplicationApi = {
  getApplications: (params) => api.get('/admin/applications', { params }),
  getApplication: (id) => api.get(`/admin/applications/${id}`),
  updateStatus: (id, data) => api.put(`/admin/applications/${id}/status`, data),
  replyToApplication: (id, reply) => api.post(`/admin/applications/${id}/reply`, { reply }),
}
export default api