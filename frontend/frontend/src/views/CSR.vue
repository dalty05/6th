<template>
  <main>
    <section class="csr-page">
      <div class="container">
        <h1 class="section-title">Corporate Social Responsibility</h1>
        
        <div class="csr-content">
          <div class="csr-hero glass-card">
            <i class="fas fa-hand-holding-heart"></i>
            <h2>Our Commitment to Community</h2>
            <p>At Meru Central Dairy, we believe in giving back to the communities that support us. Our CSR initiatives focus on education, healthcare, environmental sustainability, and farmer empowerment.</p>
          </div>
          
          <div class="csr-grid">
            <div class="csr-card glass-card" @click="openInitiativeModal(initiative)" v-for="initiative in initiatives" :key="initiative.id">
              <div class="csr-icon">{{ initiative.icon }}</div>
              <h3>{{ initiative.title }}</h3>
              <p>{{ initiative.shortDescription }}</p>
              <button class="learn-more">Learn More <i class="fas fa-arrow-right"></i></button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CSR Initiative Modal -->
    <InfoModal 
      v-model:visible="showInitiativeModal" 
      :title="selectedInitiative?.title || 'CSR Initiative'"
    >
      <div v-if="selectedInitiative" class="initiative-details">
        <div class="initiative-icon-large">{{ selectedInitiative.icon }}</div>
        
        <div class="initiative-section">
          <h4>About This Initiative</h4>
          <p>{{ selectedInitiative.fullDescription }}</p>
        </div>
        
        <div class="initiative-section">
          <h4>Key Achievements</h4>
          <ul>
            <li v-for="achievement in selectedInitiative.achievements" :key="achievement">
              <i class="fas fa-check-circle"></i> {{ achievement }}
            </li>
          </ul>
        </div>
        
        <div class="initiative-section">
          <h4>Impact So Far</h4>
          <div class="impact-stats">
            <div class="impact-stat" v-for="stat in selectedInitiative.impactStats" :key="stat.label">
              <span class="impact-number">{{ stat.value }}</span>
              <span class="impact-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
        
        <div class="initiative-section">
          <h4>Get Involved</h4>
          <p>Interested in supporting this initiative? Contact our CSR team at <strong>csr@merudairy.co.ke</strong></p>
        </div>
        
        <div class="initiative-actions">
          <a href="mailto:csr@merudairy.co.ke" class="btn btn-primary">
            Contact CSR Team <i class="fas fa-envelope"></i>
          </a>
        </div>
      </div>
    </InfoModal>
  </main>
</template>

<script>
import InfoModal from '@/components/common/InfoModal.vue'

