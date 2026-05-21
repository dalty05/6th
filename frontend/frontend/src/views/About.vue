<template>
  <main>
    <section class="about-page">
      <div class="container">
        <h1 class="section-title">About Us</h1>
        
        <div class="about-content">
          <div class="about-text">
            <h2>Meru Central Dairy Co-operative Union Ltd</h2>
            <p>Meru Central Dairy Co-operative Union Ltd is Kenya's biggest dairy co-operative, serving millions of customers across the country with high-quality Mount Kenya Milk products.</p>
            
            <h3>Our History</h3>
            <p>Founded with the vision of empowering local farmers and providing nutritious dairy products to Kenyan families, Meru Central Dairy has grown from a small cooperative to a industry leader.</p>
            
            <h3>Our Mission</h3>
            <p>To provide high-quality, safe, and nutritious dairy products while empowering our farmers and contributing to the economic growth of our community.</p>
            
            <h3>Our Vision</h3>
            <p>To be the leading dairy cooperative in Africa, setting standards for quality, sustainability, and farmer welfare.</p>
          </div>
          
          <div class="about-image">
            <div class="placeholder-image">
              <!-- <svg width="100%" height="300" viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg"> -->
                <img src="/about.jpg" alt="Meru Dairy Farm" style="width: 100%; height: 100%; object-fit: cover;">
                <!-- <rect width="400" height="300" fill="#e0e7ff"/>
                <text x="200" y="150" text-anchor="middle" fill="#1e3a8a" font-size="16">Meru Dairy Farm</text>
              </svg> -->
            </div>
          </div>
        </div>
        
        <div class="food-safety">
          <h3>Food Safety Policy Statement</h3>

          <div class="safety-points">
          <p>We are committed to producing safe, high-quality dairy products that meet all regulatory standards. Our food safety management system ensures traceability from farm to table.</p>
          
          
          
          
          <p>Meru Central Dairy Co-operative Union Ltd (MCDCU) is committed to producing safe, wholesome and high-quality dairy products.</p>

          <p>MCDCU top management is committed to ensure that this policy is effectively communicated, implemented and maintained at all levels of the organization and supported by measurable objectives.</p>

          <p> In pursuit of this commitment, MCDCU is dedicated to full compliance with all applicable food safety requirements including statutory, regulatory and mutually agreed customer food safety requirements and maintaining KS ISO 22000:2018 compliant food safety system.</p>

          <p> MCDCU ensures effective communication of food safety information internally across all departments and externally with suppliers, customers, regulators and other relevant stakeholders to ensure alignment and transparency in the food safety chain at all times.</p>

          <p>MCDCU ensures that adequate resources, training and support are provided to enhance employee competence and awareness of their roles in maintaining food safety. </p>
          <p>MCDCU ensures continual improvement of an effective Food Safety Management System (FSMS). To maintain its suitability, this food safety policy will be reviewed from time to time.</p>

          </div>







          <button class="btn btn-outline" @click="downloadPolicy">Download Policy Statement</button>

        </div>
      </div>
    </section>
  </main>
</template>

<script>





export default {
  name: 'About',
  methods: {
    downloadPolicy() {
      alert('Policy statement will be available for download soon.')
    }
  }
}
</script>

<style scoped>

.safety-points p {
  margin-bottom: 1rem;
  color: #555;
  text-align: justify;
}




.about-page {
  padding: 4rem 0;
  min-height: 70vh;
}

.about-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  margin-bottom: 3rem;
}

.about-text h2 {
  color: var(--primary-blue);
  margin-bottom: 1rem;
}

.about-text h3 {
  color: var(--primary-blue);
  margin: 1.5rem 0 0.5rem;
}

.about-text p {
  line-height: 1.6;
  color: #555;
}

.about-image .placeholder-image {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  background: #e0e7ff;
}

.food-safety {
  background: var(--gray-light);
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  max-width: 80%;
 align-self: center;
  margin: 0 auto;
}

.food-safety h3 {
  color: var(--primary-blue);
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .about-content {
    grid-template-columns: 1fr;
  }
}
</style>