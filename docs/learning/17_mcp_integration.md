# SDK 与 MCP 集成

## 前置知识

了解 JSON-RPC、stdio 和结构化输出。

## 模块职责、输入与输出

create_server 固定已发布快照，提供定义、引用、调用、影响、计划与补丁预检。FastAPI 使用同一 SDK。 [源码](../../src/repoguard/mcp_server.py)。

## 算法、数据结构与成本

标准 MCP SDK 管理协议。每个读操作的主成本由相应分析或图查询决定。Graph 输出对节点数和深度设预算。

## 验证、工程边界与练习

用 MCP 客户端执行 initialize、list_tools 和 find_definition。检查结构化字段与提交。 [测试或实测证据](../../tests/e2e/test_transports.py)。

## 面试题

适配工具怎样避免混用两个提交版本并保持动态执行权限分离？
