# 环境审计

| 项目 | 实测环境或结论 |
|---|---|
| 宿主机 | Windows NT 10.0.19045，Intel64 Family 6 Model 183，20 个逻辑 CPU |
| Python 与 pip | 宿主 Python 3.13.5，项目工作区内独立 .venv。Docker API 与测试运行器使用 Python 3.12 |
| Git | 2.51.0.windows.1。开始时工作区为空，初始化 main 分支 |
| Node.js 与 npm | v24.15.0 和 11.12.1，Vue 通过 TypeScript 检查与生产构建 |
| Docker | Docker Desktop 28.3.2 Linux 引擎，Compose 2.38.2 |
| 网络与依赖 | GitHub、PyPI 和 npm 官方仓库的所需下载完成。工作区 npm 缓存用于隔离默认系统缓存权限问题 |
| 宿主执行限制 | 受限账户不能访问 Docker 命名管道。Docker 验证使用授权命令和独立 Linux 容器 |

Click 只从固定提交取源码。下载的上游项目、测试临时 Git 仓库和覆盖工作文件位于忽略目录。研究采用 Git 标签和源码 URL，见 [来源清单](../artifacts/source-provenance.json)。
