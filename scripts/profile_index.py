from __future__ import annotations

import argparse
import cProfile
import json
import os
import platform
import pstats
import tempfile
from pathlib import Path
from time import perf_counter

from repoguard.sdk import RepoGuard


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("repository", type=Path)
    cli.add_argument("--revision", default="HEAD")
    cli.add_argument("--output", type=Path, default=Path("artifacts/click-profile.json"))
    args = cli.parse_args()
    with tempfile.TemporaryDirectory() as work:
        engine = RepoGuard(args.repository, Path(work) / "profile.sqlite")
        profile = cProfile.Profile()
        start = perf_counter()
        snapshot = profile.runcall(engine.indexer.index, args.revision, persist=False, mode="full")
        elapsed = perf_counter() - start
    stats = pstats.Stats(profile)
    hotspots = sorted(stats.stats.items(), key=lambda row: row[1][3], reverse=True)[:20]
    report = {
        "commit": snapshot.commit,
        "python": platform.python_version(),
        "host": platform.platform(),
        "logical_cpus": os.cpu_count(),
        "workers": engine.indexer.workers,
        "profiled_wall_seconds": elapsed,
        "total_calls": stats.total_calls,
        "hotspots": [
            {
                "file": Path(item[0]).name,
                "line": item[1],
                "function": item[2],
                "seconds": value[2],
                "cumulative_seconds": value[3],
                "calls": value[1],
            }
            for item, value in hotspots
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
