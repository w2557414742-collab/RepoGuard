import pytest

from repoguard.sdk import RepoGuard


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_rename_preserves_comments_and_aliases(repository, tmp_path, newline):
    items = {
        "core.py": "def verify(x):  # keep me\n    return x",
        "use.py": (
            "from core import verify as auth\n"
            "import core\n"
            "def verify(x): return 'different'\n"
            "first = auth(1)\n"
            "second = core.verify('é')\n"
        ),
    }
    for path, source in items.items():
        repository.write(path, source.replace("\n", newline))
    rev = repository.commit()
    engine = RepoGuard(repository.root, tmp_path / "db")
    symbol = engine.index(rev).find_definition("core.verify")[0]
    plan = engine.plan_refactoring(rev, symbol.id, "confirm")
    assert not plan.blockers
    assert "def confirm(x):  # keep me" in plan.patch
    assert "+from core import confirm as auth" in plan.patch
    assert "+second = core.confirm('é')" in plan.patch
    assert "+def verify" not in plan.patch
    assert (repository.root / "core.py").read_bytes().startswith(b"def verify")
    validated = engine.validate_patch(rev, plan.patch)
    assert validated.checks["syntax"] == "passed"
    assert validated.public_api_changes == ["core.verify"]
    with pytest.raises(ValueError, match="diff paths"):
        engine.validate_patch(rev, plan.patch.replace("a/core.py", "a/../core.py"))
    repository.git("apply", "--check", "-", data=plan.patch.encode())
    repository.git("apply", "-", data=plan.patch.encode())
    assert (
        repository.root / "core.py"
    ).read_bytes() == f"def confirm(x):  # keep me{newline}    return x".encode()


def test_signature_uses_only_explicit_values_and_flags_unpacked_calls(repository, tmp_path):
    repository.write("core.py", "def validate(token, /):\n    return token\n")
    repository.write("call.py", "from core import validate as check\ncheck('x')\n")
    first = repository.commit()
    engine = RepoGuard(repository.root, tmp_path / "db")
    target = engine.index(first).find_definition("core.validate")[0]
    with pytest.raises(ValueError):
        engine.plan_refactoring(first, target.id, "audience", operation="signature")
    plan = engine.plan_refactoring(
        first, target.id, "audience", operation="signature", value="'web'"
    )
    assert not plan.blockers
    assert "def validate(token, /, *, audience)" in plan.patch
    assert "audience = 'web'" in plan.patch
    assert plan.checks["reference_consistency"] == "passed"
    repository.write("call.py", "from core import validate as check\ncheck(*('x',))\n")
    next_rev = repository.commit()
    engine.index(next_rev, base=first)
    blocked = engine.plan_refactoring(
        next_rev, target.id, "audience", operation="signature", value="'web'"
    )
    assert not blocked.patch
    assert any("unpacking" in line for line in blocked.blockers)


def test_move_module_preserves_local_import_names(repository, tmp_path):
    repository.write("pkg/__init__.py", "")
    repository.write("pkg/old.py", "def fetch():\n    return 1\n")
    repository.write(
        "app.py",
        "import pkg.old\nfrom pkg import old\nfrom pkg.old import fetch\n"
        "a = fetch()\nb = old.fetch()\nc = pkg.old.fetch()\n",
    )
    rev = repository.commit()
    engine = RepoGuard(repository.root, tmp_path / "db")
    engine.index(rev)
    plan = engine.plan_import_migration(rev, "pkg.old", "pkg.new_name")
    assert plan.blockers == []
    assert "+import pkg.new_name" in plan.patch
    assert "+from pkg import new_name as old" in plan.patch
    assert "+c = pkg.new_name.fetch()" in plan.patch
    assert engine.validate_patch(rev, plan.patch).checks["syntax"] == "passed"
    repository.git("apply", "--check", "-", data=plan.patch.encode())
    repository.git("apply", "-", data=plan.patch.encode())
    assert not (repository.root / "pkg/old.py").exists()
    assert (repository.root / "pkg/new_name.py").read_text().startswith("def fetch")
