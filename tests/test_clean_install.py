from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _venv_executable(venv_dir: Path, name: str) -> Path:
    bin_dir = venv_dir / ("Scripts" if os.name == "nt" else "bin")
    return bin_dir / name


def test_clean_install_from_built_wheel(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(repo_root / "build", ignore_errors=True)
    shutil.rmtree(repo_root / "dist", ignore_errors=True)

    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )

    wheel_path = next(dist_dir.glob("zpe_bio-*.whl"))
    venv_dir = tmp_path / "clean-venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, timeout=300)
    python_bin = _venv_executable(venv_dir, "python")

    subprocess.run(
        [str(python_bin), "-m", "pip", "install", "--upgrade", "pip"],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    subprocess.run(
        [str(python_bin), "-m", "pip", "install", str(wheel_path)],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )

    import_result = subprocess.run(
        [str(python_bin), "-c", "import zpe_bio; print(zpe_bio.__version__)"],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert import_result.stdout.strip()

    cli_bin = _venv_executable(venv_dir, "zpe-bio")
    help_result = subprocess.run(
        [str(cli_bin), "--help"],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert "encode-ecg" in help_result.stdout
