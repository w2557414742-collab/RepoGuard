# 测试影响设计

`RepoGuard.select_related_tests` 加载固定基线和目标。`select` 输出用例节点、依据、回退原因和 `run_all`。CLI 的建议与实际执行分离，可用 `run-tests` 显式运行已选择的节点或全量测试。

| 模式 | 主要依据 |
|---|---|
| `file` | 改动的测试文件与可识别测试定义。 |
| `static` | 改动测试文件、反向影响图及目标符号。 |
| `coverage` | 同提交同环境的历史用例行覆盖，与变更范围及影响模块匹配。 |
| `hybrid` | 综合静态及覆盖依据。配置变化、不确定关系、缺失或过期覆盖会触发全量回退。 |

Coverage.py 在 pytest 用例协议入口切换上下文，在结束处汇总 `nodeid → 路径 → 行`。单独标记集合阶段、共享 fixture 和子进程限制造成的覆盖缺口。提交和镜像环境不匹配时，覆盖策略不能把记录当成当前证据。

实际选测试与失败召回应独立度量。Click 基准先在变体上运行全量套件取得 50 个失败，再衡量各选择策略。 [测试选择源码](src/repoguard/test_selection.py) [覆盖插件](src/repoguard/pytest_coverage.py) [对照结果](EXPERIMENT_REPORT.md)
