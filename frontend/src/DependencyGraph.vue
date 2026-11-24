<script setup lang="ts">
import cytoscape, { type Core, type ElementDefinition } from 'cytoscape'
import { onMounted, onUnmounted, ref, watch } from 'vue'
import type { GraphResult, SymbolRecord } from './types'

const props = defineProps<{ graph: GraphResult; focus: string }>()
const emit = defineEmits<{ select: [symbol: SymbolRecord] }>()
const element = ref<HTMLElement>()
let canvas: Core | undefined

function draw() {
  if (!element.value) return
  canvas?.destroy()
  const known = new Set(props.graph.nodes.map(n => n.id))
  const elements: ElementDefinition[] = props.graph.nodes.map(node => ({
    data: { id: node.id, label: node.symbol?.name ?? node.kind, origin: node.id === props.focus },
  }))
  const seen = new Set<string>()
  for (const node of props.graph.nodes) for (const edge of node.evidence) {
    const id = [edge.source, edge.target, edge.kind, edge.path, edge.line].join(':')
    if (seen.has(id) || !known.has(edge.source) || !known.has(edge.target)) continue
    seen.add(id)
    elements.push({ data: { id, source: edge.source, target: edge.target, confidence: edge.confidence } })
  }
  canvas = cytoscape({
    container: element.value, elements, minZoom: 0.16, maxZoom: 2.2, wheelSensitivity: 0.2,
    layout: { name: 'breadthfirst', directed: true, padding: 32, animate: false },
    style: [
      { selector: 'node', style: { label: 'data(label)', 'font-size': 11, color: '#293d3f',
        'background-color': '#a4cdbb', 'border-color': '#568e78', 'border-width': 1,
        'text-margin-y': 6, 'text-valign': 'bottom', width: 24, height: 24 } },
      { selector: 'node[?origin]', style: { 'background-color': '#17694e', width: 34, height: 34 } },
      { selector: 'edge', style: { width: 1.4, 'line-color': '#89a09a', 'target-arrow-color': '#89a09a',
        'target-arrow-shape': 'triangle', 'curve-style': 'bezier' } },
      { selector: 'edge[confidence = "POSSIBLE"]', style: { 'line-style': 'dashed', 'line-color': '#ac7834' } },
    ],
  })
  canvas.on('tap', 'node', (event) => {
    const symbol = props.graph.nodes.find(n => n.id === event.target.id())?.symbol
    if (symbol) emit('select', symbol)
  })
}

onMounted(draw)
watch(() => props.graph, draw)
onUnmounted(() => canvas?.destroy())
</script>

<template><div ref="element" class="graph-canvas" aria-label="Dependency graph"></div></template>
