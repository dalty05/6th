<!-- components/BaseModal.vue -->
<template>
  <Teleport to="body">
    <div 
      v-if="isOpen" 
      class="modal-overlay" 
      @click.self="close"
      @keydown.esc="close"
    >
      <div 
        class="modal-container" 
        :class="[
          `size-${size}`,
          `layout-${layout}`,
          { 'no-header': !showHeader }
        ]"
        role="dialog"
        aria-modal="true"
        :aria-label="ariaLabel"
      >
        <!-- Modal Header -->
        <div v-if="showHeader" class="modal-header">
          <div class="modal-header-left">
            <slot name="header-left">
              <h3 v-if="title" class="modal-title">{{ title }}</h3>
            </slot>
          </div>
          <div class="modal-header-actions">
            <slot name="header-actions"></slot>
            <button 
              class="modal-close-btn" 
              @click="close"
              aria-label="Close modal"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <!-- Modal Body -->
        <div 
          class="modal-body" 
          :class="{ 'no-padding': noPadding }"
          ref="modalBody"
        >
          <slot></slot>
        </div>

        <!-- Modal Footer -->
        <div v-if="$slots.footer" class="modal-footer">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'BaseModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    layout: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'product', 'blog', 'job'].includes(value)
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    noPadding: {
      type: Boolean,
      default: false
    },
    ariaLabel: {
      type: String,
      default: 'Modal dialog'
    },
    closeOnEsc: {
      type: Boolean,
      default: true
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close'],
  watch: {
    isOpen: {
      handler(newVal) {
        if (newVal) {
          document.body.style.overflow = 'hidden'
          this.$nextTick(() => {
            this.focusModal()
          })
        } else {
          document.body.style.overflow = 'auto'
        }
      },
      immediate: true
    }
  },
  mounted() {
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
    document.body.style.overflow = 'auto'
  },
  methods: {
    close() {
      this.$emit('close')
    },
    handleKeydown(event) {
      if (this.isOpen && this.closeOnEsc && event.key === 'Escape') {
        this.close()
      }
    },
    focusModal() {
      const container = this.$el?.querySelector('.modal-container')
      if (container) {
        container.focus()
      }
    },
    // For scrolling to specific elements within the modal
    scrollToElement(selector) {
      const element = this.$refs.modalBody?.querySelector(selector)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.modal-container {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  max-height: 95vh;
  animation: slideUp 0.4s cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
  outline: none;
}

/* Sizes */
.modal-container.size-small {
  width: min(95vw, 600px);
}

.modal-container.size-medium {
  width: min(95vw, 1000px);
}

.modal-container.size-large {
  width: min(95vw, 1400px);
}

/* Layout variants */
.modal-container.layout-product .modal-body {
  padding: 2rem;
}

.modal-container.layout-blog .modal-body {
  padding: 0;
  overflow-y: auto;
  max-height: calc(95vh - 80px);
}

.modal-container.layout-blog .modal-body.no-padding {
  padding: 0;
}

.modal-container.layout-job .modal-body {
  padding: 0;
  overflow: hidden;
  max-height: calc(95vh - 80px);
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  flex-shrink: 0;
  z-index: 10;
  gap: 1rem;
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.modal-title {
  margin: 0;
  font-size: 1.1rem;
  color: #1e3a8a;
}

.modal-header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal-close-btn {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.modal-close-btn:hover {
  background: #f3f4f6;
  color: #1e3a8a;
  transform: rotate(90deg);
}

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  scroll-behavior: smooth;
}

.modal-body.no-padding {
  padding: 0;
}

.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 2rem;
  border-top: 1px solid #e5e7eb;
  background: white;
  flex-shrink: 0;
}

/* When header is hidden */
.modal-container.no-header .modal-body {
  padding-top: 2rem;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
  }
  
  .modal-container {
    width: 98vw;
    max-height: 98vh;
    border-radius: 16px;
  }
  
  .modal-header {
    padding: 0.75rem 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 0.75rem 1rem;
    flex-wrap: wrap;
  }
  
  .modal-container.layout-blog .modal-body {
    max-height: calc(98vh - 60px);
  }
  
  .modal-container.layout-job .modal-body {
    max-height: calc(98vh - 60px);
  }
}

@media (max-width: 480px) {
  .modal-container {
    border-radius: 12px;
  }
  
  .modal-header {
    padding: 0.5rem 0.75rem;
  }
  
  .modal-body {
    padding: 0.75rem;
  }
  
  .modal-footer {
    padding: 0.5rem 0.75rem;
  }
  
  .modal-title {
    font-size: 0.95rem;
  }
}
</style>