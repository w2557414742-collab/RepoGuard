# 跨文件导入与引用

基于实际源码。

## 学习目标与原理

追踪相对导入、别名、重导出和空目标。 模块导出和子模块会生成不同候选。visited 和深度上限用于截断循环。

## 源码、函数与调用

Collector.visit_ImportFrom 记录事实，Resolver.imported 被表达式和模块成员解析复用。 [imported · src/repoguard/resolution.py:84](../../src/repoguard/resolution.py#L84-L114)

- [第 89 行](../../src/repoguard/resolution.py#L89) 中的 `if not module or name == "*" or (module, name) in seen or self._export_depth >= 60:`。同一对查询在递归链出现时停止。
- [第 91 行](../../src/repoguard/resolution.py#L91) 中的 `parents = self.modules(module)`。查找模块候选并记录探测。
- [第 110 行](../../src/repoguard/resolution.py#L110) 中的 `self.footprint.add(mutation_key(name))`。记录动态成员观察。

## 数据结构、复杂度与选型

Catalog、Candidate 和 footprint 连接符号与失效依赖。 耗时与已经遍历的候选和重导出链有关。 做词法可核实解析，根据条件和动态写入降低置信度。

## Debug 与对应验证

在 `imported` 下断点，观察 `module、name、seen、footprint`。[test_incremental_matches_full_and_resolves_former_miss](../../tests/integration/test_index_and_impact.py#L47)

## 独立练习

创建两层重导出和一个后添加的模块，比较三版引用。

## 面试追问

为什么未找到的模块也需要进入失效集合？

## 验收标准

候选状态与路径随新增目标正确变化。
