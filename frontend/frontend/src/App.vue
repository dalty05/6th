<template>
<div id="app">
    <Navbar v-if="!isAdminRoute" />
    
    <router-view />
    <Footer v-if="!isAdminRoute" />
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  },
  setup() {
    const route = useRoute()
    
    const isAdminRoute = computed(() => {
      return route.path.startsWith('/admin') || route.path.startsWith('/partner')
    })
    
    return {
      isAdminRoute
    }
  }
}
</script>



<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}




/* Image loading optimization */
img {
  image-rendering: crisp-edges;
  image-rendering: -webkit-optimize-contrast;
}

/* Lazy loading effect */
.product-image,
.product-main-image {
  opacity: 0;
  animation: fadeIn 0.5s ease-in forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}





body {
  font-family: 'Poppins', 'Segoe UI', sans-serif;
  color: #333;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

/* Color scheme */
:root {
  --primary-blue: #1e3a8a;
  --primary-light: #3b82f6;
  --accent-blue: #0ea5e9;
  --white: #ffffff;
  --gray-light: #f3f4f6;
  --gray: #6b7280;
  --success: #10b981;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--primary-blue);
  color: var(--white);
}

.btn-primary:hover {
  background: var(--primary-light);
  transform: translateY(-2px);
}

.btn-outline {
  border: 2px solid var(--primary-blue);
  color: var(--primary-blue);
  background: transparent;
}

.btn-outline:hover {
  background: var(--primary-blue);
  color: var(--white);
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 3rem;
  color: var(--primary-blue);
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: var(--accent-blue);
  border-radius: 2px;
}
</style>


