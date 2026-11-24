# 架构守卫

## 前置知识

理解模块边界、依赖方向和聚集度。

## 模块职责、输入与输出

load_rules 读取 YAML，evaluate 匹配模块边和 SCC，compare 返回引入、已有和消除的违规。 [源码](../../src/repoguard/architecture.py)。

## 算法、数据结构与成本

前缀比较按点分模块组件边界。每条规则扫描相关模块依赖边。循环规则另取有向投影。

## 验证、工程边界与练习

在 fixture 删除 app.other 导入，并核对违规证据路径及 resolved 分组。 [测试或实测证据](../../tests/integration/test_index_and_impact.py)。

## 面试题

如何用规范化键避免把行号移动当成架构回归？