export default {
  name: 'CSR',
  components: {
    InfoModal
  },
  data() {
    return {
      showInitiativeModal: false,
      selectedInitiative: null,
      initiatives: [
        {
          id: 1,
          icon: '👨‍🌾',
          title: 'Farmer Training Programs',
          shortDescription: 'Free training on modern dairy farming techniques, animal health, and sustainable practices.',
          fullDescription: 'Our Farmer Training Program provides comprehensive education to dairy farmers on modern farming techniques, animal husbandry, disease prevention, milk quality improvement, and sustainable agricultural practices. We partner with agricultural experts to deliver hands-on training sessions.',
          achievements: [
            'Trained over 50,000 farmers since inception',
            '30% average increase in milk production',
            'Improved milk quality standards across the region',
            'Reduced cattle disease incidents by 40%'
          ],
          impactStats: [
            { value: '50K+', label: 'Farmers Trained' },
            { value: '30%', label: 'Production Increase' },
            { value: '200+', label: 'Training Sessions' }
          ]
        },
        {
          id: 2,
          icon: '🏥',
          title: 'Community Healthcare',
          shortDescription: 'Medical camps and health insurance for farmers and their families.',
          fullDescription: 'We organize free medical camps in rural areas, providing basic healthcare services, check-ups, and medicine distribution. We also offer subsidized health insurance to our cooperative members and their families.',
          achievements: [
            '10+ free medical camps annually',
            '5,000+ patients treated each year',
            'Health insurance coverage for 20,000+ families',
            'Partnership with local hospitals'
          ],
          impactStats: [
            { value: '20K+', label: 'Families Insured' },
            { value: '5K+', label: 'Patients Treated' },
            { value: '10+', label: 'Medical Camps/Year' }
          ]
        },
        {
          id: 3,
          icon: '📚',
          title: 'Education Support',
          shortDescription: 'Scholarships and educational materials for farmers\' children.',
          fullDescription: 'We provide scholarships to bright students from farming families, donate educational materials to rural schools, and run after-school tutoring programs in partnership with local educators.',
          achievements: [
            '500+ students on scholarships',
            '50+ schools received donations',
            '95% scholarship retention rate',
            'Partnered with 20 educational institutions'
          ],
          impactStats: [
            { value: '500+', label: 'Scholarships' },
            { value: '50', label: 'Schools Supported' },
            { value: '95%', label: 'Retention Rate' }
          ]
        },
        {
          id: 4,
          icon: '🌱',
          title: 'Environmental Sustainability',
          shortDescription: 'Water conservation, tree planting, and eco-friendly farming practices.',
          fullDescription: 'Our environmental initiatives include water recycling programs, tree planting campaigns, promotion of biogas from waste, and training on sustainable farming methods that protect the environment.',
          achievements: [
            '50,000+ trees planted',
            'Water recycling implemented at all facilities',
            'Biogas systems installed for 1,000+ farmers',
            'Carbon footprint reduced by 25%'
          ],
          impactStats: [
            { value: '50K+', label: 'Trees Planted' },
            { value: '25%', label: 'Carbon Reduction' },
            { value: '1K+', label: 'Biogas Systems' }
          ]
        },
        {
          id: 5,
          icon: '👩‍🎓',
          title: 'Youth Empowerment',
          shortDescription: 'Internship and apprenticeship programs for young people.',
          fullDescription: 'We offer paid internships and apprenticeships to young people interested in the dairy industry, providing hands-on experience, mentorship, and career development opportunities.',
          achievements: [
            '200+ youth trained annually',
            '80% employment rate post-training',
            'Mentorship program with industry experts',
            'Partnership with technical colleges'
          ],
          impactStats: [
            { value: '200+', label: 'Youth Trained' },
            { value: '80%', label: 'Employment Rate' },
            { value: '50+', label: 'Mentors' }
          ]
        },
        {
          id: 6,
          icon: '💧',
          title: 'Water Conservation',
          shortDescription: 'Clean water access and conservation programs for farming communities.',
          fullDescription: 'We work to provide clean water access to farming communities through borehole drilling, water tank installation, and rainwater harvesting systems, plus education on water conservation.',
          achievements: [
            '50+ boreholes drilled',
            '100+ water tanks installed',
            '10,000+ people with clean water access',
            'Water conservation training for 5,000+ farmers'
          ],
          impactStats: [
            { value: '50+', label: 'Boreholes' },
            { value: '10K+', label: 'People Served' },
            { value: '5K+', label: 'Farmers Trained' }
          ]
        }
      ]
    }
  },
  methods: {
    openInitiativeModal(initiative) {
      this.selectedInitiative = initiative
      this.showInitiativeModal = true
    }
  }
}
</script>

<style scoped>
.csr-page {
  padding: 4rem 0;
  min-height: 70vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
}

.section-title {
  font-size: 2.5rem;
  color: #1e3a8a;
  text-align: center;
  margin-bottom: 2rem;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: #f59e0b;
  border-radius: 2px;
}

.csr-hero {
  text-align: center;
  padding: 3rem;
  margin-bottom: 3rem;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
  border-radius: 24px;
}

.csr-hero i {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.csr-hero h2 {
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

.csr-hero p {
  max-width: 700px;
  margin: 0 auto;
  opacity: 0.9;
}

.csr-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.csr-card {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
  border: 1px solid #e5e7eb;
}

.csr-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  border-color: #f59e0b;
}

.csr-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.csr-card h3 {
  font-size: 1.3rem;
  color: #1e3a8a;
  margin-bottom: 0.75rem;
}

.csr-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1.25rem;
}

.learn-more {
  background: none;
  border: none;
  color: #f59e0b;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: gap 0.3s;
}

.learn-more:hover {
  gap: 0.75rem;
}

/* Initiative Modal Styles */
.initiative-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.initiative-icon-large {
  font-size: 4rem;
  text-align: center;
  padding: 1rem;
  background: #f0f4ff;
  border-radius: 50%;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.initiative-section h4 {
  color: #1e3a8a;
  margin-bottom: 0.75rem;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.initiative-section p {
  color: #555;
  line-height: 1.6;
}

.initiative-section ul {
  list-style: none;
  padding: 0;
}

.initiative-section ul li {
  padding: 0.4rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #555;
}

.initiative-section ul li i {
  color: #10b981;
  width: 20px;
}

.impact-stats {
  display: flex;
  justify-content: space-around;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
}

.impact-stat {
  text-align: center;
}

.impact-number {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: #f59e0b;
}

.impact-label {
  font-size: 0.75rem;
  color: #666;
}

.initiative-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.btn-primary:hover {
  background: #d97706;
}

.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

@media (max-width: 768px) {
  .csr-page {
    padding: 2rem 0;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  .csr-hero {
    padding: 2rem;
  }
  
  .csr-hero h2 {
    font-size: 1.4rem;
  }
  
  .csr-grid {
    grid-template-columns: 1fr;
  }
  
  .impact-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .initiative-actions {
    justify-content: stretch;
  }
  
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>