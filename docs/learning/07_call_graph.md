# 调用图精度与可信度

基于实际源码。

## 学习目标与原理

区分静态调用、可能边和没有目标的引用。 限定名及词法绑定产生候选，对象动态分派受限于现有事实。

## 源码、函数与调用

Collector.visit_Call 产生 Usage，edge_for 输出图边。 [edge_for · src/repoguard/resolution.py:242](../../src/repoguard/resolution.py#L242-L296)

- [第 251 行](../../src/repoguard/resolution.py#L251) 中的 `if kind == EdgeType.CALLS:`。对调用使用相应关系种类与候选过滤。
- [第 269 行](../../src/repoguard/resolution.py#L269) 中的 `if not candidates:`。为空时显式保存未解析关系。
- [第 291 行](../../src/repoguard/resolution.py#L291) 中的 `Confidence.POSSIBLE if uncertain or len(candidates) > 1 else Confidence.RESOLVED,`。多个或不确定的候选降低可信度。

## 数据结构、复杂度与选型

Edge 有源、目标、表达式、行号和 Confidence。 成本为候选过滤和排序。 保留未解析边用于影响和回退，不假定所有调用目标。

## Debug 与对应验证

在 `edge_for` 下断点，观察 `use.kind、values、candidates`。[test_reference_resolution_and_graph](../../tests/integration/test_index_and_impact.py#L22)

## 独立练习

加入模糊导入或运行时赋值，观察解出的边是否降级。

## 面试追问

为什么语法调用位置已知仍无法给出运行时目标？

## 验收标准

三种置信度都能从样本定位，不能把可能边计作确定命中。
