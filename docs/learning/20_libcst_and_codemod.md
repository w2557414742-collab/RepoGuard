# LibCST 结构化重写

基于实际源码。

## 学习目标与原理

理解完整语法树与坐标感知的名称修改。 AST 判断语义引用目标，CST 保持格式与注释并修改对应位置。

## 源码、函数与调用

plan 创建 Rewrite，LibCST 在遍历退出名称时调用 leave_Name。 [leave_Name · src/repoguard/refactoring.py:66](../../src/repoguard/refactoring.py#L66-L75)

- [第 71 行](../../src/repoguard/refactoring.py#L71) 中的 `and (position := self.position(original_node)) in self.positions`。把 CST 节点映射到解析出的源码坐标。
- [第 73 行](../../src/repoguard/refactoring.py#L73) 中的 `self.changed.add(position)`。记录实际改写位置。
- [第 74 行](../../src/repoguard/refactoring.py#L74) 中的 `return updated_node.with_changes(value=self.name)`。生成保留原节点结构的新节点。

## 数据结构、复杂度与选型

原节点、已更新节点、坐标集合和实际变更记录。 访问与 CST 节点数近似成正比，位置匹配使用集合。 避免全局文本替换导致同名符号误改。

## Debug 与对应验证

在 `leave_Name` 下断点，观察 `original_node、position、self.changed`。[test_rename_preserves_comments_and_aliases](../../tests/integration/test_refactoring.py#L7)

## 独立练习

添加同名局部函数与注释，比较文本替换和 CST 计划。

## 面试追问

为什么生成补丁时还需要重新验证 AST 事实？

## 验收标准

保留注释、别名与 CRLF，并用测试验证外部计划。
