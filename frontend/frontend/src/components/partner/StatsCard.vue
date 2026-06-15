<template>
  <div class="stats-card glass-card" :class="trendClass">
    <div class="stats-card-icon">
      <i :class="icon"></i>
    </div>
    <div class="stats-card-content">
      <div class="stats-card-value">{{ formattedValue }}</div>
      <div class="stats-card-label">{{ title }}</div>
      <div v-if="trend" class="stats-card-trend" :class="trendDirection">
        <i :class="trendIcon"></i>
        <span>{{ trend }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  trend: {
    type: Number,
    default: null
  },
  format: {
    type: String,
    default: 'number' // number, currency, percentage
  }
})

const formattedValue = computed(() => {
  if (props.format === 'percentage') {
    return `${props.value}%`
  }
  if (props.format === 'currency') {
    return `KES ${props.value.toLocaleString()}`
  }
  if (typeof props.value === 'number') {
    if (props.value >= 1000000) return `${(props.value / 1000000).toFixed(1)}M`
    if (props.value >= 1000) return `${(props.value / 1000).toFixed(1)}K`
  }
  return props.value
})

const trendDirection = computed(() => {
  if (!props.trend) return ''
  return props.trend > 0 ? 'trend-up' : 'trend-down'
})

const trendIcon = computed(() => {
  if (!props.trend) return ''
  return props.trend > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  return props.trend > 0 ? 'has-trend-up' : 'has-trend-down'
})
</script>

<style scoped>
.stats-card {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-5);
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  transition: transform var(--transition-base);
}

.stats-card:hover {
  transform: translateY(-2px);
}

.stats-card-icon {
  width: 56px;
  height: 56px;
  background: var(--primary-blue-lighter);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-card-icon i {
  font-size: var(--text-2xl);
  color: var(--accent-orange);
}

.stats-card-content {
  flex: 1;
}

.stats-card-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--primary-blue);
  line-height: 1.2;
}

.stats-card-label {
  font-size: var(--text-sm);
  color: var(--gray-500);
  margin-top: var(--spacing-1);
}

.stats-card-trend {
  font-size: var(--text-xs);
  margin-top: var(--spacing-2);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.trend-up {
  color: var(--success);
}

.trend-down {
  color: var(--error);
}
</style>