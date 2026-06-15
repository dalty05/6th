<template>
  <div class="redirect-container">
    <div class="redirect-card">
      <div class="spinner"></div>
      <h3>Redirecting you...</h3>
      <p>Please wait while we take you to your destination.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

onMounted(async () => {
  const code = route.params.code
  
  // Redirect to backend tracking endpoint
  window.location.href = `/api/r/${code}`
})
</script>

<style scoped>
.redirect-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.redirect-card {
  text-align: center;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

h3 {
  color: #333;
  margin-bottom: 0.5rem;
}

p {
  color: #666;
}
</style>