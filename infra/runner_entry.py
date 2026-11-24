import json
import subprocess
import sys
import tarfile
from pathlib import Path


def extract() -> None:
    with tarfile.open(fileobj=sys.stdin.buffer, mode="r|*") as archive:
        for member in archive:
            if member.isfile() or member.isdir():
                archive.extract(member, "/work", filter="data", set_attrs=False)


def main() -> int:
    request = json.loads(sys.stdin.buffer.readline(1024 * 1024 + 1))
    extract()
    destination = Path("/tmp/result.json")
    coverage = request["coverage"]
    env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": "/tmp",
        "PYTHONPATH": "/work/src:/work",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "REPOGUARD_COLLECT_COVERAGE": "1" if coverage else "0",
        "REPOGUARD_PYTEST_RESULT": str(destination),
    }
    args = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "repoguard.pytest_coverage",
        "-p",
        "no:cacheprovider",
        "-q",
    ]
    if request["nodeids"]:
        args.extend(["--", *request["nodeids"]])
    result = subprocess.run(args, cwd="/work", env=env, check=False)
    if destination.is_file():
        print("REPOGUARD_RESULT " + destination.read_text(encoding="utf-8").strip(), flush=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
