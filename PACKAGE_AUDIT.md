# 体积与发布内容审计

按普通文件逻辑字节数统计当前工作区，包括 Git、环境、缓存和实验克隆。忽略重解析点、访问失败项及本报告自身。硬链接按路径计数。候选清单使用 Git 的跟踪和忽略规则。

- 本地合计 874,661,151 B (834.14 MiB)，文件 24,304。
- Git 已跟踪 0 个路径，现有文件 0 B (0.00 MiB)。
- 可提交内容 163 个文件，2,497,020 B (2.38 MiB)，本报告另计。
- 本地 refs 可达 blob 0 个，其中 ≥1 MiB 的对象 0 个。
- 跳过路径 0，重复计算额外不可读文件 0。
- 内容完全相同的重复组 976，按每组保留一份估算冗余 13,031,742 B (12.43 MiB)。

## 一级目录

| 目录 | 本地大小 |
|---|---:|
| `frontend` | 424,480,230 B (404.82 MiB) |
| `.venv` | 209,867,823 B (200.15 MiB) |
| `.benchmark` | 190,764,375 B (181.93 MiB) |
| `.repoguard` | 46,415,872 B (44.27 MiB) |
| `artifacts` | 1,917,923 B (1.83 MiB) |
| `src` | 469,975 B (0.45 MiB) |
| `build` | 157,829 B (0.15 MiB) |
| `tests` | 142,363 B (0.14 MiB) |
| `docs` | 66,387 B (0.06 MiB) |
| `dist` | 54,145 B (0.05 MiB) |
| `.hypothesis` | 44,132 B (0.04 MiB) |
| `scripts` | 37,734 B (0.04 MiB) |
| `.git` | 26,291 B (0.03 MiB) |
| `benchmarks` | 19,855 B (0.02 MiB) |
| `.ruff_cache` | 11,166 B (0.01 MiB) |
| `infra` | 3,106 B (0.00 MiB) |
| `.pytest_cache` | 2,272 B (0.00 MiB) |
| `.github` | 951 B (0.00 MiB) |
| `configs` | 262 B (0.00 MiB) |

## 最大的 30 个文件

