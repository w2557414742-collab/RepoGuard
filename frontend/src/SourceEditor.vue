<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import type { editor } from 'monaco-editor'

const props = defineProps<{ code: string; line: number }>()
const element = ref<HTMLElement>()
let instance: editor.IStandaloneCodeEditor | undefined
let active = true

function update() {
  if (!instance) return
  instance.setValue(props.code)
  instance.revealLineInCenter(props.line)
  if (props.line > 0) instance.setPosition({ lineNumber: props.line, column: 1 })
}

onMounted(async () => {
  const [monaco, worker] = await Promise.all([
    import('monaco-editor/esm/vs/editor/editor.api'),
    import('monaco-editor/esm/vs/editor/editor.worker?worker'),
    import('monaco-editor/esm/vs/basic-languages/python/python.contribution'),
  ])
  if (!active || !element.value) return
  Object.assign(globalThis, { MonacoEnvironment: { getWorker: () => new worker.default() } })
  monaco.editor.defineTheme('repoguard', {
    base: 'vs', inherit: true, rules: [],
    colors: { 'editor.background': '#f9fbfa', 'editor.lineHighlightBackground': '#e8f3ee' },
  })
  instance = monaco.editor.create(element.value, {
    value: props.code, language: 'python', theme: 'repoguard', readOnly: true,
    minimap: { enabled: false }, fontSize: 13, automaticLayout: true,
    scrollBeyondLastLine: false, renderLineHighlight: 'all',
  })
  update()
})
watch(() => [props.code, props.line], update)
onUnmounted(() => { active = false; instance?.dispose() })
</script>

<template><div ref="element" class="source-editor" aria-label="Python source"></div></template>
