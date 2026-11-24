# 补丁的静态预审

基于实际源码。

## 学习目标与原理

验证路径、提交上下文、语法与 API 变化。 将统一 diff 应用到内存中的旧 blob，重新解析变化文件并观察未解析调用。

## 源码、函数与调用

CLI 和 MCP 通过 RepoGuard.validate_patch 到预检。 [validate_patch · src/repoguard/verification.py:137](../../src/repoguard/verification.py#L137-L209)

- [第 148 行](../../src/repoguard/verification.py#L148) 中的 `for old, new, hunks in patch_entries(patch):`。先解析并校验文件头与区间。
- [第 161 行](../../src/repoguard/verification.py#L161) 中的 `content = apply_hunks(source, hunks)`。用原始提交内容匹配上下文。
- [第 172 行](../../src/repoguard/verification.py#L172) 中的 `parsed, unit = parse(record, content, repo.id, roots)`。将内存中的新文件重新解析。

## 数据结构、复杂度与选型

PatchValidation 保存检查状态和诊断。 读取补丁和变更字节，再重建关系以形成对照。 边界优先于便利，禁止越界和无法映射的上下文。

## Debug 与对应验证

在 `validate_patch` 下断点，观察 `changed、content、old_contracts`。[test_move_module_preserves_local_import_names](../../tests/integration/test_refactoring.py#L67)

## 独立练习

篡改 hunk 上下文或用 ../ 路径，观察具体失败阶段。

## 面试追问

静态验证通过后仍会有哪些回归风险？

## 验收标准

定位一次路径/上下文拒绝，另解释运行行为为何仍需回归。
