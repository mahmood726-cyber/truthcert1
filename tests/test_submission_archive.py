"""Submission export safety using text transport fixtures only."""
import importlib.util
from pathlib import Path
import zipfile
import subprocess
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "PLOS_ONE_Submission/convert_files.py"
spec = importlib.util.spec_from_file_location("submission_converter", SCRIPT)
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


def test_converter_resolves_its_own_directory():
    assert converter.BASE_DIR == SCRIPT.parent


def test_import_needs_no_optional_document_packages():
    result = subprocess.run([sys.executable, "-S", "-c",
        "import runpy, sys; runpy.run_path(sys.argv[1], run_name='import_check')", str(SCRIPT)],
        capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("invalid", ["missing", "directory", "empty", "duplicate", "output"])
def test_invalid_inputs_preserve_existing_archive(tmp_path, invalid):
    source = tmp_path / "source.txt"
    source.write_text("software transport fixture", encoding="utf-8")
    output = tmp_path / "bundle.zip"
    output.write_bytes(b"existing archive fixture")
    entries = {
        "missing": [source, tmp_path / "absent.txt"],
        "directory": [source, tmp_path],
        "empty": [],
        "duplicate": [source, source],
        "output": [source, output],
    }[invalid]
    with pytest.raises((ValueError, FileNotFoundError, IsADirectoryError)):
        converter.create_zip_archive(entries, output)
    assert output.read_bytes() == b"existing archive fixture"


def test_archive_contains_all_input_bytes(tmp_path):
    sources = [tmp_path / name for name in ("first.txt", "second.txt")]
    for i, source in enumerate(sources):
        source.write_bytes(f"software fixture {i}".encode())
    output = tmp_path / "bundle.zip"
    converter.create_zip_archive(sources, output)
    with zipfile.ZipFile(output) as archive:
        assert archive.namelist() == [source.name for source in sources]
        for source in sources:
            assert archive.read(source.name) == source.read_bytes()


def test_write_failure_preserves_archive_and_removes_temporary_file(tmp_path, monkeypatch):
    source = tmp_path / "source.txt"
    source.write_text("software fixture", encoding="utf-8")
    output = tmp_path / "bundle.zip"
    output.write_bytes(b"previous archive")
    def fail_write(*args, **kwargs):
        raise OSError("simulated disk failure")
    monkeypatch.setattr(zipfile.ZipFile, "write", fail_write)
    with pytest.raises(OSError, match="disk failure"):
        converter.create_zip_archive([source], output)
    assert output.read_bytes() == b"previous archive"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["bundle.zip", "source.txt"]
