# 影响传播与风险排序

基于实际源码。

## 学习目标与原理

解释消费方、路径与风险如何从双版本图生成。 旧图找被删符号的依赖方，新图找变更后的关系。风险按跳数、边权重和置信衰减。

## 源码、函数与调用

SDK 调 changes 和 analyze，再由 API 或 CLI 格式化。 [analyze · src/repoguard/impact.py:177](../../src/repoguard/impact.py#L177-L276)

- [第 196 行](../../src/repoguard/impact.py#L196) 中的 `changes = classify(base, target, files)`。产生可定位的变化记录。
- [第 214 行](../../src/repoguard/impact.py#L214) 中的 `paths = graph.walk(`。从变化种子向调用及依赖方传播。
- [第 231 行](../../src/repoguard/impact.py#L231) 中的 `score = risk_step(score, WEIGHTS.get(edge.kind, 0.6), uncertain)`。逐边累加距离与置信效果。

## 数据结构、复杂度与选型

SymbolChange、Finding、ImpactReport 保存双侧证据。 两次构图加有界反向 BFS 与结果排序。 用可追溯路径表达风险，而非给出模型概率。

## Debug 与对应验证

在 `analyze` 下断点，观察 `seeds、paths、findings`。[test_impact_evidence_and_hybrid_fallback](../../tests/integration/test_index_and_impact.py#L72)

## 独立练习

删除一个被间接调用的函数，画出旧版本证据。

## 面试追问

最短 BFS 见证是否总有最高折扣后风险？

## 验收标准

呈现路径组件、置信度、风险及可能漏报。
