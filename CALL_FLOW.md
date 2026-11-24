# 实际调用流程

下图表示源码中可追踪的直接调用或数据流。SDK、CLI、HTTP 与 MCP 相互独立，分析复用同一 SDK 和底层模块。

## 仓库读取

```mermaid
flowchart LR
    A[RepoGuard] --> B[Repository.commit]
    B --> C[Repository.inventory]
    C --> D[Repository.blobs]
    D --> E[Repository._batch]
    E --> F[Git objects]
```

## AST、符号表与代码关系图

```mermaid
flowchart LR
    Blob --> parse
    parse --> Collector
    Collector --> Unit
    Unit --> Catalog
    Catalog --> R[Resolver.resolve]
    R --> Snapshot
    Snapshot --> CodeGraph
```

## 混合检索

```mermaid
flowchart LR
    View --> H[Search.hybrid]
    H --> E[Search.exact]
    H --> B[Search.bm25]
    H --> G[CodeGraph.walk]
    E --> R[reciprocal_rank]
    B --> R
    G --> R
    R --> Hit
```

## Git 差异与影响

```mermaid
flowchart LR
    A[RepoGuard.analyze_change_impact] --> B[Repository.changes]
    A --> C[analyze]
    B --> C
    C --> D[classify base and target]
    C --> E[Reverse CodeGraph.walk]
    D --> E
    E --> F[risk_step]
    F --> G[ImpactReport]
```

## 增量索引

```mermaid
flowchart LR
    I[Indexer.index] --> L[Store.load baseline]
    I --> N[Repository.inventory]
    L --> C[Compare file identities]
    N --> C
    C --> P[Parse changed files]
    P --> F[Build catalog and invalidation keys]
    L --> F
    F --> R[Resolve affected files]
    F --> U[Reuse unaffected edges]
    R --> S[Store.save]
    U --> S
```

## 测试选择

```mermaid
flowchart LR
    I[ImpactReport] --> S[select]
    B[Base CoverageMap] --> S
    T[Target Snapshot] --> S
    S --> R[Selection and fallback reasons]
    R -. explicit execution .-> D[sandbox.run_tests]
```

## 结构化重构

```mermaid
flowchart LR
    S[SDK plan_refactoring] --> P[refactoring.plan]
    P --> R[Resolve evidenced locations]
    R --> C[LibCST Rewrite]
    C --> E[Reparse and compare semantic_counts]
    E --> U[unified_patch]
```

## Patch 预检与回归

```mermaid
flowchart LR
    A[validate_patch] --> B[patch_entries]
    B --> C[apply_hunks against fixed blob]
    C --> D[parse changed unit]
    D --> E[Compare API signatures and call uncertainty]
    E --> F[PatchValidation]
    F -. separate explicit workflow .-> G[Docker pytest]
```

Tree-sitter、向量阶段、PageRank 与通用 Worktree 应用属于待实现范围。SQLite 初始化、提交和查询边界见 [索引设计](INDEX_DESIGN.md)。
