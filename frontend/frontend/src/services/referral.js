import api from './api'

class ReferralService {
  
    
  async getAnalytics(days = 30) {
    const response = await api.get('/admin/referral/analytics', {
      params: { days }
    })
    return response.data
  }
  
  
  async getLinks() {
    const response = await api.get('/admin/partners/links')
    return response.data
  }
  
  // Create new link
  async createLink(data) {
    const response = await api.post('/admin/partners/links', data)
    return response.data
  }
  
  // Update link
  async updateLink(id, data) {
    const response = await api.put(`/admin/partners/links/${id}`, data)
    return response.data
  }
  
  // Delete link
  async deleteLink(id) {
    const response = await api.delete(`/admin/partners/links/${id}`)
    return response.data
  }
  
  // Get partner stats
  async getPartnerStats(partnerId) {
    const response = await api.get(`/admin/referral/partner/${partnerId}/stats`)
    return response.data
  }
  
  // Get all partners
  async getPartners() {
    const response = await api.get('/admin/referral/partners')
    return response.data
  }
}

export default new ReferralService()