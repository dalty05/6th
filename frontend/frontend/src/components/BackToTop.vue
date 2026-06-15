<template>
  <Transition name="fade">
    <button 
      v-show="visible" 
      @click="scrollToTop" 
      class="back-to-top"
      aria-label="Back to top"
    >
      <div class="back-to-top-icon">
        <span>↑</span>
      </div>
      <span></span><span></span>
      
    
      <span class="back-to-top-text">Top</span>
    </button>
  </Transition>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { scrollToSection } from '@/utils/scroll.js'

export default {
  name: 'BackToTop',
  setup() {
    const visible = ref(false)
    
    const handleScroll = () => {
      visible.value = window.scrollY > 500
    }
    
    const scrollToTop = () => {
      scrollToSection('home', 0)
    }
    
    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })
    
    return { visible, scrollToTop }
  }
}
</script>

<!-- <style scoped>
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: rgba(30,58,138,0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 50px;
  padding: 12px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  z-index: 999;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.back-to-top:hover {
  background: #f59e0b;
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(245,158,11,0.4);
}

.back-to-top-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.back-to-top-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

@media (max-width: 768px) {
  .back-to-top {
    bottom: 20px;
    right: 20px;
    padding: 10px 16px;
  }
  
  .back-to-top-text {
    display: none;
  }
  
  .back-to-top-icon {
    font-size: 1rem;
  }
}
</style> -->