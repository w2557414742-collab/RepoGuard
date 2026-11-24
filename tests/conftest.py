from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


class GitFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "repoguard@example.invalid")
        self.git("config", "user.name", "RepoGuard fixture")
        self.git("config", "core.autocrlf", "false")

    def git(self, *args: str, data: bytes | None = None) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.root), *args],
            input=data,
            capture_output=True,
            check=True,
        )
        return result.stdout.decode().strip()

    def write(self, path: str, text: str | bytes) -> None:
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(text.encode() if isinstance(text, str) else text)

    def commit(self) -> str:
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture revision")
        return self.git("rev-parse", "HEAD")


@pytest.fixture
def repository(tmp_path):
    return GitFixture(tmp_path / "target")


@pytest.fixture
def history(repository):
    files = {
        "src/app/__init__.py": "from .core import verify as check\n",
        "src/app/core.py": "def verify(token):\n    return len(token) > 0\n",
        "src/app/other.py": "def verify(token):\n    return False\n",
        "src/app/service.py": (
            "from . import check as validate\n"
            "from .other import verify\n"
            "def handle(token):\n    return validate(token)\n"
            "def shadow(validate):\n    return validate('x')\n"
            "def outer():\n"
            "    def verify(token):\n        return True\n"
            "    def inner(token):\n        nonlocal verify\n        return verify(token)\n"
            "    return inner('x')\n"
        ),
        "tests/test_service.py": (
            "from app.service import handle\ndef test_handle():\n    assert handle('x')\n"
        ),
        "src/app/base.py": "class Base:\n    def run(self):\n        return 3\n",
        "src/app/child.py": (
            "from .base import Base\n"
            "class Child(Base):\n    def run(self):\n        return 4\n"
            "class Inherited(Base):\n    def use(self):\n        return self.run()\n"
            "def call():\n    return Child.run(None)\n"
        ),
        "src/app/cycle_a.py": "from . import cycle_b\ndef start():\n    return cycle_b.end()\n",
        "src/app/cycle_b.py": "from . import cycle_a\ndef end():\n    return 1\n",
        "src/app/missing.py": "from .future import later\ndef use():\n    return later()\n",
        "src/app/unused.py": "def independent():\n    return 1\n",
    }
    for path, source in files.items():
        repository.write(path, source)
    base = repository.commit()
    repository.write(
        "src/app/core.py", "def verify(token, audience='local'):\n    return bool(token)\n"
    )
    repository.write("src/app/future.py", "def later():\n    return 'now present'\n")
    repository.git("mv", "src/app/child.py", "src/app/descendant.py")
    repository.git("rm", "src/app/other.py")
    target = repository.commit()
    return repository, base, target
