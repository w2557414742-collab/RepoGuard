<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import type { Benchmark, Edge, GraphResult, Hit, Impact, RefactorPlan, Selection,
  Snapshot, SymbolRecord, Violation } from './types'

const SourceEditor = defineAsyncComponent(() => import('./SourceEditor.vue'))
const DependencyGraph = defineAsyncComponent(() => import('./DependencyGraph.vue'))
const BenchmarkChart = defineAsyncComponent(() => import('./BenchmarkChart.vue'))
const tabs = [
  { name: 'Explore', icon: '⌕' }, { name: 'Changes', icon: '⇄' }, { name: 'Tests', icon: '✓' },
  { name: 'Refactoring', icon: '◇' }, { name: 'Architecture', icon: '▤' }, { name: 'Benchmarks', icon: '▥' },
] as const
type Tab = typeof tabs[number]['name']
const tab = ref<Tab>('Explore')
const revision = ref('HEAD')
const base = ref('HEAD~1')
const target = ref('HEAD')
const snapshot = ref<Snapshot>()
const query = ref('')
const fileFilter = ref('')
const hits = ref<Hit[]>([])
const searched = ref(false)
const selected = ref<SymbolRecord>()
const source = ref('')
const sourcePath = ref('')
const sourceLine = ref(1)
const graph = ref<GraphResult>()
const references = ref<Edge[]>([])
const graphKind = ref('')
const reverse = ref(true)
const mode = ref('hybrid')
const impact = ref<Impact>()
const selection = ref<Selection>()
const plan = ref<RefactorPlan>()
const newName = ref('')
const operation = ref('rename')
const newValue = ref('')
const violations = ref<Record<string, Violation[]>>()
const benchmark = ref<Benchmark>()
const diff = ref('')
const diffPath = ref('')
const error = ref('')
const pending = ref(0)
let fileRequest = 0
let graphRequest = 0
let navigationRequest = 0

const files = computed(() => (snapshot.value?.files ?? []).filter(item =>
  item.path.toLowerCase().includes(fileFilter.value.toLowerCase()),
).slice(0, 250))
const compact = (value?: number) => value?.toLocaleString() ?? '—'

async function request<T>(path: string, params: Record<string, string> = {}, body?: object): Promise<T> {
  const url = new URL('/v1/' + path, location.origin)
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value)
  const result = await fetch(url, body ? {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  } : undefined)
  if (!result.ok) {
    const message = await result.json().catch(() => ({}))
    throw new Error(typeof message.detail === 'string' ? message.detail : `HTTP ${result.status}`)
  }
  return result.json()
}

async function perform(action: () => Promise<void>) {
  pending.value += 1
  error.value = ''
  try { await action() }
  catch (cause) { error.value = cause instanceof Error ? cause.message : String(cause) }
  finally { pending.value -= 1 }
}

function loadSnapshot() {
  return perform(async () => {
    const value = await request<Snapshot>('snapshot', { revision: revision.value })
    snapshot.value = value
    ++navigationRequest
    ++fileRequest
    ++graphRequest
    sourcePath.value = ''
    references.value = []
    selected.value = undefined
    graph.value = undefined
    hits.value = []
    searched.value = false
  })
}

function search() {
  return perform(async () => {
    hits.value = await request<Hit[]>('symbols', { q: query.value, revision: revision.value })
    searched.value = true
    if (hits.value.length && !selected.value) await navigate(hits.value[0].symbol)
  })
}

async function showFile(path: string, line = 1) {
  const id = ++fileRequest
  const response = await request<{ source: string }>('file', { path, revision: revision.value })
  if (id !== fileRequest) return
  source.value = response.source
  sourcePath.value = path
  sourceLine.value = line
}

async function loadGraph() {
  if (!selected.value) return
  const id = ++graphRequest
  const params = { revision: revision.value, depth: '2', limit: '60', reverse: String(reverse.value) }
  const value = await request<GraphResult>(`graph/${selected.value.id}`,
    graphKind.value ? { ...params, kinds: graphKind.value } : params)
  if (id === graphRequest) graph.value = value
}

