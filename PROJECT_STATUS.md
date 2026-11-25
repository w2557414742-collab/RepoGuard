# RepoGuard 交付状态

截至 2026-11-24，主路径覆盖 Python Git 快照、索引和增量更新、图与影响报告、Docker 测试选择、LibCST 补丁和本地平台。可从 [README](README.md) 运行。环境、评测和复现分别记录在 [环境审计](docs/environment.md)、[实验报告](EXPERIMENT_REPORT.md) 与 [实验协议](BENCHMARK_PROTOCOL.md)。

2026-11-25 复核了私库权限、Git 历史、文件树和已有测试记录。本轮更新交付文档并从发布提交生成离线源码包。 [发布登记](GITHUB_PUBLISH_REPORT.md) [源码归档入口](CHATGPT_HANDOFF.md)

本地服务入口为 [RepoGuard Explorer](http://127.0.0.1:8080)。Click 的两个实际快照保存在当前工作区的 `.repoguard/click.sqlite`，文件以仓库路径及解释器版本定位。验收见 [测试报告](TEST_REPORT.md)。

| 阶段 | 已验证交付 | 下一步 |
|---|---|---|
| 0–1 索引基础 | 13 个上游项目源码取证、AST 编译诊断、Git 对象扫描、SQLite 快照及 CLI | 跨平台、更多真实仓库兼容验证 |
| 2 符号与代码图 | 局部和跨文件符号、保守继承、可信度、图查询与 SCC | Pyright / SCIP 独立对照、完整类型分派、CFG 与数据流 |
| 3 增量更新 | 文件和边的依赖失效、事务发布、两组真实仓库版本对照 | SQLite 跨版本去重、Tree-sitter 树级编辑与计量 |
| 4 影响分析 | 历史 Git 差异、符号分类、反向传播、风险及 Markdown 证据 | 分支合并基线策略、PR 提供商导入、传播预算评测 |
| 5 测试选择 | 文件、静态、覆盖和混合选择，离线 Docker 全量和选择实验 | 子进程覆盖、共享 fixture 归因、更多真实失败历史 |
| 6 重构与架构 | 函数与类重命名、普通模块移动、显式签名迁移、补丁预检和 YAML 规则 | 部分符号迁移、更多签名转换、自动类型检查、通用独立 Worktree 应用流程 |
| 7 基准 | Click 上实际完成 A–E 和两个变异，用独立回归结果校验 | 扩大实证数据规模，外部语义基线，授权后评估 LLM |
| 8 服务 | SQLite、Python SDK、FastAPI、MCP 1.x stdio、Vue、Docker Compose、CI 配置 | PostgreSQL/SQLAlchemy/Alembic、Redis 队列、SWE-RepairLab 流程验收 |
| 9 进阶验证 | Hypothesis、有限 CrossHair 契约、cProfile、原始报告和 19 份学习资料 | 变异矩阵及等价性分析、额外安全审计和更长性能基线 |

检索已实现符号、BM25、RRF 和图扩展。学习式代码嵌入与 FAISS 集成是独立待办。接手路径见 [HANDOFF.md](HANDOFF.md)。

## 发布前逐项复核

状态以源码与本轮实际运行确定。VERIFIED 表示本轮有可重现测试或运行证据。PARTIALLY_VERIFIED 表示实现覆盖了所列场景的子集，或有明确验证缺口。IMPLEMENTED 表示源码存在，当前缺少独立验收。NOT_RUN 表示对应检查尚未执行。BLOCKED 表示运行缺少前置条件。NOT_IMPLEMENTED 表示当前仓库缺少该能力。

| 范围 | 能力 | 状态 | 源码、验收和边界 |
|---|---|---|---|
| 仓库 | Git 对象读取、固定 SHA、文件内容 Hash | VERIFIED | `Repository.inventory/blobs` 与 `parse`。覆盖工作区和已提交内容不一致。 |
| 仓库 | Git Diff 与代码版本管理 | VERIFIED | `Repository.changes` 保留双侧路径和范围。SQLite 隔离提交与索引选项。 |
| 仓库 | 通用 Git Worktree 编排 | NOT_IMPLEMENTED | Click 对照使用临时独立克隆。 |
| 解析 | Python AST、函数/类/方法和 Symbol Table | VERIFIED | `Collector` 提取定义、位置、签名和作用域。 |
| 解析 | Scope、定义和引用、导入及跨文件解析 | VERIFIED | 单测与集成验证别名、重导出、同名、嵌套作用域、未命中失效和动态写入。 |
| 解析 | 完整 Python 类型与动态分派 | NOT_IMPLEMENTED | 解析带可信度，现阶段仅覆盖有静态证据的情形。 |
| 解析 | Tree-sitter、Java 或其他语言适配 | NOT_IMPLEMENTED | CPython AST 是当前解析入口。 |
| 关系 | Import、Call、Reference、Dependency、Inheritance | VERIFIED | `Resolver` 产出可定位关系，图对照含模块环和调用路径。 |
| 关系 | CFG、Data Flow | NOT_IMPLEMENTED | 图数据是静态定义、引用和依赖。 |
| 检索 | BM25、混合检索、RRF、图增强 | VERIFIED | 精确命中、词法和有界图融合，测试包括同名与 RRF 去重。 |
| 检索 | 正文向量分块、嵌入、FAISS、学习式 Reranker | NOT_IMPLEMENTED | 当前用符号名、签名和种类作检索文档。 |
| 影响 | 变更符号、跨文件传播、风险排序和证据链 | VERIFIED | 双版本反向传播覆盖调用与依赖方。 |
| 影响 | 任意双向传播的影响判定 | PARTIALLY_VERIFIED | 图查询支持上下游方向，影响算法使用反向图。 |
| 影响 | 不确定关系与未知依赖处理 | VERIFIED | `POSSIBLE/UNRESOLVED` 与混合测试回退有验证。 |
| 增量 | 变化检测、文件级增量、依赖失效、缓存一致性 | VERIFIED | 同提交全量与增量逐项一致，并发发布得到同一收据。 |
| 增量 | Tree-sitter 语法树内的增量编辑 | NOT_IMPLEMENTED | 当前复用粒度为文件及其关系。 |
| 测试 | pytest、Coverage.py、测试到代码映射 | VERIFIED | Click Docker 实际采集逐 pytest nodeid 数据，覆盖记录有提交和镜像标识。 |
| 测试 | 受影响测试选择、独立回归、保守回退 | VERIFIED | 四策略与独立全量对照。参数化和动态运行已覆盖。 |
| 测试 | 子进程完整覆盖及共享 fixture 精确归因 | NOT_IMPLEMENTED | 缺少信息会使混合路径触发全量回退。 |
| 重构 | LibCST、结构化 Codemod、函数重命名及跨文件引用 | VERIFIED | 支持明确的模块级目标，定位后改写，保留格式和注释。 |
| 重构 | 参数签名修改 | PARTIALLY_VERIFIED | 支持增加用户提供值的仅关键字参数。解包或无法证明的调用会阻塞。 |
| 重构 | 导入更新、模块迁移、Patch Generation | VERIFIED | 计划与补丁预检覆盖普通 Python 模块迁移和跨文件引用。 |
| 重构 | 静态预检和回归 | PARTIALLY_VERIFIED | 已验证上下文、语法、公开接口与静态引用。真实 Click 改名经过 Docker 回归。类型充分性和任意补丁的语义等价仍未知。 |
| 交付 | 架构规则、CLI、SDK、FastAPI、MCP stdio | VERIFIED | 真实传输端到端用例与 HTTP 探测。 |
| 交付 | Docker、Compose、Vue 工作台、自动化测试 | VERIFIED | 本地生产构建、HTTP 烟测、Click Docker 对照及项目测试。 |
| 交付 | GitHub Actions 配置与托管运行 | VERIFIED | 已发布源码基线触发的 Python 3.11、Python 3.13 和 frontend 三个作业全部成功。[实际运行](https://github.com/w2557414742-collab/RepoGuard/actions/runs/45422632193) |
| 交付 | PostgreSQL、Redis、数据库迁移体系 | NOT_IMPLEMENTED | SQLite DDL 随源码交付。 |
| 交付 | SWE-RepairLab 联动 | NOT_IMPLEMENTED | 现有 SDK、REST 和 MCP 可作为将来接入点。 |
| 发布 | GitHub 私有仓库与远端一致性 | VERIFIED | 现有仓库已恢复 Private，默认分支 `main`。复核时本地与远端基线的 SHA 一致，165 个文件均匹配。 [仓库](https://github.com/w2557414742-collab/RepoGuard) [验收记录](GITHUB_PUBLISH_REPORT.md) |
| 发布 | ChatGPT 私库连接 | BLOCKED | 当前连接器不可用，源码审查可用 ZIP 交接。 [离线审查入口](CHATGPT_HANDOFF.md) |

证据入口为 [源码索引](FUNCTION_REFERENCE.md)、[测试报告](TEST_REPORT.md)、[实验报告](EXPERIMENT_REPORT.md) 与 [发布登记](GITHUB_PUBLISH_REPORT.md)。
