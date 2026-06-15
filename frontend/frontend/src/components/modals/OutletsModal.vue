<template>
  <div class="outlets-modal">
    <div class="modal-header">
      <h2><i class="fas fa-store"></i> Our Physical Shops & Depots</h2>
      <p>Find a Meru Dairy location near you</p>
      <button class="close-btn" @click="closeModal">&times;</button>
    </div>

    <div class="modal-body">
      <!-- Category Filters -->
      <div class="category-filters">
        <button 
          v-for="cat in categories" 
          :key="cat.value"
          :class="['filter-btn', { active: selectedCategory === cat.value }]"
          @click="selectedCategory = cat.value"
        >
          {{ cat.label }}
          <span class="count">{{ cat.count }}</span>
        </button>
      </div>

      <div class="locations-container">
        <!-- List View -->
        <div class="locations-list">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading locations...</p>
          </div>
          
          <div v-else-if="filteredOutlets.length === 0" class="no-results">
            <i class="fas fa-map-marker-alt"></i>
            <p>No locations found in this category</p>
          </div>
          
          <div v-else>
            <div v-for="outlet in filteredOutlets" :key="outlet.id" class="location-card">
              <div class="location-icon">
                <i :class="getCategoryIcon(outlet.category)"></i>
              </div>
              <div class="location-details">
                <h4>{{ outlet.name }}</h4>
                <p class="category-badge">{{ outlet.category_display }}</p>
                <p><i class="fas fa-map-marker-alt"></i> {{ outlet.address }}, {{ outlet.city }}</p>
                <p v-if="outlet.phone"><i class="fas fa-phone"></i> {{ outlet.phone }}</p>
                <p v-if="outlet.email"><i class="fas fa-envelope"></i> {{ outlet.email }}</p>
                <p v-if="outlet.working_hours"><i class="fas fa-clock"></i> {{ outlet.working_hours }}</p>
                <div class="services" v-if="outlet.services && outlet.services.length">
                  <span v-for="service in outlet.services" :key="service" class="service-tag">
                    {{ service }}
                  </span>
                </div>
                <a :href="getDirectionsUrl(outlet)" target="_blank" class="directions-link">
                  <i class="fas fa-directions"></i> Get Directions
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Map View -->
        <div class="locations-map">
          <div id="outlet-map" class="map-container"></div>
          <div v-if="!mapLoaded" class="map-placeholder">
            <i class="fas fa-map-marked-alt"></i>
            <p>Map will appear here</p>
            <small>Google Maps will display once you have an API key</small>
          </div>
        </div>
      </div>
    </div>

    <div class="modal-footer">
      <button @click="closeModal" class="btn-close">Close</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const emit = defineEmits(['close'])

const outlets = ref([])
const categories = ref([])
const selectedCategory = ref('all')
const loading = ref(false)
const mapLoaded = ref(false)

const loadOutlets = async () => {
  loading.value = true
  try {
    const response = await api.get('/outlets')
    outlets.value = response.data
  } catch (error) {
    console.error('Error loading outlets:', error)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await api.get('/outlets/categories')
    categories.value = [{ value: 'all', label: 'All Locations', count: outlets.value.length }, ...response.data]
  } catch (error) {
    console.error('Error loading categories:', error)
    // Fallback categories
    categories.value = [
      { value: 'all', label: 'All Locations', count: outlets.value.length },
      { value: 'office_branch', label: '🏢 Office Branch', count: 0 },
      { value: 'depot', label: '🚚 Depot', count: 0 },
      { value: 'outlet', label: '🏪 Retail Outlet', count: 0 }
    ]
  }
}

const filteredOutlets = computed(() => {
  if (selectedCategory.value === 'all') return outlets.value
  return outlets.value.filter(o => o.category === selectedCategory.value)
})

const getCategoryIcon = (category) => {
  const icons = {
    office_branch: 'fas fa-building',
    depot: 'fas fa-warehouse',
    outlet: 'fas fa-store'
  }
  return icons[category] || 'fas fa-map-marker-alt'
}

const getDirectionsUrl = (outlet) => {
  return `https://www.google.com/maps/dir/?api=1&destination=${outlet.latitude},${outlet.longitude}`
}

const closeModal = () => {
  emit('close')
}

onMounted(() => {
  loadOutlets()
  loadCategories()
})
</script>

<style scoped>
.outlets-modal {
  background: white;
  border-radius: 16px;
  width: 90vw;
  max-width: 1100px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
  position: relative;
}

.modal-header h2 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-header p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.9;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255,255,255,0.2);
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255,255,255,0.3);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
}

.category-filters {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-btn.active {
  background: #1e3a8a;
  color: white;
}

.filter-btn .count {
  background: rgba(0,0,0,0.1);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
}

.filter-btn.active .count {
  background: rgba(255,255,255,0.2);
}

.locations-container {
  display: flex;
  gap: 1.5rem;
  height: calc(100% - 50px);
  min-height: 400px;
}

.locations-list {
  flex: 1;
  overflow-y: auto;
  max-height: 500px;
  padding-right: 0.5rem;
}

.location-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 0.75rem;
  transition: all 0.3s;
}

.location-card:hover {
  transform: translateX(4px);
  background: #e0e7ff;
}

.location-icon i {
  font-size: 1.5rem;
  color: #1e3a8a;
}

.location-details {
  flex: 1;
}

.location-details h4 {
  margin: 0 0 0.25rem;
  color: #1e3a8a;
}

.category-badge {
  display: inline-block;
  background: #e5e7eb;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  margin-bottom: 0.5rem;
}

.location-details p {
  margin: 0.25rem 0;
  font-size: 0.8rem;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.location-details i {
  width: 16px;
}

.services {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.5rem 0;
}

.service-tag {
  background: #e5e7eb;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  color: #374151;
}

.directions-link {
  display: inline-block;
  margin-top: 0.5rem;
  color: #f59e0b;
  text-decoration: none;
  font-size: 0.8rem;
}

.directions-link:hover {
  text-decoration: underline;
}

.locations-map {
  flex: 1.5;
  border-radius: 12px;
  overflow: hidden;
  background: #f3f4f6;
  min-height: 400px;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.map-placeholder i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
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
  padding: 2rem;
  color: #9ca3af;
}

.no-results i {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
}

.btn-close {
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .outlets-modal {
    width: 95vw;
    height: 85vh;
  }
  
  .locations-container {
    flex-direction: column;
  }
  
  .locations-map {
    min-height: 300px;
  }
}
</style>