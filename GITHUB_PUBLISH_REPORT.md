# GitHub 私有仓库发布登记

## 当前实际状态

| 验收项 | 2026-11-24 状态 |
|---|---|
| 本地仓库 | 已初始化，路径为当前 RepoGuard 工作区 |
| 当前分支 | `main`，尚无首个提交 |
| 本地最新 SHA | 暂无。未产生可供远端核对的 commit |
| 工作区 | 自有源码、测试、文档和实验工件为发布候选。索引数据库、缓存、环境和第三方克隆已被忽略 |
| 远程仓库 | 未配置远程 |
| 所属账号与 URL | BLOCKED，等待 GitHub CLI 登录并确认账号及目标仓库 |
| 私有可见性、默认分支和推送 SHA | NOT_RUN |
| GitHub 展示、文件完整性、远端 CI 与安全扫描 | NOT_RUN |
| 本地安全审计 | 见 [SECURITY_AUDIT.md](SECURITY_AUDIT.md) |
| ChatGPT 已连接私有仓库 | BLOCKED，等待有效仓库及用户授权 |

## 用户本人完成登录

本环境未找到 GitHub CLI，无法确认当前 GitHub 登录状态。Windows 支持以下安装方式。重开终端后由用户完成浏览器登录。

```powershell
winget install --id GitHub.cli --exact --source winget
gh --version
gh auth login --hostname github.com --web --git-protocol https
gh auth status --hostname github.com
gh api user --jq .login
```

如果没有 WinGet，可从官方发行页安装 MSI。浏览器登录由账户持有人自行完成。 [GitHub CLI 安装包](https://github.com/cli/cli/releases/latest) [登录手册](https://cli.github.com/manual/gh_auth_login)

## 授权后执行的发布命令

先确认授权的 GitHub 账号和新建或复用的私有仓库。检查已有仓库的身份和可见性。仓库已存在时，读取分支和提交历史后再决定如何接入。以下命令用于已确认的新仓库，当前记录尚未执行。

```powershell
Set-Location D:/ai-project/RepoGuard
git status --short --branch
git remote -v
git ls-files -ci --exclude-standard
git add -- .
git diff --cached --check
git diff --cached --name-status
$scanner = ".\.benchmark\release-tools\gitleaks.exe"
& $scanner git . --staged --redact=100
if ($LASTEXITCODE -ne 0) { throw "Review the staged secret scan before committing" }
git commit -m "Prepare RepoGuard source and release evidence"
& $scanner git . --log-opts=--all --redact=100
if ($LASTEXITCODE -ne 0) { throw "Review the history secret scan before pushing" }
gh auth setup-git
$owner = gh api user --jq .login
gh repo create "$owner/RepoGuard" --private --source . --remote origin
gh repo view "$owner/RepoGuard" --json url,owner,visibility
# 确认 visibility 为 PRIVATE、账号正确并且 origin 与目标一致后再推送。
git push -u origin main
```

推送后比较本地和远端引用，检查 README、锁文件、测试、教程、LICENSE 和 THIRD_PARTY_NOTICES。待 GitHub CI 有实际运行后记录结果。

```powershell
$actual = git rev-parse HEAD
git ls-remote origin refs/heads/main
gh repo view --json url,owner,visibility,defaultBranchRef
gh run list --branch main --commit $actual --limit 5
git status --short --branch
```

获得访问授权后可在 ChatGPT 的 GitHub 连接器中选择该私有仓库，交付审查时记录固定 SHA。 [GitHub CLI 创建仓库](https://cli.github.com/manual/gh_repo_create) [ChatGPT GitHub 连接器说明](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt)
