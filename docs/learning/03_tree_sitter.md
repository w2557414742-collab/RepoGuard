# Tree-sitter 树级增量规划

未来规划 · NOT_IMPLEMENTED。

## 学习目标与原理

区分文件级复用和可编辑语法树的增量更新。 Tree-sitter 的旧树重用需要编辑的字节范围与点坐标。规划中的后端需做全量/增量事实对照。

## 源码、函数与调用

当前 Indexer 调用 CPython parse。未来扩展点在文件解析输入与 Unit 输出之间。 [parse · src/repoguard/parser.py:40](../../src/repoguard/parser.py#L40-L68)

- [第 57 行](../../src/repoguard/parser.py#L57) 中的 `tree = ast.parse(text, filename=file.path)`。当前入口使用 CPython。
- [第 61 行](../../src/repoguard/parser.py#L61) 中的 `collector.visit(tree)`。两种实现将来必须给出等价的可消费事实。

## 数据结构、复杂度与选型

已有 Unit 持久化语法事实。未来还需旧树、编辑描述和解析器版本。 现有文件级以重解析字节计。树级复杂度依语法、编辑和重用而变，实测待开展。 保留现有 Python 事实契约，先对齐差异再替换后端。

## Debug 与对应验证

在 `parse` 下断点，观察 `ast.parse、Unit 输出`。[test_encoding_binary_and_compiler_diagnostics](../../tests/unit/test_parser.py#L12)

## 独立练习

在独立实验中比较旧树复用和全量树，再把两者投影到相同事实 schema。

## 面试追问

改动包头时旧树的偏移如何同步？

## 验收标准

能明确指出仓库中的现行入口和未来所缺的编辑、旧树与同等性测试。
