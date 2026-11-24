# 面试源码串讲

基于实际源码。

## 学习目标与原理

用一个真实示例串联索引、图、测试、静态验证和发布。 基线和目标分离，风险、回退与实验数据可沿源码追溯。

## 源码、函数与调用

SDK 入口读版本、生成差异、叠加可选覆盖后交给 analyze。 [analyze_change_impact · src/repoguard/sdk.py:107](../../src/repoguard/sdk.py#L107-L125)

- [第 117 行](../../src/repoguard/sdk.py#L117) 中的 `old, new = self.view(base), self.view(target)`。从固定提交取已发布视图。
- [第 118 行](../../src/repoguard/sdk.py#L118) 中的 `files = self.repository.changes(`。读取两版本 Git 变更。
- [第 125 行](../../src/repoguard/sdk.py#L125) 中的 `return analyze(old.snapshot, new.snapshot, files, depth=depth, base_coverage_edges=edges)`。把双侧事实与可选覆盖边交给核心影响分析。

## 数据结构、复杂度与选型

固定提交的 Snapshot、FileChange、Edge 和 ImpactReport。 能够分别分析 Git 扫描、图构建和有界遍历；实测结果依样本与缓存。 主张证据范围内的结论，展示一个有效场景和一个退化场景。

## Debug 与对应验证

在 `analyze_change_impact` 下断点，观察 `old、new、files、edges`。[test_impact_evidence_and_hybrid_fallback](../../tests/integration/test_index_and_impact.py#L72)

## 独立练习

以 Click 的新旧提交讲解增量与全量耗时，再用自己的示例解释回退。

## 面试追问

索引快了但漏掉一条边时如何定位根因，如何展示修复证据？

## 验收标准

能口述五个源码入口、一个实测数值和一个明确局限。
