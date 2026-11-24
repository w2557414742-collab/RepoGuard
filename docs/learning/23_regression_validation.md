# Docker 中复现回归

基于实际源码。

## 学习目标与原理

隔离运行原版本、故障变体或重构变体并读回执。 发送固定提交归档与节点选择器，接收不可变镜像执行的用例结果。

## 源码、函数与调用

CLI 或 benchmark 明确执行 run_tests。目标源码和网络环境隔离。 [run_tests · src/repoguard/sandbox.py:97](../../src/repoguard/sandbox.py#L97-L246)

- [第 148 行](../../src/repoguard/sandbox.py#L148) 中的 `"--network=none",`。禁用容器网络。
- [第 166 行](../../src/repoguard/sandbox.py#L166) 中的 `execution = bounded_exchange(command, request + b"\n" + archive, timeout)`。限流输入输出并设置时间预算。

## 数据结构、复杂度与选型

TestRun 保存提交、镜像、耗时、失败和用例集合。 程序运行没有统一算法上界，使用时间、CPU、内存、输出、归档预算。 静态检查与动态测试分开，失败真值来自独立全量运行。

## Debug 与对应验证

在 `run_tests` 下断点，观察 `image_id、nodeids、result 回执`。[实际记录](../../artifacts/click-dynamic.json)

## 独立练习

比较干净与受控变体的失败 ID 和镜像 ID。

## 面试追问

通过当前测试集能否证明重构语义等价？

## 验收标准

能复查至少一个失败用例及原始收集数，并说明测试隔离。
