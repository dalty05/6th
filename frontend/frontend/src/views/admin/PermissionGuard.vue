<!-- src/components/admin/PermissionGuard.vue -->
<template>
  <div v-if="hasPermission">
    <slot />
  </div>
  <div v-else-if="showFallback" class="permission-denied">
    <i class="fas fa-lock"></i>
    <p>You don't have permission to access this content</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePermission } from '@/composables/usePermission'

const props = defineProps({
  resource: { type: String, required: true },
  action: { type: String, required: true },
  showFallback: { type: Boolean, default: true }
})

const { can } = usePermission()
const hasPermission = computed(() => can(props.resource, props.action))
</script>