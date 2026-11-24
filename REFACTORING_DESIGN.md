# 验证式重构设计

[refactoring.py](src/repoguard/refactoring.py) 将已解析位置与 LibCST 节点绑定，按符号 ID 重命名模块级函数或类。`signature` 添加必填的仅关键字参数，实参取用户传入的 Python 字面量。对参数展开、同名绑定、动态歧义、装饰器和不完整索引报告阻塞。未按位置匹配到的修改同样阻塞。

[import_migration.py](src/repoguard/import_migration.py) 支持完整普通模块移动，更新 `import`、`from import` 和已解析的限定引用，保留使用方的显式别名。目标模块路径须可表示为 `.py` 源文件。跨包且无别名的限定导入、混合的 `from` 导入及通配符场景会阻塞。

计划在内存生成统一差异，重新解析改动文件并重建解析边。通过映射前后符号名称和路径检查已解析边计数。预检 [verification.py](src/repoguard/verification.py) 还接受独立补丁，检查提交上下文、语法、引入的未解析调用和公共签名变化。类型检查和运行测试在计划中分项显示。Click 重构实验只对独立克隆执行补丁和回归测试。

补丁默认供审查。模块成员方法、拆分部分导出、跨语言和任意签名迁移留待后续。回归覆盖特定环境中的行为和用例。
