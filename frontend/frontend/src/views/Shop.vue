<template>
  <main>
    <section class="shop-page">
      <div class="container">
        <h1 class="section-title">Shop Online</h1>
        <div class="shop-content">
          <p class="shop-intro">Our online shop is available now. In the meantime, you can visit our physical stores or contact us for bulk orders.</p>
          
          <div class="shop-info">
            <h3>Contact our sales team:</h3>
            <p>Phone: +254 719 111 444</p>
            <p>Email: sales@merudairy.co.ke</p>
          </div>
          <a href="https://shop.mountkenyamilk.co.ke/" target="_blank" class="btn btn-primary">Visit Our Online Shop</a>
          <br>
          <br>
          <router-link to="/products" class="btn btn-primary">Browse Our Products</router-link>
          <br>
          <br>
          <p class="shop-info">
            We are working hard to bring you the best online shopping experience. Stay tuned for updates and new features!  
          </p>
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