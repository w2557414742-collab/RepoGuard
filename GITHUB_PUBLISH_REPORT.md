# GitHub 私有仓库发布登记

## 正式发布验收

| 验收项 | 2026-11-24 状态 |
|---|---|
| GitHub 仓库 | [w2557414742-collab/RepoGuard](https://github.com/w2557414742-collab/RepoGuard) |
| 所属账号与权限 | `w2557414742-collab`，已核实登录身份及仓库管理、推送权限 |
| 可见性 | Private，创建后和首次推送后由 GitHub API 确认 |
| 默认分支与远程 | `main`，本地 `main` 跟踪 `origin/main` |
| 首次发布提交 | `36e31b3f1574f925245bc08b2212ed948eda03b4`，首次推送后核对本地与远程 SHA 一致 |
| 文件完整性 | 165 个路径、文件模式和对象 SHA 全部匹配。本地及 GitHub 树为 `cb0055c3eec5903839d11d9bef6df73fec9457a6`，已确认 GitHub 识别根 [README](https://github.com/w2557414742-collab/RepoGuard/blob/main/README.md) |
| 首次 GitHub Actions | 成功，Python 3.11、Python 3.13 和 frontend 全部通过。[运行 45422632193](https://github.com/w2557414742-collab/RepoGuard/actions/runs/45422632193) |
| 密钥与敏感内容 | 首次推送前 Gitleaks 扫描两个可达提交，零发现。165 文件的清单已审查，依赖环境、第三方克隆和完整 SQLite 索引保留在本地。[安全审计](SECURITY_AUDIT.md) |
| ChatGPT 连接器 | 远程仓库已建立，连接器的仓库访问授权待核实 |

## 核验与持续发布

发布前精确查询仓库返回 404，随后创建空的 Private 仓库。推送前读取远端分支清单，确认仓库为空。首次推送使用普通 Git 推送，保留两个原有提交。接入代理后的 GitHub CLI 连接出现 TLS 中断，账户及远端元数据核验使用同一 CLI 凭据库和用户指定代理访问 GitHub 官方 HTTPS API。

本文件记录已完成验收的源码基线与首轮 CI。后续仅交接文档的提交会产生独立 SHA 和 Actions 运行，实时结果见 [main 分支](https://github.com/w2557414742-collab/RepoGuard/commits/main/) 与 [main 的 Actions 记录](https://github.com/w2557414742-collab/RepoGuard/actions?query=branch%3Amain)。提交新的交接文档后，应核对远端引用和文件树，并保留此前运行链接。

已知检查结果仍包括 Mypy 34 项诊断及 Bandit 5 项中等级、43 项低等级发现。本轮发布保留现有分析算法和实验数据。 [测试报告](TEST_REPORT.md)

仓库所有者可在 ChatGPT 的 GitHub 连接器中选择此私有仓库并授予所需访问范围。源码审查应明确指定目标提交。 [ChatGPT GitHub 连接器说明](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt)
