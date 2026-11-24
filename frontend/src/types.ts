export interface SymbolRecord {
  id: string
  qualified_name: string
  name: string
  path: string
  kind: string
  line: number
  end_line: number
  signature: string
}

export interface Edge {
  source: string
  target: string
  kind: string
  path: string
  line: number
  confidence: string
  expression: string
}

export interface Hit { symbol: SymbolRecord; score: number; method: string; evidence: Edge[] }
export interface FileRecord { path: string; lines: number }
export interface Snapshot {
  files: FileRecord[]
  metadata: {
    target_commit: string
    python_lines: number
    symbols: number
    edges: number
    test_symbols: number
    file_status: Record<string, number>
  }
}
export interface GraphNode { id: string; symbol: SymbolRecord | null; path: string; kind: string; evidence: Edge[] }
export interface GraphResult { nodes: GraphNode[]; truncated: boolean }
export interface FileChange {
  status: string
  old_path: string | null
  new_path: string | null
  old_ranges: [number, number][]
  new_ranges: [number, number][]
}
export interface Impact {
  changes: { kind: string; path: string; before: SymbolRecord | null; after: SymbolRecord | null; public_api: boolean }[]
  files: FileChange[]
  impacts: { symbol: SymbolRecord; risk: number; classification: string; confidence: string; evidence: Edge[] }[]
  fallback_reasons: string[]
}
export interface Selection { run_all: boolean; reasons: string[]; tests: string[]; evidence: Record<string, string[]> }
export interface RefactorPlan { blockers: string[]; patch: string; checks: Record<string, string>; api_change: string }
export interface Violation { rule: string; source: string; target: string; evidence: Edge[] }
export interface Benchmark { repository: string; base: string; target: string; index: Record<string, {
  median_seconds: number; parsed_files: number; resolved_files: number; peak_traced_bytes: number;
}> }
