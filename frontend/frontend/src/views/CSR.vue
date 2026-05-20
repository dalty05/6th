<template>
  <main>
    <section class="csr-page">
      <div class="container">
        <h1 class="section-title">Corporate Social Responsibility</h1>
        
        <div class="csr-content">
          <div class="csr-section">
            <h2>Our Commitment to Community</h2>
            <p>At Meru Central Dairy, we believe in giving back to the communities that support us. Our CSR initiatives focus on education, healthcare, environmental sustainability, and farmer empowerment.</p>
          </div>
          
          <div class="csr-grid">
            <div class="csr-card">
              <h3>Farmer Training Programs</h3>
              <p>We provide free training to our farmers on modern dairy farming techniques, animal health, and sustainable practices.</p>
            </div>
            
            <div class="csr-card">
              <h3>School Milk Program</h3>
              <p>Partnering with local schools to provide nutritious milk to children, supporting their growth and education.</p>
            </div>
            
            <div class="csr-card">
              <h3>Water Conservation</h3>
              <p>Implementing water recycling and conservation measures across our facilities to protect local water resources.</p>
            </div>
            
            <div class="csr-card">
              <h3>Youth Empowerment</h3>
              <p>Internship and apprenticeship programs for young people interested in the dairy industry.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: 'CSR'
}
</script>

<style scoped>
.csr-page {
  padding: 4rem 0;
  min-height: 70vh;
}

.csr-section {
  text-align: center;
  max-width: 800px;
  margin: 0 auto 3rem;
}

.csr-section h2 {
  color: var(--primary-blue);
  margin-bottom: 1rem;
}

.csr-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.csr-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s;
}

.csr-card:hover {
  transform: translateY(-5px);
}

.csr-card h3 {
  color: var(--primary-blue);
  margin-bottom: 1rem;
}

.csr-card p {
  color: #555;
  line-height: 1.6;
}
</style>