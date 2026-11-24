# 逐用例 Coverage 上下文

基于实际源码。

## 学习目标与原理

识别 pytest 用例、集合和共享 fixture 的覆盖边界。 Coverage.py 在 pytest 协议期间以 nodeid 标记执行，结束时切回空上下文。

## 源码、函数与调用

runner_entry 启动 pytest 插件，插件汇总给 CoverageMap。 [pytest_runtest_protocol · src/repoguard/pytest_coverage.py:43](../../src/repoguard/pytest_coverage.py#L43-L51)

- [第 46 行](../../src/repoguard/pytest_coverage.py#L46) 中的 `_coverage.switch_context(item.nodeid)`。进入用例时采用完整 pytest nodeid。
- [第 48 行](../../src/repoguard/pytest_coverage.py#L48) 中的 `return (yield)`。协议执行期间覆盖器保持该上下文。
- [第 51 行](../../src/repoguard/pytest_coverage.py#L51) 中的 `_coverage.switch_context("")`。结束后标为无当前用例。

## 数据结构、复杂度与选型

nodeid、路径、执行行，外加采集提交和镜像 ID。 采集随运行事件数增长，汇总随覆盖行上下文增长。 上下文方式也记录参数化节点，隔离环境由 Docker 控制。

## Debug 与对应验证

在 `pytest_runtest_protocol` 下断点，观察 `item.nodeid、_coverage`。[实际记录](../../artifacts/click-dynamic.json)

## 独立练习

解压基准 gzip 文件，比较两个有参数的 nodeid 的行集合。

## 面试追问

为何共享 fixture 的行可能只归到第一个用例？

## 验收标准

描述已知归因缺口，并验证映射不含源码正文。
