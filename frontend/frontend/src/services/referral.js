// src/services/referral.js
import axios from 'axios'

const API_URL = '/api'

class ReferralService {
  /**
   * Get all referral links for current partner
   */
  async getLinks() {
    const response = await axios.get(`${API_URL}/referral/links`)
    return response.data
  }

  /**
   * Create a new referral link
   */
  async createLink(data) {
    const response = await axios.post(`${API_URL}/referral/links`, data)
    return response.data
  }

  /**
   * Update an existing referral link
   */
  async updateLink(id, data) {
    const response = await axios.put(`${API_URL}/referral/links/${id}`, data)
    return response.data
  }

  /**
   * Delete a referral link
   */
  async deleteLink(id) {
    const response = await axios.delete(`${API_URL}/referral/links/${id}`)
    return response.data
  }

  /**
   * Toggle link active status
   */
  async toggleLinkStatus(id, isActive) {
    const response = await axios.put(`${API_URL}/referral/links/${id}/status`, { is_active: isActive })
    return response.data
  }

  /**
   * Get stats for all links
   */
  async getStats() {
    const response = await axios.get(`${API_URL}/referral/stats`)
    return response.data
  }

  /**
   * Get detailed analytics with charts data
   */
  async getAnalytics(days = 30) {
    const response = await axios.get(`${API_URL}/referral/analytics?days=${days}`)
    return response.data
  }

  /**
   * Get top performing links
   */
  async getTopLinks(limit = 5) {
    const response = await axios.get(`${API_URL}/referral/top-links?limit=${limit}`)
    return response.data
  }
}

export default new ReferralService()