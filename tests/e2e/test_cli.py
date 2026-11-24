import json
import subprocess
import sys


def test_cli_roundtrip(history, tmp_path):
    repo, base, target = history
    args = [
        sys.executable,
        "-m",
        "repoguard.cli",
        "--repo",
        str(repo.root),
        "--db",
        str(tmp_path / "index.sqlite"),
    ]
    for command in (["index", "--target", base], ["index", "--target", target, "--base", base]):
        result = subprocess.run([*args, *command], capture_output=True, check=True)
        assert json.loads(result.stdout)["symbols"] > 0
    result = subprocess.run(
        [*args, "definition", "app.core.verify"], capture_output=True, check=True
    )
    assert json.loads(result.stdout)[0]["signature"] == "(token, audience='local')"
    report = subprocess.run(
        [*args, "impact", base, target, "--format", "markdown"], capture_output=True, check=True
    )
    assert "public API signature or removal" in report.stdout.decode()
