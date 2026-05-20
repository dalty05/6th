<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-section">
          <h3>Mount Kenya Milk</h3>
          <p>Kenya's biggest dairy co-operative, providing quality dairy products since inception.</p>
          <div class="social-links">
            <a href="#" target="_blank"><i class="fab fa-facebook"></i></a>
            <a href="#" target="_blank"><i class="fab fa-twitter"></i></a>
            <a href="#" target="_blank"><i class="fab fa-instagram"></i></a>
          </div>
        </div>
        
        <div class="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/about">About Us</router-link></li>
            <li><router-link to="/products">Products</router-link></li>
            <li><router-link to="/shop">Shop Online</router-link></li>
            <li><router-link to="/blog">Blog</router-link></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>Important Links</h4>
          <ul>
            <li><router-link to="/contact">Contact Us</router-link></li>
            <li><router-link to="/careers">Job Opportunities</router-link></li>
            <li><router-link to="/csr">CSR</router-link></li>
            <li><a href="/privacy-policy">Privacy Policy</a></li>
            <li><a href="/terms">Terms & Conditions</a></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>Contact Info</h4>
          <ul>
            <li><i class="fas fa-map-marker-alt"></i> Meru, Kenya</li>
            <li><i class="fas fa-phone"></i> +254 710901376</li>
            <li><i class="fas fa-envelope"></i> maziwa@merudairy.co.ke</li>
          </ul>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; 2024 Meru Central Dairy Co-operative Union Ltd. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
}
</script>

<style scoped>
.footer {
  background: #1a2a3a;
  color: #fff;
  padding: 3rem 0 1rem;
  margin-top: auto;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3,
.footer-section h4 {
  margin-bottom: 1rem;
  color: #fff;
}

.footer-section p {
  color: #ccc;
  line-height: 1.6;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 0.5rem;
}

.footer-section ul li a {
  color: #ccc;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-section ul li a:hover {
  color: var(--accent-blue);
}

.footer-section ul li i {
  margin-right: 10px;
  color: var(--accent-blue);
}

.social-links {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.social-links a {
  color: #fff;
  font-size: 1.2rem;
  transition: transform 0.3s;
}

.social-links a:hover {
  transform: translateY(-3px);
}

.footer-bottom {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid #334155;
  color: #ccc;
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .social-links {
    justify-content: center;
  }
}
</style>