# 基准与真值独立性

基于实际源码。

## 学习目标与原理

重现 Click 索引对照并区分加速与统计范围。 相同目标、固定配置复跑多次，比较符号和边一致性。测试失败用独立套件。

## 源码、函数与调用

run_click.main 编排 measure_index、evaluate_impact、evaluate_tests 和重构。 [measure_index · benchmarks/run_click.py:139](../../benchmarks/run_click.py#L139-L176)

- [第 141 行](../../benchmarks/run_click.py#L141) 中的 `reference = engine.indexer.index(target, mode="full", persist=False)`。独立全量快照作为语义参考。
- [第 151 行](../../benchmarks/run_click.py#L151) 中的 `tracemalloc.start()`。另一次运行统计 Python 分配峰值。
- [第 157 行](../../benchmarks/run_click.py#L157) 中的 `matches = {`。核对符号和关系等多项一致性。

## 数据结构、复杂度与选型

JSON 保留原始时间、内存峰值、重算范围和用例。 测量成本随模式、重复次数和被测工作量增长。 冻结真实仓库和手工标注，计时与内存单独采集。

## Debug 与对应验证

在 `measure_index` 下断点，观察 `reference、timings、matches`。[实际记录](../../artifacts/click-static.json)

## 独立练习

用训练样例增加一条带歧义的真实查询，记录失败率而不改变冻结基线。

## 面试追问

为什么只挑最快的一次会产生偏差？

## 验收标准

重新计算一次中位数和准确性结论，注明运行环境。
