<template>
  <div class="csr-modal-content">
    <div class="modal-intro">
      <div class="intro-icon">
        <i class="fas fa-hand-holding-heart"></i>
      </div>
      <div class="intro-text">
        <h3>Our Commitment to Community</h3>
        <p>At Meru Central Dairy, we believe in giving back to the communities that support us.</p>
      </div>
    </div>

    <div class="initiatives-grid">
      <div v-for="initiative in initiatives" :key="initiative.id" class="initiative-card">
        <div class="initiative-icon">{{ initiative.icon }}</div>
        <div class="initiative-info">
          <h4>{{ initiative.title }}</h4>
          <p>{{ initiative.shortDescription }}</p>
          <button @click="showInitiativeDetails(initiative)" class="btn-details">
            Learn More <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="impact-stats">
      <div class="stat-item">
        <span class="stat-number">50K+</span>
        <span class="stat-label">Farmers Trained</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">10K+</span>
        <span class="stat-label">People Impacted</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">200+</span>
        <span class="stat-label">Communities</span>
      </div>
    </div>

    <div class="modal-footer-note">
      <i class="fas fa-envelope"></i>
      <p>Interested in partnering? Contact us at <strong>csr@merudairy.co.ke</strong></p>
    </div>
  </div>
</template>

<script setup>
import { toast } from 'vue3-toastify'

const initiatives = [
  {
    id: 1,
    icon: '👨‍🌾',
    title: 'Farmer Training Programs',
    shortDescription: 'Free training on modern dairy farming techniques, animal health, and sustainable practices.'
  },
  {
    id: 2,
    icon: '🏥',
    title: 'Community Healthcare',
    shortDescription: 'Medical camps and health insurance for farmers and their families.'
  },
  {
    id: 3,
    icon: '📚',
    title: 'Education Support',
    shortDescription: 'Scholarships and educational materials for farmers\' children.'
  },
  {
    id: 4,
    icon: '🌱',
    title: 'Environmental Sustainability',
    shortDescription: 'Water conservation, tree planting, and eco-friendly farming practices.'
  },
  {
    id: 5,
    icon: '👩‍🎓',
    title: 'Youth Empowerment',
    shortDescription: 'Internship and apprenticeship programs for young people.'
  },
  {
    id: 6,
    icon: '💧',
    title: 'Water Conservation',
    shortDescription: 'Clean water access and conservation programs for farming communities.'
  }
]

const showInitiativeDetails = (initiative) => {
  toast.info(`${initiative.title}: More details coming soon!`, {
    autoClose: 3000,
    position: 'top-right'
  })
}
</script>

<style scoped>
.csr-modal-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-intro {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  border-radius: 16px;
  color: white;
}

.intro-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.intro-icon i {
  font-size: 1.5rem;
}

.intro-text h3 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
}

.intro-text p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.9;
}

.initiatives-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  max-height: 350px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.initiative-card {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.3s;
}

.initiative-card:hover {
  background: #fef3c7;
  transform: translateX(4px);
}

.initiative-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.initiative-info {
  flex: 1;
}

.initiative-info h4 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
  font-size: 0.9rem;
}

.initiative-info p {
  color: #666;
  font-size: 0.75rem;
  margin: 0 0 0.5rem;
  line-height: 1.4;
}

.btn-details {
  background: none;
  border: none;
  color: #f59e0b;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.7rem;
  transition: gap 0.3s;
  padding: 0;
}

.btn-details:hover {
  gap: 0.5rem;
  color: #d97706;
}

.impact-stats {
  display: flex;
  justify-content: space-around;
  gap: 1rem;
  padding: 1rem;
  background: #f0f4ff;
  border-radius: 12px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #f59e0b;
}

.stat-label {
  font-size: 0.7rem;
  color: #666;
}

.modal-footer-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  font-size: 0.8rem;
  color: #666;
}

.modal-footer-note i {
  color: #f59e0b;
}

.modal-footer-note strong {
  color: #1e3a8a;
}

/* Scrollbar */
.initiatives-grid::-webkit-scrollbar {
  width: 4px;
}

.initiatives-grid::-webkit-scrollbar-track {
  background: #e5e7eb;
  border-radius: 4px;
}

.initiatives-grid::-webkit-scrollbar-thumb {
  background: #f59e0b;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .modal-intro {
    flex-direction: column;
    text-align: center;
  }
  
  .initiatives-grid {
    grid-template-columns: 1fr;
    max-height: 300px;
  }
  
  .impact-stats {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .modal-footer-note {
    flex-direction: column;
    text-align: center;
  }
}
</style>