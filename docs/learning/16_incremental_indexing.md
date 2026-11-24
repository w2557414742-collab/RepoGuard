# 增量索引的三路对照

基于实际源码。

## 学习目标与原理

分辨 full、file 和 dependency 三种执行成本。 Git OID 不变即可复用语法事实，依赖模式还利用足迹复用边。

## 源码、函数与调用

Indexer 从基线和目标快照生成新版本，Store 处理发布。 [index · src/repoguard/indexer.py:64](../../src/repoguard/indexer.py#L64-L199)

- [第 93 行](../../src/repoguard/indexer.py#L93) 中的 `if old is not None and old.oid == current.oid and old.mode == current.mode:`。按路径和对象 ID 检查语法事实能否复用。
- [第 100 行](../../src/repoguard/indexer.py#L100) 中的 `entries = iter(zip(reparsed, self.repo.blobs(reparsed), strict=True))`。只读取将解析的文件体。
- [第 119 行](../../src/repoguard/indexer.py#L119) 中的 `and not previous.footprints[path] & changed_modules`。根据探测足迹决定能否复用旧关系。

## 数据结构、复杂度与选型

units、edges、footprints 按文件索引。 清单与目录构建仍是全局成本，另按实际失效量链接。 验证语义一致性后再解释时间改善，SQLite 全版读取可超过节省。

## Debug 与对应验证

在 `index` 下断点，观察 `old.oid、reparsed、resolved_paths`。[test_incremental_matches_full_and_resolves_former_miss](../../tests/integration/test_index_and_impact.py#L47)

## 独立练习

对同个目标提交做 full 与 dependency 比较，去掉运行时长字段再对照。

## 面试追问

额外读取旧缓存为什么可能让增量更慢？

## 验收标准

必须比较符号和边，不能只比较文件数量。
