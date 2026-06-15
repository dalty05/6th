<template>
  <div class="partner-help">
    <div class="page-header">
      <div>
        <h1>Help Center</h1>
        <p>Everything you need to know about being a Meru Dairy Partner</p>
      </div>
    </div>

    <div class="help-grid">
      <!-- Getting Started Section -->
      <div class="help-section glass-card">
        <div class="section-icon">
          <i class="fas fa-rocket"></i>
        </div>
        <h2>Getting Started</h2>
        <div class="faq-list">
          <div class="faq-item" @click="toggleFaq('getting-started-1')">
            <div class="faq-question">
              <span>How do I create my first referral link?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['getting-started-1'] }"></i>
            </div>
            <div v-if="openFaqs['getting-started-1']" class="faq-answer">
              <p>Click on "Referral Links" in the sidebar, then click "Create New Link". Enter a name for your campaign, optionally add a destination URL, and click "Save". Your unique referral link will be generated instantly.</p>
            </div>
          </div>
          
          <div class="faq-item" @click="toggleFaq('getting-started-2')">
            <div class="faq-question">
              <span>Where can I find my referral code?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['getting-started-2'] }"></i>
            </div>
            <div v-if="openFaqs['getting-started-2']" class="faq-answer">
              <p>Your unique referral code is displayed on your Partner Dashboard. You can also find it in your Profile page under "Referral Code".</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tracking & Analytics Section -->
      <div class="help-section glass-card">
        <div class="section-icon">
          <i class="fas fa-chart-line"></i>
        </div>
        <h2>Tracking & Analytics</h2>
        <div class="faq-list">
          <div class="faq-item" @click="toggleFaq('tracking-1')">
            <div class="faq-question">
              <span>How are clicks tracked?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['tracking-1'] }"></i>
            </div>
            <div v-if="openFaqs['tracking-1']" class="faq-answer">
              <p>Every time someone clicks your unique referral link, we record the click along with information like IP address, referrer source, and timestamp. This helps you understand where your traffic is coming from.</p>
            </div>
          </div>
          
          <div class="faq-item" @click="toggleFaq('tracking-2')">
            <div class="faq-question">
              <span>What counts as a conversion?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['tracking-2'] }"></i>
            </div>
            <div v-if="openFaqs['tracking-2']" class="faq-answer">
              <p>A conversion occurs when a user who clicked your referral link completes a desired action, such as making a purchase or signing up for our newsletter. Conversion rates help you measure campaign effectiveness.</p>
            </div>
          </div>
          
          <div class="faq-item" @click="toggleFaq('tracking-3')">
            <div class="faq-question">
              <span>How often are statistics updated?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['tracking-3'] }"></i>
            </div>
            <div v-if="openFaqs['tracking-3']" class="faq-answer">
              <p>Statistics are updated in real-time. You can see your latest clicks and conversions immediately on your dashboard and analytics page.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Link Management Section -->
      <div class="help-section glass-card">
        <div class="section-icon">
          <i class="fas fa-link"></i>
        </div>
        <h2>Link Management</h2>
        <div class="faq-list">
          <div class="faq-item" @click="toggleFaq('links-1')">
            <div class="faq-question">
              <span>Can I edit my referral links after creation?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['links-1'] }"></i>
            </div>
            <div v-if="openFaqs['links-1']" class="faq-answer">
              <p>Yes, you can edit the name, destination URL, and campaign name of your referral links at any time. The link code itself remains unchanged so existing tracking continues to work.</p>
            </div>
          </div>
          
          <div class="faq-item" @click="toggleFaq('links-2')">
            <div class="faq-question">
              <span>Can I deactivate a referral link?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['links-2'] }"></i>
            </div>
            <div v-if="openFaqs['links-2']" class="faq-answer">
              <p>Yes, you can deactivate any referral link. Deactivated links will no longer redirect users, but historical click data is preserved for your records.</p>
            </div>
          </div>
          
          <div class="faq-item" @click="toggleFaq('links-3')">
            <div class="faq-question">
              <span>Is there a limit to how many links I can create?</span>
              <i class="fas fa-chevron-down" :class="{ rotated: openFaqs['links-3'] }"></i>
            </div>
            <div v-if="openFaqs['links-3']" class="faq-answer">
              <p>No, there is no limit! You can create as many referral links as you need for your marketing campaigns.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Best Practices Section -->
      <div class="help-section glass-card">
        <div class="section-icon">
          <i class="fas fa-lightbulb"></i>
        </div>
        <h2>Best Practices</h2>
        <div class="best-practices-list">
          <div class="practice-item">
            <i class="fas fa-tag"></i>
            <div>
              <strong>Use Descriptive Names</strong>
              <p>Name your links by campaign (e.g., "Summer Sale 2024") to easily track performance by initiative.</p>
            </div>
          </div>
          <div class="practice-item">
            <i class="fas fa-chart-simple"></i>
            <div>
              <strong>Monitor Your Analytics</strong>
              <p>Regularly check your analytics to see which campaigns are performing best and optimize accordingly.</p>
            </div>
          </div>
          <div class="practice-item">
            <i class="fas fa-bullhorn"></i>
            <div>
              <strong>Promote Strategically</strong>
              <p>Share your links on relevant platforms where your target audience spends time.</p>
            </div>
          </div>
          <div class="practice-item">
            <i class="fas fa-calendar"></i>
            <div>
              <strong>Set Expiry Dates</strong>
              <p>For time-limited campaigns, set expiry dates to automatically deactivate links after your promotion ends.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Support Section -->
    <div class="contact-support glass-card">
      <div class="support-content">
        <i class="fas fa-headset"></i>
        <div>
          <h3>Still have questions?</h3>
          <p>Our support team is here to help you succeed</p>
        </div>
        <button @click="contactSupport" class="btn btn-primary">
          Contact Support <i class="fas fa-arrow-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { toast } from 'vue3-toastify'

