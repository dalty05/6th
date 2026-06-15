<template>
  <button class="mobile-menu-btn" @click="$emit('toggle')">
    <i class="fas fa-bars"></i>
  </button>
</template>

<script setup>
defineEmits(['toggle'])
</script>

<style scoped>
.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #1e3a8a;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s;
}

.mobile-menu-btn:hover {
  background: #f8fafc;
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: block;
  }
}
</style>