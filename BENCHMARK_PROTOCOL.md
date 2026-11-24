# 实验协议

## 固定输入

项目为 [pallets/click 8.1.8](https://github.com/pallets/click/tree/8.1.8)。基线为 `c23223b13c847ae472faa258907ffb5c27b504fa`，发布版本为 `934813e4d421071a1b3db3973c02fe2721359a6e`。人工标注、变异锚点与目标重命名在 [数据清单](benchmarks/ground_truth/click-8.1.8.json)。

## 执行步骤

```powershell
git clone --depth 2 --branch 8.1.8 https://github.com/pallets/click.git .benchmark/click-full
docker build -f infra/runner.Dockerfile -t repoguard-runner:0.1 .
python benchmarks/run_click.py .benchmark/click-full --repeats 3
python scripts/profile_index.py .benchmark/click-full
python -m pip install -e ".[verify]"
python scripts/verify_contracts.py
```

| 实验 | 基准与独立标签 | 度量 |
|---|---|---|
| A 符号定位 | 阅读 Click 定义与引用，比较文本匹配、AST 名称、作用域解析 | 位置 precision、recall、F1，调用未解析边比例，查询耗时 |
| B 增量索引 | 相同提交重新建立完整索引，对照仅文件复用和依赖失效策略 | 三次耗时中位数、另一次 tracemalloc 峰值、重算范围、语义一致性 |
| C 变更影响 | 人工确认格式化调用入口，与独立全量测试捕获的失败文件合并 | 影响文件 precision、recall、F1、recall@10，原始漏报与误报 |
| D 测试选择 | 发布版本收集覆盖率，变异版本独立执行全量测试生成失败集合 | 失败召回、实际收集比例、耗时、加速比、漏测和回退 |
| E 重构验证 | 人工点名两个代码位置，比较文本、LibCST 名称匹配与符号感知 | 位置命中、漏改误改、独立回归结果及耗时 |

`run_click.py` 在单独临时克隆创建受控提交。数据量、Python、CPU、工作线程、容器镜像 ID 和结果保存在 JSON。B 排除新版本发布事务，计入基线 SQLite 反序列化。原始实验 JSON 保留节点 ID、选择依据、实际失败和回退原因。单仓库少量样本支持复现和差异定位，统计推广需要更多仓库和变更。 [逐用例覆盖上下文](artifacts/click-baseline-coverage.json.gz)
