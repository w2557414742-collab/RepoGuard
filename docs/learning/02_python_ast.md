# CPython AST 和源码位置

基于实际源码。

## 学习目标与原理

解释解析、编译检查、文件诊断和 AST 访问。 AST 抽取语法树和位置。Python AST 的列偏移采用 UTF-8 字节数。

## 源码、函数与调用

Indexer._parse_entry 调用 parse，随后访问 Collector。 [parse · src/repoguard/parser.py:40](../../src/repoguard/parser.py#L40-L68)

- [第 57 行](../../src/repoguard/parser.py#L57) 中的 `tree = ast.parse(text, filename=file.path)`。将源码转为 AST。
- [第 59 行](../../src/repoguard/parser.py#L59) 中的 `compile(tree, file.path, "exec", dont_inherit=True)`。校验可编译性，丢弃字节码结果。
- [第 61 行](../../src/repoguard/parser.py#L61) 中的 `collector.visit(tree)`。遍历 AST 并构建 Unit。

## 数据结构、复杂度与选型

输入原字节，输出 File 和可选 Unit。 时间 O(B+AST 节点)，保留语法树与收集事实。 使用 tokenize 处理编码和 AST 访问器处理 Python 结构。

## Debug 与对应验证

在 `parse` 下断点，观察 `encoding、tree、collector.unit`。[test_encoding_binary_and_compiler_diagnostics](../../tests/unit/test_parser.py#L12)

## 独立练习

建立 Latin-1 文件、混合 Unicode 和错误 nonlocal 样本。

## 面试追问

为什么 ast.parse 成功仍可能需要 compile 检查？

## 验收标准

报告解析状态和准确的 Unicode 源码位置，未执行模块。
