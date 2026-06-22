
<template>
  <div class="chart-widget">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  type: { type: String, default: 'line' },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) }
})

const chartCanvas = ref(null)
let chartInstance = null

onMounted(() => {
  chartInstance = new Chart(chartCanvas.value, {
    type: props.type,
    data: props.data,
    options: props.options
  })
})

watch(() => props.data, (newData) => {
  if (chartInstance) {
    chartInstance.data = newData
    chartInstance.update()
  }
}, { deep: true })
</script>