
<template>
  <main>
    <!-- Scroll Progress Indicator -->
    <ScrollProgress />
    
    <!-- Back to Top Button -->
    <BackToTop />

    <!-- Hero Section -->
    <section id="home" class="hero-section" ref="heroSection" >

<!-- :style="{ paddingTop: navbarHeight + 'px' }" -->

      <swiper
        :modules="modules"
        :slides-per-view="1"
        :space-between="0"
        :loop="true"
        :autoplay="{ delay: 5000, disableOnInteraction: false }"
        :pagination="{ clickable: true, dynamicBullets: true }"
        :navigation="true"
        :effect="'fade'"
        :speed="1000"
        class="hero-swiper"
      >
        <swiper-slide v-for="slide in slides" :key="slide.id">
          <div class="slide-background">
            <img :src="slide.image" :alt="slide.title" class="slide-image" @error="setImagePlaceholder">
          </div>
          <div class="slide-content">
            <div class="container">
              <div class="hero-text animate-fade-in-up">
                <span class="hero-badge"><i class="fas fa-trophy"></i> {{ slide.badge }}</span>
                <h1 class="hero-title" v-html="slide.title"></h1>
                <p class="hero-description">{{ slide.description }}</p>
                <div class="hero-buttons">
                  <button @click="scrollToProducts" class="btn btn-primary btn-large">
                    Explore Products <i class="fas fa-arrow-right btn-icon"></i>
                  </button>
                  <button @click="scrollToAbout" class="btn btn-outline-light btn-large">
                    Learn More <i class="fas fa-play-circle"></i>
                  </button>
                  <button v-if="slide.id === 4" @click="openBookingModal" class="btn btn-tour btn-large">
                    <i class="fas fa-factory"></i> Book a Factory Tour
                  </button>
                </div>
              </div>
            </div>
          </div>
        </swiper-slide>
      </swiper>

      <!-- Hero Stats - Moved down for better spacing -->
      <div class="hero-stats-container">
        <div class="container">
          <div class="hero-stats">
            <div class="stat-card" v-for="stat in statistics" :key="stat.label">
              <div class="stat-number">{{ stat.value }}{{ stat.suffix }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- <div class="scroll-indicator">
        <span>Scroll to explore</span>
        <div class="scroll-mouse"></div>
      </div> -->
    </section>

    <!-- About Section -->
    <section id="about" class="about-section">
      <div class="container">
        <div class="section-header-with-image">
          <div class="section-header-content">
            <span class="section-badge"><i class="fas fa-leaf"></i> Our Story</span>
            <h2 class="section-title">Kenya's Largest<br>Dairy Co-operative</h2>
            <p class="section-subtitle">
              Meru Central Dairy Co-operative Union Ltd has grown from humble beginnings 
              to become Kenya's biggest dairy processor, empowering over 120,000 farmers 
              and serving millions of customers nationwide.
            </p>
            <div style="margin-top: 24px;">
              <button @click="openBookingModal" class="btn btn-primary btn-large">
                <i class="fas fa-calendar-plus"></i> Schedule Your Factory Tour
              </button>
            </div>
          </div>
          <div class="section-header-image">
            <img src="/images/about-header.jpeg" alt="About Meru Dairy" @error="setImagePlaceholder">
            <div class="image-overlay-text"><i class="fas fa-quote-right"></i></div>
          </div>
        </div>

        <div class="about-grid">
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

          <div class="ceo-message glass-card">
            <div class="ceo-image">
              <img src="/images/ceo.jpeg" alt="CEO - Dr. Kenneth Gitonga" @error="setImagePlaceholder">
              <div class="ceo-badge"><i class="fas fa-crown"></i> CEO</div>
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
                <h4>Mr. Kenneth Gitonga</h4>
                <span>Chief Executive Officer</span>
                <div class="ceo-signature"><i class="fas fa-certificate"></i> 20+ Years in Dairy Industry</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header-with-image reverse">
          <div class="section-header-image">
            <img src="/images/features-header.jpeg" alt="Our Features" @error="setImagePlaceholder">
          </div>
          <div class="section-header-content">
            <span class="section-badge"><i class="fas fa-star"></i> Why Choose Us</span>
            <h2 class="section-title">Excellence in Every Drop</h2>
            <p class="section-subtitle">Discover what makes Mount Kenya Milk the preferred choice for millions of Kenyans</p>
          </div>
        </div>
        
        <div class="features-grid">
          <div class="feature-card glass-card" v-for="feature in features" :key="feature.title">
            <div class="feature-icon"><i :class="feature.icon"></i></div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Products Section -->
    <section id="products" class="products-section">
      <div class="container">
        <div class="section-header-with-image">
          <div class="section-header-content">
            <span class="section-badge"><i class="fas fa-box-open"></i> Our Collection</span>
            <h2 class="section-title">Premium Dairy Products</h2>
            <p class="section-subtitle">Crafted with care for your family's nutrition and wellbeing</p>
          </div>
          <div class="section-header-image">
            <img src="/images/products-header.jpeg" alt="Our Products" @error="setImagePlaceholder">
          </div>
        </div>
        
        <div v-if="productsLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading products...</p>
        </div>
        
        <div v-else class="products-grid">
          <div class="product-card-wrapper" v-for="product in displayedProducts" :key="product.id">
            <div class="product-card">
              <div class="product-image" @click="openProductModal(product.id)">
                <img v-if="product.image_url" :src="product.image_url" :alt="product.name" @error="handleImageError">
                <div v-else class="image-placeholder"><i class="fas fa-milk"></i><span>{{ product.name }}</span></div>
                <div class="product-overlay">
                  <button class="view-details-btn"><i class="fas fa-eye"></i> Quick View</button>
                </div>
              </div>
              <div class="product-badge" v-if="product.featured"><i class="fas fa-fire"></i> Featured</div>
              <div class="product-info">
                <h3>{{ truncate(product.name, 40) }}</h3>
                <p class="product-description">{{ truncate(product.description, 80) }}</p>
                <div class="product-meta" v-if="product.packaging_sizes">
                  <i class="fas fa-weight-hanging"></i>
                  <span>{{ product.packaging_sizes }}</span>
                </div>
                <button @click="openProductModal(product.id)" class="product-details-btn">
                  Quick View <i class="fas fa-arrow-right"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="!productsLoading && displayedProducts.length === 0 && !hasMoreProducts" class="no-products">
          <div class="no-products-icon"><i class="fas fa-box-open"></i></div>
          <h3>No Products Found</h3>
          <p>Check back soon for our delicious dairy products!</p>
        </div>
        
        <div v-if="hasMoreProducts && !productsLoading" class="load-more-container">
          <button @click="loadMoreProducts" class="btn-load-more" :disabled="productsLoadingMore">
            <i v-if="productsLoadingMore" class="fas fa-spinner fa-spin"></i>
            <span v-else><i class="fas fa-arrow-down"></i> Load More Products</span>
          </button>
        </div>
        
        <div v-if="displayedProducts.length > 0 && !productsLoading" class="product-count">
          <span>Showing {{ displayedProducts.length }} of {{ totalProducts }} products</span>
        </div>
      </div>
    </section>

    <!-- Product Detail Modal -->
    <div v-if="showProductModal" class="modal-overlay" @click.self="closeProductModal">
      <div class="modal-container product-modal">
        <button class="modal-close" @click="closeProductModal"><i class="fas fa-times"></i></button>
        
        <div v-if="productModalLoading" class="modal-loading">
          <div class="loading-spinner"></div>
          <p>Loading product details...</p>
        </div>
        
        <div v-else-if="selectedProduct" class="product-modal-content">
          <div class="product-modal-image">
            <img v-if="selectedProduct.image_url" :src="selectedProduct.image_url" :alt="selectedProduct.name" @error="handleImageError">
            <div v-else class="image-placeholder-large"><i class="fas fa-milk"></i></div>
          </div>
          
          <div class="product-modal-info">
            <div class="product-category-badge"><i class="fas fa-tag"></i> {{ selectedProduct.category || 'Dairy Product' }}</div>
            <h2>{{ selectedProduct.name }}</h2>
            
            <div class="info-section">
              <h4><i class="fas fa-info-circle"></i> Description</h4>
              <p>{{ selectedProduct.description }}</p>
            </div>
            
            <div class="info-section" v-if="selectedProduct.benefits">
              <h4><i class="fas fa-heart"></i> Key Benefits</h4>
              <p>{{ selectedProduct.benefits }}</p>
            </div>
            
            <div class="info-section" v-if="selectedProduct.packaging_sizes">
              <h4><i class="fas fa-box"></i> Available Sizes</h4>
              <div class="packaging-badges">
                <span v-for="size in selectedProduct.packaging_sizes.split(',')" :key="size" class="size-badge">
                  {{ size.trim() }}
                </span>
              </div>
            </div>
            
            <div class="info-section" v-if="selectedProduct.ingredients">
              <h4><i class="fas fa-list"></i> Ingredients</h4>
              <p>{{ selectedProduct.ingredients }}</p>
            </div>
            
            <div class="info-section" v-if="selectedProduct.nutritional_info">
              <h4><i class="fas fa-chart-line"></i> Nutritional Information</h4>
              <p>{{ selectedProduct.nutritional_info }}</p>
            </div>
            
            <div class="info-section" v-if="selectedProduct.storage_instructions">
              <h4><i class="fas fa-temperature-low"></i> Storage Instructions</h4>
              <p>{{ selectedProduct.storage_instructions }}</p>
            </div>
            
            <div class="info-section" v-if="selectedProduct.shelf_life">
              <h4><i class="fas fa-hourglass-half"></i> Shelf Life</h4>
              <p>{{ selectedProduct.shelf_life }}</p>
            </div>
            
            <div class="modal-actions">
              <button @click="scrollToContact" class="btn btn-outline">Inquiry <i class="fas fa-envelope"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Shop Online Section -->
    <section id="shop" class="shop-section">
      <div class="container">
        <div class="section-header-with-image reverse">
          <div class="section-header-image">
            <img src="/images/shop-header.jpeg" alt="Shop Online" @error="setImagePlaceholder">
          </div>
          <div class="section-header-content">
            <span class="section-badge"><i class="fas fa-shopping-cart"></i> Shop Online</span>
            <h2 class="section-title">Convenient Delivery<br>at Your Doorstep</h2>
            <p class="section-subtitle">Order fresh dairy products online and get them delivered to your home</p>
          </div>
        </div>
        
        <div class="shop-grid">
          <div class="shop-card glass-card">
            <div class="shop-icon"><i class="fas fa-store"></i></div>
            <h3>Online Store</h3>
            <p>Browse and order our full range of dairy products from our online shop</p>
            <a href="https://shop.mountkenyamilk.co.ke/" target="_blank" class="shop-link">Visit Our Shop <i class="fas fa-arrow-right"></i></a>
          </div>
          
          <div class="shop-card glass-card">
            <div class="shop-icon"><i class="fas fa-boxes"></i></div>
            <h3>Bulk Orders</h3>
            <p>Special pricing for wholesale and bulk purchases</p>
            <button @click="scrollToContact" class="shop-link">Contact Sales <i class="fas fa-arrow-right"></i></button>
          </div>
          
          <div class="shop-card glass-card">
            <div class="shop-icon"><i class="fas fa-truck-fast"></i></div>
            <h3>Fast Delivery</h3>
            <p>Free delivery on orders above KES 2,000 within Nairobi</p>
            <button @click="scrollToContact" class="shop-link">Learn More <i class="fas fa-arrow-right"></i></button>
          </div>
          
          <div class="shop-card glass-card tour-card">
            <div class="shop-icon"><i class="fas fa-factory"></i></div>
            <h3>Factory Tour</h3>
            <p>Experience the magic of dairy production with a guided factory tour</p>
            <button @click="openBookingModal" class="shop-link tour-link">
              Book a Tour <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
        
        <div class="physical-shops-section">
          <button @click="showOutletsModal = true" class="btn-outlets">
            <i class="fas fa-store"></i> Find Physical Shops & Depots Near You</button>
        </div>
        
        <div class="shop-cta">
          <a href="https://shop.mountkenyamilk.co.ke/" target="_blank" class="btn btn-primary btn-large">Start Shopping Now <i class="fas fa-arrow-right btn-icon"></i></a>
          <button @click="scrollToContact" class="btn btn-outline btn-large">Need Help? Contact Us <i class="fas fa-headset"></i></button>
        </div>
      </div>
    </section>

    <!-- Outlets Modal -->
    <div class="modal-overlay" v-if="showOutletsModal" @click.self="showOutletsModal = false">
      <OutletsModal @close="showOutletsModal = false" />
    </div>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="container">
        <div class="section-header-with-image">
          <div class="section-header-content">
            <span class="section-badge"><i class="fas fa-comment-dots"></i> Testimonials</span>
            <h2 class="section-title">What Our Customers Say</h2>
            <p class="section-subtitle">Trusted by millions across Kenya</p>
          </div>
          <div class="section-header-image">
            <img src="/images/testimonials-header.jpeg" alt="Customer Testimonials" @error="setImagePlaceholder">
          </div>
        </div>
        
        <div class="testimonials-grid">
          <div class="testimonial-card glass-card" v-for="testimonial in testimonials" :key="testimonial.id">
            <div class="quote-mark"><i class="fas fa-quote-left"></i></div>
            <p class="testimonial-text">{{ testimonial.content }}</p>
            <div class="testimonial-author">
              <div class="author-info"><strong>{{ testimonial.name }}</strong><span>{{ testimonial.role }}</span></div>
              <div class="rating"><i v-for="i in testimonial.rating" :key="i" class="fas fa-star"></i></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Blog Section -->
    <section id="blog" class="blog-section">
      <div class="container">
        <div class="section-header-with-image">
          <div class="section-header-content">
            <span class="section-badge"><i class="fas fa-newspaper"></i> Our Blog</span>
            <h2 class="section-title">Stories & Updates</h2>
            <p class="section-subtitle">Insights from the heart of Kenya's dairy industry</p>
          </div>
          <div class="section-header-image">
            <img src="/images/blog-header.jpeg" alt="Our Blog" @error="setImagePlaceholder">
          </div>
        </div>
        
        <div v-if="blogsLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading blog posts...</p>
        </div>
        
        <div v-else class="blog-grid">
          <div class="blog-card-wrapper" v-for="post in displayedBlogs" :key="post.id">
            <div class="blog-card">
              <div class="blog-image" @click="openBlogModal(post.slug)">
                <img v-if="post.featured_image" :src="post.featured_image" :alt="post.title" @error="handleBlogImageError">
                <div v-else class="image-placeholder"><i class="fas fa-newspaper"></i></div>
                <div class="blog-overlay">
                  <button class="read-btn"><i class="fas fa-eye"></i> Read More</button>
                </div>
              </div>
              <div class="blog-info">
                <div class="blog-meta">
                  <span><i class="fas fa-calendar-alt"></i> {{ formatDate(post.created_at) }}</span>
                </div>
                <h3>{{ truncate(post.title, 50) }}</h3>
                <p class="blog-excerpt">{{ truncate(post.excerpt || post.content, 100) }}</p>
                <button @click="openBlogModal(post.slug)" class="blog-read-btn">
                  Read More <i class="fas fa-arrow-right"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="!blogsLoading && displayedBlogs.length === 0" class="no-blogs">
          <div class="no-blogs-icon"><i class="fas fa-newspaper"></i></div>
          <h3>No Blog Posts Yet</h3>
          <p>Check back soon for updates and stories!</p>
        </div>
        
        <div v-if="hasMoreBlogs && !blogsLoading" class="load-more-container">
          <button @click="loadMoreBlogs" class="btn-load-more" :disabled="blogsLoadingMore">
            <i v-if="blogsLoadingMore" class="fas fa-spinner fa-spin"></i>
            <span v-else><i class="fas fa-arrow-down"></i> Load More Posts</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Blog Modal -->
    <div v-if="showBlogModal && selectedBlog" class="modal-overlay" @click.self="closeBlogModal">
      <div class="modal-container modal-blog-large">
        <button class="modal-close" @click="closeBlogModal">
          <i class="fas fa-times"></i>
        </button>

        <div class="modal-blog-content-large">
          <div class="modal-blog-image-large">
            <img 
              :src="selectedBlog.featured_image || '/images/blog-placeholder.jpg'" 
              :alt="selectedBlog.title"
              @error="handleBlogImageError"
            />
          </div>

          <div class="modal-blog-body-large">
            <div class="modal-blog-header-large">
              <div class="blog-meta-modal">
                <span><i class="fas fa-calendar-alt"></i> {{ formatDate(selectedBlog.created_at) }}</span>
                <span><i class="fas fa-user"></i> {{ selectedBlog.author || 'Admin' }}</span>
                <span v-if="selectedBlog.views"><i class="fas fa-eye"></i> {{ selectedBlog.views }} views</span>
              </div>
              <h2>{{ selectedBlog.title }}</h2>
            </div>

            <div class="modal-blog-text-large">
              <div v-if="selectedBlog.excerpt" class="blog-excerpt-modal">
                <p>{{ selectedBlog.excerpt }}</p>
              </div>
              <div class="blog-full-content-large" v-html="selectedBlog.content"></div>
            </div>

            <div class="modal-actions-large">
              <button class="btn btn-primary" @click="closeBlogModal">
                Close
              </button>
              <button class="btn btn-outline" @click="shareBlog">
                <i class="fas fa-share-alt"></i> Share
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Section -->
    <section id="contact" class="contact-section">
      <div class="container">
        <div class="contact-grid">
          <div class="contact-info-wrapper">
            <div class="section-header-left">
              <span class="section-badge">Get in Touch</span>
              <h2>Contact Us</h2>
              <p>We'd love to hear from you</p>
            </div>
            
            <div class="info-cards">
              <div class="info-card glass-card">
                <div class="info-icon">📍</div>
                <div class="info-content"><h3>Address</h3><p>Meru Town, Kenya</p></div>
              </div>
              <div class="info-card glass-card">
                <div class="info-icon">📞</div>
                <div class="info-content">
                  <h3>Phone</h3>
                  <p><a href="tel:+254710901376">+254 710 901 376</a><br><a href="tel:+254719111444">+254 719 111 444</a></p>
                </div>
              </div>
              <div class="info-card glass-card">
                <div class="info-icon">✉️</div>
                <div class="info-content">
                  <h3>Email</h3>
                  <p><a href="mailto:maziwa@merudairy.co.ke">maziwa@merudairy.co.ke</a><br><a href="mailto:sales@merudairy.co.ke">sales@merudairy.co.ke</a></p>
                </div>
              </div>
              <div class="info-card glass-card">
                <div class="info-icon">🕒</div>
                <div class="info-content"><h3>Working Hours</h3><p>Mon-Fri: 8AM - 5PM<br>Sat: 9AM - 1PM</p></div>
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
          
          <div class="contact-form-wrapper">
            <div class="form-card glass-card">
              <div class="form-header">
                <div class="form-icon">📨</div>
                <h3>Send us a Message</h3>
                <p>We'll get back to you within 24 hours</p>
              </div>
              
              <div v-if="successMessage" class="alert-success"><i class="fas fa-check-circle"></i> {{ successMessage }}</div>
              <div v-if="errorMessage" class="alert-error"><i class="fas fa-exclamation-circle"></i> {{ errorMessage }}</div>
              
              <form @submit.prevent="submitContactForm" class="contact-form">
                <div class="form-group">
                  <div class="input-wrapper"><i class="fas fa-user input-icon"></i><input type="text" v-model="contactForm.name" placeholder="Your Name" required></div>
                </div>
                <div class="form-group">
                  <div class="input-wrapper"><i class="fas fa-envelope input-icon"></i><input type="email" v-model="contactForm.email" placeholder="Your Email" required></div>
                </div>
                <div class="form-group">
                  <div class="input-wrapper"><i class="fas fa-tag input-icon"></i><input type="text" v-model="contactForm.subject" placeholder="Subject" required></div>
                </div>
                <div class="form-group">
                  <div class="input-wrapper"><i class="fas fa-comment input-icon"></i><textarea v-model="contactForm.message" placeholder="Your Message" rows="5" required></textarea></div>
                </div>
                <button type="submit" class="btn-submit" :disabled="isSubmitting">
                  <span v-if="!isSubmitting">Send Message <i class="fas fa-paper-plane"></i></span>
                  <span v-else><i class="fas fa-spinner fa-spin"></i> Sending...</span>
                </button>
              </form>
              
              <div class="form-note"><i class="fas fa-lock"></i><p>Your information is safe with us. We never share your data.</p></div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <div class="modal-icon success"><i class="fas fa-check-circle"></i></div>
          <h3>Message Sent!</h3>
          <p>Thank you for contacting us. We'll get back to you soon.</p>
          <button @click="showModal = false" class="btn-close">Close</button>
        </div>
      </div>
    </section>

    <!-- Tour Booking Modal -->
    <TourBookingModal 
      :is-open="showBookingModal"
      @close="closeBookingModal"
    />

    <!-- Floating Book a Tour Button -->
    <button 
      class="book-tour-float" 
      @click="openBookingModal"
      aria-label="Book a Factory Tour"
    >
      <i class="fas fa-factory"></i>
      <span>Book a Tour</span>
    </button>
  </main>
</template>




<script>
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, Pagination, Navigation, EffectFade } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/autoplay'
import 'swiper/css/pagination'
import 'swiper/css/navigation'
import 'swiper/css/effect-fade'

