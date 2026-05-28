<template>
  <div class="link-card glass-card">
    <div class="link-header">
      <div class="link-info">
        <h3>{{ link.name }}</h3>
        <span class="campaign-tag" v-if="link.campaign_name">
          <i class="fas fa-tag"></i> {{ link.campaign_name }}
        </span>
        <span class="status-badge" :class="link.is_active ? 'active' : 'inactive'">
          {{ link.is_active ? 'Active' : 'Inactive' }}
        </span>
      </div>
      <div class="link-actions">
        <button @click="$emit('edit', link)" class="icon-btn" title="Edit">
          <i class="fas fa-edit"></i>
        </button>
        <button @click="$emit('toggle', link)" class="icon-btn" :title="link.is_active ? 'Deactivate' : 'Activate'">
          <i :class="link.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
        </button>
        <button @click="$emit('delete', link)" class="icon-btn delete-btn" title="Delete">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </div>
    
    <div class="link-url">
      <code>{{ fullUrl }}</code>
      <CopyLinkButton :link="fullUrl" />
    </div>
    
    <div class="link-stats">
      <div class="stat-item">
        <span class="stat-value">{{ link.total_clicks || 0 }}</span>
        <span class="stat-label">Total Clicks</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ link.unique_clicks || 0 }}</span>
        <span class="stat-label">Unique Clicks</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ link.conversions || 0 }}</span>
        <span class="stat-label">Conversions</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ link.conversion_rate || 0 }}%</span>
        <span class="stat-label">Conversion Rate</span>
      </div>
    </div>
    
    <div class="link-footer">
      <span class="created-date">
        <i class="far fa-calendar-alt"></i> Created: {{ formatDate(link.created_at) }}
      </span>
      <span v-if="link.expires_at" class="expiry-date">
        <i class="far fa-clock"></i> Expires: {{ formatDate(link.expires_at) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import CopyLinkButton from './CopyLinkButton.vue'

const props = defineProps({
  link: {
    type: Object,
    required: true
  },
  baseUrl: {
    type: String,
    default: window.location.origin
  }
})

const emit = defineEmits(['edit', 'toggle', 'delete'])

const fullUrl = computed(() => `${props.baseUrl}/r/${props.link.link_code}`)

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.link-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: transform 0.3s, box-shadow 0.3s;
}

.link-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.link-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.link-info h3 {
  margin: 0 0 0.5rem 0;
  color: #1e3a8a;
}

.campaign-tag {
  display: inline-block;
  background: #e0e7ff;
  color: #1e3a8a;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  margin-right: 0.5rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.link-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s;
  color: #666;
}

.icon-btn:hover {
  background: #f8fafc;
  color: #f59e0b;
}

.delete-btn:hover {
  color: #dc2626;
}

.link-url {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.link-url code {
  font-size: 0.85rem;
  color: #1e3a8a;
  word-break: break-all;
}

.link-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  text-align: center;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 12px;
}

.stat-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
  color: #1e3a8a;
}

.stat-label {
  font-size: 0.7rem;
  color: #666;
}

.link-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #999;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.link-footer i {
  margin-right: 0.25rem;
}

@media (max-width: 768px) {
  .link-header {
    flex-direction: column;
  }
  
  .link-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>