<template>
  <div class="data-table-container">
    <!-- Search and Filter Bar -->
    <div class="table-toolbar" v-if="showToolbar">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          :placeholder="searchPlaceholder"
          @input="onSearch"
        >
      </div>
      
      <div class="filters" v-if="filters.length">
        <select v-for="filter in filters" :key="filter.key" v-model="filterValues[filter.key]" @change="onFilterChange">
          <option value="">All {{ filter.label }}</option>
          <option v-for="option in filter.options" :key="option" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      
      <div class="table-actions" v-if="$slots.actions">
        <slot name="actions" />
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="table-loading">
      <div class="loading-spinner"></div>
      <p>Loading data...</p>
    </div>
    
    <!-- Table -->
    <div v-else class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key" :style="{ width: column.width }">
              <div class="th-content" :class="{ sortable: column.sortable }" @click="column.sortable && sort(column.key)">
                {{ column.label }}
                <i v-if="column.sortable && sortKey === column.key" class="fas" :class="sortOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down'"></i>
                <i v-else-if="column.sortable" class="fas fa-sort"></i>
              </div>
            </th>
            <th v-if="$slots.actions" style="width: 120px">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in paginatedData" :key="index">
            <td v-for="column in columns" :key="column.key">
              <div v-if="column.type === 'image' && row[column.key]">
                <img :src="row[column.key]" class="table-image" :alt="row[column.altKey]">
              </div>
              <div v-else-if="column.type === 'status'">
                <span class="status-badge" :class="getStatusClass(row[column.key])">
                  {{ row[column.key] }}
                </span>
              </div>
              <div v-else-if="column.type === 'date'">
                {{ formatDate(row[column.key]) }}
              </div>
              <div v-else-if="column.type === 'truncate'">
                {{ truncate(row[column.key], column.maxLength || 100) }}
              </div>
              <div v-else>
                {{ row[column.key] }}
              </div>
            </td>
            <td v-if="$slots.actions" class="actions-cell">
              <slot name="actions" :row="row" />
            </td>
          </tr>
          <tr v-if="filteredData.length === 0">
            <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="empty-row">
              <i class="fas fa-inbox"></i>
              <p>No data available</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="table-pagination">
      <button @click="currentPage--" :disabled="currentPage === 1" class="pagination-btn">
        <i class="fas fa-chevron-left"></i>
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="currentPage++" :disabled="currentPage === totalPages" class="pagination-btn">
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  searchPlaceholder: {
    type: String,
    default: 'Search...'
  },
  searchKeys: {
    type: Array,
    default: () => []
  },
  filters: {
    type: Array,
    default: () => []
  },
  itemsPerPage: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['search', 'filter', 'sort'])

// State
const searchQuery = ref('')
const filterValues = ref({})
const sortKey = ref('')
const sortOrder = ref('asc')
const currentPage = ref(1)

// Computed
const filteredData = computed(() => {
  let result = [...props.data]
  
  // Apply search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    const searchKeys = props.searchKeys.length ? props.searchKeys : props.columns.map(c => c.key)
    
    result = result.filter(item => {
      return searchKeys.some(key => {
        const value = item[key]
        return value && String(value).toLowerCase().includes(query)
      })
    })
  }
  
  // Apply filters
  for (const [key, value] of Object.entries(filterValues.value)) {
    if (value) {
      result = result.filter(item => item[key] === value)
    }
  }
  
  // Apply sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      let aVal = a[sortKey.value]
      let bVal = b[sortKey.value]
      
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase()
        bVal = bVal.toLowerCase()
      }
      
      if (sortOrder.value === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / props.itemsPerPage))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * props.itemsPerPage
  const end = start + props.itemsPerPage
  return filteredData.value.slice(start, end)
})

// Methods
const onSearch = () => {
  currentPage.value = 1
  emit('search', searchQuery.value)
}

const onFilterChange = () => {
  currentPage.value = 1
  emit('filter', filterValues.value)
}

const sort = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('sort', { key: sortKey.value, order: sortOrder.value })
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const truncate = (text, length) => {
  if (!text) return '-'
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const getStatusClass = (status) => {
  const classes = {
    published: 'status-published',
    draft: 'status-draft',
    active: 'status-active',
    inactive: 'status-inactive',
    approved: 'status-approved',
    pending: 'status-pending'
  }
  return classes[status?.toLowerCase()] || 'status-default'
}

// Watch for data changes to reset pagination
watch(() => props.data, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.data-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
  gap: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.search-box i {
  color: #999;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  width: 250px;
}

.filters {
  display: flex;
  gap: 0.5rem;
}

.filters select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #1e3a8a;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.th-content.sortable {
  cursor: pointer;
  user-select: none;
}

.th-content i {
  color: #999;
  font-size: 0.8rem;
}

.table-image {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 8px;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-published, .status-active, .status-approved {
  background: #d1fae5;
  color: #065f46;
}

.status-draft, .status-inactive {
  background: #fef3c7;
  color: #92400e;
}

.status-pending {
  background: #e0e7ff;
  color: #1e40af;
}

.status-default {
  background: #f3f4f6;
  color: #374151;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.empty-row {
  text-align: center;
  padding: 3rem !important;
  color: #999;
}

.empty-row i {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.table-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #f59e0b;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.85rem;
  color: #666;
}

.table-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .filters {
    flex-wrap: wrap;
  }
  
  .filters select {
    flex: 1;
  }
}
</style>