<template>
  <div v-if="hasPermission" class="permission-guard">
    <slot />
  </div>
  <div v-else-if="showFallback" class="permission-denied">
    <div class="denied-content">
      <i class="fas fa-lock"></i>
      <h3>Access Denied</h3>
      <p>You don't have permission to {{ actionText }} this {{ resourceName }}.</p>
      <p v-if="contactAdmin" class="contact-hint">
        Please contact your administrator if you need access.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePermission } from '@/composables/usePermission'

const props = defineProps({
  resource: {
    type: String,
    required: true,
    validator: (value) => ['products', 'blog', 'users', 'partners', 'referrals', 'statistics'].includes(value)
  },
  action: {
    type: String,
    required: true,
    validator: (value) => ['create', 'read', 'update', 'delete'].includes(value)
  },
  showFallback: {
    type: Boolean,
    default: true
  },
  contactAdmin: {
    type: Boolean,
    default: false
  }
})

const { can } = usePermission()

const hasPermission = computed(() => can(props.resource, props.action))

const resourceNames = {
  products: 'Products',
  blog: 'Blog Posts',
  users: 'Users',
  partners: 'Partners',
  referrals: 'Referral Links',
  statistics: 'Statistics'
}

const actionNames = {
  create: 'create',
  read: 'view',
  update: 'edit',
  delete: 'delete'
}

const resourceName = computed(() => resourceNames[props.resource] || props.resource)
const actionName = computed(() => actionNames[props.action] || props.action)
const actionText = computed(() => `${actionName.value} ${resourceName.value}`)
</script>

<style scoped>
.permission-guard {
  display: contents;
}

.permission-denied {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 2rem;
}

.denied-content {
  text-align: center;
  max-width: 400px;
}

.denied-content i {
  font-size: 4rem;
  color: #dc2626;
  margin-bottom: 1rem;
}

.denied-content h3 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.denied-content p {
  color: #666;
  margin-bottom: 0.5rem;
}

.contact-hint {
  font-size: 0.85rem;
  color: #999;
  margin-top: 1rem;
}
</style>