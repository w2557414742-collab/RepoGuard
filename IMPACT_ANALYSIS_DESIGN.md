# 变更影响分析设计

[repository.py](src/repoguard/repository.py) 从 Git 映射增、删、修改和移动文件，并根据两侧内容计算有界行区间。[impact.py](src/repoguard/impact.py) 对双版本符号 ID、签名和内容摘要分类。删除和旧调用使用基线证据，新增和修改使用目标证据。非 Python 配置变化及分析缺失可触发全量测试回退。

有权重的反向 BFS 以变更符号和涉及模块为种子，同时考虑 `CALLS`、`REFERENCES`、`IMPORTS`、`DEPENDS_ON`、`INHERITS` 和 `OVERRIDES`。路径上每一步按边类型、距离和不确定性衰减。风险分是排序启发式。BFS 为每个符号选一个见证路径，双版本结果保留较高风险路径。

报告包含实现、签名、增删、模块移动、依赖、配置或未知变更，公共 API 标记，影响证据，相关循环和建议验证范围。配置如 import hook、入口点和动态加载可能超出静态图。影响排名的实际召回和误报见 [实验报告](EXPERIMENT_REPORT.md)。