async function navigate(symbol: SymbolRecord) {
  const id = ++navigationRequest
  selected.value = symbol
  plan.value = undefined
  graph.value = undefined
  const [edges] = await Promise.all([
    request<Edge[]>(`references/${symbol.id}`, { revision: revision.value }),
    showFile(symbol.path, symbol.line),
    loadGraph(),
  ])
  if (id === navigationRequest) references.value = edges
}

function choose(symbol: SymbolRecord) {
  return perform(() => navigate(symbol))
}

function showDiff(path: string) {
  return perform(async () => {
    const data = await request<{ diff: string }>('diff', { base: base.value, target: target.value, path })
    diffPath.value = path
    diff.value = data.diff
  })
}

function compare() {
  return perform(async () => {
    const params = { base: base.value, target: target.value }
    if (tab.value === 'Changes') {
      impact.value = await request<Impact>('impact', params)
      diff.value = ''
      diffPath.value = ''
    }
    if (tab.value === 'Tests') selection.value = await request<Selection>('tests', { ...params, mode: mode.value })
    if (tab.value === 'Architecture') violations.value = await request<Record<string, Violation[]>>('architecture', params)
  })
}

function preview() {
  if (!selected.value) return
  return perform(async () => {
    plan.value = await request<RefactorPlan>('refactoring/plan', {}, {
      revision: revision.value, symbol_id: selected.value?.id, name: newName.value,
      operation: operation.value, value: operation.value === 'signature' ? newValue.value : null,
    })
  })
}

function openTab(name: Tab) {
  tab.value = name
  error.value = ''
  if (name === 'Benchmarks' && !benchmark.value) {
    void perform(async () => { benchmark.value = await request<Benchmark>('benchmark') })
  }
}

