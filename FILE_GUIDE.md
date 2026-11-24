# 核心文件导航

| 文件 | 主要入口 | 上游与下游 |
|---|---|---|
| [repository.py](src/repoguard/repository.py) | `Repository.commit/inventory/blobs/changes` | UI 与 SDK 最终读 Git 对象。索引和影响分析共享文件清单。 |
| [model.py](src/repoguard/model.py) | `Unit`、`Symbol`、`Scope`、`Edge`、`Snapshot` | 分析、存储与传输共用的数据模型。 |
| [parser.py](src/repoguard/parser.py) | `parse`、`Collector` | 从 Git blob 提取定义和引用位置，交给链接器。 |
| [resolution.py](src/repoguard/resolution.py) | `Catalog`、`Resolver.lookup/imported/resolve` | 读取 `Unit`，生成可信边和依赖探测集合。 |
| [indexer.py](src/repoguard/indexer.py) | `IndexOptions`、`Indexer.index` | 比较 Git 清单，选择重新解析或链接的文件，发布版本。 |
| [store.py](src/repoguard/store.py) | `Store.save/load` | SQLite 原子保存和按版本恢复文件、语法事实与边。 |
| [graph.py](src/repoguard/graph.py) | `CodeGraph.adjacent/walk/cycles` | NetworkX 投影用于邻接、BFS、SCC 和影响分析。 |
| [retrieval.py](src/repoguard/retrieval.py) | `Search.exact/bm25/hybrid`、`reciprocal_rank` | 读取符号元数据和可选图，从 SDK 输出带证据的命中。 |
| [impact.py](src/repoguard/impact.py) | `classify`、`analyze`、`markdown` | 双版本变化分类、证据与风险传播，供报告和测试选择。 |
| [test_selection.py](src/repoguard/test_selection.py) | `select`、`CoverageMap.evidence_edges` | 根据变化及覆盖归因建议测试范围。 |
| [pytest_coverage.py](src/repoguard/pytest_coverage.py) | `pytest_runtest_protocol`、`pytest_sessionfinish` | 容器内切换覆盖上下文并落盘测试回执。 |
| [sandbox.py](src/repoguard/sandbox.py) | `run_tests`、`bounded_exchange` | 发送 Git 快照及测试节点到 Docker，限制输入、输出及运行资源。 |
| [refactoring.py](src/repoguard/refactoring.py) | `plan`、`Rewrite`、`unified_patch` | 使用 LibCST 改写可信引用位置，重建语义事实并比较。 |
| [import_migration.py](src/repoguard/import_migration.py) | `plan_module_move` | 在普通 Python 模块移动时更新 Git 路径和导入。 |
| [verification.py](src/repoguard/verification.py) | `patch_entries`、`apply_hunks`、`validate_patch` | 读固定 blob，在内存校验外部或生成的 Python 补丁。 |
| [architecture.py](src/repoguard/architecture.py) | `load_rules`、`evaluate`、`compare` | 对两个快照做模块前缀、耦合和循环规则差分。 |
| [sdk.py](src/repoguard/sdk.py) | `RepoGuard`、`View` | 三个接口的共同入口，固定快照并委派算法。 |
| [cli.py](src/repoguard/cli.py) | `main`、`dispatch` | argparse 参数转换及 JSON、Markdown 序列化。 |
| [api.py](src/repoguard/api.py) | `create_app` | 在 HTTP 路由上承接索引和查询，限制写索引入口。 |
| [mcp_server.py](src/repoguard/mcp_server.py) | `create_server` | 发布固定快照的 stdio MCP 工具和结构化结果。 |
| [App.vue](frontend/src/App.vue) | Vue 工作台及 API 绑定 | 从本地服务读取符号、浏览图和补丁。 |
| [run_click.py](benchmarks/run_click.py) | `measure_index`、`evaluate_tests`、`evaluate_rename` | 对冻结公开提交运行独立对照，保存实验结果。 |

精确签名和当前行号见 [FUNCTION_REFERENCE.md](FUNCTION_REFERENCE.md)。
