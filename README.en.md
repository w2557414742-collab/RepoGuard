# RepoGuard

Repository-Level Change Impact Analysis & Verified Refactoring Platform.

RepoGuard reads immutable Git commits, builds a versioned Python symbol and dependency index, and reports change evidence. It supports file-level incremental indexing, source navigation, test selection, structured LibCST refactoring previews, and an offline Docker test runner. The CLI, Python SDK, FastAPI, MCP stdio server, and Vue workbench share one analysis engine.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,refactor,testing,architecture,api,mcp]'
git clone --depth 2 --branch 8.1.8 https://github.com/pallets/click.git .benchmark/click-full
repoguard --repo .benchmark/click-full index --base HEAD~1 --target HEAD
repoguard --repo .benchmark/click-full search click.formatting.iter_rows
repoguard --repo .benchmark/click-full impact HEAD~1 HEAD --format markdown
repoguard --repo .benchmark/click-full select-tests HEAD~1 HEAD
repoguard --repo .benchmark/click-full plan click.formatting.iter_rows aligned_rows
python -m pytest -q
```

- [Chinese README](README.md) and [Windows quickstart](WINDOWS_QUICKSTART.md).
- [Architecture](ARCHITECTURE.md), [source navigation](FUNCTION_REFERENCE.md), and [call flows](CALL_FLOW.md).
- [Benchmark protocol](BENCHMARK_PROTOCOL.md), [observed outcomes](EXPERIMENT_REPORT.md), and [release checks](TEST_REPORT.md).
- [Implemented features and limits](PROJECT_STATUS.md) and [GitHub release status](GITHUB_PUBLISH_REPORT.md).

The benchmark covers one public Click release and controlled changes. Implementation limits include incomplete runtime dispatch, SQLite whole-version reads, and conservative test fallback. Embeddings, FAISS, Tree-sitter and full data flow are future work.
