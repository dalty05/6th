<template>
  <main>
    <section class="careers-page">
      <div class="container">
        <h1 class="section-title">Job Opportunities</h1>
        
        <div class="careers-content">
          <p class="intro">Join Kenya's biggest dairy cooperative! We're always looking for talented individuals to join our team.</p>
          
          <div class="job-listings">
            <div class="job-card" v-for="job in jobs" :key="job.id">
              <h3>{{ job.title }}</h3>
              <p class="job-location">{{ job.location }}</p>
              <p class="job-description">{{ job.description }}</p>
              <button @click="applyForJob(job)" class="btn btn-outline">Apply Now</button>
            </div>
          </div>
          
          <div class="no-jobs" v-if="jobs.length === 0">
            <p>No open positions at the moment. Please check back later!</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: 'Careers',
  data() {
    return {
      jobs: [
        {
          id: 1,
          title: 'Dairy Production Manager',
          location: 'Meru, Kenya',
          description: 'We are seeking an experienced production manager to oversee our dairy processing operations.'
        },
        {
          id: 2,
          title: 'Quality Control Officer',
          location: 'Meru, Kenya',
          description: 'Join our quality assurance team to ensure all products meet our high standards.'
        },
        {
          id: 3,
          title: 'Sales Representative',
          location: 'Nairobi, Kenya',
          description: 'Looking for dynamic sales professionals to expand our market presence.'
        }
      ]
    }
  },
  methods: {
    applyForJob(job) {
      alert(`Thank you for your interest in the ${job.title} position. Please send your CV to careers@merudairy.co.ke`)
    }
  }
}
</script>

<style scoped>
.careers-page {
  padding: 4rem 0;
  min-height: 70vh;
}

.intro {
  text-align: center;
  font-size: 1.2rem;
  margin-bottom: 3rem;
  color: #555;
}

.job-listings {
  max-width: 800px;
  margin: 0 auto;
}

.job-card {
  background: white;
  padding: 2rem;
  margin-bottom: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.job-card h3 {
  color: var(--primary-blue);
  margin-bottom: 0.5rem;
}

.job-location {
  color: var(--accent-blue);
  margin-bottom: 1rem;
}

.job-description {
  margin-bottom: 1rem;
  color: #555;
}
</style>