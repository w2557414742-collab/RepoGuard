# Git Diff 与双侧行映射

基于实际源码。

## 学习目标与原理

把文件级 Git 状态转成旧、新侧行区间。 先通过 Git 得到 A/M/D/R，再用 SequenceMatcher 计算变更操作。

## 源码、函数与调用

Repository.changes 触发文本比较，影响模块读取 FileChange。 [_changed_lines · src/repoguard/repository.py:194](../../src/repoguard/repository.py#L194-L230)

- [第 223 行](../../src/repoguard/repository.py#L223) 中的 `edits = difflib.SequenceMatcher(a=a, b=b, autojunk=True).get_opcodes()`。匹配旧文件和新文件的行块。
- [第 223 行](../../src/repoguard/repository.py#L223) 中的 `edits = difflib.SequenceMatcher(a=a, b=b, autojunk=True).get_opcodes()`。把修改、删除或插入转换成可遍历操作。

## 数据结构、复杂度与选型

FileChange 的旧路径、新路径和双侧闭区间。 SequenceMatcher 可能昂贵，代码按文件字节和行数乘积限制输入。 行号用于证据。符号差异也比较签名和哈希。

## Debug 与对应验证

在 `_changed_lines` 下断点，观察 `left、right、opcodes`。[test_impact_evidence_and_hybrid_fallback](../../tests/integration/test_index_and_impact.py#L72)

## 独立练习

构造插入、删除和文件重命名，确认哪一侧可能为空。

## 面试追问

为什么重命名可能被 Git 启发式映射为删除加新增？

## 验收标准

给出两侧位置与文件状态，不依赖当前 checkout。
