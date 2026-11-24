# 混合测试选择

基于实际源码。

## 学习目标与原理

切换文件、静态、覆盖和混合选择并解释回退。 把变化文件、图影响和覆盖记录映射到 pytest nodeid。

## 源码、函数与调用

SDK 将 ImpactReport、Snapshot 和可选覆盖交给 select。 [select · src/repoguard/test_selection.py:89](../../src/repoguard/test_selection.py#L89-L160)

- [第 102 行](../../src/repoguard/test_selection.py#L102) 中的 `if mode not in {"file", "static", "coverage", "hybrid"}:`。限制可解释的四条选择路径。
- [第 128 行](../../src/repoguard/test_selection.py#L128) 中的 `elif coverage.commit != report.base:`。覆盖记录需与历史基线提交匹配。
- [第 154 行](../../src/repoguard/test_selection.py#L154) 中的 `return Selection(`。将选择范围与回退建议显式交给调用方。

## 数据结构、复杂度与选型

Selection 持有候选、依据、run_all 和原因。 按覆盖用例和行范围工作，行交集成本受变更区间数影响。 不确定性保守回退，失败召回使用独立全量测试判断。

## Debug 与对应验证

在 `select` 下断点，观察 `mode、reasons、coverage.environment`。[test_impact_evidence_and_hybrid_fallback](../../tests/integration/test_index_and_impact.py#L72)

## 独立练习

用错误环境 ID 导入同一份覆盖，验证不会把旧覆盖当作新证据。

## 面试追问

为什么多选测试与降低遗漏风险不是同一项指标？

## 验收标准

报告模式、覆盖新旧、实际候选以及执行全量的条件。
