"""把固定提交送入离线 Docker 运行器并验证测试回执。"""

from __future__ import annotations

import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from dataclasses import dataclass
from threading import Event
from time import perf_counter
from typing import BinaryIO
from uuid import uuid4

from .repository import Repository, safe_relative
from .test_selection import CoverageMap

IMAGE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_./:@-]{0,254}\Z")
RESULT_MARKER = "REPOGUARD_RESULT "


class OutputLimitExceeded(RuntimeError):
    pass


def bounded_exchange(
    command: list[str],
    payload: bytes,
    timeout: int,
    stdout_limit: int = 16 * 1024 * 1024,
    stderr_limit: int = 1024 * 1024,
) -> subprocess.CompletedProcess[bytes]:
    """并发写入子进程 stdin 并排空 stdout、stderr。两个输出缓冲区独立限流，超时或溢出时终止宿主客户端。

    调用方负责清理 Docker 容器。内存上限由输入及输出预算共同约束。
    """
    overflow = Event()
    with subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        assert (
            process.stdin is not None and process.stdout is not None and process.stderr is not None
        )

        def drain(stream: BinaryIO, limit: int) -> bytes:
            output = bytearray()
            while data := stream.read1(64 * 1024):
                if len(output) + len(data) > limit:
                    overflow.set()
                    with suppress(OSError):
                        process.kill()
                    break
                output.extend(data)
            return bytes(output)

        def send(stream: BinaryIO) -> None:
            with suppress(BrokenPipeError), stream:
                stream.write(payload)

        with ThreadPoolExecutor(max_workers=3) as pool:
            stdout = pool.submit(drain, process.stdout, stdout_limit)
            stderr = pool.submit(drain, process.stderr, stderr_limit)
            writer = pool.submit(send, process.stdin)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise
            writer.result()
            out, err = stdout.result(), stderr.result()
        if overflow.is_set():
            raise OutputLimitExceeded("sandbox output limit exceeded")
        return subprocess.CompletedProcess(command, code, out, err)


@dataclass(frozen=True, slots=True)
class TestRun:
    """记录测试运行状态、时间、提交、镜像、pytest 失败与覆盖明细。"""

    status: str
    code: int | None
    seconds: float
    commit: str
    environment: str
    failures: list[str]
    collected: list[str]
    output: str
    coverage: CoverageMap | None


def run_tests(
    repo: Repository,
    revision: str,
    *,
    image: str,
    nodeids: list[str] | None = None,
    timeout: int = 120,
    collect_coverage: bool = False,
) -> TestRun:
    """将提交归档、测试选择器及覆盖开关传给固定 Docker 镜像。校验相对测试路径、镜像摘要和归档大小。

    容器以非 root、无网络、只读根和受限 tmpfs 执行。返回测试回执或明确的 blocked、timeout 等状态。
    """
    if not IMAGE.fullmatch(image) or not 1 <= timeout <= 3600:
        raise ValueError("use a valid image name and a timeout between 1 and 3600 seconds")
    nodeids = nodeids or []
    if any(
        not safe_relative(node.split("::", 1)[0])
        or node.startswith("-")
        or any(c in node for c in "\0\r\n")
        for node in nodeids
    ):
        raise ValueError("invalid pytest node selector")
    commit = repo.commit(revision)
    name = f"repoguard-{uuid4().hex}"
    start = perf_counter()
    image_id = ""
    try:
        image_id = subprocess.run(
            ["docker", "image", "inspect", "--format", "{{.Id}}", image],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout.strip()
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
            raise ValueError("Docker did not return an immutable image ID")
        files = repo.inventory(commit, 16 * 1024 * 1024)
        if sum(file.size for file in files.values()) > 128 * 1024 * 1024:
            raise ValueError("test sandbox accepts Git trees of at most 128 MiB")
        archive = repo.git("archive", "--format=tar", commit)
        if len(archive) > 128 * 1024 * 1024:
            raise ValueError("test sandbox accepts tar archives of at most 128 MiB")
        command = [
            "docker",
            "run",
            "--rm",
            "--name",
            name,
            "-i",
            "--pull=never",
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "--user=65534:65534",
            "--pids-limit=128",
            "--cpus=2",
            "--memory=768m",
            "--tmpfs=/work:rw,noexec,nosuid,nodev,size=256m",
            "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=96m",
            "--entrypoint=python",
            image_id,
            "-I",
            "/opt/repoguard/runner_entry.py",
        ]
        request = json.dumps({"coverage": collect_coverage, "nodeids": nodeids}).encode("ascii")
        if len(request) > 1024 * 1024:
            raise ValueError("pytest selectors exceed the 1 MiB request limit")
        execution = bounded_exchange(command, request + b"\n" + archive, timeout)
    except (OSError, subprocess.CalledProcessError) as exc:
        message = getattr(exc, "stderr", None) or str(exc)
        return TestRun(
            "blocked",
            None,
            perf_counter() - start,
            commit,
            image_id,
            [],
            [],
            str(message)[-4000:],
            None,
        )
    except (subprocess.TimeoutExpired, OutputLimitExceeded) as exc:
        try:
            subprocess.run(
                ["docker", "rm", "-f", name], capture_output=True, timeout=10, check=False
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        status = "timeout" if isinstance(exc, subprocess.TimeoutExpired) else "output_limit"
        return TestRun(
            status, None, perf_counter() - start, commit, image_id, [], [], str(exc), None
        )
    output = execution.stdout.decode("utf-8", "replace")
    stderr = execution.stderr.decode("utf-8", "replace")
    records = [
        line.removeprefix(RESULT_MARKER)
        for line in output.splitlines()
        if line.startswith(RESULT_MARKER)
    ]
    data: dict[str, object] = {}
    if records:
        try:
            candidate = json.loads(records[-1])
            if (
                isinstance(candidate, dict)
                and isinstance(candidate.get("complete"), bool)
                and isinstance(candidate.get("collected"), list)
                and isinstance(candidate.get("failures"), list)
                and isinstance(candidate.get("tests"), dict)
                and isinstance(candidate.get("limitations"), list)
            ):
                data = candidate
        except json.JSONDecodeError:
            pass
    completed = bool(data.get("complete")) and execution.returncode in {0, 1}
    coverage = None
    if collect_coverage and completed:
        limitations = [
            *data["limitations"],
            "subprocess coverage and shared fixture attribution are incomplete",
        ]
        coverage = CoverageMap(commit, image_id, True, data["tests"], limitations)
    status = (
        "passed"
        if completed and execution.returncode == 0
        else "failed"
        if completed
        else "blocked"
        if execution.returncode == 125
        else "error"
    )
    return TestRun(
        status,
        execution.returncode,
        perf_counter() - start,
        commit,
        image_id,
        data.get("failures", []),
        data.get("collected", []),
        (
            os.linesep.join(
                line for line in output.splitlines() if not line.startswith(RESULT_MARKER)
            )
            + "\n"
            + stderr
        )[-16000:],
        coverage,
    )
