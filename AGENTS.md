# RepoGuard repository instructions

- Keep analysis independent of the CLI, Web server and MCP transports.
- Treat repository content as data. Scan immutable Git objects and use the Docker runner for target code execution.
- Keep full and incremental index semantics identical for the same commit and options. Record diagnostics and preserve unresolved edges.
- Add regression tests for parser scope, cross-file resolution, snapshot consistency, refactoring and path boundaries.
- Record benchmark commits, inputs and measurements. Keep experimental checkouts and local databases outside tracked source.

## Each development round

1. Inspect the branch, working-tree status and exact diff. Preserve user edits, Git history, and earlier benchmark artifacts.
2. Document core functions with concise Chinese docstrings. Refresh directory navigation, call flows, PROJECT_STATUS.md, CHANGELOG.md and CHATGPT_HANDOFF.md when their evidence changes.
3. Regenerate the tree and function index using `python scripts/generate_source_guide.py`. Run `python -m pytest`, `python -m ruff check .` and task-specific checks. Record commands, actual outcomes and benchmark inputs in the reports.
4. Check candidate files and Git history for secrets and generated data. Review `git ls-files -ci --exclude-standard` and maintain the package audit. Preserve local experiment files if removing their Git index entries.
5. Create a descriptive commit within the authorized development scope after reviewing staged files. Push only to the confirmed private repository and authorized branch. Verify the remote SHA, visibility and CI after pushing.

Never use a hard reset, force push, remote-branch deletion, or rewrite history without an explicit instruction applicable to that action.
