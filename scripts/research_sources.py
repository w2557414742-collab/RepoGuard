"""Record source provenance without executing upstream code."""

from __future__ import annotations

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

PROJECTS = {
    "tree-sitter/tree-sitter": ("v0.27.2", "lib/src/parser.c"),
    "joernio/joern": (
        "v4.0.690",
        "semanticcpg/src/main/scala/io/shiftleft/semanticcpg/language/package.scala",
    ),
    "github/codeql": (
        "codeql-cli/v2.21.4",
        "python/ql/lib/semmle/python/dataflow/new/DataFlow.qll",
    ),
    "scip-code/scip": ("v0.10.0", "scip.proto"),
    "microsoft/pyright": ("1.1.400", "packages/pyright-internal/src/analyzer/binder.ts"),
    "Instagram/LibCST": ("v1.9.0", "libcst/metadata/scope_provider.py"),
    "ast-grep/ast-grep": (
        "0.51.3",
        "crates/core/src/matcher/pattern.rs",
        "crates/core/src/matcher.rs",
    ),
    "Aider-AI/aider": ("v0.86.3.dev", "aider/repomap.py"),
    "coveragepy/coveragepy": ("7.8.2", "coverage/control.py"),
    "tarpas/pytest-testmon": ("v2.3.1", "testmon/pytest_testmon.py"),
    "boxed/mutmut": ("3.8.1", "src/mutmut/__main__.py", "mutmut/__main__.py"),
    "pschanely/CrossHair": ("v0.0.114", "crosshair/core.py"),
    "HypothesisWorks/hypothesis": (
        "v6.131.0",
        "hypothesis-python/src/hypothesis/core.py",
    ),
}


def get(url: str) -> str:
    request = Request(url, headers={"User-Agent": "RepoGuard-source-audit"})
    with urlopen(request, timeout=18) as response:
        data = response.read()
    return data.decode("utf-8")


def collect(item: tuple[str, tuple[str, ...]]) -> dict:
    slug, (tag, *paths) = item
    result = {"repository": f"https://github.com/{slug}", "tag": tag}
    try:
        ref = f"refs/tags/{tag}"
        listing = subprocess.run(
            [
                "git",
                "-c",
                "http.sslBackend=openssl",
                "ls-remote",
                result["repository"],
                ref,
                ref + "^{}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout
        refs = {name: oid for oid, name in (line.split() for line in listing.splitlines())}
        result["commit"] = refs.get(ref + "^{}") or refs[ref]
        base = f"https://raw.githubusercontent.com/{slug}/{result['commit']}/"
        for path in paths:
            try:
                data = get(base + path)
            except OSError:
                continue
            out = Path(".benchmark/research") / f"{slug.replace('/', '_')}.txt"
            out.write_text(data, encoding="utf-8")
            result["source"] = f"https://github.com/{slug}/blob/{result['commit']}/{path}"
            result["source_lines"] = len(data.splitlines())
            break
        for path in (
            "LICENSE",
            "LICENSE.txt",
            "LICENSE.md",
            "COPYING",
            "hypothesis-python/LICENSE.txt",
        ):
            try:
                license_text = get(base + path)
            except OSError:
                continue
            (Path(".benchmark/research") / f"{slug.replace('/', '_')}_license.txt").write_text(
                license_text,
                encoding="utf-8",
            )
            result["license_source"] = f"https://github.com/{slug}/blob/{result['commit']}/{path}"
            break
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        result["error"] = str(exc)
    return result


if __name__ == "__main__":
    Path(".benchmark/research").mkdir(parents=True, exist_ok=True)
    Path("artifacts").mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        data = list(pool.map(collect, PROJECTS.items()))
    Path("artifacts/source-provenance.json").write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
