# Python 词法作用域

基于实际源码。

## 学习目标与原理

通过调用点理解绑定顺序、遮蔽与闭包。 查找从当前作用域上溯，需要考虑 global、nonlocal、类体及绑定生效行。

## 源码、函数与调用

Collector 保存 Binding 和 Scope，Resolver.lookup 输出候选给表达式解析。 [lookup · src/repoguard/resolution.py:151](../../src/repoguard/resolution.py#L151-L187)

- [第 159 行](../../src/repoguard/resolution.py#L159) 中的 `if name in scope.globals and scope.kind != "module":`。global 声明将查询转到模块。
- [第 165 行](../../src/repoguard/resolution.py#L165) 中的 `options = scope.bindings.get(name)`。读取该作用域的同名绑定。
- [第 181 行](../../src/repoguard/resolution.py#L181) 中的 `if "*" in scope.bindings or scope.parent is None:`。当前链未完成查找时继续上溯。

## 数据结构、复杂度与选型

作用域字典用名字定位绑定列表和父作用域。 基本查找随作用域深度和候选绑定数增长。 工程上保守处理控制流和运行时写入。

## Debug 与对应验证

在 `lookup` 下断点，观察 `scope.id、options、parent`。[test_scope_shadow_class_globals_and_comprehension](../../tests/unit/test_parser.py#L22)

## 独立练习

增加闭包内外同名函数和后置绑定，检查候选是否从一个变为多个。

## 面试追问

方法体为何跳过类体作用域？

## 验收标准

写出三个位置的预期目标并用实际测试确认。