| 路径 | 大小 |
|---|---:|
| `.repoguard/click.sqlite` | 46,415,872 B (44.27 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/1d/15/cd0379a7e5fe047f00102e1b79f6817b0f04df0862dcdd0e61f893fef29f0843a1e9511cebc9323802a7d5587f1cfbc3bc3bf7184f3fea42edb3104f5900` | 39,041,559 B (37.23 MiB) |
| `.venv/Scripts/ruff.exe` | 26,961,712 B (25.71 MiB) |
| `.benchmark/mvp.sqlite` | 22,949,888 B (21.89 MiB) |
| `.benchmark/release-tools/gitleaks.exe` | 22,575,104 B (21.53 MiB) |
| `.benchmark/release-tools/python/6ec57f84c680d3a3778b__mypyc.cp313-win_amd64.pyd` | 20,294,656 B (19.35 MiB) |
| `.venv/bin/z3.exe` | 18,488,320 B (17.63 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/18/44/1611999f90e18b75ddd72bcaf2adf5b3dc020ff18ca655788f1c475ec2b52aee6874aab2ab7c72cd09771b07ab139cc2e7399df3b5288a71c885524209c1` | 18,441,599 B (17.59 MiB) |
| `.venv/Lib/site-packages/z3/lib/libz3.dll` | 17,944,064 B (17.11 MiB) |
| `.benchmark/pip-cache/http-v2/b/d/3/3/6/bd33697e904e2aa1781067d4c0f1b675b0744334fbe59cb43a7021bd.body` | 17,113,449 B (16.32 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/d8/7d/8b1c882ccb72c0e8fd09e661b394afb98749ee9768bd0931f0d48acf80c9997591e0100c8f995555aafed75101d7d2dd673e318c2f41a2cb446dcdb92078` | 15,967,143 B (15.23 MiB) |
| `frontend/node_modules/monaco-editor/dev/vs/editor/editor.main.js.map` | 15,591,326 B (14.87 MiB) |
| `frontend/node_modules/monaco-editor/min-maps/vs/editor/editor.main.js.map` | 13,276,062 B (12.66 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/ab/4c/9a14f8200bd15476c587e1b95abd15859b176b22875b92828d02326e74023a080f6034fc47b55d917193447a9655964e32bc16243a46e4e87215a48c8764` | 12,178,508 B (11.61 MiB) |
| `frontend/node_modules/monaco-editor/dev/vs/language/typescript/tsWorker.js` | 11,597,448 B (11.06 MiB) |
| `.benchmark/pip-cache/http-v2/e/f/3/d/9/ef3d9dff883f4643535eb752ef5248e0fa01ad60fee925e33a271629.body` | 11,390,802 B (10.86 MiB) |
| `frontend/node_modules/monaco-editor/esm/vs/language/typescript/ts.worker.js` | 11,190,649 B (10.67 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/b4/6e/7aa4c4f934d6bd6e718cd85237d78a143273265cb12682eebf5f907de5b654a3c86034928b7a8cc513bebb89157e13c7a4eefce4b197b3c301522aedad07` | 11,183,996 B (10.67 MiB) |
| `frontend/node_modules/@esbuild/win32-x64/esbuild.exe` | 10,617,344 B (10.13 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/a1/36/d54ec5df2ae121c5fb47a8be71a6b80ba1cd24eee49c030b6bc8281617a84f6052d1c0e50788598718204a3f934f14d903568a4e89ec94a98187f056b790` | 10,432,423 B (9.95 MiB) |
| `.venv/Lib/site-packages/cryptography/hazmat/bindings/_rust.pyd` | 9,897,472 B (9.44 MiB) |
| `frontend/node_modules/monaco-editor/dev/vs/editor/editor.main.js` | 9,520,350 B (9.08 MiB) |
| `frontend/node_modules/typescript/lib/typescript.js` | 9,066,411 B (8.65 MiB) |
| `frontend/node_modules/echarts/dist/echarts.js.map` | 8,101,179 B (7.73 MiB) |
| `frontend/node_modules/echarts/dist/echarts.esm.mjs.map` | 8,101,111 B (7.73 MiB) |
| `frontend/node_modules/echarts/dist/echarts.esm.js.map` | 8,101,110 B (7.73 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/0f/c5/c6d536d81936bca8a69ef989ca1028684f021d6574aa22b67939e049272fe79d23c2a8a39615ed934df907fc5b5a6144b8ea1236e460e44b66c118b32c2a` | 6,766,845 B (6.45 MiB) |
| `frontend/node_modules/typescript/lib/_tsc.js` | 6,172,356 B (5.89 MiB) |
| `.venv/Lib/site-packages/pydantic_core/_pydantic_core.cp313-win_amd64.pyd` | 5,780,480 B (5.51 MiB) |
| `frontend/node_modules/monaco-editor/min/vs/language/typescript/tsWorker.js` | 5,749,518 B (5.48 MiB) |

## 最大的 20 个目录

| 路径 | 大小 |
|---|---:|
| `frontend` | 424,480,230 B (404.82 MiB) |
| `frontend/node_modules` | 233,620,168 B (222.80 MiB) |
| `.venv` | 209,867,823 B (200.15 MiB) |
| `.benchmark` | 190,764,375 B (181.93 MiB) |
| `frontend/.npm-cache` | 187,141,580 B (178.47 MiB) |
| `frontend/.npm-cache/_cacache` | 186,994,474 B (178.33 MiB) |
| `frontend/.npm-cache/_cacache/content-v2` | 186,801,419 B (178.15 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512` | 186,801,419 B (178.15 MiB) |
| `.venv/Lib` | 161,017,959 B (153.56 MiB) |
| `.venv/Lib/site-packages` | 161,017,959 B (153.56 MiB) |
| `.benchmark/release-tools` | 102,451,554 B (97.71 MiB) |
| `frontend/node_modules/monaco-editor` | 98,831,340 B (94.25 MiB) |
| `.benchmark/release-tools/python` | 60,900,028 B (58.08 MiB) |
| `frontend/node_modules/echarts` | 60,297,703 B (57.50 MiB) |
| `frontend/node_modules/echarts/dist` | 53,114,420 B (50.65 MiB) |
| `.repoguard` | 46,415,872 B (44.27 MiB) |
| `frontend/node_modules/monaco-editor/dev` | 44,692,876 B (42.62 MiB) |
| `frontend/node_modules/monaco-editor/dev/vs` | 44,362,694 B (42.31 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/1d` | 39,388,420 B (37.56 MiB) |
| `frontend/.npm-cache/_cacache/content-v2/sha512/1d/15` | 39,041,559 B (37.23 MiB) |

## 最大的 10 个可提交文件

| 路径 | 大小 |
|---|---:|
| `artifacts/click-dynamic.json` | 1,270,844 B (1.21 MiB) |
| `artifacts/click-mutant-impact.md` | 205,988 B (0.20 MiB) |
| `artifacts/click-release-impact.md` | 175,712 B (0.17 MiB) |
| `artifacts/click-static.json` | 162,570 B (0.16 MiB) |
| `FUNCTION_REFERENCE.md` | 100,003 B (0.10 MiB) |
| `frontend/package-lock.json` | 52,364 B (0.05 MiB) |
| `artifacts/click-baseline-coverage.json.gz` | 51,231 B (0.05 MiB) |
| `src/repoguard/parser.py` | 19,148 B (0.02 MiB) |
| `benchmarks/run_click.py` | 18,282 B (0.02 MiB) |
| `frontend/src/App.vue` | 17,506 B (0.02 MiB) |

## Git 历史大型对象

本次检查的可达 Git 历史中未发现 ≥1 MiB 的 blob。

## 重复组样例

- 1,121,654 B (1.07 MiB) × 2，`frontend/node_modules/echarts/dist/echarts.esm.min.js`、`frontend/node_modules/echarts/dist/echarts.esm.min.mjs`。
- 4,898 B (0.00 MiB) × 121，`.benchmark/click-full/.git/hooks/pre-rebase.sample`、`.benchmark/click-local/.git/hooks/pre-rebase.sample`、`.benchmark/click/.git/hooks/pre-rebase.sample`。
- 4,726 B (0.00 MiB) × 121，`.benchmark/click-full/.git/hooks/fsmonitor-watchman.sample`、`.benchmark/click-local/.git/hooks/fsmonitor-watchman.sample`、`.benchmark/click/.git/hooks/fsmonitor-watchman.sample`。
- 3,650 B (0.00 MiB) × 121，`.benchmark/click-full/.git/hooks/update.sample`、`.benchmark/click-local/.git/hooks/update.sample`、`.benchmark/click/.git/hooks/update.sample`。
- 366,925 B (0.35 MiB) × 2，`.benchmark/click-full/.git/objects/pack/pack-76116fd2389fb05d43c3841d695b30156cf4687b.pack`、`.benchmark/click-local/.git/objects/pack/pack-76116fd2389fb05d43c3841d695b30156cf4687b.pack`。
- 2,783 B (0.00 MiB) × 121，`.benchmark/click-full/.git/hooks/push-to-checkout.sample`、`.benchmark/click-local/.git/hooks/push-to-checkout.sample`、`.benchmark/click/.git/hooks/push-to-checkout.sample`。
- 2,308 B (0.00 MiB) × 121，`.benchmark/click-full/.git/hooks/sendemail-validate.sample`、`.benchmark/click-local/.git/hooks/sendemail-validate.sample`、`.benchmark/click/.git/hooks/sendemail-validate.sample`。
- 252,416 B (0.24 MiB) × 2，`.benchmark/release-tools/python/yaml/_yaml.cp313-win_amd64.pyd`、`.venv/Lib/site-packages/yaml/_yaml.cp313-win_amd64.pyd`。

## 发布清单与生成边界

| 类别 | 文件与处理 |
|---|---|
| 自有源码与文档 | 保留 src、tests、scripts、infra、configs、前端源码及 npm 锁文件。SQLite schema 随 store.py 发布。 |
| 必要实验材料 | 保留公开 Click 提交、人工标注、基准驱动、运行摘要、压缩覆盖行映射和上游许可。 |
| 外部代码与依赖 | Click 公共克隆、其 Git 对象、venv、node_modules 和缓存保留本地，由清单重新生成。 |
| 本地生成物 | SQLite 数据库、构建包、开发缓存和重复实验运行留在忽略目录。 |
| 预留可再生工件 | Tree-sitter 语法缓存、FAISS、向量、权重、图导出、Docker 归档和卷备份有忽略规则。相关功能状态见 PROJECT_STATUS.md。 |

用 `python scripts/package_audit.py` 重新生成。发布前核对 `git ls-files -ci --exclude-standard`，若发现已跟踪的忽略项，确认后才仅从索引移除。
