"""The production entry point must load syntactically valid runtimes."""
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="Node is required to check production JavaScript")
@pytest.mark.parametrize("name", ["app.js", "app.min.js"])
def test_production_runtime_syntax(name):
    result = subprocess.run([NODE, "--check", str(ROOT / name)],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr[-2000:]
