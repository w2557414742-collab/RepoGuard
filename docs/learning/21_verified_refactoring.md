# 验证式重构计划

基于实际源码。

## 学习目标与原理

解释重构前提、检查与阻塞状态。 仅在索引证明的引用位置形成结构化变换，并比较修改后的静态关系。

## 源码、函数与调用

RepoGuard.plan_refactoring 调 plan，产出 Plan 和 unified diff。 [plan · src/repoguard/refactoring.py:225](../../src/repoguard/refactoring.py#L225-L401)

- [第 351 行](../../src/repoguard/refactoring.py#L351) 中的 `rewritten = MetadataWrapper(cst.parse_module(source)).visit(transform).code`。在 CST 上挂接位置元数据再改写。
- [第 386 行](../../src/repoguard/refactoring.py#L386) 中的 `catalog = Catalog(updated_units)`。从修改后的语法事实重建解析目录。
- [第 391 行](../../src/repoguard/refactoring.py#L391) 中的 `expected = semantic_counts(symbols, before_edges, renamed)`。按身份与边种类对照确定关系。

## 数据结构、复杂度与选型

Plan 保存位置、补丁、检查和阻塞原因。 主要成本是 CST 变换和整个语义目录重建。 保守阻塞动态引用和有歧义的调用，回归单独执行。

## Debug 与对应验证

在 `plan` 下断点，观察 `blockers、updated_units、expected`。[test_signature_uses_only_explicit_values_and_flags_unpacked_calls](../../tests/integration/test_refactoring.py#L42)

## 独立练习

给调用添加 **kwargs，比较正常与阻塞的计划收据。

## 面试追问

签名变化时如何避免猜测参数值？

## 验收标准

补丁能被预检，阻塞案例不产生可自动应用的补丁。