onMounted(loadSnapshot)
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand"><span class="mark">RG</span><span>RepoGuard</span></div>
      <nav aria-label="Main navigation">
        <button v-for="item in tabs" :key="item.name" :class="{ active: tab === item.name }"
          :aria-current="tab === item.name ? 'page' : undefined" @click="openTab(item.name)">
          <span aria-hidden="true">{{ item.icon }}</span>{{ item.name }}
        </button>
      </nav>
      <form class="revision" @submit.prevent="loadSnapshot">
        <label for="revision">Index revision</label>
        <div class="inline"><input id="revision" v-model.trim="revision" required /><button class="square" aria-label="Load revision">↵</button></div>
        <code v-if="snapshot">{{ snapshot.metadata.target_commit.slice(0, 12) }}</code>
      </form>
    </aside>

    <main>
      <header class="top">
        <div><p class="context">Repository intelligence</p><h1>{{ tab === 'Explore' ? 'Repository explorer' : tab }}</h1></div>
        <div class="status" role="status"><span :class="{ online: snapshot }"></span>{{ pending ? 'Loading…' : snapshot ? 'Index available' : 'Awaiting index' }}</div>
      </header>
      <div v-if="error" class="notice error" role="alert">{{ error }}</div>

      <template v-if="tab === 'Explore'">
        <div class="stats">
          <div><span>Python files</span><strong>{{ compact(snapshot?.metadata.file_status.indexed) }}</strong></div>
          <div><span>Symbols</span><strong>{{ compact(snapshot?.metadata.symbols) }}</strong></div>
          <div><span>Relationships</span><strong>{{ compact(snapshot?.metadata.edges) }}</strong></div>
          <div><span>Python lines</span><strong>{{ compact(snapshot?.metadata.python_lines) }}</strong></div>
        </div>
        <form class="search" @submit.prevent="search">
          <label class="sr-only" for="symbol-query">Search symbols</label><span aria-hidden="true">⌕</span>
          <input id="symbol-query" v-model.trim="query" placeholder="Search by name, qualified name, or signature" required />
          <button class="primary">Search</button>
        </form>
        <div class="explorer">
          <section class="panel file-panel">
            <div class="panel-heading"><h2>{{ searched ? 'Search results' : 'Indexed files' }}</h2>
              <button v-if="searched" class="plain" @click="searched = false">Show files</button></div>
            <template v-if="searched">
              <button v-for="hit in hits" :key="hit.symbol.id" class="list-item"
                :class="{ chosen: selected?.id === hit.symbol.id }" @click="choose(hit.symbol)">
                <strong>{{ hit.symbol.qualified_name }}</strong><small>{{ hit.symbol.kind }} · {{ hit.symbol.path }}:{{ hit.symbol.line }}</small>
              </button>
              <p v-if="!hits.length" class="empty">No matches.</p>
            </template>
            <template v-else>
              <input v-model="fileFilter" class="filter" placeholder="Filter paths" aria-label="Filter file paths" />
              <button v-for="file in files" :key="file.path" class="list-item" :class="{ chosen: sourcePath === file.path }"
                @click="perform(() => showFile(file.path))"><strong>{{ file.path }}</strong><small>{{ compact(file.lines) }} lines</small></button>
              <p v-if="!files.length" class="empty">No indexed files to display.</p>
            </template>
          </section>
          <div class="detail">
            <section class="panel">
              <div class="panel-heading"><h2>Source</h2><code v-if="sourcePath">{{ sourcePath }}</code></div>
              <SourceEditor v-if="sourcePath" :code="source" :line="sourceLine" />
              <p v-else class="empty">Select a file or search for a symbol.</p>
            </section>
            <section class="panel">
              <div class="panel-heading"><h2>Dependencies</h2>
                <div v-if="selected" class="inline">
                  <select v-model="graphKind" aria-label="Edge type" @change="perform(loadGraph)">
                    <option value="">All relationships</option><option value="CALLS">Calls</option>
                    <option value="IMPORTS">Imports</option><option value="REFERENCES">References</option>
                    <option value="DEPENDS_ON">Module dependencies</option><option value="INHERITS">Inherits</option>
                  </select>
                  <button class="plain" @click="reverse = !reverse; perform(loadGraph)">{{ reverse ? 'Incoming' : 'Outgoing' }}</button>
                </div>
              </div>
              <DependencyGraph v-if="graph && selected" :graph="graph" :focus="selected.id"
                @select="symbol => perform(() => showFile(symbol.path, symbol.line))" />
              <p v-else class="empty">Select a symbol to load its dependency graph.</p>
              <p v-if="graph?.truncated" class="notice">Graph limited to 60 nodes.</p>
              <p v-if="graph" class="graph-legend"><span></span> Possible relationship</p>
            </section>
            <section v-if="selected" class="panel">
              <div class="panel-heading"><h2>References</h2><span>{{ references.length }}</span></div>
              <button v-for="(edge, index) in references" :key="index" class="list-item"
                @click="perform(() => showFile(edge.path, edge.line))">
                <strong>{{ edge.path }}:{{ edge.line }}</strong><small>{{ edge.kind }} · {{ edge.confidence }}</small>
              </button>
            </section>
          </div>
        </div>
      </template>

      <template v-if="['Changes', 'Tests', 'Architecture'].includes(tab)">
        <form class="compare panel" @submit.prevent="compare">
          <label>Base revision<input v-model.trim="base" required /></label>
          <label>Target revision<input v-model.trim="target" required /></label>
          <label v-if="tab === 'Tests'">Selection strategy<select v-model="mode">
            <option value="hybrid">Hybrid</option><option value="static">Static dependencies</option><option value="file">Modified test files</option>
          </select></label>
          <button class="primary">{{ tab === 'Tests' ? 'Select tests' : 'Compare' }}</button>
        </form>
      </template>

      <template v-if="tab === 'Changes' && impact">
        <p v-if="impact.fallback_reasons.length" class="notice">{{ impact.fallback_reasons.join(' · ') }}</p>
        <section class="panel">
          <div class="panel-heading"><h2>Changed files</h2><span>{{ impact.files.length }}</span></div>
          <button v-for="item in impact.files" :key="item.new_path ?? item.old_path ?? ''" class="list-item"
            @click="showDiff(item.new_path ?? item.old_path ?? '')">
            <strong>{{ item.status }} · {{ item.new_path ?? item.old_path }}</strong>
            <small>{{ item.new_ranges.map(([start, end]) => `${start}–${end}`).join(', ') || 'See diff' }}</small>
          </button>
          <pre v-if="diffPath" class="diff" aria-label="Git diff">{{ diff || 'No textual diff.' }}</pre>
        </section>
        <section class="panel">
          <div class="panel-heading"><h2>Changed symbols</h2><span>{{ impact.changes.length }}</span></div>
          <div v-for="(item, index) in impact.changes" :key="index" class="list-item">
            <strong>{{ item.after?.qualified_name ?? item.before?.qualified_name ?? item.path }}</strong>
            <small>{{ item.kind }}{{ item.public_api ? ' · public API' : '' }}</small>
          </div>
        </section>
        <section class="panel">
          <div class="panel-heading"><h2>Ranked impact</h2><span>{{ impact.impacts.length }}</span></div>
          <details v-for="item in impact.impacts" :key="item.symbol.id" class="evidence">
            <summary>{{ item.symbol.qualified_name }} <span>{{ item.classification }} · {{ item.risk.toFixed(2) }}</span></summary>
            <ol><li v-for="(edge, index) in item.evidence" :key="index">{{ edge.kind }} · {{ edge.path }}:{{ edge.line }} · {{ edge.confidence }}</li></ol>
          </details>
        </section>
      </template>

      <template v-if="tab === 'Tests' && selection">
        <p v-if="selection.run_all" class="notice">Full-suite fallback · {{ selection.reasons.join(' · ') }}</p>
        <section class="panel"><div class="panel-heading"><h2>Related tests</h2><span>{{ selection.tests.length }}</span></div>
          <p v-if="!selection.tests.length" class="empty">No matching tests were identified.</p>
          <div v-for="test in selection.tests" :key="test" class="list-item"><strong>{{ test }}</strong><small>{{ selection.evidence[test]?.join(' · ') }}</small></div>
        </section>
      </template>

      <template v-if="tab === 'Refactoring'">
        <p v-if="!selected" class="notice">Select a symbol in the repository explorer to preview a refactoring.</p>
        <template v-else>
          <form class="compare panel" @submit.prevent="preview">
            <div class="target-symbol"><small>Target symbol</small><strong>{{ selected.qualified_name }}</strong></div>
            <label>Operation<select v-model="operation"><option value="rename">Rename</option><option value="signature">Add required keyword</option></select></label>
            <label>New name<input v-model.trim="newName" required /></label>
            <label v-if="operation === 'signature'">Python literal<input v-model.trim="newValue" required /></label>
            <button class="primary">Preview</button>
          </form>
          <section v-if="plan" class="panel">
            <div class="panel-heading"><h2>Patch preview</h2><span>{{ plan.api_change }}</span></div>
            <ul v-if="plan.blockers.length" class="notice"><li v-for="blocker in plan.blockers" :key="blocker">{{ blocker }}</li></ul>
            <pre v-if="plan.patch" class="diff">{{ plan.patch }}</pre>
            <dl class="checks"><template v-for="(status, check) in plan.checks" :key="check"><dt>{{ check }}</dt><dd>{{ status }}</dd></template></dl>
          </section>
        </template>
      </template>

      <template v-if="tab === 'Architecture' && violations">
        <section v-for="(items, state) in violations" :key="state" class="panel">
          <div class="panel-heading"><h2 class="capitalize">{{ state }}</h2><span>{{ items.length }}</span></div>
          <details v-for="(item, index) in items" :key="index" class="evidence">
            <summary>{{ item.rule }} <span>{{ item.source }}{{ item.target ? ' → ' + item.target : '' }}</span></summary>
            <ol><li v-for="(edge, i) in item.evidence" :key="i">{{ edge.path }}:{{ edge.line }} · {{ edge.confidence }}</li></ol>
          </details>
        </section>
      </template>

      <template v-if="tab === 'Benchmarks' && benchmark">
        <section class="panel">
          <div class="panel-heading"><h2>Median indexing time</h2><span>{{ benchmark.repository.split('/').slice(-2).join('/') }}</span></div>
          <BenchmarkChart :benchmark="benchmark" />
          <table><thead><tr><th>Strategy</th><th>Files parsed</th><th>Files resolved</th><th>Peak traced memory</th></tr></thead>
            <tbody><tr v-for="(record, name) in benchmark.index" :key="name">
              <td>{{ name }}</td><td>{{ record.parsed_files }}</td><td>{{ record.resolved_files }}</td><td>{{ (record.peak_traced_bytes / 1024 / 1024).toFixed(1) }} MiB</td>
            </tr></tbody></table>
        </section>
      </template>
    </main>
  </div>
</template>
