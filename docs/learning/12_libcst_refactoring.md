# LibCST 补丁与验证

## 前置知识

掌握保留格式的 CST、统一差异和信息不全时的停止条件。

## 模块职责、输入与输出

plan 接收符号 ID、操作、名称和可选字面量，返回 Plan。validate_patch 接收独立 diff 并预检提交上下文。 [源码](../../src/repoguard/refactoring.py)。

## 算法、数据结构与成本

按已解析位置更新 CST，重新构建受影响文件的事实并校验关系。开销主要来自 CST、占用图大小的重解析检查。

## 验证、工程边界与练习

比较 CRLF 与没有尾换行的补丁。为调用添加 **kwargs 并观察签名迁移被阻塞。 [测试或实测证据](../../tests/integration/test_refactoring.py)。

## 面试题

保持格式、引用一致性和语义等价分别需要什么证据？
