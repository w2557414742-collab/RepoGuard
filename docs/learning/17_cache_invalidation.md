# 缓存失效与空探测

基于实际源码。

## 学习目标与原理

说明命名空间、动态成员与未命中变化怎样影响索引。 失效键由变化路径、命名空间差集和动态成员差集生成。

## 源码、函数与调用

Indexer.index 用 _changed_modules 与 Resolver.footprint 比较。 [_changed_modules · src/repoguard/indexer.py:212](../../src/repoguard/indexer.py#L212-L236)

- [第 227 行](../../src/repoguard/indexer.py#L227) 中的 `old_namespaces = {`。收集基线中的命名空间前缀。
- [第 233 行](../../src/repoguard/indexer.py#L233) 中的 `mutation_key(name)`。为动态成员写入生成专用失效键。

## 数据结构、复杂度与选型

模块名、命名空间前缀及 mutation_key 的集合。 集合成本随受影响路径和已记录查询数变化。 保留负探测，允许先前缺少的定义在新增后解析。

## Debug 与对应验证

在 `_changed_modules` 下断点，观察 `changed、old_namespaces、changed_members`。[test_runtime_binding_changes_invalidate_dependent_confidence](../../tests/integration/test_index_and_impact.py#L164)

## 独立练习

新增一个同名类动态写入，确认调用置信度在增量和全量下相同。

## 面试追问

为什么只缓存已解析边不足以做跨文件增量？

## 验收标准

给出一个正探测和一个负探测的失效例子。
