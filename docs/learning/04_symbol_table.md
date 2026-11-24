# 符号表和稳定 ID

基于实际源码。

## 学习目标与原理

能推导同名符号 ID，并区分作用域与源码位置。 符号身份包含仓库、路径、作用域、名字、种类和重复出现序号。

## 源码、函数与调用

Collector.add_symbol 写 Unit.symbols，Catalog 与 Resolver 以 ID 建边。 [add_symbol · src/repoguard/parser.py:107](../../src/repoguard/parser.py#L107-L145)

- [第 120 行](../../src/repoguard/parser.py#L120) 中的 `ordinal = self.counts.get(key, 0)`。同名定义使用稳定序号。
- [第 122 行](../../src/repoguard/parser.py#L122) 中的 `sid = identity(self.repo, self.path, *key, str(ordinal))`。派生仓库范围内的符号 ID。
- [第 123 行](../../src/repoguard/parser.py#L123) 中的 `parent = self.symbols[self.scope.owner]`。写入符号目录。

## 数据结构、复杂度与选型

Symbol 同时保存身份、父符号、内容摘要和坐标。 单次散列随身份串与定义文本增长，目录 O(S)。 行号保留为查询证据，身份按定义结构构造。

## Debug 与对应验证

在 `add_symbol` 下断点，观察 `key、ordinal、parent.id`。[test_reference_resolution_and_graph](../../tests/integration/test_index_and_impact.py#L22)

## 独立练习

在同一个作用域插入同名定义，再单独插空行，对照符号 ID。

## 面试追问

重命名或文件移动后为何需要重新解析身份？

## 验收标准

能解释两种修改中哪一组 ID 可能变化。
