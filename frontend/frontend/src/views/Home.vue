<template>
  <main>
    <!-- Scroll Progress Indicator -->
    <ScrollProgress />
    
    <!-- Back to Top Button -->
    <BackToTop />

    <!-- Hero Section -->
    <section id="home" class="hero-section">
      <div class="hero-background">
        <div class="hero-overlay"></div>
        <div class="hero-pattern"></div>
      </div>
      
      <div class="container">
        <div class="hero-content">
          <div class="hero-text animate-fade-in-up">
            <span class="hero-badge">
              <i class="fas fa-trophy"></i> Kenya's Biggest Dairy Co-operative
            </span>
            <h1 class="hero-title">Pure <span class="highlight">Mount Kenya</span><br>Milk Delivered Fresh</h1>
            <p class="hero-description">
              From our farms to your table, experience the richness of nature 
              with Mount Kenya Milk products.
            </p>
            <div class="hero-buttons">
              <button @click="scrollToProducts" class="btn btn-primary btn-large">
                Explore Products
                <i class="fas fa-arrow-right btn-icon"></i>
              </button>
              <button @click="scrollToAbout" class="btn btn-outline-light btn-large">
                Learn More
                <i class="fas fa-play-circle"></i>
              </button>
            </div>
          </div>
          
          <div class="hero-stats animate-fade-in-up delay-2">
            <div class="stat-card" v-for="stat in statistics" :key="stat.label">
              <div class="stat-number">{{ stat.value }}{{ stat.suffix }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <span>Scroll to explore</span>
        <div class="scroll-mouse"></div>
      </div>
    </section>

    <!-- About Section with CEO Message -->
    <section id="about" class="about-section">
      <div class="container">
        <!-- Section Header with Image -->
        <div class="section-header-with-image">
          <div class="section-header-content">
            <span class="section-badge">
              <i class="fas fa-leaf"></i> Our Story
            </span>
            <h2 class="section-title">Kenya's Largest<br>Dairy Co-operative</h2>
            <p class="section-subtitle">
              Meru Central Dairy Co-operative Union Ltd has grown from humble beginnings 
              to become Kenya's biggest dairy processor, empowering over 120,000 farmers 
              and serving millions of customers nationwide.
            </p>
          </div>
          <div class="section-header-image">
            <img src="/images/about-header.jpeg" alt="About Meru Dairy" @error="setImagePlaceholder">
            <div class="image-overlay-text">
              <i class="fas fa-quote-right"></i>
            </div>
          </div>
        </div>

        <div class="about-grid">
          <!-- About Stats -->
          <div class="about-stats-grid">
            <div class="about-stat-card">
              <div class="stat-icon"><i class="fas fa-calendar-alt"></i></div>
              <div class="stat-number">50+</div>
              <div class="stat-label">Years of Excellence</div>
            </div>
            <div class="about-stat-card">
              <div class="stat-icon"><i class="fas fa-users"></i></div>
              <div class="stat-number">120K+</div>
              <div class="stat-label">Happy Farmers</div>
            </div>
            <div class="about-stat-card">
              <div class="stat-icon"><i class="fas fa-smile"></i></div>
              <div class="stat-number">10M+</div>
              <div class="stat-label">Customers Served</div>
            </div>
            <div class="about-stat-card">
              <div class="stat-icon"><i class="fas fa-truck"></i></div>
              <div class="stat-number">50+</div>
              <div class="stat-label">Distribution Centers</div>
            </div>
          </div>

          <!-- CEO Message Section -->
          <div class="ceo-message glass-card">
            <div class="ceo-image">
              <img src="/images/ceo.jpeg" alt="CEO - Dr. Sarah Wanjiku" @error="setImagePlaceholder">
              <div class="ceo-badge">
                <i class="fas fa-crown"></i> CEO
              </div>
            </div>
            <div class="ceo-content">
              <div class="quote-icon"><i class="fas fa-quote-left"></i></div>
              <p class="ceo-text">
                "Our journey from a small cooperative to Kenya's largest dairy processor 
                has been driven by our unwavering commitment to quality, farmer empowerment, 
                and customer satisfaction. We believe in creating value at every step - 
                from the dedicated farmers who care for their cows, to the families who 
                trust our products on their tables. Together, we are building a healthier, 
                more prosperous Kenya."
              </p>
              <div class="ceo-info">
                <h4>Dr. Sarah Wanjiku</h4>
                <span>Chief Executive Officer</span>
                <div class="ceo-signature">
                  <i class="fas fa-certificate"></i> 20+ Years in Dairy Industry
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <!-- Section Header -->
        <div class="section-header-with-image reverse">
          <div class="section-header-image">
            <img src="/images/features-header.jpeg" alt="Our Features" @error="setImagePlaceholder">
          </div>
          <div class="section-header-content">
            <span class="section-badge">
              <i class="fas fa-star"></i> Why Choose Us
            </span>
            <h2 class="section-title">Excellence in Every Drop</h2>
            <p class="section-subtitle">
              Discover what makes Mount Kenya Milk the preferred choice for millions of Kenyans
            </p>
          </div>
        </div>
        
        <div class="features-grid">
          <div class="feature-card glass-card" v-for="feature in features" :key="feature.title" data-aos="fade-up">
            <div class="feature-icon">
              <i :class="feature.icon"></i>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>


      <!-- Products Section with Load More (No Scrolling) -->
<section id="products" class="products-section">
  <div class="container">
    <!-- Section Header -->
    <div class="section-header-with-image">
      <div class="section-header-content">
        <span class="section-badge">
          <i class="fas fa-box-open"></i> Our Collection
        </span>
        <h2 class="section-title">Premium Dairy Products</h2>
        <p class="section-subtitle">
          Crafted with care for your family's nutrition and wellbeing
        </p>
      </div>
      <div class="section-header-image">
        <img src="/images/products-header.jpeg" alt="Our Products" @error="setImagePlaceholder">
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="productsLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading products...</p>
    </div>
    
    <!-- Products Grid -->
    <div v-else class="products-grid">
      <div class="product-card glass-card" v-for="product in displayedProducts" :key="product.id" data-aos="fade-up">
        <div class="product-image" @click="openProductModal(product.id)">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" @error="handleImageError">
          <div v-else class="image-placeholder">
            <i class="fas fa-milk"></i>
            <p>{{ product.name }}</p>
          </div>
          <div class="product-overlay">
            <button class="view-details">
              <i class="fas fa-eye"></i> Quick View
            </button>
          </div>
        </div>
        <div class="product-badge" v-if="product.featured">
          <i class="fas fa-fire"></i> Featured
        </div>
        <h3>{{ product.name }}</h3>
        <p>{{ truncate(product.description, 80) }}</p>
        <div class="product-meta" v-if="product.packaging_sizes">
          <i class="fas fa-weight-hanging"></i>
          <span>{{ product.packaging_sizes }}</span>
        </div>
        <button @click="openProductModal(product.id)" class="product-details-btn">
          Quick View <i class="fas fa-arrow-right"></i>
        </button>
      </div>
    </div>
    
    <!-- No Products Message -->
    <div v-if="!productsLoading && displayedProducts.length === 0 && !hasMoreProducts" class="no-products">
      <div class="no-products-icon"><i class="fas fa-box-open"></i></div>
      <h3>No Products Found</h3>
      <p>Check back soon for our delicious dairy products!</p>
    </div>
    
    <!-- Load More Button - STAYS IN PLACE, NO SCROLLING -->
    <div v-if="hasMoreProducts && !productsLoading" class="load-more-container">
      <button 
        @click="loadMoreProducts" 
        class="btn-load-more" 
        :disabled="productsLoadingMore"
      >
        <i v-if="productsLoadingMore" class="fas fa-spinner fa-spin"></i>
        <span v-else>
          <i class="fas fa-arrow-down"></i> Load More Products 
        </span>
      </button>
      <p v-if="productsLoadingMore" class="loading-text">Loading more products...</p>
    </div>
    
    <!-- Product Count Display -->
    <div v-if="displayedProducts.length > 0 && !productsLoading" class="product-count">
      <span>Showing {{ displayedProducts.length }} of {{ totalProducts }} products</span>
    </div>
  </div>
</section>

    <!-- Shop Online Section -->
    <section id="shop" class="shop-section">
      <div class="container">
        <!-- Section Header -->
        <div class="section-header-with-image reverse">
          <div class="section-header-image">
            <img src="/images/shop-header.jpeg" alt="Shop Online" @error="setImagePlaceholder">
          </div>
          <div class="section-header-content">
            <span class="section-badge">
              <i class="fas fa-shopping-cart"></i> Shop Online
            </span>
            <h2 class="section-title">Convenient Delivery<br>at Your Doorstep</h2>
            <p class="section-subtitle">
              Order fresh dairy products online and get them delivered to your home
            </p>
          </div>
        </div>
        
        <div class="shop-grid">
          <div class="shop-card glass-card" data-aos="fade-up">
            <div class="shop-icon"><i class="fas fa-store"></i></div>
            <h3>Online Store</h3>
            <p>Browse and order our full range of dairy products from our online shop</p>
            <a href="https://shop.mountkenyamilk.co.ke/" target="_blank" class="shop-link">
              Visit Our Shop <i class="fas fa-arrow-right"></i>
            </a>
          </div>
          
          <div class="shop-card glass-card" data-aos="fade-up" data-aos-delay="100">
            <div class="shop-icon"><i class="fas fa-boxes"></i></div>
            <h3>Bulk Orders</h3>
            <p>Special pricing for wholesale and bulk purchases</p>
            <button @click="scrollToContact" class="shop-link">
              Contact Sales <i class="fas fa-arrow-right"></i>
            </button>
          </div>
          
          <div class="shop-card glass-card" data-aos="fade-up" data-aos-delay="200">
            <div class="shop-icon"><i class="fas fa-truck-fast"></i></div>
            <h3>Fast Delivery</h3>
            <p>Free delivery on orders above KES 2,000 within Nairobi</p>
            <button @click="scrollToContact" class="shop-link">
              Learn More <i class="fas fa-arrow-right"></i>
            </button>
          </div>
          
          <div class="shop-card glass-card" data-aos="fade-up" data-aos-delay="300">
            <div class="shop-icon"><i class="fas fa-shield-alt"></i></div>
            <h3>Secure Payments</h3>
            <p>Pay via M-Pesa, Credit Card, or Cash on Delivery</p>
            <button @click="scrollToContact" class="shop-link">
              Payment Options <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
        
        <div class="shop-cta">
          <a href="https://shop.mountkenyamilk.co.ke/" target="_blank" class="btn btn-primary btn-large">
            Start Shopping Now <i class="fas fa-arrow-right btn-icon"></i>
          </a>
          <button @click="scrollToContact" class="btn btn-outline btn-large">
            Need Help? Contact Us <i class="fas fa-headset"></i>
          </button>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="container">
        <!-- Section Header -->
        <div class="section-header-with-image">
          <div class="section-header-content">
            <span class="section-badge">
              <i class="fas fa-comment-dots"></i> Testimonials
            </span>
            <h2 class="section-title">What Our Customers Say</h2>
            <p class="section-subtitle">Trusted by millions across Kenya</p>
          </div>
          <div class="section-header-image">
            <img src="/images/testimonials-header.jpeg" alt="Customer Testimonials" @error="setImagePlaceholder">
          </div>
        </div>
        
        <div class="testimonials-grid">
          <div class="testimonial-card glass-card" v-for="testimonial in testimonials" :key="testimonial.id" data-aos="fade-up">
            <div class="quote-mark"><i class="fas fa-quote-left"></i></div>
            <p class="testimonial-text">{{ testimonial.content }}</p>
            <div class="testimonial-author">
              <div class="author-info">
                <strong>{{ testimonial.name }}</strong>
                <span>{{ testimonial.role }}</span>
              </div>
              <div class="rating">
                <i v-for="i in testimonial.rating" :key="i" class="fas fa-star"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Blog Section -->
    <!-- Blog Section with Load More -->
<section id="blog" class="blog-section">
  <div class="container">
    <!-- Section Header -->
    <div class="section-header-with-image reverse">
      <div class="section-header-image">
        <img src="/images/blog-header.jpeg" alt="Latest News" @error="setImagePlaceholder">
      </div>
      <div class="section-header-content">
        <span class="section-badge">
          <i class="fas fa-newspaper"></i> Latest Updates
        </span>
        <h2 class="section-title">From Our Blog</h2>
        <p class="section-subtitle">
          Stay updated with the latest news and stories from our dairy community
        </p>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="blogsLoading && displayedBlogs.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading latest articles...</p>
    </div>
    
    <!-- Blog Grid -->
    <div v-else class="blog-grid">
      <div class="blog-card glass-card" v-for="post in displayedBlogs" :key="post.id" data-aos="fade-up">
        <div class="blog-image" @click="openBlogModal(post.slug)">
          <img v-if="post.featured_image" :src="post.featured_image" :alt="post.title" @error="handleImageError">
          <div v-else class="image-placeholder">
            <i class="fas fa-newspaper"></i>
          </div>
          <div class="blog-overlay">
            <button class="quick-read-btn">
              <i class="fas fa-eye"></i> Quick Read
            </button>
          </div>
        </div>
        <div class="blog-content">
          <div class="blog-meta">
            <span class="blog-date"><i class="far fa-calendar-alt"></i> {{ formatDate(post.created_at) }}</span>
            <span class="blog-views"><i class="far fa-eye"></i> {{ post.views || 0 }}</span>
          </div>
          <h3>{{ truncate(post.title, 60) }}</h3>
          <p>{{ truncate(post.excerpt || post.content, 100) }}</p>
          <div class="blog-footer">
            <span class="blog-author"><i class="far fa-user"></i> By {{ post.author || 'Admin' }}</span>
            <button @click="openBlogModal(post.slug)" class="read-more">
              Quick Read <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- No Posts Message -->
    <div v-if="!blogsLoading && displayedBlogs.length === 0" class="no-posts">
      <div class="no-posts-icon"><i class="fas fa-inbox"></i></div>
      <h3>No Blog Posts Yet</h3>
      <p>Check back soon for updates and news from Meru Dairy!</p>
    </div>
    
    <!-- Load More Button -->
    <div v-if="hasMoreBlogs && !blogsLoading" class="load-more-container">
      <button 
        @click="loadMoreBlogs" 
        class="btn-load-more btn-load-more-blog" 
        :disabled="blogsLoadingMore"
      >
        <i v-if="blogsLoadingMore" class="fas fa-spinner fa-spin"></i>
        <span v-else>
          <i class="fas fa-arrow-down"></i> Load More Articles ({{ displayedBlogs.length }} of {{ totalBlogs }})
        </span>
      </button>
    </div>
    
    <!-- View All Link when no more to load -->
    <div v-if="!hasMoreBlogs && displayedBlogs.length > 0 && !blogsLoading" class="view-all-link">
      <router-link to="/blog" class="btn-link">
        View All {{ totalBlogs }} Articles <i class="fas fa-arrow-right"></i>
      </router-link>
    </div>
  </div>
</section>



<!-- Blog Modal for Quick Reading -->
<div v-if="showBlogModal" class="modal-overlay" @click.self="closeBlogModal">
  <div class="modal-container modal-blog glass-card">
    <button class="modal-close" @click="closeBlogModal">
      <i class="fas fa-times"></i>
    </button>
    
    <div v-if="blogModalLoading" class="modal-loading">
      <div class="loading-spinner"></div>
      <p>Loading article...</p>
    </div>
    
    <div v-else-if="selectedBlog" class="modal-blog-content">
      <div class="modal-blog-image">
        <img v-if="selectedBlog.featured_image" :src="selectedBlog.featured_image" :alt="selectedBlog.title" @error="handleImageError">
        <div v-else class="image-placeholder-large">
          <i class="fas fa-newspaper"></i>
        </div>
      </div>
      
      <div class="modal-blog-info">
        <div class="blog-meta-modal">
          <span class="blog-date"><i class="far fa-calendar-alt"></i> {{ formatDate(selectedBlog.created_at) }}</span>
          <span class="blog-views"><i class="far fa-eye"></i> {{ selectedBlog.views || 0 }} views</span>
          <span class="blog-author"><i class="far fa-user"></i> By {{ selectedBlog.author || 'Admin' }}</span>
        </div>
        
        <h2>{{ selectedBlog.title }}</h2>
        
        <div class="modal-blog-excerpt" v-if="selectedBlog.excerpt">
          <i class="fas fa-quote-left"></i>
          <p>{{ selectedBlog.excerpt }}</p>
        </div>
        
        <div class="modal-blog-content-preview">
          <p>{{ truncate(selectedBlog.content || selectedBlog.excerpt, 500) }}</p>
        </div>
        
        <div class="modal-actions">
          <router-link :to="`/blog/${selectedBlog.slug}`" class="btn btn-primary">
            Read Full Article <i class="fas fa-arrow-right"></i>
          </router-link>
          <button @click="scrollToContact" class="btn btn-outline">
            Contact Us <i class="fas fa-envelope"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

    <!-- Contact Section -->
    <section id="contact" class="contact-section">
      <div class="container">
        <!-- Section Header -->
        <div class="section-header-with-image">
          <div class="section-header-content">
            <span class="section-badge">
              <i class="fas fa-envelope"></i> Get in Touch
            </span>
            <h2 class="section-title">Contact Us</h2>
            <p class="section-subtitle">We'd love to hear from you</p>
          </div>
          <div class="section-header-image">
            <img src="/images/contact-header.jpeg" alt="Contact Us" @error="setImagePlaceholder">
          </div>
        </div>
        
        <div class="contact-grid">
          <div class="contact-info-wrapper" data-aos="fade-right">
            <div class="info-cards">
              <div class="info-card glass-card">
                <div class="info-icon"><i class="fas fa-map-marker-alt"></i></div>
                <div class="info-content">
                  <h3>Address</h3>
                  <p>Meru Town, Kenya</p>
                </div>
              </div>
              
              <div class="info-card glass-card">
                <div class="info-icon"><i class="fas fa-phone-alt"></i></div>
                <div class="info-content">
                  <h3>Phone</h3>
                  <p><a href="tel:+254710901376">+254 710 901 376</a><br><a href="tel:+254719111444">+254 719 111 444</a></p>
                </div>
              </div>
              
              <div class="info-card glass-card">
                <div class="info-icon"><i class="fas fa-envelope"></i></div>
                <div class="info-content">
                  <h3>Email</h3>
                  <p><a href="mailto:maziwa@merudairy.co.ke">maziwa@merudairy.co.ke</a><br><a href="mailto:sales@merudairy.co.ke">sales@merudairy.co.ke</a></p>
                </div>
              </div>
              
              <div class="info-card glass-card">
                <div class="info-icon"><i class="fas fa-clock"></i></div>
                <div class="info-content">
                  <h3>Working Hours</h3>
                  <p>Mon-Fri: 8AM - 5PM<br>Sat: 9AM - 1PM</p>
                </div>
              </div>
            </div>
            
            <div class="social-links-section">
              <h3><i class="fas fa-share-alt"></i> Connect With Us</h3>
              <div class="social-links-grid">
                <a href="#" class="social-link glass-card"><i class="fab fa-facebook-f"></i> Facebook</a>
                <a href="#" class="social-link glass-card"><i class="fab fa-twitter"></i> Twitter</a>
                <a href="#" class="social-link glass-card"><i class="fab fa-instagram"></i> Instagram</a>
                <a href="#" class="social-link glass-card"><i class="fab fa-linkedin-in"></i> LinkedIn</a>
              </div>
            </div>
          </div>
          
          <div class="contact-form-wrapper" data-aos="fade-left">
            <div class="form-card glass-card">
              <div class="form-header">
                <div class="form-icon"><i class="fas fa-paper-plane"></i></div>
                <h3>Send us a Message</h3>
                <p>We'll get back to you within 24 hours</p>
              </div>
              
              <form @submit.prevent="submitContactForm" class="contact-form">
                <div class="form-group">
                  <div class="input-wrapper">
                    <i class="fas fa-user input-icon"></i>
                    <input type="text" v-model="contactForm.name" placeholder="Your Name" required>
                  </div>
                </div>
                
                <div class="form-group">
                  <div class="input-wrapper">
                    <i class="fas fa-envelope input-icon"></i>
                    <input type="email" v-model="contactForm.email" placeholder="Your Email" required>
                  </div>
                </div>
                
                <div class="form-group">
                  <div class="input-wrapper">
                    <i class="fas fa-tag input-icon"></i>
                    <input type="text" v-model="contactForm.subject" placeholder="Subject" required>
                  </div>
                </div>
                
                <div class="form-group">
                  <div class="input-wrapper">
                    <i class="fas fa-comment input-icon"></i>
                    <textarea v-model="contactForm.message" placeholder="Your Message" rows="4" required></textarea>
                  </div>
                </div>
                
                <button type="submit" class="btn-submit" :disabled="isSubmitting">
                  <span v-if="!isSubmitting">Send Message <i class="fas fa-paper-plane"></i></span>
                  <span v-else>Sending... <i class="fas fa-spinner fa-spin"></i></span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>






     <div v-if="showProductModal" class="modal-overlay" @click.self="closeProductModal">
      <div class="modal-container glass-card">
        <button class="modal-close" @click="closeProductModal">
          <i class="fas fa-times"></i>
        </button>
        
        <div v-if="productModalLoading" class="modal-loading">
          <div class="loading-spinner"></div>
          <p>Loading product details...</p>
        </div>
        
        <div v-else-if="selectedProduct" class="modal-content">
          <div class="modal-image">
            <img v-if="selectedProduct.image_url" :src="selectedProduct.image_url" :alt="selectedProduct.name" @error="handleImageError">
            <div v-else class="image-placeholder-large">
              <i class="fas fa-milk"></i>
            </div>
          </div>
          
          <div class="modal-info">
            <div class="product-category-badge">
              <i class="fas fa-tag"></i> {{ selectedProduct.category || 'Dairy Product' }}
            </div>
            <h2>{{ selectedProduct.name }}</h2>
            
            <div class="modal-description">
              <h4><i class="fas fa-info-circle"></i> Description</h4>
              <p>{{ selectedProduct.description }}</p>
            </div>
            
            <div class="modal-benefits" v-if="selectedProduct.benefits">
              <h4><i class="fas fa-heart"></i> Key Benefits</h4>
              <p>{{ selectedProduct.benefits }}</p>
            </div>
            
            <div class="modal-packaging" v-if="selectedProduct.packaging_sizes">
              <h4><i class="fas fa-box"></i> Available Sizes</h4>
              <div class="packaging-badges">
                <span v-for="size in selectedProduct.packaging_sizes.split(',')" :key="size" class="size-badge">
                  {{ size.trim() }}
                </span>
              </div>
            </div>
            
            <div class="modal-ingredients" v-if="selectedProduct.ingredients">
              <h4><i class="fas fa-list"></i> Ingredients</h4>
              <p>{{ selectedProduct.ingredients }}</p>
            </div>
            
            <div class="modal-nutrition" v-if="selectedProduct.nutritional_info">
              <h4><i class="fas fa-chart-line"></i> Nutritional Information</h4>
              <p>{{ selectedProduct.nutritional_info }}</p>
            </div>
            
            <div class="modal-actions">
              <!-- <router-link :to="`/product/${selectedProduct.id}`" class="btn btn-primary">
                View Full Details <i class="fas fa-arrow-right"></i>
              </router-link> -->
              <button @click="scrollToContact" class="btn btn-outline">
                Inquiry <i class="fas fa-envelope"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>






  </main>
</template>

<script>
import axios from 'axios'
import { scrollToSection } from '@/utils/scroll'
import ScrollProgress from '@/components/ScrollProgress.vue'
import BackToTop from '@/components/BacktoTop.vue'

export default {
  name: 'Home',
  components: {
    ScrollProgress,
    BackToTop
  },
  data() {
  return {
    // Products
    allProducts: [],
    displayedProducts: [],
    productsPage: 1,
    productsPerPage: 6,
    hasMoreProducts: true,
    totalProducts: 0,
    productsLoading: true,
    productsLoadingMore: false,
    
    // Product Modal
    showProductModal: false,
    selectedProduct: null,
    productModalLoading: false,



    // Blogs
    allBlogs: [],
    displayedBlogs: [],
    blogsPage: 1,
    blogsPerPage: 3,
    hasMoreBlogs: true,
    totalBlogs: 0,
    blogsLoading: true,
    blogsLoadingMore: false,

    // Blog Modal
    showBlogModal: false,
    selectedBlog: null,
    blogModalLoading: false,









      
      // Other data
      features: [
        { icon: 'fas fa-tint', title: '100% Pure & Fresh', description: 'Pasteurized and packed fresh daily from the slopes of Mount Kenya' },
        { icon: 'fas fa-hand-holding-heart', title: 'Farmer Owned', description: 'Supporting over 120,000 local farmers through fair trade practices' },
        { icon: 'fas fa-microscope', title: 'Quality Assured', description: 'Rigorous quality testing at every stage of production' },
        { icon: 'fas fa-truck-fast', title: 'Nationwide Delivery', description: 'Reaching millions of customers across Kenya every day' }
      ],
      statistics: [],
      testimonials: [],
      latestBlogs: [],
      blogLoading: true,
      contactForm: {
        name: '',
        email: '',
        subject: '',
        message: ''
      },
      isSubmitting: false
    }
  },
  mounted() {
    this.fetchProducts()
    this.fetchStatistics()
    this.fetchTestimonials()
    this.fetchBlogs()
    this.setupAOS()
  },
  methods: {
    // ========== PRODUCTS METHODS ==========
     async fetchProducts(reset = true) {
    try {
      if (reset) {
        this.productsLoading = true
        this.productsPage = 1
        this.hasMoreProducts = true
        this.displayedProducts = []
      }
      
      const response = await axios.get(`/api/products?page=${this.productsPage}&per_page=${this.productsPerPage}`)
      
      if (response.data && response.data.data) {
        const newProducts = response.data.data
        
        if (reset) {
          this.displayedProducts = newProducts
        } else {
          // Append new products WITHOUT scrolling
          this.displayedProducts = [...this.displayedProducts, ...newProducts]
        }
        
        // Store total products count
        this.totalProducts = response.data.pagination.total_items || 0
        
        // Check if there are more products
        this.hasMoreProducts = response.data.pagination.has_next || false
        
        // Store all products for reference
        if (reset) {
          this.allProducts = newProducts
        } else {
          this.allProducts = [...this.allProducts, ...newProducts]
        }
      }
      
      this.productsLoading = false
      this.productsLoadingMore = false
      
    } catch (error) {
      console.error('Error fetching products:', error)
      this.productsLoading = false
      this.productsLoadingMore = false
      
      // Fallback sample data for demo
      this.displayedProducts = [
        {
          id: 1,
          name: 'Mount Kenya Fresh Milk',
          category: 'Fresh Milk',
          description: 'Pure, fresh milk from the slopes of Mount Kenya. Pasteurized and packed fresh daily.',
          benefits: 'Rich in calcium and protein, supports bone health',
          packaging_sizes: '500ml, 1L, 2L',
          featured: true,
          image_url: null
        },
        {
          id: 2,
          name: 'Mount Kenya Yoghurt',
          category: 'Yoghurt',
          description: 'Creamy, delicious yoghurt made from fresh milk.',
          benefits: 'Contains probiotics for gut health',
          packaging_sizes: '200ml, 500ml, 1L',
          featured: true,
          image_url: null
        },
        {
          id: 3,
          name: 'Mount Kenya Lala',
          category: 'Lala',
          description: 'Traditional fermented milk drink, rich and tangy.',
          benefits: 'Natural probiotics, aids digestion',
          packaging_sizes: '500ml, 1L',
          featured: true,
          image_url: null
        },
        {
          id: 4,
          name: 'Mount Kenya Ghee',
          category: 'Ghee',
          description: 'Pure clarified butter, perfect for cooking.',
          benefits: 'Lactose-free, high smoke point',
          packaging_sizes: '500g, 1kg',
          featured: true,
          image_url: null
        }
      ]
      this.totalProducts = this.displayedProducts.length
      this.hasMoreProducts = false
    }
  },
  
  async loadMoreProducts() {
    // Prevent multiple simultaneous loads
    if (this.productsLoadingMore || !this.hasMoreProducts) return
    
    this.productsLoadingMore = true
    this.productsPage++
    
    // Fetch next page WITHOUT resetting
    await this.fetchProducts(false)
    
    // After products are loaded, ensure we stay at the same scroll position
    // The products will simply appear below the existing ones
    this.$nextTick(() => {
      // Optional: Add a subtle highlight effect to newly loaded products
      const newProducts = document.querySelectorAll('.product-card:not(.loaded)')
      newProducts.forEach(product => {
        product.classList.add('loaded')
        product.style.animation = 'fadeInUp 0.5s ease-out'
      })
    })
  },
  
    
    // async loadMoreProducts() {
    //   if (this.productsLoadingMore || !this.hasMoreProducts) return
      
    //   this.productsLoadingMore = true
    //   this.productsPage++
    //   await this.fetchProducts(false)
    // },
    
    async openProductModal(productId) {
      this.showProductModal = true
      this.productModalLoading = true
      
      try {
        // First check if we already have the product in displayedProducts
        const existingProduct = this.displayedProducts.find(p => p.id === productId)
        
        if (existingProduct && existingProduct.benefits) {
          // If we have full details, use them
          this.selectedProduct = existingProduct
          this.productModalLoading = false
        } else {
          // Fetch full product details
          const response = await axios.get(`/api/products/${productId}`)
          this.selectedProduct = response.data
          this.productModalLoading = false
        }
      } catch (error) {
        console.error('Error fetching product details:', error)
        this.productModalLoading = false
        // Fallback: use product from displayed list
        this.selectedProduct = this.displayedProducts.find(p => p.id === productId)
      }
    },
    
    closeProductModal() {
      this.showProductModal = false
      this.selectedProduct = null
      this.productModalLoading = false
    },
    
    // ========== STATISTICS METHODS ==========
    async fetchStatistics() {
      try {
        const response = await axios.get('/api/statistics')
        this.statistics = response.data.length > 0 ? response.data : [
          { label: 'Our Farmers', value: '120,000', suffix: '+' },
          { label: 'Cooperative Societies', value: '120', suffix: '+' },
          { label: 'Litres Processed', value: '600,000', suffix: '+' },
          { label: 'Customers Served', value: '10,000,000', suffix: '+' }
        ]
      } catch (error) {
        console.error('Error fetching statistics:', error)
        this.statistics = [
          { label: 'Our Farmers', value: '120,000', suffix: '+' },
          { label: 'Cooperative Societies', value: '120', suffix: '+' },
          { label: 'Litres Processed', value: '600,000', suffix: '+' },
          { label: 'Customers Served', value: '10,000,000', suffix: '+' }
        ]
      }
    },
    
    // ========== TESTIMONIALS METHODS ==========
    async fetchTestimonials() {
      try {
        const response = await axios.get('/api/testimonials?limit=3')
        this.testimonials = response.data
      } catch (error) {
        console.error('Error fetching testimonials:', error)
        this.testimonials = []
      }
    },
    
    
async fetchBlogs(reset = true) {
  try {
    if (reset) {
      this.blogsLoading = true
      this.blogsPage = 1
      this.hasMoreBlogs = true
      this.displayedBlogs = []
    }

    const perPage = this.blogsPerPage
    let response

    if (reset) {
      // Initial load
      response = await axios.get(`/api/blog?simple=true&per_page=${perPage}`)

      const payload = response?.data
      const dataArray = Array.isArray(payload)
        ? payload
        : (payload?.items && Array.isArray(payload.items) ? payload.items : [])

      this.displayedBlogs = dataArray
      this.totalBlogs = dataArray.length
      this.hasMoreBlogs = dataArray.length === perPage
    } else {
      // Load more
      response = await axios.get(`/api/blog?page=${this.blogsPage}&per_page=${perPage}`)

      const payload = response?.data
      const newBlogs = payload?.data && Array.isArray(payload.data)
        ? payload.data
        : (payload?.items && Array.isArray(payload.items) ? payload.items : [])

      const existingIds = new Set(this.displayedBlogs.map(b => b.id))
      const uniqueNewBlogs = newBlogs.filter(b => !existingIds.has(b.id))

      this.displayedBlogs = [...this.displayedBlogs, ...uniqueNewBlogs]
      this.totalBlogs = payload?.pagination?.total_items || this.totalBlogs
      this.hasMoreBlogs = payload?.pagination?.has_next || false
    }

    this.blogsLoading = false
    this.blogsLoadingMore = false
  } catch (error) {
    console.error('Error fetching blogs:', error)
    this.blogsLoading = false
    this.blogsLoadingMore = false

    // Fallback sample data
    if (this.displayedBlogs.length === 0) {
      this.displayedBlogs = [
        {
          id: 1,
          title: 'Welcome to Meru Dairy',
          slug: 'welcome-to-meru-dairy',
          excerpt: 'Learn about our journey and commitment to quality dairy products.',
          content: 'Full article content...',
          views: 150,
          created_at: new Date().toISOString(),
          author: 'Communications Team'
        },
        {
          id: 2,
          title: 'Farmer Success Stories',
          slug: 'farmer-success-stories',
          excerpt: 'Read inspiring stories from our cooperative members.',
          content: 'Full article content...',
          views: 89,
          created_at: new Date().toISOString(),
          author: 'Farmer Support Team'
        }
      ]
      this.totalBlogs = this.displayedBlogs.length
    }
    this.hasMoreBlogs = false
  }
},


async loadMoreBlogs() {
  if (this.blogsLoadingMore || !this.hasMoreBlogs) return
  
  this.blogsLoadingMore = true
  this.blogsPage++
  
  await this.fetchBlogs(false)
  
  this.$nextTick(() => {
    const newBlogs = document.querySelectorAll('.blog-card:not(.loaded)')
    newBlogs.forEach(blog => {
      blog.classList.add('loaded')
      blog.style.animation = 'fadeInUp 0.5s ease-out'
    })
  })
},

async loadMoreBlogs() {
  // Prevent multiple simultaneous loads
  if (this.blogsLoadingMore || !this.hasMoreBlogs) return
  
  this.blogsLoadingMore = true
  this.blogsPage++
  
  // Fetch next page WITHOUT resetting
  await this.fetchBlogs(false)
  
  // After loading, scroll to the newly added blogs smoothly
  this.$nextTick(() => {
    const newBlogs = document.querySelectorAll('.blog-card:not(.loaded)')
    if (newBlogs.length > 0) {
      newBlogs.forEach(blog => {
        blog.classList.add('loaded')
        blog.style.animation = 'fadeInUp 0.5s ease-out'
      })
    }
  })
},
  
  async openBlogModal(slug) {
    this.showBlogModal = true
    this.blogModalLoading = true
    
    try {
      // First check if we already have the blog in displayedBlogs
      const existingBlog = this.displayedBlogs.find(b => b.slug === slug)
      
      if (existingBlog && existingBlog.content) {
        // If we have full content, use it
        this.selectedBlog = existingBlog
        this.blogModalLoading = false
      } else {
        // Fetch full blog details
        const response = await axios.get(`/api/blog/${slug}`)
        this.selectedBlog = response.data
        this.blogModalLoading = false
      }
    } catch (error) {
      console.error('Error fetching blog details:', error)
      this.blogModalLoading = false
      // Fallback: use blog from displayed list
      this.selectedBlog = this.displayedBlogs.find(b => b.slug === slug)
    }
  },
  
  closeBlogModal() {
    this.showBlogModal = false
    this.selectedBlog = null
    this.blogModalLoading = false
  },
  
    
    // ========== UI METHODS ==========
    setupAOS() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1'
            entry.target.style.transform = 'translateY(0)'
          }
        })
      }, { threshold: 0.1 })
      
      setTimeout(() => {
        document.querySelectorAll('[data-aos]').forEach(el => {
          el.style.opacity = '0'
          el.style.transform = 'translateY(30px)'
          el.style.transition = 'all 0.6s ease-out'
          observer.observe(el)
        })
      }, 100)
    },
    
    setImagePlaceholder(e) {
      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"%3E%3Crect width="400" height="300" fill="%23e0e7ff"/%3E%3Ctext x="200" y="150" text-anchor="middle" fill="%231e3a8a" font-size="16"%3EMeru Dairy%3C/text%3E%3C/svg%3E'
    },
    
    scrollToAbout() {
      scrollToSection('about', 80)
    },
    
    scrollToProducts() {
      scrollToSection('products', 80)
    },
    
    scrollToContact() {
      scrollToSection('contact', 80)
      this.closeProductModal()
    },
    
    readPost(slug) {
      this.$router.push(`/blog/${slug}`)
    },
    
    viewAllBlogs() {
      this.$router.push('/blog')
    },
    
    async submitContactForm() {
      this.isSubmitting = true
      try {
        await axios.post('/api/contact', this.contactForm)
        alert('Thank you for your message! We will get back to you soon.')
        this.contactForm = { name: '', email: '', subject: '', message: '' }
      } catch (error) {
        alert('Thank you for your message! We will get back to you soon.')
        this.contactForm = { name: '', email: '', subject: '', message: '' }
      } finally {
        this.isSubmitting = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Recent'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    
    truncate(text, length) {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    },
    
    handleImageError(e) {
      const placeholder = e.target.parentElement?.querySelector('.image-placeholder')
      if (placeholder) {
        e.target.style.display = 'none'
        placeholder.style.display = 'flex'
      }
    }
  }
}
</script>

