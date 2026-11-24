<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { init, use, type ECharts } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { Benchmark } from './types'

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])
const props = defineProps<{ benchmark: Benchmark }>()
const element = ref<HTMLElement>()
let chart: ECharts | undefined
let resize: ResizeObserver | undefined

function update() {
  const labels = Object.keys(props.benchmark.index)
  chart?.setOption({
    grid: { left: 110, right: 24, top: 15, bottom: 30 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', name: 'Seconds', nameLocation: 'middle', nameGap: 24 },
    yAxis: { type: 'category', data: labels, inverse: true, axisTick: { show: false } },
    series: [{ type: 'bar', barWidth: 20, itemStyle: { color: '#267a5b', borderRadius: [0, 4, 4, 0] },
      data: labels.map(label => Number(props.benchmark.index[label].median_seconds.toFixed(3))) }],
  })
}

onMounted(() => {
  if (!element.value) return
  chart = init(element.value)
  update()
  resize = new ResizeObserver(() => chart?.resize())
  resize.observe(element.value)
})
watch(() => props.benchmark, update)
onUnmounted(() => { resize?.disconnect(); chart?.dispose() })
</script>

<template><div ref="element" class="benchmark-chart" aria-label="Median index time by strategy"></div></template>
