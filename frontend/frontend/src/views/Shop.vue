<template>
  <main>
    <section class="shop-page">
      <div class="container">
        <h1 class="section-title">Shop Online</h1>
        <div class="shop-content">
          <p class="shop-intro">Coming soon! Our online shop will be available shortly. In the meantime, please visit our physical stores or contact us for bulk orders.</p>
          
          <div class="shop-info">
            <h3>Contact our sales team:</h3>
            <p>Phone: +254 719 111 444</p>
            <p>Email: sales@merudairy.co.ke</p>
          </div>
          
          <router-link to="/products" class="btn btn-primary">Browse Our Products</router-link>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: 'Shop'
}
</script>

<style scoped>
.shop-page {
  padding: 4rem 0;
  min-height: 70vh;
}

.shop-content {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.shop-intro {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #555;
}

.shop-info {
  background: var(--gray-light);
  padding: 2rem;
  border-radius: 12px;
  margin: 2rem 0;
}
</style>