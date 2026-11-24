"""Run CrossHair against RepoGuard's own reviewed contract fixtures."""

import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter


def check(function: str) -> dict:
    command = [
        sys.executable,
        "-m",
        "crosshair",
        "check",
        "benchmarks.contracts.risk_contracts." + function,
        "--report_all",
        "--per_condition_timeout",
        "2",
        "--per_path_timeout",
        "0.5",
    ]
    start = perf_counter()
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
    except subprocess.TimeoutExpired:
        return {"function": function, "status": "INCONCLUSIVE", "reason": "process timeout"}
    output = run.stdout + run.stderr
    if run.returncode == 1 and "when calling" in output:
        status = "FOUND_COUNTEREXAMPLE"
    elif "Confirmed over all paths" in output and run.returncode == 0:
        status = "NO_COUNTEREXAMPLE_FOUND"
    elif run.returncode not in {0, 1} or "No module named" in output:
        status = "UNSUPPORTED"
    else:
        status = "INCONCLUSIVE"
    return {
        "function": function,
        "status": status,
        "exit": run.returncode,
        "seconds": perf_counter() - start,
        "output": output.strip(),
        "command": command[2:],
    }


if __name__ == "__main__":
    output = Path("artifacts/risk-contracts.json")
    output.parent.mkdir(exist_ok=True)
    results = [check(item) for item in ("bounded_step", "reversed_uncertainty")]
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(output)
