# SDK、FastAPI 与 MCP

基于实际源码。

## 学习目标与原理

追踪固定版本的结构化 transport 工具到 SDK。 共享 SDK 保持分析逻辑独立，stdio 协商和序列化由 MCP SDK 处理。

## 源码、函数与调用

MCP create_server 固定 View；FastAPI create_app 另作 HTTP 适配。 [create_server · src/repoguard/mcp_server.py:15](../../src/repoguard/mcp_server.py#L15-L84)

- [第 18 行](../../src/repoguard/mcp_server.py#L18) 中的 `view = engine.view(revision)`。绑定已发布的提交。
- [第 21 行](../../src/repoguard/mcp_server.py#L21) 中的 `@server.tool()`。把受控 SDK 能力注册成结构化工具。

## 数据结构、复杂度与选型

RepoGuard、View、dict 结构化响应。 传输层开销小于实际查询和图构建，用节点预算限制输出。 默认暴露读取、影响分析、补丁预览等审查操作。

## Debug 与对应验证

在 `create_server` 下断点，观察 `revision、view、structuredContent`。[test_mcp_stdio_protocol](../../tests/e2e/test_transports.py#L43)

## 独立练习

在实际客户端做 initialize、list_tools 和 find_definition，并核对提交。

## 面试追问

为什么仓库在索引后修改 HEAD 不应改变固定会话里的查询？

## 验收标准

真实 MCP 会话返回 symbol 结构数据，传输层可替换。
