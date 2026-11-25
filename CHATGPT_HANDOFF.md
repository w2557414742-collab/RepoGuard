# ChatGPT 源码审查交接

## 审查对象

RepoGuard — Repository-Level Change Impact Analysis & Verified Refactoring Platform

大型代码仓库变更影响分析与验证式自动重构平台。

- 私有仓库的默认分支为 `main`。本轮归档前，已核对通过托管 CI 的源码基线 `289874102a6c515b429148679e0ecaee022bce8c`，首次发布提交 `36e31b3f1574f925245bc08b2212ed948eda03b4` 保留在历史中。 [GitHub 私有仓库](https://github.com/w2557414742-collab/RepoGuard) [源码基线](https://github.com/w2557414742-collab/RepoGuard/tree/289874102a6c515b429148679e0ecaee022bce8c) [发布状态](GITHUB_PUBLISH_REPORT.md)
- 无法使用 GitHub 连接器时，可上传 `RepoGuard-source.zip` 审查。以 ZIP 注释中的 Git SHA 固定审查版本，从归档根目录的 `RepoGuard/CHATGPT_HANDOFF.md` 开始阅读。归档包含全部跟踪的源码、测试、课程和实验材料。 [文件清单](PROJECT_TREE.txt)
- 目录包括 `src/repoguard`、`tests`、`frontend`、`infra`、`benchmarks`、`configs`、`scripts`、`artifacts` 和 `docs`。 [实际目录树](PROJECT_TREE.txt)
- 先读 [README](README.md)，再看 [架构](ARCHITECTURE.md)、[文件入口](FILE_GUIDE.md)、[函数索引](FUNCTION_REFERENCE.md)、[调用关系](CALL_FLOW.md)。按 [28 节课程](docs/learning/00_project_overview.md) 从 Git 固定提交、AST 和作用域学到回归与部署。

## 核心能力与证据

1. `repository → parser → resolution → indexer/store` 将固定 Git 对象变成 SQLite 快照。跨文件解析保留置信度和未命中依赖。 [增量设计](INCREMENTAL_INDEXING_DESIGN.md)
2. `graph/retrieval/impact` 提供多重图、BM25/RRF、反向证据及风险排序。 [影响设计](IMPACT_ANALYSIS_DESIGN.md)
3. `test_selection/pytest_coverage/sandbox` 将变化映射到用例。回退和 Docker 隔离明确记录。 [测试影响](TEST_IMPACT_DESIGN.md)
4. `refactoring/import_migration/verification` 形成在内存验证的 LibCST 补丁。 [重构设计](REFACTORING_DESIGN.md)
5. `sdk/cli/api/mcp_server` 和 Vue 工作台提供真实入口。SWE-RepairLab 的项目联动还未实现，已有通用 SDK、HTTP 和 MCP 接口。 [能力矩阵](PROJECT_STATUS.md)

## 测试与基准

本地 pytest 20 项通过，Ruff、依赖检查、HTTP 冒烟和前端构建通过。Mypy 34 项诊断及 Bandit 5 项中等级、43 项低等级发现仍待处理。GitHub 托管 CI 的 Python 3.11、Python 3.13 和 frontend 均通过。Click 8.1.8 的两组全量与增量索引逐项一致。在该变体实验中，覆盖策略收集 627 个用例，覆盖独立全量执行所发现的全部 50 个失败，全量共收集 650 个用例。 [测试记录](TEST_REPORT.md) [实验结果](EXPERIMENT_REPORT.md) [基线托管 CI](https://github.com/w2557414742-collab/RepoGuard/actions/runs/45423996129)

## 待解决的工程问题

- SQLite 基线反序列化和整版写入增加内存与耗时。跨版本去重和按需读取须另测。
- 动态分派与反射缺少完整类型、CFG 和数据流。未知外部关系会扩大回退。
- 当前语法增量只复用文件级事实。Tree-sitter、正文切块、学习式嵌入、FAISS 和 Reranker 未实现。
- Docker fixture 与子进程覆盖的归因不完整。单仓库统计缺少跨仓库推广证据。
- 扩展前清理类型诊断，建立跨仓库基线。随后评估将分析接口接入 SWE-RepairLab 的项目协调流程。 [失败与局限](FAILURE_ANALYSIS.md) [后续计划](HANDOFF.md)
