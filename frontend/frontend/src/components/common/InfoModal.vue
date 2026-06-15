<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-overlay" @click.visible="close">
        <div class="modal-backdrop-blur"></div>
        <div class="modal-container glass-card" @click.stop>
          <div class="modal-header">
            <h2>{{ title }}</h2>
            <button @click="close" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <slot>
              <div v-html="content"></div>
            </slot>
          </div>
          <div class="modal-footer">
            <button @click="close" class="btn btn-primary">Close</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Information'
  },
  content: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'update:visible'])

const close = () => {
  emit('close')
  emit('update:visible', false)
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
    document.body.style.position = 'fixed'
    document.body.style.width = '100%'
    document.body.style.top = `-${window.scrollY}px`
  } else {
    const scrollY = document.body.style.top
    document.body.style.overflow = ''
    document.body.style.position = ''
    document.body.style.width = ''
    document.body.style.top = ''
    window.scrollTo(0, parseInt(scrollY || '0') * -1)
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-backdrop-blur {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.modal-container {
  position: relative;
  background: white;
  border-radius: 24px;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease;
  z-index: 10000;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  position: sticky;
  top: 0;
  z-index: 1;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #9ca3af;
  transition: all 0.3s;
  line-height: 1;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  color: #ef4444;
  background: #fee2e2;
}

/* Modal Body */
.modal-body {
  padding: 1.5rem;
  max-height: calc(85vh - 130px);
  overflow-y: auto;
}

/* Custom Scrollbar for Modal Body */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #f59e0b;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #d97706;
}

/* Modal Footer */
.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  background: white;
  position: sticky;
  bottom: 0;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* Animations */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Glass Card Effect */
.glass-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    max-width: none;
    max-height: 90vh;
  }
  
  .modal-header h2 {
    font-size: 1.1rem;
  }
  
  .modal-body {
    padding: 1rem;
    max-height: calc(90vh - 120px);
  }
  
  .close-btn {
    font-size: 1.5rem;
    width: 32px;
    height: 32px;
  }
}
</style>