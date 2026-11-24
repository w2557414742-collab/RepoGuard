# Docker 与本地部署

基于实际源码。

## 学习目标与原理

区分 API 容器、前端容器和短生命周期目标沙箱。 API 挂载只读 Git，客户端只访问本地转发。测试沙箱从 stdin 解包并执行。

## 源码、函数与调用

compose.yml 启动 API/Web。sandbox.run_tests 单独启动 runner_entry。 [main · infra/runner_entry.py:15](../../infra/runner_entry.py#L15-L44)

- [第 16 行](../../infra/runner_entry.py#L16) 中的 `request = json.loads(sys.stdin.buffer.readline(1024 * 1024 + 1))`。解析输入的执行请求。
- [第 17 行](../../infra/runner_entry.py#L17) 中的 `extract()`。只解包指定的 Git 档案。
- [第 41 行](../../infra/runner_entry.py#L41) 中的 `result = subprocess.run(args, cwd="/work", env=env, check=False)`。在沙箱内执行 pytest。

## 数据结构、复杂度与选型

提交 tar、受限 tmpfs、选择器 JSON、结果回执。 构建时间依赖镜像层，测试受 CPU、内存及输出预算。 只让 Nginx 暴露本机端口，目标代码在另一个无网容器。

## Debug 与对应验证

在 `main` 下断点，观察 `request、PYTEST_DISABLE_PLUGIN_AUTOLOAD、result`。[test_runner_captures_output_and_caps_excessive_streams](../../tests/unit/test_sandbox_io.py#L8)

## 独立练习

运行 smoke_http 并检查 /v1 文件请求和容器健康。

## 面试追问

API 和目标测试隔离时，哪个有权限接触只读 Git 对象？

## 验收标准

能同时展示 HTTP 健康和目标沙箱回执，并区分两者。
