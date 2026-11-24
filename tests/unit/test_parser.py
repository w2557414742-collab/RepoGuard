from repoguard.model import File
from repoguard.parser import parse
from repoguard.repository import safe_relative
from repoguard.resolution import Catalog, Resolver


def scan(text):
    raw = text.encode() if isinstance(text, str) else text
    return parse(File("a.py", "a" * 40, len(raw), "100644", "pending"), raw, "repo", (".",))


def test_encoding_binary_and_compiler_diagnostics():
    file, unit = scan(b"# coding: latin-1\ndef caf\xe9():\n    return 1\n")
    assert file.status == "indexed"
    assert any(s.name == "caf" + "\xe9" for s in unit.symbols.values())
    assert scan(b"\0a")[0].status == "binary"
    assert scan(b"def missing(")[0].status == "parse_error"
    assert "nonlocal" in scan("def f():\n    nonlocal absent")[0].detail
    assert scan('x = """first\u2028second"""\ndef fn(): return x')[0].lines == 2


def test_scope_shadow_class_globals_and_comprehension():
    _, unit = scan(
        "def factory(): return 1\n"
        "class Test:\n"
        "    def factory(self): return 10\n"
        "    def method(self): return factory()\n"
        "def shadow():\n"
        "    factory()\n"
        "    factory = 0\n"
        "def explicit():\n"
        "    global factory\n"
        "    return factory()\n"
        "def parts(values):\n"
        "    return [factory() for factory in values]\n"
        "def run(value):\n"
        "    getattr(value, 'hidden')()\n"
    )
    edges, _ = Resolver(Catalog({"a.py": unit})).resolve(unit)
    calls = {edge.line: edge for edge in edges if edge.kind == "CALLS"}
    assert unit.symbols[calls[4].target].qualified_name == "a.factory"
    assert calls[6].target is None
    assert unit.symbols[calls[10].target].qualified_name == "a.factory"
    assert calls[12].target is None
    assert calls[14].target is None


def test_safe_paths():
    for path in ("", "../escape", "/root", "x/../escape", "C:/absolute", "a\\b", "x//y", "p\na"):
        assert not safe_relative(path)
    assert safe_relative("src/pkg/file space.py")
