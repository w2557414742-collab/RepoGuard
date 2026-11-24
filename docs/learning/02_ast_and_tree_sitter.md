# AST 与增量语法解析

## 前置知识

理解 AST、词法偏移以及内容摘要。

## 模块职责、输入与输出

parse 接收 Git 文件和原始字节并输出 File 与 Unit。Collector 访问 CPython AST。 [源码](../../src/repoguard/parser.py)。

## 算法、数据结构与成本

解析前识别源编码，转换 UTF-8 字节列偏移，编译检查作用域合法性。语法收集成本随文件规模增长。

## 验证、工程边界与练习

构造 latin-1 源码和无效 nonlocal。查阅上游研究的 Tree-sitter 节点重用机制。当前增量粒度为文件。 [测试或实测证据](../../tests/unit/test_parser.py)。

## 面试题

支持树级增量必须提供旧树和哪些位置信息？
