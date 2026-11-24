# ChatGPT 源码审查交接

## 审查对象

RepoGuard — Repository-Level Change Impact Analysis & Verified Refactoring Platform

大型代码仓库变更影响分析与验证式自动重构平台。

- GitHub 地址待建立。当前分支为 `main`，尚无 Git 提交。此文件描述 2026-11-24 审计后的本地发布候选，远端版需以核实的完整 SHA 指定。 [发布状态](GITHUB_PUBLISH_REPORT.md)
- 目录包括 `src/repoguard`、`tests`、`frontend`、`infra`、`benchmarks`、`configs`、`scripts`、`artifacts` 和 `docs`。 [实际目录树](PROJECT_TREE.txt)
- 先读 [README](README.md)，再看 [架构](ARCHITECTURE.md)、[文件入口](FILE_GUIDE.md)、[函数索引](FUNCTION_REFERENCE.md)、[调用关系](CALL_FLOW.md)。按 [28 节课程](docs/learning/00_project_overview.md) 从 Git 固定提交、AST 和作用域学到回归与部署。

## 核心能力与证据

1. `repository → parser → resolution → indexer/store` 将固定 Git 对象变成 SQLite 快照。跨文件解析保留置信度和未命中依赖。 [增量设计](INCREMENTAL_INDEXING_DESIGN.md)
2. `graph/retrieval/impact` 提供多重图、BM25/RRF、反向证据及风险排序。 [影响设计](IMPACT_ANALYSIS_DESIGN.md)
3. `test_selection/pytest_coverage/sandbox` 将变化映射到用例。回退和 Docker 隔离明确记录。 [测试影响](TEST_IMPACT_DESIGN.md)
4. `refactoring/import_migration/verification` 形成在内存验证的 LibCST 补丁。 [重构设计](REFACTORING_DESIGN.md)
5. `sdk/cli/api/mcp_server` 和 Vue 工作台提供真实入口。SWE-RepairLab 的项目联动还未实现，已有通用 SDK、HTTP 和 MCP 接口。 [能力矩阵](PROJECT_STATUS.md)

## 测试与基准

本轮运行了项目 pytest、Ruff、Mypy、Bandit、依赖检查、端到端传输、前端构建和 Click Docker 对照。分别记录通过、发现、退出码和运行限制。Click 8.1.8 与固定父提交的索引，以及受控格式化变异和实际补丁对照均已测量。 [测试记录](TEST_REPORT.md) [实验与复现](BENCHMARK_PROTOCOL.md)

## 待解决的工程问题

- SQLite 基线反序列化和整版写入增加内存与耗时。跨版本去重和按需读取须另测。
- 动态分派与反射缺少完整类型、CFG 和数据流。未知外部关系会扩大回退。
- 当前语法增量只复用文件级事实。Tree-sitter、正文切块、学习式嵌入、FAISS 和 Reranker 未实现。
- Docker fixture 与子进程覆盖的归因不完整。单仓库统计缺少跨仓库推广证据。
- 扩展前清理类型诊断，建立跨仓库基线。随后评估将分析接口接入 SWE-RepairLab 的项目协调流程。 [失败与局限](FAILURE_ANALYSIS.md) [后续计划](HANDOFF.md)
