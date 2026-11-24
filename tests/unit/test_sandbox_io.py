from sys import executable

import pytest

from repoguard.sandbox import OutputLimitExceeded, bounded_exchange


def test_runner_captures_output_and_caps_excessive_streams():
    command = [
        executable,
        "-c",
        "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read() + b'!')",
    ]
    result = bounded_exchange(command, b"source", 5)
    assert result.returncode == 0 and result.stdout == b"source!"
    noisy = [executable, "-c", "import sys; sys.stderr.write('x' * 100000)"]
    with pytest.raises(OutputLimitExceeded):
        bounded_exchange(noisy, b"", 5, stderr_limit=1024)
