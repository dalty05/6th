
import axios from 'axios'
import { toast } from 'vue3-toastify'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})


// frontend/src/services/api.js

// ✅ Add request caching
const cache = new Map()
const CACHE_TTL = 300000 // 5 minutes

api.interceptors.request.use(config => {
  // Cache GET requests
  if (config.method === 'get') {
    const cacheKey = `${config.url}${JSON.stringify(config.params || {})}`
    const cached = cache.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return Promise.resolve({
        ...config,
        adapter: () => Promise.resolve({
          data: cached.data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config
        })
      })
    }
  }
  return config
})

api.interceptors.response.use(response => {
  // Cache GET responses
  if (response.config.method === 'get' && response.status === 200) {
    const cacheKey = `${response.config.url}${JSON.stringify(response.config.params || {})}`
    cache.set(cacheKey, {
      data: response.data,
      timestamp: Date.now()
    })
  }
  return response
})

// ✅ Add request deduplication
const pendingRequests = new Map()

api.interceptors.request.use(config => {
  const key = `${config.method}:${config.url}`
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key)
  }
  
  const promise = new Promise((resolve, reject) => {
    config._resolve = resolve
    config._reject = reject
  })
  pendingRequests.set(key, promise)
  return config
})

api.interceptors.response.use(
  response => {
    const key = `${response.config.method}:${response.config.url}`
    pendingRequests.delete(key)
    if (response.config._resolve) {
      response.config._resolve(response)
    }
    return response
  },
  error => {
    const key = `${error.config.method}:${error.config.url}`
    pendingRequests.delete(key)
    if (error.config._reject) {
      error.config._reject(error)
    }
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