<template>
  <div class="analytics-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <button 
          v-for="range in dateRanges" 
          :key="range.days"
          @click="setRange(range.days)"
          :class="{ active: selectedRange === range.days }"
          class="range-btn"
        >
          {{ range.label }}
        </button>
      </div>
    </div>
    
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  title: {
    type: String,
    default: 'Performance Overview'
  },
  data: {
    type: Object,
    required: true
  }
})

const chartCanvas = ref(null)
let chartInstance = null
const selectedRange = ref(30)

const dateRanges = [
  { days: 7, label: '7 Days' },
  { days: 14, label: '14 Days' },
  { days: 30, label: '30 Days' },
  { days: 90, label: '90 Days' }
]

const setRange = (days) => {
  selectedRange.value = days
  emit('rangeChange', days)
}

const emit = defineEmits(['rangeChange'])

const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels: props.data.labels || [],
      datasets: [
        {
          label: 'Clicks',
          data: props.data.clicks || [],
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Conversions',
          data: props.data.conversions || [],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: '#e5e7eb'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  })
}

watch(() => props.data, () => {
  if (chartCanvas.value) {
    createChart()
  }
}, { deep: true })

onMounted(() => {
  if (chartCanvas.value) {
    createChart()
  }
})
</script>

<style scoped>
.analytics-chart {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.chart-header h3 {
  color: #1e3a8a;
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.range-btn {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.range-btn:hover {
  background: #e0e7ff;
}

.range-btn.active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

.chart-container {
  height: 300px;
  position: relative;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .chart-controls {
    justify-content: center;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>