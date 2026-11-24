# 依赖感知增量索引

## 前置知识

理解缓存键、失效条件和事务。

## 模块职责、输入与输出

Indexer.index 接收基线、目标提交和对照模式，交给 Store 发布新 Snapshot。 [源码](../../src/repoguard/indexer.py)。

## 算法、数据结构与成本

Git 对象 ID 不变的文件复用语法事实。依赖足迹检测模块及动态成员的变化。基础目录组装和整版加载仍有 O(F+S+E) 成本。

## 验证、工程边界与练习

运行 Click 三种索引模式。确认移动或删除后的边集合与独立全量索引一致。 [测试或实测证据](../../tests/integration/test_index_and_impact.py)。

## 面试题

解析文件减少时，SQLite 基线读取如何掩盖收益？
