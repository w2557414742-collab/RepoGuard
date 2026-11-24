# 测试影响与保守回退

## 前置知识

理解 pytest nodeid、fixture、Coverage.py 上下文。

## 模块职责、输入与输出

pytest_coverage 钩子记录覆盖，select 将历史用例与变更区间、影响模块和目标测试关联。 [源码](../../src/repoguard/test_selection.py)。

## 算法、数据结构与成本

按用例和路径匹配行区间。复杂度随覆盖映射条目数和区间数增长。输入包括提交、镜像环境和完整性状态。

## 验证、工程边界与练习

用匹配与不匹配的镜像 ID 调用选择器，然后对比 Click 变异完整失败集。共享 fixture、子进程仍有归因缺口。 [测试或实测证据](../../tests/integration/test_index_and_impact.py)。

## 面试题

为何历史覆盖不能单独充当选择器的准确率标签？
