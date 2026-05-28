<template>
  <div class="scroll-progress-container">
    <div class="scroll-progress" :style="{ width: progress + '%' }"></div>
    <div class="scroll-percentage" :style="{ opacity: progress > 5 ? 1 : 0 }">
      {{ Math.round(progress) }}%
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { getScrollProgress } from '@/utils/scroll'

export default {
  name: 'ScrollProgress',
  setup() {
    const progress = ref(0)
    
    const updateProgress = () => {
      progress.value = getScrollProgress()
    }
    
    onMounted(() => {
      window.addEventListener('scroll', updateProgress)
      updateProgress()
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', updateProgress)
    })
    
    return { progress }
  }
}
</script>

<style scoped>
.scroll-progress-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1001;
  pointer-events: none;
}

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #f59e0b, #3b82f6, #10b981);
  background-size: 200% 100%;
  animation: gradientMove 2s ease infinite;
  transition: width 0.1s ease-out;
  box-shadow: 0 0 10px rgba(245,158,11,0.5);
}

.scroll-percentage {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(30,58,138,0.9);
  backdrop-filter: blur(10px);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  transition: opacity 0.3s;
  pointer-events: none;
  z-index: 1000;
}

@keyframes gradientMove {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

@media (max-width: 768px) {
  .scroll-percentage {
    display: none;
  }
}
</style>