<style scoped>
/* Add these new styles to your existing CSS */

/* ========== PRODUCTS SECTION ENHANCEMENTS ========== */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.product-card {
  position: relative;
  background: white;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
  animation: fadeInUp 0.5s ease-out;
}

.product-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.product-image {
  position: relative;
  height: 250px;
  overflow: hidden;
  cursor: pointer;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.product-card:hover .product-image img {
  transform: scale(1.1);
}

.product-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(30,58,138,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .product-overlay {
  opacity: 1;
}

.view-details {
  background: transparent;
  color: white;
  border: 2px solid white;
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.view-details:hover {
  background: white;
  color: #1e3a8a;
}

.product-details-btn {
  margin: 0 20px 20px;
  background: none;
  border: none;
  color: #f59e0b;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.product-details-btn:hover {
  gap: 12px;
  color: #d97706;
}

/* Load More Button */
.load-more-container {
  text-align: center;
  margin: 40px 0 20px;
  padding: 20px 0;
}

.btn-load-more {
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  border: none;
  color: white;
  padding: 14px 32px;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  box-shadow: 0 4px 15px rgba(30,58,138,0.3);
}

.btn-load-more:hover:not(:disabled) {
  background: #1e3a8a;
  color: white;
  transform: translateY(-2px);
}

.btn-load-more:hover:not(:disabled) i {
  transform: translateY(3px);
}

.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.view-all-link {
  text-align: center;
  margin-top: 20px;
}

.btn-link {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-link:hover {
  gap: 12px;
  color: #d97706;
}

/* No Products */
.no-products {
  text-align: center;
  padding: 60px;
  background: #f8fafc;
  border-radius: 20px;
}

.no-products-icon {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 20px;
}

.no-products h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

/* ========== MODAL STYLES ========== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  overflow-y: auto;
  padding: 20px;
}

.modal-container {
  position: relative;
  max-width: 1000px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  background: white;
  border-radius: 24px;
  padding: 30px;
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(0,0,0,0.1);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s;
  z-index: 10;
}

.modal-close:hover {
  background: #ef4444;
  color: white;
}

.modal-loading {
  text-align: center;
  padding: 60px;
}

.modal-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.modal-image {
  border-radius: 16px;
  overflow: hidden;
  background: #f8fafc;
}

.modal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder-large {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  font-size: 5rem;
  color: #1e3a8a;
}

.modal-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-category-badge {
  display: inline-block;
  background: #e0e7ff;
  color: #1e3a8a;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  width: fit-content;
}

.modal-info h2 {
  font-size: 1.8rem;
  color: #1e3a8a;
  margin: 0;
}

.modal-info h4 {
  color: #1e3a8a;
  margin-bottom: 8px;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-info p {
  color: #666;
  line-height: 1.6;
}

.packaging-badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.size-badge {
  background: #f3f4f6;
  color: #1e3a8a;
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
}

.modal-actions {
  display: flex;
  gap: 15px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.btn-outline {
  background: transparent;
  color: #1e3a8a;
  border: 2px solid #1e3a8a;
  border-radius: 50px;
  padding: 10px 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-outline:hover {
  background: #1e3a8a;
  color: white;
}

/* Modal Responsive */
@media (max-width: 768px) {
  .modal-content {
    grid-template-columns: 1fr;
  }
  
  .modal-container {
    padding: 20px;
  }
  
  .modal-info h2 {
    font-size: 1.4rem;
  }
}

/* Animation for modal */
.modal-overlay {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
/* ========== HERO SECTION ========== */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  overflow: hidden;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" opacity="0.05"><path fill="white" d="M50,30 L60,50 L50,70 L40,50 Z"/><circle cx="70" cy="30" r="10"/><circle cx="30" cy="70" r="10"/></svg>') repeat;
}

.hero-pattern {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(to top, #f8fafc, transparent);
}

.hero-content {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 100px 0;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-text {
  max-width: 700px;
  margin-bottom: 60px;
}

.hero-badge {
  display: inline-block;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.85rem;
  color: white;
  margin-bottom: 20px;
}

.hero-badge i {
  margin-right: 8px;
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  color: white;
  line-height: 1.2;
  margin-bottom: 20px;
}

.hero-title .highlight {
  color: #f59e0b;
  position: relative;
  display: inline-block;
}

.hero-description {
  font-size: 1.2rem;
  color: rgba(255,255,255,0.9);
  margin-bottom: 30px;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.btn-large {
  padding: 14px 32px;
  font-size: 1rem;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.btn-outline-light {
  background: transparent;
  color: white;
  border: 2px solid white;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-outline-light:hover {
  background: white;
  color: #1e3a8a;
  transform: translateY(-2px);
}

.btn-icon {
  transition: transform 0.3s;
}

.btn-large:hover .btn-icon {
  transform: translateX(5px);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255,255,255,0.2);
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #f59e0b;
  margin-bottom: 5px;
}

.stat-label {
  color: white;
  font-size: 0.9rem;
}

.scroll-indicator {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  color: white;
  z-index: 1;
}

.scroll-indicator span {
  display: block;
  font-size: 0.8rem;
  margin-bottom: 10px;
  opacity: 0.7;
}

.scroll-mouse {
  width: 26px;
  height: 40px;
  border: 2px solid white;
  border-radius: 20px;
  position: relative;
  margin: 0 auto;
}

.scroll-mouse::after {
  content: '';
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 8px;
  background: white;
  border-radius: 2px;
  animation: scroll 2s infinite;
}

@keyframes scroll {
  0% { transform: translate(-50%, 0); opacity: 1; }
  100% { transform: translate(-50%, 15px); opacity: 0; }
}

/* ========== SECTION HEADER WITH IMAGE ========== */
.section-header-with-image {
  display: flex;
  align-items: center;
  gap: 50px;
  margin-bottom: 60px;
}

.section-header-with-image.reverse {
  flex-direction: row-reverse;
}

.section-header-content {
  flex: 1;
}

.section-header-image {
  flex: 1;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.section-header-image img {
  width: 100%;
  height: 250px;
  object-fit: cover;
  transition: transform 0.3s;
}

.section-header-image:hover img {
  transform: scale(1.05);
}

.image-overlay-text {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(245,158,11,0.9);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-badge {
  display: inline-block;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  color: white;
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.section-badge i {
  margin-right: 8px;
}

.section-title {
  font-size: 2.5rem;
  color: #1e3a8a;
  margin-bottom: 20px;
  line-height: 1.2;
}

.section-subtitle {
  color: #666;
  font-size: 1rem;
  line-height: 1.6;
}

/* ========== ABOUT SECTION ========== */
.about-section {
  padding: 80px 0;
  background: white;
}

.about-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

.about-stat-card {
  text-align: center;
  padding: 30px;
  background: #f8fafc;
  border-radius: 20px;
  transition: transform 0.3s;
}

.about-stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
  color: #f59e0b;
  margin-bottom: 15px;
}

.about-stat-card .stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #1e3a8a;
}

.about-stat-card .stat-label {
  color: #666;
  font-size: 0.9rem;
}

.ceo-message {
  display: flex;
  gap: 40px;
  padding: 40px;
  background: linear-gradient(135deg, #f0f4ff, white);
}

.ceo-image {
  flex-shrink: 0;
  position: relative;
  width: 250px;
  height: 250px;
  border-radius: 20px;
  overflow: hidden;
}

.ceo-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ceo-badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: #f59e0b;
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.ceo-content {
  flex: 1;
  position: relative;
}

.quote-icon {
  font-size: 3rem;
  color: #f59e0b;
  opacity: 0.3;
  margin-bottom: 10px;
}

.ceo-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #555;
  margin-bottom: 20px;
}

.ceo-info h4 {
  font-size: 1.3rem;
  color: #1e3a8a;
  margin-bottom: 5px;
}

.ceo-info span {
  color: #f59e0b;
  font-weight: 500;
}

.ceo-signature {
  margin-top: 10px;
  color: #666;
  font-size: 0.85rem;
}

.ceo-signature i {
  color: #f59e0b;
  margin-right: 5px;
}

/* ========== FEATURES SECTION ========== */
.features-section {
  padding: 80px 0;
  background: #f8fafc;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.feature-card {
  padding: 40px 30px;
  text-align: center;
  background: white;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-icon {
  font-size: 3rem;
  color: #f59e0b;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.3rem;
  color: #1e3a8a;
  margin-bottom: 15px;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* ========== PRODUCTS SECTION ========== */
.products-section {
  padding: 80px 0;
  background: white;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.product-card {
  position: relative;
  background: white;
  overflow: hidden;
  transition: all 0.3s;
}

.product-card:hover {
  transform: translateY(-10px);
}

.product-image {
  position: relative;
  height: 250px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.product-card:hover .product-image img {
  transform: scale(1.1);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  gap: 10px;
  font-size: 3rem;
  color: #1e3a8a;
}

.product-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(30,58,138,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .product-overlay {
  opacity: 1;
}

.view-details {
  background: transparent;
  color: white;
  border: 2px solid white;
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.view-details:hover {
  background: white;
  color: #1e3a8a;
}

.product-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background: #f59e0b;
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  z-index: 1;
}

.product-badge i {
  margin-right: 5px;
}

.product-card h3 {
  padding: 20px 20px 10px;
  font-size: 1.2rem;
  color: #1e3a8a;
}

.product-card p {
  padding: 0 20px;
  color: #666;
  margin-bottom: 10px;
}

.product-meta {
  padding: 0 20px 20px;
  color: #f59e0b;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ========== SHOP SECTION ========== */
.shop-section {
  padding: 80px 0;
  background: #f8fafc;
}

.shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

.shop-card {
  padding: 40px 30px;
  text-align: center;
  background: white;
  transition: all 0.3s;
}

.shop-card:hover {
  transform: translateY(-10px);
}

.shop-icon {
  font-size: 3rem;
  color: #f59e0b;
  margin-bottom: 20px;
}

.shop-card h3 {
  font-size: 1.3rem;
  color: #1e3a8a;
  margin-bottom: 15px;
}

.shop-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.shop-link {
  background: none;
  border: none;
  color: #f59e0b;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: all 0.3s;
}

.shop-link:hover {
  gap: 12px;
  color: #d97706;
}

.shop-cta {
  text-align: center;
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-outline {
  background: transparent;
  color: #1e3a8a;
  border: 2px solid #1e3a8a;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  font-size: 1rem;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: #1e3a8a;
  color: white;
  transform: translateY(-2px);
}

.btn-outline i {
  margin-left: 8px;
}

/* ========== TESTIMONIALS SECTION ========== */
.testimonials-section {
  padding: 80px 0;
  background: white;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.testimonial-card {
  padding: 30px;
  position: relative;
  background: #f8fafc;
}

.quote-mark {
  font-size: 3rem;
  color: #f59e0b;
  opacity: 0.3;
  margin-bottom: 15px;
}

.testimonial-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 20px;
}

.testimonial-author {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.author-info strong {
  display: block;
  color: #1e3a8a;
  margin-bottom: 5px;
}

.author-info span {
  font-size: 0.85rem;
  color: #666;
}

.rating {
  color: #fbbf24;
}

/* ========== BLOG SECTION ========== */
.blog-section {
  padding: 80px 0;
  background: #f8fafc;
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.blog-card {
  background: white;
  overflow: hidden;
  transition: all 0.3s;
}

.blog-card:hover {
  transform: translateY(-5px);
}

.blog-image {
  height: 220px;
  overflow: hidden;
}

.blog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.blog-card:hover .blog-image img {
  transform: scale(1.1);
}

.blog-content {
  padding: 25px;
}

.blog-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-size: 0.85rem;
  color: #666;
}

.blog-meta i {
  margin-right: 5px;
}

.blog-card h3 {
  font-size: 1.2rem;
  color: #1e3a8a;
  margin-bottom: 10px;
  line-height: 1.4;
}

.blog-card p {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.6;
}

.blog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.blog-author {
  font-size: 0.8rem;
  color: #666;
}

.blog-author i {
  margin-right: 5px;
}

.read-more {
  color: #f59e0b;
  font-weight: 600;
  background: none;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.read-more:hover {
  gap: 10px;
}

/* ========== CONTACT SECTION ========== */
.contact-section {
  padding: 80px 0;
  background: white;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
}

.info-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.info-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: #f8fafc;
  transition: all 0.3s;
}

.info-card:hover {
  transform: translateX(5px);
}

.info-icon {
  font-size: 2rem;
  color: #f59e0b;
}

.info-content h3 {
  color: #1e3a8a;
  margin-bottom: 8px;
  font-size: 1.1rem;
}

.info-content p {
  color: #666;
  line-height: 1.5;
}

.info-content a {
  color: #f59e0b;
  text-decoration: none;
}

.social-links-section h3 {
  margin-bottom: 15px;
  font-size: 1.1rem;
  color: #1e3a8a;
}

.social-links-section h3 i {
  margin-right: 8px;
  color: #f59e0b;
}

.social-links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 15px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #f8fafc;
  text-decoration: none;
  color: #1e3a8a;
  font-weight: 500;
  transition: all 0.3s;
}

.social-link:hover {
  background: #1e3a8a;
  color: white;
  transform: translateY(-3px);
}

.form-card {
  padding: 40px;
  background: #f8fafc;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-icon {
  font-size: 3rem;
  color: #f59e0b;
  margin-bottom: 10px;
}

.form-header h3 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin-bottom: 8px;
}

.form-header p {
  color: #666;
}

.form-group {
  margin-bottom: 20px;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.input-wrapper textarea ~ .input-icon {
  top: 20px;
  transform: none;
}

.input-wrapper input,
.input-wrapper textarea {
  width: 100%;
  padding: 12px 12px 12px 45px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-family: inherit;
  font-size: 0.9rem;
  background: white;
  transition: all 0.3s;
}

.input-wrapper input:focus,
.input-wrapper textarea:focus {
  outline: none;
  border-color: #1e3a8a;
  box-shadow: 0 0 0 3px rgba(30,58,138,0.1);
}

.btn-submit {
  width: 100%;
  padding: 14px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-submit:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ========== GLASS CARD EFFECT ========== */
.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

.view-all {
  text-align: center;
}

.btn-secondary {
  background: transparent;
  color: #1e3a8a;
  border: 2px solid #1e3a8a;
  border-radius: 50px;
  padding: 12px 30px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary:hover {
  background: #1e3a8a;
  color: white;
  transform: translateY(-2px);
}

/* ========== LOADING STATES ========== */
.loading-state {
  text-align: center;
  padding: 60px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-posts {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
}

.no-posts-icon {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 20px;
}

.no-posts h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
}

/* ========== ANIMATIONS ========== */
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

.delay-2 {
  animation-delay: 0.2s;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ========== RESPONSIVE ========== */
@media (max-width: 968px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .section-header-with-image,
  .section-header-with-image.reverse {
    flex-direction: column;
  }
  
  .contact-grid {
    grid-template-columns: 1fr;
  }
  
  .ceo-message {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .ceo-image {
    width: 200px;
    height: 200px;
  }
  
  .section-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .features-grid,
  .products-grid,
  .testimonials-grid,
  .blog-grid,
  .shop-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-stats {
    grid-template-columns: 1fr 1fr;
  }
  
  .about-stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .form-card {
    padding: 25px;
  }
  
  .shop-cta {
    flex-direction: column;
    align-items: center;
  }
  
  .shop-cta .btn-large {
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }
}
</style>