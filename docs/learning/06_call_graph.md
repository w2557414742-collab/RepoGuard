# 静态调用图

## 前置知识

了解动态分派、别名和候选集合。

## 模块职责、输入与输出

Collector.visit_Call 保存表达式和位置，Resolver.edge_for 生成 CALLS 边。SDK 的 get_callers 读取反向边。 [源码](../../src/repoguard/resolution.py)。

## 算法、数据结构与成本

逐步解析限定成员，接收者及装饰器调用可降级。成本取决于候选集合和继承路径深度。

## 验证、工程边界与练习

对已知函数加入模块属性动态写入，检查调用边降级，以及增量结果和全量结果是否相等。 [测试或实测证据](../../tests/integration/test_index_and_impact.py)。

## 面试题

为什么确定的语法名字可能对应多个运行时函数？
