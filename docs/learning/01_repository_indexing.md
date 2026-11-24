# Git 快照与仓库索引

## 前置知识

掌握 Git tree 和 blob。

## 模块职责、输入与输出

Repository.inventory 接收提交并返回带路径、模式、大小和对象 ID 的文件。Repository.blobs 批量交给 Indexer。 [源码](../../src/repoguard/repository.py)。

## 算法、数据结构与成本

ls-tree 从提交枚举文件，cat-file 以包大小限制批读取。总成本为 O(F+B)，F 为树条目，B 为读取字节。

## 验证、工程边界与练习

添加一个被 .gitignore 排除的未跟踪文件和一个已提交的语法错误文件。对比文件清单和诊断。 [测试或实测证据](../../tests/integration/test_index_and_impact.py)。

## 面试题

为何 Git 对象输入能防止工作区中的符号版本漂移？
