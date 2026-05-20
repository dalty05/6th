<template>
  <main>
    <section class="contact-page">
      <div class="container">
        <h1 class="section-title">Contact Us</h1>
        
        <div class="contact-grid">
          <div class="contact-info">
            <h3>Get in Touch</h3>
            <div class="info-item">
              <i class="fas fa-map-marker-alt"></i>
              <div>
                <strong>Address</strong>
                <p>Meru Central Dairy Co-operative Union Ltd<br>Meru Town, Kenya</p>
              </div>
            </div>
            
            <div class="info-item">
              <i class="fas fa-phone"></i>
              <div>
                <strong>Phone</strong>
                <p>+254 710 901 376<br>+254 719 111 444</p>
              </div>
            </div>
            
            <div class="info-item">
              <i class="fas fa-envelope"></i>
              <div>
                <strong>Email</strong>
                <p>maziwa@merudairy.co.ke<br>sales@merudairy.co.ke</p>
              </div>
            </div>
            
            <div class="info-item">
              <i class="fas fa-clock"></i>
              <div>
                <strong>Working Hours</strong>
                <p>Monday - Friday: 8:00 AM - 5:00 PM<br>Saturday: 9:00 AM - 1:00 PM</p>
              </div>
            </div>
          </div>
          
          <div class="contact-form">
            <h3>Send us a Message</h3>
            <form @submit.prevent="submitForm">
              <input type="text" v-model="form.name" placeholder="Your Name" required>
              <input type="email" v-model="form.email" placeholder="Your Email" required>
              <input type="text" v-model="form.subject" placeholder="Subject" required>
              <textarea v-model="form.message" placeholder="Your Message" rows="5" required></textarea>
              <button type="submit" class="btn btn-primary">Send Message</button>
            </form>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: 'Contact',
  data() {
    return {
      form: {
        name: '',
        email: '',
        subject: '',
        message: ''
      }
    }
  },
  methods: {
    submitForm() {
      alert('Thank you for your message! We will get back to you soon.')
      this.form = { name: '', email: '', subject: '', message: '' }
    }
  }
}
</script>

<style scoped>
.contact-page {
  padding: 4rem 0;
  min-height: 70vh;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

.contact-info h3,
.contact-form h3 {
  color: var(--primary-blue);
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-item i {
  font-size: 1.5rem;
  color: var(--accent-blue);
}

.info-item strong {
  display: block;
  margin-bottom: 0.25rem;
}

.contact-form input,
.contact-form textarea {
  width: 100%;
  padding: 12px;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
}

@media (max-width: 768px) {
  .contact-grid {
    grid-template-columns: 1fr;
  }
}
</style>