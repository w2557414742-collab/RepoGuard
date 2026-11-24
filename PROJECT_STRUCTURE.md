# 项目结构

[PROJECT_TREE.txt](PROJECT_TREE.txt) 由 Git 可跟踪路径生成。树中包含发布候选文件，工作区缓存和第三方克隆的数量与体积记录在 [PACKAGE_AUDIT.md](PACKAGE_AUDIT.md)。

| 目录 | 职责、输入和输出 | 学习重点 |
|---|---|---|
| `src/repoguard` | 接受 Git 提交、选项与查询，产生 SQLite 快照、关系、影响报告和补丁。CLI、HTTP、SDK、MCP 在同一包中作为入口。 | 学习从 Git 对象到 `Unit`、`Edge` 与 `Snapshot` 的数据边界。 |
| `tests` | 临时 Git fixture、作用域单测、集成测试和传输端到端测试。 | 全量与增量一致性、命令行、路径保护、并发发布及补丁预检。 |
| `benchmarks` | 冻结的 Click 提交和人工标签、受控变体与对照驱动、CrossHair 契约。 | 独立失败真值、策略对照及实验范围。 |
| `artifacts` | 实际实验的 JSON、gzip 覆盖映射、影响报告、验证过的统一 diff 和发布验收摘要。 | 由结果追溯到输入和运行环境。 |
| `scripts` | 演示、性能剖析、源码导航生成、体积审计、契约验证与服务探测。 | 在低风险的只读路径复现项目流程。 |
| `infra` | API、Vue 镜像、Nginx 转发和 Git 测试沙箱。 | 服务部署与目标仓库执行的隔离边界。 |
| `frontend` | Vue/TypeScript 工作台。通过 `/v1/` 读取仓库、源码、图、差异、重构和基准。 | 从界面请求追踪到 HTTP 和 SDK，并检查图请求预算。 |
| `configs` | 受支持的架构规则样例。根目录另有 `.env.example`。 | 模块前缀和规则的解释方式。 |
| `docs` | 学习课程、上游源码研究与环境记录。 | 课程链接对应真实函数和测试。 |
| `.github` | Linux 上的 Python、MCP、Vue 构建和测试工作流。 | 依赖矩阵与部署入口的分工。 |

运行本地流程后会出现 `.venv`、`.repoguard`、`.benchmark`、缓存与构建目录。SQLite DDL 位于 [store.py](src/repoguard/store.py)，没有独立迁移目录。函数级索引见 [FUNCTION_REFERENCE.md](FUNCTION_REFERENCE.md)。
