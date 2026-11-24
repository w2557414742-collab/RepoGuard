# 从 Git 提交到分析视图

基于实际源码。

## 学习目标与原理

识别仓库输入、分析事实、持久化版本和查询视图。 Git SHA 固定输入，符号与边经过两个阶段生成，SQLite 提供完整快照。

## 源码、函数与调用

CLI、API 或 MCP 通过 RepoGuard 进入 Indexer。发布后的 View 提供图与搜索。 [index · src/repoguard/indexer.py:64](../../src/repoguard/indexer.py#L64-L199)

- [第 80 行](../../src/repoguard/indexer.py#L80) 中的 `commit = self.repo.commit(target)`。将目标修订固定为完整提交 ID。
- [第 109 行](../../src/repoguard/indexer.py#L109) 中的 `catalog = Catalog(units)`。构建事实名录，为后续跨文件链接提供索引。
- [第 194 行](../../src/repoguard/indexer.py#L194) 中的 `if persist and not self.store.save(snapshot):`。通过存储写事务发布最终快照。

## 数据结构、复杂度与选型

Snapshot 包含文件、Unit、边、探测集合及元数据。 枚举 O(F)，解析成本取决于读取字节和节点，持久化取决于这一版的边。 AST 与 SQLite 足以复现当前 Python 路径。

## Debug 与对应验证

在 `index` 下断点，观察 `Store.load 的版本键、published`。[test_cli_roundtrip](../../tests/e2e/test_cli.py#L6)

## 独立练习

分别对同一 SHA 建立两个独立索引，比较两个数据集。

## 面试追问

为什么外部命名分支不适合作为索引主键？

## 验收标准

列出从 Git 对象到查询响应的三个边界并指出对应文件。

## 课程顺序

- [Git 对象和版本](01_repository_management.md)
- [CPython AST 和源码位置](02_python_ast.md)
- [Tree-sitter 树级增量规划](03_tree_sitter.md)
- [符号表和稳定 ID](04_symbol_table.md)
- [Python 词法作用域](05_scope_resolution.md)
- [跨文件导入与引用](06_cross_file_reference.md)
- [调用图精度与可信度](07_call_graph.md)
- [依赖多重图与循环](08_dependency_graph.md)
- [代码分块规划与现有符号文档](09_code_chunking.md)
- [BM25 词法检索](10_bm25.md)
- [代码嵌入规划](11_code_embedding.md)
- [FAISS 规划与现有混合查询](12_faiss_and_hybrid_search.md)
- [BFS、DFS 和 PageRank 对照](13_graph_algorithms.md)
- [Git Diff 与双侧行映射](14_git_diff_analysis.md)
- [影响传播与风险排序](15_change_impact_analysis.md)
- [增量索引的三路对照](16_incremental_indexing.md)
- [缓存失效与空探测](17_cache_invalidation.md)
- [混合测试选择](18_test_impact_analysis.md)
- [逐用例 Coverage 上下文](19_coverage_analysis.md)
- [LibCST 结构化重写](20_libcst_and_codemod.md)
- [验证式重构计划](21_verified_refactoring.md)
- [补丁的静态预审](22_static_analysis.md)
- [Docker 中复现回归](23_regression_validation.md)
- [基准与真值独立性](24_benchmark_evaluation.md)
- [SDK、FastAPI 与 MCP](25_api_sdk_and_mcp.md)
- [Docker 与本地部署](26_docker_deployment.md)
- [面试源码串讲](27_interview_preparation.md)
