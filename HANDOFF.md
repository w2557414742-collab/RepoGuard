# 后续研发交接

## 当前入口

在仓库根目录使用 `.venv`。先运行 `python -m pytest -q` 和 `python -m ruff check .`。使用 [演示脚本](scripts/demo.ps1) 执行 Click 静态流程。使用 [实验协议](BENCHMARK_PROTOCOL.md) 复跑 Docker。当前索引格式为 3，Python 版本变化也会产生不同快照。

## 下一轮验收顺序

1. 扩大独立标签与故障集。增加至少一个 Flask 或 HTTPX 提交，在每个仓库为调用目标、影响集合和失败测试建立独立标签。先保存原始结果，再调整排序。
2. 优化 SQLite 基线读取和快照写放大。先基于现有 A–E 协议测量 I/O 消耗，再比较按文件加载及基线去重。修改版本语义时增加旧格式检测与并发发布测试。
3. 接入 Pyright 或 SCIP 外部对照，重点复核接收者类型、多个继承基类和重导出。将解析率、可能候选和精确命中分别评测。
4. 扩展测试与重构。加入子进程覆盖、会话共享 fixture 处理、通用独立 Git worktree 应用与类型检查。保持补丁默认预览，目标代码仅匿名容器执行。
5. 接入 PostgreSQL、Alembic 与 Redis 作业时，复用当前快照语义和协议 Schema。另评估本地代码模型、FAISS、托管 PR 和 SWE-RepairLab 的端到端集成。

项目状态见 [PROJECT_STATUS.md](PROJECT_STATUS.md)。不要用 Click 单样本统计替代多仓库延迟、失败召回或重构成功率。