import axios from 'axios'
import { scrollToSection } from '@/utils/scroll'
import ScrollProgress from '@/components/ScrollProgress.vue'
import BackToTop from '@/components/BackToTop.vue'
import OutletsModal from '@/components/modals/OutletsModal.vue'
import TourBookingModal from '@/components/TourBookingModal.vue'

export default {
  name: 'Home',
  components: {
    ScrollProgress,
    BackToTop,
    OutletsModal,
    Swiper,
    SwiperSlide,
    TourBookingModal
  },
  
  data() {
    return {
      modules: [Autoplay, Pagination, Navigation, EffectFade],
      
      slides: [
        {
          id: 1,
          image: '/images/hero/fresh-milk-hero.jpg',
          badge: "Kenya's Biggest Dairy Co-operative",
          title: 'Pure <span class="highlight">Mount Kenya</span><br>Milk Delivered Fresh',
          description: 'From our farms to your table, experience the richness of nature with Mount Kenya Milk products.'
        },
        {
          id: 2,
          image: '/images/hero/yoghurt-hero.jpg',
          badge: 'Creamy & Delicious',
          title: 'Premium <span class="highlight">Yoghurt</span><br>Made Fresh Daily',
          description: 'Delicious, probiotic-rich yoghurt made from the finest Mount Kenya milk.'
        },
        {
          id: 3,
          image: '/images/hero/farmers-hero.jpg',
          badge: 'Empowering Farmers',
          title: 'Supporting <span class="highlight">120,000+</span><br>Local Farmers',
          description: 'Building a sustainable future for Kenyan dairy farmers and their communities.'
        },
        {
          id: 4,
          image: '/images/hero/tour-hero.jpg',
          badge: 'Experience Dairy Magic',
          title: 'Book a <span class="highlight">Factory Tour</span><br>Today!',
          description: 'Come behind the scenes and see how we transform fresh milk into Kenya\'s favorite dairy products.'
        }
      ],
      
      // Products
      allProducts: [],
      displayedProducts: [],
      productsPage: 1,
      productsPerPage: 6,
      hasMoreProducts: true,
      totalProducts: 0,
      productsLoading: true,
      productsLoadingMore: false,
      isFetchingProducts: false,
      
      // Product Modal
      showProductModal: false,
      selectedProduct: null,
      productModalLoading: false,

      // Blog
      allBlogs: [],
      displayedBlogs: [],
      blogsPage: 1,
      blogsPerPage: 6,
      hasMoreBlogs: true,
      totalBlogs: 0,
      blogsLoading: true,
      blogsLoadingMore: false,
      isFetchingBlogs: false,

      // Blog Modal
      showBlogModal: false,
      selectedBlog: null,
      blogModalLoading: false,

      // Tour
      showBookingModal: false,
      tourPackages: [],
      featuredTourPackage: null,
      isFetchingTourPackages: false,

      // Contact
      contactForm: {
        name: '',
        email: '',
        subject: '',
        message: ''
      },
      isSubmitting: false,
      successMessage: '',
      errorMessage: '',
      showModal: false,
      showOutletsModal: false,
      navbarHeight: 80,
      
      features: [
        { icon: 'fas fa-tint', title: '100% Pure & Fresh', description: 'Pasteurized and packed fresh daily from the slopes of Mount Kenya' },
        { icon: 'fas fa-hand-holding-heart', title: 'Farmer Owned', description: 'Supporting over 120,000 local farmers through fair trade practices' },
        { icon: 'fas fa-microscope', title: 'Quality Assured', description: 'Rigorous quality testing at every stage of production' },
        { icon: 'fas fa-truck-fast', title: 'Nationwide Delivery', description: 'Reaching millions of customers across Kenya every day' }
      ],
      
      statistics: [
        { value: '120', suffix: 'K+', label: 'Active Farmers' },
        { value: '250', suffix: 'K+', label: 'Liters Daily' },
        { value: '50', suffix: '+', label: 'Years Serving Kenya' }
      ],
      
      testimonials: [
        { id: 1, name: 'Grace Kawira', role: 'Nairobi Resident', content: "Mount Kenya Milk is the absolute best for my family tea. Rich and always fresh.", rating: 5 },
        { id: 2, name: 'John Mwangi', role: 'Hotelier', content: "The yogurt consistency is incredible. My customers won't take anything else.", rating: 5 }
      ]
    }
  },
  
  mounted() {
    this.updateNavbarHeight()
    this.fetchProducts()
    this.fetchBlogs()
    this.fetchTourPackages()
    this.setupAOS()
    
    window.addEventListener('resize', this.updateNavbarHeight, { passive: true })
  },
  
  beforeUnmount() {
    window.removeEventListener('resize', this.updateNavbarHeight)
    
    // Destroy Swiper instance if it exists
    if (this.$refs.swiper && this.$refs.swiper.swiper) {
      this.$refs.swiper.swiper.destroy(true, true)
    }
  },
  
  methods: {
    // ==================== NAVBAR ====================
    updateNavbarHeight() {
      if (window.requestAnimationFrame) {
        window.requestAnimationFrame(() => {
          const navbarSelectors = [
            '.navbar',
            'nav',
            '.header',
            '.main-header',
            '.site-header'
          ]
          
          let navbar = null
          for (const selector of navbarSelectors) {
            navbar = document.querySelector(selector)
            if (navbar) break
          }
          
          if (navbar) {
            this.navbarHeight = navbar.offsetHeight || 80
          } else {
            this.navbarHeight = 80
          }
        })
      } else {
        const navbar = document.querySelector('.navbar') || document.querySelector('nav')
        this.navbarHeight = navbar ? navbar.offsetHeight : 80
      }
    },
    
    // ==================== PRODUCTS ====================
    async fetchProducts(reset = true) {
      if (this.isFetchingProducts) return
      
      try {
        if (reset) {
          this.productsLoading = true
          this.productsPage = 1
          this.hasMoreProducts = true
          this.displayedProducts = []
        } else {
          this.productsLoadingMore = true
        }
        
        this.isFetchingProducts = true
        
        const response = await axios.get(`/api/products?page=${this.productsPage}&per_page=${this.productsPerPage}`)
        
        if (response.data && response.data.data) {
          const newProducts = response.data.data
          this.displayedProducts = reset ? newProducts : [...this.displayedProducts, ...newProducts]
          this.totalProducts = response.data.pagination?.total_items || 0
          this.hasMoreProducts = response.data.pagination?.has_next || false
          this.allProducts = reset ? newProducts : [...this.allProducts, ...newProducts]
        }
      } catch (error) {
        console.error('Error fetching products:', error)
      } finally {
        this.productsLoading = false
        this.productsLoadingMore = false
        this.isFetchingProducts = false
      }
    },
    
    loadMoreProducts() {
      if (this.hasMoreProducts && !this.productsLoadingMore && !this.isFetchingProducts) {
        this.productsPage++
        this.fetchProducts(false)
      }
    },
    
    openProductModal(id) {
      this.selectedProduct = this.displayedProducts.find(p => p.id === id) || null
      if (this.selectedProduct) {
        this.showProductModal = true
        document.body.style.overflow = 'hidden'
      }
    },
    
    closeProductModal() {
      this.showProductModal = false
      this.selectedProduct = null
      document.body.style.overflow = 'auto'
    },
    
    // ==================== BLOGS ====================
    async fetchBlogs(reset = true) {
      if (this.isFetchingBlogs) return
      
      try {
        if (reset) {
          this.blogsLoading = true
          this.blogsPage = 1
          this.hasMoreBlogs = true
          this.displayedBlogs = []
        } else {
          this.blogsLoadingMore = true
        }
        
        this.isFetchingBlogs = true
        
        const response = await axios.get(`/api/blog?page=${this.blogsPage}&per_page=${this.blogsPerPage}`)
        
        if (response.data && response.data.data) {
          const newBlogs = response.data.data
          this.displayedBlogs = reset ? newBlogs : [...this.displayedBlogs, ...newBlogs]
          this.totalBlogs = response.data.pagination?.total_items || 0
          this.hasMoreBlogs = response.data.pagination?.has_next || false
        }
      } catch (error) {
        console.error('Error fetching blogs:', error)
      } finally {
        this.blogsLoading = false
        this.blogsLoadingMore = false
        this.isFetchingBlogs = false
      }
    },
    
    loadMoreBlogs() {
      if (this.hasMoreBlogs && !this.blogsLoadingMore && !this.isFetchingBlogs) {
        this.blogsPage++
        this.fetchBlogs(false)
      }
    },
    
    openBlogModal(slug) {
      this.selectedBlog = this.displayedBlogs.find(b => b.slug === slug) || null
      if (this.selectedBlog) {
        this.showBlogModal = true
        document.body.style.overflow = 'hidden'
      }
    },
    
    closeBlogModal() {
      this.showBlogModal = false
      this.selectedBlog = null
      document.body.style.overflow = 'auto'
    },
    
    shareBlog() {
      if (this.selectedBlog) {
        const url = `${window.location.origin}/blog/${this.selectedBlog.slug}`
        if (navigator.share) {
          navigator.share({
            title: this.selectedBlog.title,
            text: this.selectedBlog.excerpt || this.selectedBlog.title,
            url: url
          }).catch(() => {})
        } else {
          navigator.clipboard.writeText(url).then(() => {
            alert('Blog link copied to clipboard!')
          }).catch(() => {})
        }
      }
    },
    
    // ==================== TOUR ====================
    async fetchTourPackages() {
      if (this.isFetchingTourPackages) return
      
      this.isFetchingTourPackages = true
      try {
        const response = await axios.get('/api/tour/packages')
        this.tourPackages = response.data.packages || []
        if (this.tourPackages.length > 0) {
          this.featuredTourPackage = this.tourPackages[0]
        }
      } catch (error) {
        console.error('Error fetching tour packages:', error)
      } finally {
        this.isFetchingTourPackages = false
      }
    },
    
    openBookingModal() {
      this.showBookingModal = true
      document.body.style.overflow = 'hidden'
    },
    
    closeBookingModal() {
      this.showBookingModal = false
      document.body.style.overflow = 'auto'
    },
    
    // ==================== CONTACT ====================
    async submitContactForm() {
      this.isSubmitting = true
      this.errorMessage = ''
      
      try {
        const response = await axios.post('/api/contact', this.contactForm)
        if (response.status === 201 || response.status === 200) {
          this.successMessage = 'Thank you for your message! We will get back to you within 24 hours.'
          this.contactForm = { name: '', email: '', subject: '', message: '' }
          this.showModal = true
          setTimeout(() => {
            this.showModal = false
            this.successMessage = ''
          }, 5000)
        }
      } catch (error) {
        console.error('Error sending message:', error)
        this.errorMessage = error.response?.data?.error || 'Failed to send message. Please try again later.'
        setTimeout(() => {
          this.errorMessage = ''
        }, 5000)
      } finally {
        this.isSubmitting = false
      }
    },
    
    // ==================== NAVIGATION ====================
    scrollToProducts() {
      scrollToSection('products')
    },
    
    scrollToAbout() {
      scrollToSection('about')
    },
    
    scrollToContact() {
      this.closeProductModal()
      this.closeBlogModal()
      scrollToSection('contact')
    },
    
    // ==================== UTILITIES ====================
    truncate(text, length) {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    },
    
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-KE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    
    handleImageError(event) {
      event.target.src = '/images/placeholder.png'
    },
    
    handleBlogImageError(event) {
      event.target.src = '/images/blog-placeholder.jpg'
    },
    
    setImagePlaceholder(event) {
      event.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100%" height="100%" fill="%23eeeeee"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="10" fill="%23999999">Image Missing</text></svg>'
    },
    
    setupAOS() {
      if (window.AOS) {
        window.AOS.init({
          duration: 800,
          once: true
        })
      }
    }
  }
}
</script>


