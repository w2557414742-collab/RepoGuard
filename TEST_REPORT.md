# 验收测试报告

验收日期为 2026-11-24。宿主测试使用 Windows 和 Python 3.13.5。Linux Docker 镜像运行 Python 3.12。

| 验收项 | 观察结果 |
|---|---|
| 项目 pytest | 20 个通过，12.97 秒。覆盖编码、作用域、导入重导出、图与循环、增量一致性、并发发布、覆盖映射、架构、补丁和路径校验 |
| CLI 与协议 | CLI 双版本索引、定义和 Markdown 影响验收。MCP 客户端实际完成 stdio 握手、工具枚举和结构化调用 |
| 质量与包 | Ruff 检查和格式校验通过，pip check 通过，Python wheel 构建成功 |
| 发布快照 | Windows SQLite 本地保存 Click 基线和目标共两个快照，共 66,404 条持久化关系，SQLite quick_check 返回 ok |
| Click Docker | 650 个测试用例被收集。628 个通过、21 个跳过、1 个预期失败。最终限流执行器复跑得到同样的收集数与覆盖上下文数 |
| 前端 | Vue TypeScript 检查和生产构建通过。2026-11-24 的 npm audit 报告 0 项已知告警 |
| Compose | API 和 Web 容器启动并正常提供服务。部署探测使用真实 Click 数据查询符号、源码、依赖、Git 差异、测试选择、架构、补丁和评测结果 |
| 浏览器 | 从搜索定位 Click 函数，确认 Monaco 源码和依赖图渲染，预览重命名补丁，查看真实 Git 变化和实验图表 |

本地验收入口包括 [CLI 测试](tests/e2e/test_cli.py)、[协议测试](tests/e2e/test_transports.py) 和 [HTTP 冒烟脚本](scripts/smoke_http.py)。Click 测试与基准的原始结果见 [动态记录](artifacts/click-dynamic.json)。CI 配置包含 Python 3.11 的测试矩阵，当前报告的宿主实测版本为 Python 3.13.5。

## GitHub 发布准备复验

针对教学化及发布清单做了第二次实际复验。Windows Python 3.13.5，Docker 28.3.2。运行命令、退出码和输出保存在 [release-checks](artifacts/release-checks/)。

| 检查 | 本轮结果 | 运行证据 |
|---|---|---|
| pytest | 20 个通过。覆盖 CLI、API、MCP、作用域、图、增量一致性、并发、重构和路径边界 | [pytest.log](artifacts/release-checks/pytest.log) |
| Ruff | 退出码 0 | [ruff.log](artifacts/release-checks/ruff.log) |
| Mypy 2.4.1 | 退出码 1，21 个源码文件中 11 个有诊断，共 34 项，含两个外部 stub 缺失 | [mypy.log](artifacts/release-checks/mypy.log) |
| Bandit 1.9.4 | 退出码 1，5 个中等级、43 个低等级，0 个高等级 | [分项记录](artifacts/release-checks/bandit.json) |
| pip check | 通过，无损坏依赖 | [pip-check.log](artifacts/release-checks/pip-check.log) |
| CLI Help 与 HTTP 接口 | 通过。实际 HTTP 命中 Click 快照、符号、依赖、差异、测试、补丁与评测 | [CLI](artifacts/release-checks/cli-help.log) [HTTP](artifacts/release-checks/http.log) |
| 前端生产构建 | 通过 TypeScript 检查及 Vite 构建。Monaco 分块尺寸有警告 | [frontend-build.log](artifacts/release-checks/frontend-build.log) |
| Docstring 行为核对 | 添加 129 处中文说明。21 个核心模块去掉 Docstring 后的 AST 与原版逐项一致 | [运行收据](artifacts/release-checks/results.json) |
| Click Docker 与回归 | 650 个用例，628 通过、21 跳过、1 个预期失败。独立变体捕获 50 个失败，三种改名方案对照复跑 | [Click 复跑](artifacts/release-checks/click-rerun.json) |
| GitHub 托管 CI | NOT_RUN，远程仓库尚未创建 | [发布报告](GITHUB_PUBLISH_REPORT.md) |

Mypy 和 Bandit 的发现单列，运行测试没有因此计为失败。GitHub 私有发布需完成用户登录与授权。 [安全审计](SECURITY_AUDIT.md)
