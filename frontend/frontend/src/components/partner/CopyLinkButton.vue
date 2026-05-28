<template>
  <button class="copy-btn" :class="{ copied: isCopied }" @click="copyLink">
    <i v-if="isCopied" class="fas fa-check"></i>
    <i v-else class="fas fa-copy"></i>
    <span>{{ isCopied ? 'Copied!' : 'Copy' }}</span>
  </button>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  link: {
    type: String,
    required: true
  }
})

const isCopied = ref(false)

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(props.link)
    isCopied.value = true
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
    alert('Failed to copy link. Please copy manually.')
  }
}
</script>

<style scoped>
.copy-btn {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.copy-btn:hover {
  background: #d97706;
  transform: translateY(-2px);
}

.copy-btn.copied {
  background: #10b981;
}
</style>