const openFaqs = reactive({
  'getting-started-1': false,
  'getting-started-2': false,
  'tracking-1': false,
  'tracking-2': false,
  'tracking-3': false,
  'links-1': false,
  'links-2': false,
  'links-3': false
})

const toggleFaq = (id) => {
  openFaqs[id] = !openFaqs[id]
}

const contactSupport = () => {
  toast.info('Support contact: partners@merudairy.co.ke')
}
</script>

<style scoped>
.partner-help {
  min-height: 100vh;
  background: var(--gray-50);
  padding: var(--spacing-6);
}

.page-header {
  margin-bottom: var(--spacing-6);
}

.page-header h1 {
  color: var(--primary-blue);
  margin: 0 0 var(--spacing-1) 0;
}

.page-header p {
  color: var(--gray-500);
  margin: 0;
}

.help-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-6);
}

.help-section {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
}

.section-icon {
  width: 48px;
  height: 48px;
  background: var(--primary-blue-lighter);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-4);
}

.section-icon i {
  font-size: var(--text-2xl);
  color: var(--accent-orange);
}

.help-section h2 {
  color: var(--primary-blue);
  font-size: var(--text-xl);
  margin-bottom: var(--spacing-4);
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.faq-item {
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--gray-50);
  font-weight: var(--font-medium);
}

.faq-question i {
  transition: transform var(--transition-base);
  color: var(--gray-400);
}

.faq-question i.rotated {
  transform: rotate(180deg);
}

.faq-answer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--gray-200);
  color: var(--gray-600);
  line-height: 1.6;
}

.faq-answer p {
  margin: 0;
}

.best-practices-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.practice-item {
  display: flex;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background: var(--gray-50);
  border-radius: var(--radius-lg);
}

.practice-item i {
  font-size: var(--text-xl);
  color: var(--accent-orange);
  margin-top: var(--spacing-1);
}

.practice-item strong {
  display: block;
  color: var(--primary-blue);
  margin-bottom: var(--spacing-1);
}

.practice-item p {
  margin: 0;
  color: var(--gray-600);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.contact-support {
  background: linear-gradient(135deg, var(--primary-blue), var(--gray-800));
  color: white;
  padding: var(--spacing-6);
  border-radius: var(--radius-xl);
}

.support-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--spacing-4);
}

.support-content i {
  font-size: var(--text-4xl);
}

.support-content h3 {
  margin: 0 0 var(--spacing-1) 0;
}

.support-content p {
  margin: 0;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .partner-help {
    padding: var(--spacing-4);
  }
  
  .help-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .support-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>