<style scoped>
/* ========================================
   GLOBAL & CONTAINER
   ======================================== */
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ========================================
   BUTTONS
   ======================================== */
.btn {
  border: none;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-large {
  padding: 14px 32px;
  font-size: 1rem;
}

.btn-primary {
  background: #f59e0b;
  color: white;
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
}

.btn-outline-light:hover {
  background: white;
  color: #1e3a8a;
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: #1e3a8a;
  border: 2px solid #1e3a8a;
  border-radius: 50px;
  padding: 10px 20px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: #1e3a8a;
  color: white;
}

.btn-icon {
  transition: transform 0.3s;
}

.btn-large:hover .btn-icon {
  transform: translateX(5px);
}

.btn-load-more {
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  border: none;
  color: white;
  padding: 12px 28px;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.btn-load-more:hover:not(:disabled) {
  background: #1e3a8a;
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outlets {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 50px;
  font-size: 1rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.btn-outlets:hover {
  background: #f59e0b;
  transform: translateY(-2px);
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

.btn-close {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 10px 30px;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-close:hover {
  background: #d97706;
  transform: translateY(-2px);
}

/* SECTION HEADERS*/
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

/* HERO SECTION */
.hero-section {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}


.hero-swiper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.slide-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
}

.slide-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slide-content {
  position: relative;
  z-index: 2;
  height: 100vh;
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.4);
  margin-top: 0px;
}

.hero-text {
  max-width: 700px;
  color: white;
  padding-bottom: 30px; /* Extra space before stats */
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

/* Hero Stats Container - Better spacing */
.hero-stats-container {
  position: absolute;
  bottom: 5%; 
  left: 0;
  right: 0;
  z-index: 3;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #1e3a8a;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.scroll-indicator {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  color: white;
  z-index: 3;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.scroll-indicator span {
  display: block;
  font-size: 0.8rem;
  margin-bottom: 10px;
  opacity: 0.8;
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

/* Swiper Custom Styles */
:deep(.swiper-button-next),
:deep(.swiper-button-prev) {
  color: white;
  background: rgba(0,0,0,0.3);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  transition: all 0.3s;
}

:deep(.swiper-button-next:hover),
:deep(.swiper-button-prev:hover) {
  background: rgba(245,158,11,0.8);
}

:deep(.swiper-pagination-bullet) {
  background: white;
  opacity: 0.6;
}

:deep(.swiper-pagination-bullet-active) {
  background: #f59e0b;
  opacity: 1;
}

.tour-card {
  border: 2px solid #f59e0b;
  background: linear-gradient(135deg, #fef3c7, #fffbeb);
  transition: all 0.3s;
}

.tour-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.2);
}

.tour-link {
  color: #d97706 !important;
}

.tour-link:hover {
  color: #b45309 !important;
}

.book-tour-float:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.5);
  background: #d97706;
}

.book-tour-float span {
  display: inline-block;
}

@media (max-width: 768px) {

  
  .book-tour-float span {
    display: none;
  }
  
  .book-tour-float i {
    font-size: 1.2rem;
  }
}

/* ========================================
   RESPONSIVE - HERO SPACING
   ======================================== */
@media (max-width: 968px) {
  .hero-title {
    font-size: 2.5rem;
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
  
  .hero-stats {
    grid-template-columns: 1fr 1fr;
    padding: 20px;
    gap: 15px;
  }
  

  .hero-text {
    padding-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.5rem;
  }
  
  .hero-badge {
    font-size: 0.7rem;
  }
  

  .hero-stats {
    grid-template-columns: 1fr;
    padding: 15px;
    gap: 10px;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
}

/*   Tour Card in Shop Section */
.tour-card {
  border: 2px solid #f59e0b;
  background: linear-gradient(135deg, #fef3c7, #fffbeb);
  transition: all 0.3s;
}

/*  Tour Button in Hero */
.btn-tour {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  
}

.btn-tour:hover {
  background: linear-gradient(135deg, #d97706, #b45309);
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3);
}

.btn-tour i {
  font-size: 1.1rem;
}

.book-tour-float {
  position: fixed;
  bottom: 80px;
  right: 30px;
  background: #f59e0b;
  color: white;
  border: none;
  padding: 14px 22px;
  border-radius: 50px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  font-family: inherit;
}

/* ========================================
   GLASS CARD EFFECT
   ======================================== */
.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

/* ========================================
   ABOUT SECTION
   ======================================== */
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

/* ========================================
   FEATURES SECTION
   ======================================== */
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

/* ========================================
   PRODUCTS SECTION
   ======================================== */
.products-section {
  padding: 80px 0;
  background: white;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.12);
}

.product-image {
  height: 220px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  flex-shrink: 0;
  background: #f8fafc;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.product-card:hover .product-image img {
  transform: scale(1.08);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  gap: 8px;
  font-size: 2rem;
  color: #1e3a8a;
}

.image-placeholder span {
  font-size: 0.8rem;
  font-weight: 500;
}

.product-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(30, 58, 138, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-image:hover .product-overlay {
  opacity: 1;
}

.view-details-btn {
  background: white;
  color: #1e3a8a;
  border: none;
  padding: 10px 20px;
  border-radius: 30px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-details-btn:hover {
  background: #f59e0b;
  color: white;
}

.product-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #f59e0b;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  z-index: 2;
}

.product-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-info h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a8a;
  margin-bottom: 8px;
  line-height: 1.4;
}

.product-description {
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 0.7rem;
  color: #f59e0b;
}

.product-details-btn {
  background: none;
  border: none;
  color: #f59e0b;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  margin-top: auto;
  transition: all 0.3s;
  width: fit-content;
}

.product-details-btn:hover {
  gap: 10px;
  color: #d97706;
}

/* ========================================
   PRODUCT MODAL
   ======================================== */
.product-modal {
  max-width: 1000px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
}

.product-modal-content {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 30px;
}

.product-modal-image {
  border-radius: 16px;
  overflow: hidden;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  max-height: 400px;
  padding: 20px;
}

.product-modal-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f8fafc;
}

.image-placeholder-large {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  font-size: 4rem;
  color: #1e3a8a;
  border-radius: 16px;
}

.product-modal-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 10px;
}

.product-modal-info::-webkit-scrollbar {
  width: 6px;
}

.product-modal-info::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.product-modal-info::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.product-category-badge {
  display: inline-block;
  background: #e0e7ff;
  color: #1e3a8a;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  width: fit-content;
}

.product-modal-info h2 {
  font-size: 1.5rem;
  color: #1e3a8a;
  margin: 0;
  line-height: 1.3;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

.info-section {
  margin-bottom: 8px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.3s;
}

.info-section:hover {
  background: #f0f4ff;
  transform: translateX(5px);
}

.info-section h4 {
  color: #1e3a8a;
  margin: 0 0 10px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-section h4 i {
  color: #f59e0b;
}

.info-section p {
  color: #4b5563;
  line-height: 1.6;
  font-size: 0.85rem;
  margin: 0;
}

.packaging-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.size-badge {
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  color: #1e3a8a;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 0.3s;
}

.size-badge:hover {
  background: #1e3a8a;
  color: white;
  transform: translateY(-2px);
}

.modal-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid #e5e7eb;
  display: flex;
  gap: 15px;
  justify-content: flex-start;
}

/* ========================================
   SHOP SECTION
   ======================================== */
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

.physical-shops-section {
  text-align: center;
  margin: 2rem 0;
  padding: 2rem;
  background: #f8fafc;
  border-radius: 16px;
}

.shop-cta {
  text-align: center;
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

/* ========================================
   TESTIMONIALS SECTION
   ======================================== */
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

/* ========================================
   BLOG SECTION
   ======================================== */
.blog-section {
  padding: 80px 0;
  background: #f8fafc;
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.blog-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s;
}

.blog-card:hover {
  transform: translateY(-4px);
}

.blog-image {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #f1f5f9;
  cursor: pointer;
  flex-shrink: 0;
}

.blog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}

.blog-card:hover .blog-image img {
  transform: scale(1.05);
}

.blog-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.blog-image:hover .blog-overlay {
  opacity: 1;
}

.read-btn {
  background: white;
  color: #1e3a8a;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.read-btn:hover {
  background: #f59e0b;
  color: white;
}

.blog-info {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.blog-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.blog-meta i {
  margin-right: 0.25rem;
}

.blog-info h3 {
  font-size: 1.05rem;
  color: #1e3a8a;
  margin: 0 0 0.5rem;
  line-height: 1.3;
}

.blog-excerpt {
  font-size: 0.9rem;
  color: #4b5563;
  line-height: 1.5;
  flex: 1;
  margin: 0 0 1rem;
}

.blog-read-btn {
  background: none;
  border: none;
  color: #f59e0b;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  width: fit-content;
}

.blog-read-btn:hover {
  color: #d97706;
  gap: 0.75rem;
}

/* ========================================
   BLOG MODAL 
   ======================================== */
.modal-blog-large {
  max-width: 1100px;
  width: 95%;
  max-height: 95%;
  padding: 0;
  overflow: hidden;
  border-radius: 20px;
}

.modal-blog-content-large {
  display: flex;
  flex-direction: column;
  max-height: 92vh;
  overflow: hidden;
}

.modal-blog-image-large {
  width: 100%;
  height: 350px;
  background: #f1f5f9;
  overflow: hidden;
  flex-shrink: 0;
}

.modal-blog-image-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-blog-body-large {
  flex: 1;
  padding: 2.5rem;
  overflow-y: auto;
  max-height: calc(92vh - 350px);
  background: white;
}

.modal-blog-body-large::-webkit-scrollbar {
  width: 8px;
}

.modal-blog-body-large::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.modal-blog-body-large::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.modal-blog-body-large::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.modal-blog-header-large {
  margin-bottom: 1.5rem;
}

.blog-meta-modal {
  display: flex;
  gap: 1.5rem;
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.blog-meta-modal i {
  margin-right: 0.35rem;
}

.modal-blog-header-large h2 {
  font-size: 2rem;
  color: #1e3a8a;
  margin: 0;
  line-height: 1.3;
}

.modal-blog-text-large {
  color: #4b5563;
  line-height: 1.8;
  font-size: 1rem;
}

.blog-excerpt-modal {
  background: #f1f5f9;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #f59e0b;
  font-style: italic;
}

.blog-excerpt-modal p {
  margin: 0;
}

.blog-full-content-large {
  font-size: 1rem;
}

.blog-full-content-large p {
  margin-bottom: 1rem;
}

.blog-full-content-large h1,
.blog-full-content-large h2,
.blog-full-content-large h3,
.blog-full-content-large h4 {
  color: #1e3a8a;
  margin: 1.5rem 0 0.5rem;
}

.blog-full-content-large ul,
.blog-full-content-large ol {
  padding-left: 1.5rem;
  margin: 0.5rem 0 1rem;
}

.blog-full-content-large li {
  margin-bottom: 0.25rem;
}

.blog-full-content-large blockquote {
  border-left: 4px solid #f59e0b;
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: #f8fafc;
  font-style: italic;
}

.blog-full-content-large img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1rem 0;
}

.modal-actions-large {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e5e7eb;
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
  flex-wrap: wrap;
}

.modal-actions-large .btn {
  padding: 0.6rem 1.5rem;
}

/* ========================================
   CONTACT SECTION
   ======================================== */
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

.form-note {
  margin-top: 20px;
  text-align: center;
  font-size: 0.75rem;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* ========================================
   MODAL OVERLAY
   ======================================== */
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
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.modal-container {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  position: relative;
  max-height: 100%;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(0,0,0,0.1);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #ef4444;
  color: white;
  transform: scale(1.1);
}

.modal-loading {
  text-align: center;
  padding: 60px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.modal-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.modal-icon.success {
  background: #d1fae5;
}

.modal-icon.success i {
  font-size: 2.5rem;
  color: #10b981;
}

.modal-content h3 {
  color: #1e3a8a;
  margin-bottom: 10px;
  font-size: 1.3rem;
}

.modal-content p {
  color: #6b7280;
  margin-bottom: 25px;
}

/* ========================================
   LOADING STATES
   ======================================== */
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

/* ========================================
   EMPTY STATES
   ======================================== */
.no-products,
.no-blogs {
  text-align: center;
  padding: 60px;
  background: #f8fafc;
  border-radius: 20px;
}

.no-products-icon,
.no-blogs-icon {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 16px;
}

.no-products h3,
.no-blogs h3 {
  color: #1e3a8a;
  margin-bottom: 8px;
}

/* ========================================
   ALERTS
   ======================================== */
.alert-success {
  background: #d1fae5;
  color: #065f46;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}

/* ========================================
   LOAD MORE & COUNTS
   ======================================== */
.load-more-container {
  text-align: center;
  margin: 40px 0 20px;
}

.product-count {
  text-align: center;
  font-size: 0.8rem;
  color: #9ca3af;
  margin-top: 20px;
}

/* ========================================
   ANIMATIONS
   ======================================== */
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
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

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 968px) {
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
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .product-modal-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .product-modal-image {
    max-height: 250px;
  }
  
  .product-modal-info {
    max-height: 60vh;
  }
  
  .modal-blog-image-large {
    height: 250px;
  }
  
  .modal-blog-body-large {
    padding: 1.5rem;
    max-height: calc(92vh - 250px);
  }
  
  .modal-blog-header-large h2 {
    font-size: 1.6rem;
  }
}

@media (max-width: 768px) {
  
  .hero-buttons,
  .shop-cta {
    flex-direction: column;
    align-items: center;
  }
  
  .features-grid,
  .testimonials-grid,
  .shop-grid,
  .products-grid,
  .blog-grid {
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
  
  .product-image,
  .blog-image {
    height: 180px;
  }
  
  .modal-blog-image-large {
    height: 200px;
  }
  
  .modal-blog-body-large {
    padding: 1.25rem;
    max-height: calc(92vh - 200px);
  }
  
  .modal-blog-header-large h2 {
    font-size: 1.3rem;
  }
  
  .blog-meta-modal {
    flex-wrap: wrap;
    gap: 0.75rem;
    font-size: 0.75rem;
  }
  
  :deep(.swiper-button-next),
  :deep(.swiper-button-prev) {
    width: 36px;
    height: 36px;
  }
  

  
  /*   Floating button mobile */
  .book-tour-float {
    padding: 12px 18px;
    font-size: 13px;
    /* bottom: 20px; */
    right: 20px;
  }
  
  .book-tour-float span {
    display: none; /* Hide text on mobile, show only icon */
  }
}

@media (max-width: 480px) {
  .about-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .social-links-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .hero-title {
    font-size: 1.5rem;
  }
  
  .product-image,
  .blog-image {
    height: 160px;
  }
  
  .modal-blog-image-large {
    height: 160px;
  }
  
  .modal-blog-body-large {
    padding: 1rem;
    max-height: calc(92vh - 160px);
  }
  
  .modal-blog-header-large h2 {
    font-size: 1.1rem;
  }
  
  .modal-blog-text-large {
    font-size: 0.9rem;
  }
  
  .modal-actions-large {
    flex-direction: column;
  }
  
  .modal-actions-large .btn {
    width: 100%;
    justify-content: center;
  }
}





</style>




