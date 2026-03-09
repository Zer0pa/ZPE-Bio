#!/usr/bin/env python3
"""Pinned reproducibility runner for full falsification reruns."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_PACKAGES = [
    "numpy",
    "wfdb",
    "pytest",
    "scipy",
    "matplotlib",
    "build",
    "ruff",
]

REQUIRED_RUST_TARGETS = [
    "thumbv8m.main-none-eabi",
    "x86_64-apple-darwin",
]


@dataclass
class CommandResult:
    name: str
    cmd: list[str]
    cwd: Path
    started_utc: str
    ended_utc: str
    duration_s: float
    returncode: int
    stdout: str
    stderr: str


class Runner:
    def __init__(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.results_dir = self.repo_root / "validation" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

        self.venv_python = self.repo_root / ".venv" / "bin" / "python"
        self.command_results: list[CommandResult] = []

        self.dt_result_out = self.results_dir / f"dt_results_{self.timestamp}.json"
        self.phase3_out = self.results_dir / f"phase3_hostok_{self.timestamp}.json"
        self.freeze_out = self.results_dir / f"pip_freeze_{self.timestamp}.txt"
        self.repro_manifest_out = self.results_dir / f"repro_manifest_{self.timestamp}.json"
        self.repro_hashes_out = self.results_dir / f"repro_hashes_{self.timestamp}.txt"
        self.falsification_out = self.results_dir / f"falsification_results_{self.timestamp}.md"
        self.claim_delta_out = self.results_dir / f"claim_status_delta_{self.timestamp}.md"
        self.command_log_out = self.results_dir / f"command_log_{self.timestamp}.txt"

        self.before_dt_files = set(self.results_dir.glob("dt_results_*.json"))
        self.before_phase3_files = set(self.results_dir.glob("phase3_hostok_*.json"))

        self.prior_dt_path = self._latest_from_set(self.before_dt_files)
        self.prior_phase3_path = self._latest_from_set(self.before_phase3_files)

        self.dependency_versions: dict[str, str] = {}
        self.missing_packages: list[str] = []
        self.toolchain_versions: dict[str, str] = {}
        self.installed_targets: list[str] = []

        self.dt_results_payload: dict[str, Any] | None = None
        self.phase3_payload: dict[str, Any] | None = None
        self.pytest_pass: bool | None = None
        self.stop_reason: str | None = None

    def run(self) -> int:
        if not self.venv_python.exists():
            self.stop_reason = (
                f"Missing pinned interpreter: {self.venv_python}. "
                "Create and provision .venv first."
            )
            self._write_outputs()
            return 1

        try:
            self._verify_dependency_contract()
            self._verify_toolchain_contract()
            self._build_rust_release_artifacts()
            self._run_dt_suite()
            dt_gate = self._dt_gate_status()
            if not dt_gate["dt_all_pass"]:
                self.stop_reason = "DT gate failed; stopping before pytest/phase3 per policy."
                self.pytest_pass = None
                self.phase3_payload = {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "phase": "Phase 3 Embedded (Host-OK)",
                    "overall_pass": False,
                    "status": "SKIPPED",
                    "reason": self.stop_reason,
                }
                self.phase3_out.write_text(json.dumps(self.phase3_payload, indent=2), encoding="utf-8")
                self._write_outputs()
                return 1

            self._run_pytest_suite()
            if not self.pytest_pass:
                self.stop_reason = "pytest gate failed."
                self.phase3_payload = {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "phase": "Phase 3 Embedded (Host-OK)",
                    "overall_pass": False,
                    "status": "SKIPPED",
                    "reason": self.stop_reason,
                }
                self.phase3_out.write_text(json.dumps(self.phase3_payload, indent=2), encoding="utf-8")
                self._write_outputs()
                return 1

            self._run_phase3_hostok_report()
            overall_go = self._overall_go()
            if not overall_go:
                self.stop_reason = "One or more acceptance gates failed."
            self._write_outputs()
            return 0 if overall_go else 1
        except Exception as exc:
            self.stop_reason = f"Unhandled runner error: {exc}"
            self._write_outputs()
            return 1

    def _run_command(
        self,
        name: str,
        cmd: list[str],
        cwd: Path | None = None,
        timeout: int | None = None,
        env: dict[str, str] | None = None,
    ) -> CommandResult:
        cmd_cwd = cwd or self.repo_root
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        start = datetime.now(timezone.utc)
        completed = subprocess.run(
            cmd,
            cwd=cmd_cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=merged_env,
        )
        end = datetime.now(timezone.utc)
        result = CommandResult(
            name=name,
            cmd=cmd,
            cwd=cmd_cwd,
            started_utc=start.isoformat(),
            ended_utc=end.isoformat(),
            duration_s=(end - start).total_seconds(),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        self.command_results.append(result)
        return result

    def _latest_from_set(self, files: set[Path]) -> Path | None:
        if not files:
            return None
        return max(files, key=lambda p: p.stat().st_mtime)

    def _latest_new_file(self, pattern: str, before_set: set[Path]) -> Path | None:
        after = set(self.results_dir.glob(pattern))
        new_files = sorted(after - before_set, key=lambda p: p.stat().st_mtime)
        if new_files:
            return new_files[-1]
        candidates = sorted(after, key=lambda p: p.stat().st_mtime)
        if candidates:
            return candidates[-1]
        return None

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(65536)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

    def _verify_dependency_contract(self) -> None:
        check_code = textwrap.dedent(
            f"""
            import importlib.metadata as md
            import json

            required = {REQUIRED_PACKAGES!r}
            versions = {{}}
            missing = []
            for pkg in required:
                try:
                    versions[pkg] = md.version(pkg)
                except md.PackageNotFoundError:
                    missing.append(pkg)
            print(json.dumps({{"versions": versions, "missing": missing}}, sort_keys=True))
            """
        )
        dep_result = self._run_command(
            "verify_python_dependencies",
            [str(self.venv_python), "-c", check_code],
        )
        if dep_result.returncode != 0:
            raise RuntimeError(
                "Dependency contract check failed to execute:\n"
                f"{dep_result.stdout}\n{dep_result.stderr}"
            )
        payload = json.loads(dep_result.stdout.strip() or "{}")
        self.dependency_versions = payload.get("versions", {})
        self.missing_packages = payload.get("missing", [])
        if self.missing_packages:
            raise RuntimeError(
                "Missing required python packages in .venv: "
                + ", ".join(self.missing_packages)
            )

        freeze_result = self._run_command(
            "pip_freeze",
            [str(self.venv_python), "-m", "pip", "freeze", "--all"],
        )
        if freeze_result.returncode != 0:
            raise RuntimeError(f"pip freeze failed:\n{freeze_result.stdout}\n{freeze_result.stderr}")
        self.freeze_out.write_text(freeze_result.stdout, encoding="utf-8")

    def _verify_toolchain_contract(self) -> None:
        cargo_v = self._run_command("cargo_version", ["cargo", "--version"])
        rustc_v = self._run_command("rustc_version", ["rustc", "--version"])
        rustup_v = self._run_command("rustup_version", ["rustup", "--version"])
        targets = self._run_command(
            "rustup_targets_installed",
            ["rustup", "target", "list", "--installed"],
        )

        if cargo_v.returncode != 0 or rustc_v.returncode != 0 or rustup_v.returncode != 0:
            raise RuntimeError("Rust toolchain version commands failed.")
        if targets.returncode != 0:
            raise RuntimeError("rustup target list failed.")

        self.toolchain_versions = {
            "cargo": cargo_v.stdout.strip(),
            "rustc": rustc_v.stdout.strip(),
            "rustup": rustup_v.stdout.strip().splitlines()[0] if rustup_v.stdout.strip() else "",
        }
        self.installed_targets = [line.strip() for line in targets.stdout.splitlines() if line.strip()]

        missing_targets = [t for t in REQUIRED_RUST_TARGETS if t not in self.installed_targets]
        if missing_targets:
            raise RuntimeError("Missing required rust targets: " + ", ".join(missing_targets))

    def _build_rust_release_artifacts(self) -> None:
        core_rust = self.repo_root / "core" / "rust"
        build_native = self._run_command(
            "cargo_build_release_native",
            ["cargo", "build", "--release"],
            cwd=core_rust,
        )
        if build_native.returncode != 0:
            raise RuntimeError("Native release build failed.")

        build_x86 = self._run_command(
            "cargo_build_release_x86_64_apple",
            ["cargo", "build", "--release", "--target", "x86_64-apple-darwin"],
            cwd=core_rust,
        )
        if build_x86.returncode != 0:
            raise RuntimeError("x86_64-apple-darwin release build failed.")

    def _run_dt_suite(self) -> None:
        dt_before = set(self.results_dir.glob("dt_results_*.json"))
        dt_run = self._run_command(
            "run_all_destruct_tests",
            [str(self.venv_python), "validation/destruct_tests/run_all_dts.py"],
            cwd=self.repo_root,
        )
        if dt_run.returncode != 0:
            raise RuntimeError("DT runner process failed to execute cleanly.")

        produced = self._latest_new_file("dt_results_*.json", dt_before)
        if produced is None:
            raise RuntimeError("DT results artifact was not produced.")

        payload = json.loads(produced.read_text(encoding="utf-8"))
        self.dt_results_payload = payload
        self.dt_result_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _dt_gate_status(self) -> dict[str, Any]:
        if self.dt_results_payload is None:
            return {
                "dt_all_pass": False,
                "dt_total": 0,
                "dt_fail_count": 0,
                "dt_timeout_count": 0,
                "dt_not_implemented_count": 0,
                "failed_dts": [],
            }

        results = self.dt_results_payload.get("results", [])
        status_counts = {
            "PASS": 0,
            "FAIL": 0,
            "TIMEOUT": 0,
            "NOT_IMPLEMENTED": 0,
        }
        failed_dts = []
        for row in results:
            status = row.get("status", "UNKNOWN")
            if status in status_counts:
                status_counts[status] += 1
            if status != "PASS":
                failed_dts.append(
                    {
                        "dt": row.get("dt"),
                        "name": row.get("name"),
                        "status": status,
                        "output_tail": row.get("output", "")[-1500:],
                    }
                )

        dt_all_pass = (
            len(results) == 17
            and status_counts["FAIL"] == 0
            and status_counts["TIMEOUT"] == 0
            and status_counts["NOT_IMPLEMENTED"] == 0
        )
        return {
            "dt_all_pass": dt_all_pass,
            "dt_total": len(results),
            "dt_fail_count": status_counts["FAIL"],
            "dt_timeout_count": status_counts["TIMEOUT"],
            "dt_not_implemented_count": status_counts["NOT_IMPLEMENTED"],
            "failed_dts": failed_dts,
        }

    def _run_pytest_suite(self) -> None:
        test_run = self._run_command(
            "pytest_suite",
            [str(self.venv_python), "-m", "pytest", "-q"],
            cwd=self.repo_root,
        )
        self.pytest_pass = test_run.returncode == 0

    def _run_phase3_hostok_report(self) -> None:
        phase3_before = set(self.results_dir.glob("phase3_hostok_*.json"))
        phase3_run = self._run_command(
            "phase3_hostok_report",
            [str(self.venv_python), "validation/benchmarks/phase3_hostok_report.py"],
            cwd=self.repo_root,
        )
        if phase3_run.returncode != 0:
            raise RuntimeError("phase3_hostok_report failed.")

        produced = self._latest_new_file("phase3_hostok_*.json", phase3_before)
        if produced is None:
            raise RuntimeError("Phase3 hostok artifact was not produced.")
        payload = json.loads(produced.read_text(encoding="utf-8"))
        self.phase3_payload = payload
        self.phase3_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _overall_go(self) -> bool:
        dt_gate = self._dt_gate_status()
        phase3_ok = bool(self.phase3_payload and self.phase3_payload.get("overall_pass") is True)
        return (
            dt_gate["dt_all_pass"]
            and self.pytest_pass is True
            and phase3_ok
            and not self.missing_packages
        )

    def _build_claim_delta_markdown(self) -> str:
        prior_dt_status: dict[int, str] = {}
        if self.prior_dt_path and self.prior_dt_path.exists():
            try:
                prior_payload = json.loads(self.prior_dt_path.read_text(encoding="utf-8"))
                for row in prior_payload.get("results", []):
                    prior_dt_status[int(row.get("dt"))] = str(row.get("status"))
            except Exception:
                prior_dt_status = {}

        current_dt_status: dict[int, str] = {}
        if self.dt_results_payload:
            for row in self.dt_results_payload.get("results", []):
                current_dt_status[int(row.get("dt"))] = str(row.get("status"))

        prior_phase3 = None
        if self.prior_phase3_path and self.prior_phase3_path.exists():
            try:
                prior_phase3 = json.loads(self.prior_phase3_path.read_text(encoding="utf-8")).get("overall_pass")
            except Exception:
                prior_phase3 = None
        current_phase3 = self.phase3_payload.get("overall_pass") if self.phase3_payload else None

        lines = [
            f"# Claim Status Delta ({self.timestamp})",
            "",
            "## DT Status Delta",
            "",
            "| DT | Previous | Current | Delta |",
            "| --- | --- | --- | --- |",
        ]

        for dt_num in range(1, 18):
            prev = prior_dt_status.get(dt_num, "N/A")
            curr = current_dt_status.get(dt_num, "N/A")
            delta = "UNCHANGED" if prev == curr else "CHANGED"
            lines.append(f"| DT-{dt_num} | {prev} | {curr} | {delta} |")

        lines.extend(
            [
                "",
                "## Phase3 Host-OK Delta",
                "",
                "| Metric | Previous | Current | Delta |",
                "| --- | --- | --- | --- |",
                f"| overall_pass | {prior_phase3} | {current_phase3} | {'UNCHANGED' if prior_phase3 == current_phase3 else 'CHANGED'} |",
                "",
            ]
        )
        return "\n".join(lines) + "\n"

    def _build_falsification_markdown(self) -> str:
        dt_gate = self._dt_gate_status()
        phase3_overall = self.phase3_payload.get("overall_pass") if self.phase3_payload else None
        overall_go = self._overall_go()
        failed_dts = dt_gate["failed_dts"]

        lines = [
            f"# Falsification Results ({self.timestamp})",
            "",
            "## Gate Summary",
            "",
            f"- `DT full suite (DT-1..DT-17)`: {'PASS' if dt_gate['dt_all_pass'] else 'FAIL'}",
            f"- `pytest -q`: {'PASS' if self.pytest_pass else 'FAIL' if self.pytest_pass is False else 'SKIPPED'}",
            f"- `phase3_hostok_report overall_pass`: {phase3_overall}",
            f"- `overall verdict`: {'GO' if overall_go else 'NO-GO'}",
            "",
            "## DT Counts",
            "",
            f"- total: {dt_gate['dt_total']}",
            f"- fail: {dt_gate['dt_fail_count']}",
            f"- timeout: {dt_gate['dt_timeout_count']}",
            f"- not_implemented: {dt_gate['dt_not_implemented_count']}",
            "",
        ]

        if failed_dts:
            lines.extend(
                [
                    "## DT Failures",
                    "",
                ]
            )
            for row in failed_dts:
                lines.append(
                    f"- DT-{row['dt']} `{row['name']}` `{row['status']}`\n"
                    f"  - output_tail: `{row['output_tail'].replace(chr(10), ' | ')}`"
                )
            lines.append("")
        else:
            lines.extend(["## DT Failures", "", "- none", ""])

        if self.stop_reason:
            lines.extend(["## Stop Reason", "", f"- {self.stop_reason}", ""])

        return "\n".join(lines) + "\n"

    def _write_command_log(self) -> None:
        lines = [f"# Command Log ({self.timestamp})", ""]
        for idx, result in enumerate(self.command_results, start=1):
            lines.extend(
                [
                    f"## {idx}. {result.name}",
                    f"- cmd: `{' '.join(result.cmd)}`",
                    f"- cwd: `{result.cwd}`",
                    f"- start_utc: `{result.started_utc}`",
                    f"- end_utc: `{result.ended_utc}`",
                    f"- duration_s: `{result.duration_s:.3f}`",
                    f"- returncode: `{result.returncode}`",
                    "",
                    "### stdout",
                    "```text",
                    result.stdout.rstrip(),
                    "```",
                    "",
                    "### stderr",
                    "```text",
                    result.stderr.rstrip(),
                    "```",
                    "",
                ]
            )
        self.command_log_out.write_text("\n".join(lines), encoding="utf-8")

    def _write_repro_manifest_and_hashes(self) -> None:
        dt_gate = self._dt_gate_status()
        phase3_overall = self.phase3_payload.get("overall_pass") if self.phase3_payload else None
        overall_go = self._overall_go()

        artifact_paths = [
            self.dt_result_out,
            self.phase3_out,
            self.freeze_out,
            self.falsification_out,
            self.claim_delta_out,
            self.command_log_out,
        ]

        artifacts = []
        for path in artifact_paths:
            if path.exists():
                artifacts.append(
                    {
                        "path": str(path.relative_to(self.repo_root)),
                        "sha256": self._sha256(path),
                        "size_bytes": path.stat().st_size,
                    }
                )

        manifest = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "timestamp_token": self.timestamp,
            "repo_root": str(self.repo_root),
            "entrypoint": "scripts/run_repro_falsification.sh",
            "python_contract": {
                "executable": str(self.venv_python),
                "version": self._run_command(
                    "python_version_for_manifest", [str(self.venv_python), "-V"]
                ).stdout.strip(),
                "required_packages": REQUIRED_PACKAGES,
                "resolved_versions": self.dependency_versions,
                "missing_packages": self.missing_packages,
            },
            "toolchain_contract": {
                "versions": self.toolchain_versions,
                "required_targets": REQUIRED_RUST_TARGETS,
                "installed_targets": self.installed_targets,
            },
            "pip_freeze_snapshot": {
                "path": str(self.freeze_out.relative_to(self.repo_root)),
                "sha256": self._sha256(self.freeze_out) if self.freeze_out.exists() else None,
                "line_count": len(self.freeze_out.read_text(encoding="utf-8").splitlines())
                if self.freeze_out.exists()
                else 0,
            },
            "commands": [
                {
                    "name": row.name,
                    "cmd": row.cmd,
                    "cwd": str(row.cwd),
                    "returncode": row.returncode,
                    "started_utc": row.started_utc,
                    "ended_utc": row.ended_utc,
                    "duration_s": round(row.duration_s, 6),
                }
                for row in self.command_results
            ],
            "gates": {
                "dt_total": dt_gate["dt_total"],
                "dt_all_pass": dt_gate["dt_all_pass"],
                "dt_fail_count": dt_gate["dt_fail_count"],
                "dt_timeout_count": dt_gate["dt_timeout_count"],
                "dt_not_implemented_count": dt_gate["dt_not_implemented_count"],
                "pytest_pass": self.pytest_pass,
                "phase3_overall_pass": phase3_overall,
                "overall_go": overall_go,
            },
            "artifacts": artifacts,
            "stop_reason": self.stop_reason,
        }

        self.repro_manifest_out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        hash_lines = []
        hash_targets = [
            self.dt_result_out,
            self.phase3_out,
            self.repro_manifest_out,
            self.freeze_out,
            self.falsification_out,
            self.claim_delta_out,
            self.command_log_out,
        ]
        for path in hash_targets:
            if path.exists():
                hash_lines.append(
                    f"{self._sha256(path)}  {path.relative_to(self.repo_root).as_posix()}"
                )
        self.repro_hashes_out.write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    def _write_outputs(self) -> None:
        if self.dt_results_payload is None:
            self.dt_result_out.write_text(
                json.dumps(
                    {
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "results": [],
                        "status": "NO_RESULTS",
                        "reason": self.stop_reason,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

        if self.phase3_payload is None:
            self.phase3_payload = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "phase": "Phase 3 Embedded (Host-OK)",
                "overall_pass": False,
                "status": "NO_RESULTS",
                "reason": self.stop_reason,
            }
            self.phase3_out.write_text(json.dumps(self.phase3_payload, indent=2), encoding="utf-8")

        self.claim_delta_out.write_text(self._build_claim_delta_markdown(), encoding="utf-8")
        self.falsification_out.write_text(self._build_falsification_markdown(), encoding="utf-8")
        self._write_command_log()
        self._write_repro_manifest_and_hashes()


def main() -> int:
    runner = Runner()
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
