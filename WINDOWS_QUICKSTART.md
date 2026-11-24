# Windows 快速启动

需要 PowerShell、Git 及支持的 Python 解释器。当前工作区使用 Python 3.13.5。可用虚拟环境解释器直接运行，省去更改 PowerShell 执行策略。

```powershell
Set-Location D:/ai-project/RepoGuard
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,refactor,architecture,testing,api,mcp]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

在新工作区下载冻结的公开 Click 实验输入。存在可读的本地副本时直接复用。

```powershell
git clone --depth 2 --branch 8.1.8 https://github.com/pallets/click.git .benchmark/click-full
$rg = ".\.venv\Scripts\repoguard.exe"
& $rg --repo .benchmark/click-full index --base HEAD~1 --target HEAD
& $rg --repo .benchmark/click-full search click.formatting.iter_rows
& $rg --repo .benchmark/click-full impact HEAD~1 HEAD --format markdown
& $rg --repo .benchmark/click-full select-tests HEAD~1 HEAD
& $rg --repo .benchmark/click-full plan click.formatting.iter_rows aligned_rows
```

要运行目标 pytest，先从能访问 Linux Docker Engine 的终端构建运行器。依靠沙箱测试实际仓库。

```powershell
docker build -f infra/runner.Dockerfile -t repoguard-runner:0.1 .
& $rg --repo .benchmark/click-full run-tests --image repoguard-runner:0.1
docker compose up --build -d --wait
.\.venv\Scripts\python.exe scripts/smoke_http.py
```

Compose 的默认入口为 [RepoGuard Explorer](http://127.0.0.1:8080)。用 `.env.example` 配置实验仓库位置、分支、端口和网络。发布准备与实际运行记录见 [TEST_REPORT.md](TEST_REPORT.md)。
