# Git 对象和版本

基于实际源码。

## 学习目标与原理

从提交树定位文件和对象，不依赖当前工作区。 tree 记录路径与对象 ID，blob 提供原始内容。Git 状态与 Blob 内容可以分别验证。

## 源码、函数与调用

Indexer 调用 inventory 与 blobs，Git 通过只读子进程访问对象。 [inventory · src/repoguard/repository.py:107](../../src/repoguard/repository.py#L107-L131)

- [第 111 行](../../src/repoguard/repository.py#L111) 中的 `for record in self.git("ls-tree", "-r", "-l", "-z", commit).split(b"\0"):`。从 Git 提交枚举以 NUL 分隔的记录。
- [第 130 行](../../src/repoguard/repository.py#L130) 中的 `files[path] = File(path, oid, length, mode, status)`。生成包含对象元数据和初始状态的文件记录。

## 数据结构、复杂度与选型

File 按路径保存 oid、模式、大小和状态。 树扫描 O(F+路径字节)，批读取 O(B)。 选 Git 原始对象确保可复现并避免导入目标代码。

## Debug 与对应验证

在 `inventory` 下断点，观察 `path、entry status、max_bytes`。[test_tracked_source_from_commit_and_diagnostics](../../tests/integration/test_index_and_impact.py#L121)

## 独立练习

修改工作区中已提交函数，重查原提交并对照跳过项。

## 面试追问

如何区分 Git 文件模式是链接、常规文件还是子模块？

## 验收标准

能重现原提交定义和变更后的工作区差异。
