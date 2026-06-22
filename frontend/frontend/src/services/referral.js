
import api from './api'

class ReferralService {
  // Existing methods
  async getLinks() {
    const response = await api.get('/referral/links')
    return response.data
  }

  async createLink(data) {
    const response = await api.post('/referral/links', data)
    return response.data
  }

  async updateLink(id, data) {
    const response = await api.put(`/referral/links/${id}`, data)
    return response.data
  }

  async deleteLink(id) {
    const response = await api.delete(`/referral/links/${id}`)
    return response.data
  }

  async toggleLinkStatus(id) {
    const response = await api.post(`/referral/links/${id}/toggle`)
    return response.data
  }

  async getStats() {
    const response = await api.get('/referral/stats')
    return response.data
  }

  async getTopLinks(limit = 5, sortBy = 'clicks') {
    const response = await api.get(`/referral/top-links?limit=${limit}&sort_by=${sortBy}`)
    return response.data
  }

  async getRecentLinks(limit = 10) {
    const response = await api.get(`/referral/recent?limit=${limit}`)
    return response.data
  }

  // NEW: Enhanced Analytics Methods
  async getDailyAnalytics(days = 30) {
    const response = await api.get(`/referral/analytics/daily?days=${days}`)
    return response.data
  }

  async getSourceAnalytics() {
    const response = await api.get('/referral/analytics/sources')
    return response.data
  }

  async getGeoAnalytics() {
    const response = await api.get('/referral/analytics/geo')
    return response.data
  }

  async getTimelineAnalytics() {
    const response = await api.get('/referral/analytics/timeline')
    return response.data
  }

  async getRecentClicksAnalytics(limit = 20) {
    const response = await api.get(`/referral/analytics/recent-clicks?limit=${limit}`)
    return response.data
  }

  async getAnalyticsSummary(days = 30) {
    const response = await api.get(`/referral/analytics/summary?days=${days}`)
    return response.data
  }

  async getLinkAnalytics(linkId, days = 30) {
    const response = await api.get(`/referral/links/${linkId}/analytics?days=${days}`)
    return response.data
  }

  // Legacy analytics 
  async getAnalytics(days = 30) {
    const response = await api.get(`/referral/analytics?days=${days}`)
    return response.data
  }

  async getPartnerStats(userId) {
    const response = await api.get(`/referral/partner/${userId}/stats`)
    return response.data
  }

  async getPartnerAnalytics(days = 30) {
    const response = await api.get(`/referral/analytics/partner?days=${days}`)
    return response.data
  }

  // Navigation Analytics
  async getNavigationAnalytics(code = null, days = 30) {
    const params = new URLSearchParams()
    if (code) params.append('code', code)
    params.append('days', days)
    
    const response = await api.get(`/referral/analytics/navigation?${params.toString()}`)
    return response.data
  }
}

export default new ReferralService()