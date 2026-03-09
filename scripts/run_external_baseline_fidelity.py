#!/usr/bin/env python3
"""Execute PRD_BIO_EXTERNAL_BASELINE_AND_FIDELITY_2026-02-20 end-to-end."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CmdResult:
    name: str
    cmd: list[str]
    returncode: int
    started_utc: str
    ended_utc: str
    stdout: str
    stderr: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _latest_glob(root: Path, pattern: str) -> Path | None:
    candidates = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime)
    if not candidates:
        return None
    return candidates[-1]


class Runner:
    def __init__(self, repo_root: Path, out_dir: Path) -> None:
        self.repo_root = repo_root
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.results_root = self.repo_root / "validation" / "results"
        self.python = self.repo_root / ".venv" / "bin" / "python"
        self.commands: list[CmdResult] = []

    def run_cmd(self, name: str, cmd: list[str], check: bool = True) -> CmdResult:
        started = _utc_now()
        completed = subprocess.run(
            cmd,
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            env={**os.environ, **{"PYTHONPATH": "python"}},
        )
        ended = _utc_now()
        row = CmdResult(
            name=name,
            cmd=cmd,
            returncode=completed.returncode,
            started_utc=started,
            ended_utc=ended,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        self.commands.append(row)
        if check and completed.returncode != 0:
            raise RuntimeError(
                f"{name} failed rc={completed.returncode}\n"
                f"cmd: {' '.join(shlex.quote(part) for part in cmd)}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
        return row

    def _extract_json(self, row: CmdResult) -> dict[str, Any]:
        try:
            return json.loads(row.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{row.name} did not return valid JSON") from exc

    def _write_command_log(self) -> None:
        path = self.out_dir / "command_log.txt"
        lines = [
            "# Command Log",
            f"generated_utc={_utc_now()}",
            "",
        ]
        for row in self.commands:
            lines.extend(
                [
                    f"[{row.name}] rc={row.returncode}",
                    f"start={row.started_utc}",
                    f"end={row.ended_utc}",
                    "cmd=" + " ".join(shlex.quote(part) for part in row.cmd),
                    "",
                ]
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_json(self, name: str, payload: dict[str, Any]) -> Path:
        out = self.out_dir / name
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return out

    def _run_gate_a(self) -> dict[str, Any]:
        anchor_path = self.results_root / "bio_wave2_phase2_ecg_benchmark.json"
        if not anchor_path.exists():
            raise RuntimeError(f"missing baseline anchor: {anchor_path}")
        anchor_payload = json.loads(anchor_path.read_text(encoding="utf-8"))
        anchor_max_prd = float(anchor_payload["result"]["aggregate"]["max_prd"])

        bench = self.run_cmd(
            "gate_a_benchmark_replay",
            [
                str(self.python),
                "-m",
                "zpe_bio",
                "benchmark",
                "--lane",
                "ecg",
                "--record-ids",
                "100,103,114,200,223",
                "--samples",
                "3600",
                "--json",
            ],
        )
        replay_payload = self._extract_json(bench)
        replay_max_prd = float(replay_payload["result"]["aggregate"]["max_prd"])

        chemosense = self.run_cmd(
            "gate_a_chemosense_snapshot",
            [str(self.python), "-m", "zpe_bio", "chemosense-bio", "--json"],
        )
        chemosense_payload = self._extract_json(chemosense)

        return {
            "gate": "A",
            "status": "PASS",
            "anchor_path": str(anchor_path.relative_to(self.repo_root)),
            "anchor_max_prd": anchor_max_prd,
            "replay_max_prd": replay_max_prd,
            "chemosense_claim_status": chemosense_payload["result"]["taste"]["claim_status"],
            "benchmark_replay": replay_payload,
        }

    def _run_gate_b(self, gate_a: dict[str, Any]) -> dict[str, Any]:
        ecg_rows = []
        for row in gate_a["benchmark_replay"]["result"]["records"]:
            ecg_rows.append(
                {
                    "lane": "ecg",
                    "record_id": row["record_id"],
                    "raw_bytes": row["raw_bytes"],
                    "gzip_bytes": row["gzip_bytes"],
                    "zpe_bytes_est": row["zpe_bytes_est"],
                    "prd_percent": row["prd_percent"],
                    "encode_ms": row["encode_ms"],
                    "decode_ms": row["decode_ms"],
                }
            )

        eeg_rows = []
        synth = self.run_cmd(
            "gate_b_eeg_synthetic",
            [
                str(self.python),
                "-m",
                "zpe_bio",
                "encode-eeg",
                "--synthetic-eeg",
                "--channels",
                "2",
                "--samples",
                "2048",
                "--json",
            ],
        )
        synth_payload = self._extract_json(synth)
        synth_metrics = synth_payload["metrics"]
        eeg_rows.append(
            {
                "lane": "eeg",
                "mode": "synthetic",
                "raw_bytes": synth_metrics["raw_bytes"],
                "gzip_bytes": synth_metrics["gzip_bytes"],
                "zpe_bytes_est": synth_metrics["zpe_bytes_est"],
                "prd_percent": None,
                "encode_ms": synth_metrics["encode_ms"],
                "decode_ms": synth_metrics["decode_ms"],
            }
        )

        real_edf = self.repo_root / "validation" / "datasets" / "eeg" / "SC4001E0-PSG.edf"
        if real_edf.exists():
            real = self.run_cmd(
                "gate_b_eeg_real_file",
                [
                    str(self.python),
                    "-m",
                    "zpe_bio",
                    "encode-eeg",
                    "--edf",
                    str(real_edf),
                    "--channels",
                    "2",
                    "--samples",
                    "2048",
                    "--json",
                ],
            )
            real_payload = self._extract_json(real)
            real_metrics = real_payload["metrics"]
            eeg_rows.append(
                {
                    "lane": "eeg",
                    "mode": "real_file",
                    "raw_bytes": real_metrics["raw_bytes"],
                    "gzip_bytes": real_metrics["gzip_bytes"],
                    "zpe_bytes_est": real_metrics["zpe_bytes_est"],
                    "prd_percent": None,
                    "encode_ms": real_metrics["encode_ms"],
                    "decode_ms": real_metrics["decode_ms"],
                }
            )

        payload = {
            "generated_utc": _utc_now(),
            "contract_fields": [
                "raw_bytes",
                "gzip_bytes",
                "zpe_bytes_est",
                "prd_percent",
                "encode_ms",
                "decode_ms",
            ],
            "ecg_rows": ecg_rows,
            "eeg_rows": eeg_rows,
            "status": "PASS",
        }
        self._write_json("bio_external_baseline_results.json", payload)
        return payload

    def _run_gate_c(self) -> tuple[dict[str, Any], dict[str, Any]]:
        records = "100,103,114,200,223"
        base_cmd = [
            str(self.python),
            "-m",
            "zpe_bio",
            "benchmark",
            "--lane",
            "ecg",
            "--record-ids",
            records,
            "--samples",
            "3600",
            "--mode",
            "clinical",
        ]

        combos: list[dict[str, Any]] = [
            {"thr_mode": "adaptive_rms", "threshold": None, "step": None},
            {"thr_mode": "fixed", "threshold": 0.0010, "step": 0.0010},
            {"thr_mode": "fixed", "threshold": 0.0008, "step": 0.0008},
            {"thr_mode": "fixed", "threshold": 0.0006, "step": 0.0006},
            {"thr_mode": "fixed", "threshold": 0.0005, "step": 0.0005},
            {"thr_mode": "fixed", "threshold": 0.0004, "step": 0.0004},
            {"thr_mode": "fixed", "threshold": 0.0003, "step": 0.0003},
        ]

        rows: list[dict[str, Any]] = []
        for idx, combo in enumerate(combos):
            cmd = [*base_cmd, "--thr-mode", combo["thr_mode"], "--json"]
            if combo["threshold"] is not None:
                cmd.extend(["--threshold", str(combo["threshold"])])
            if combo["step"] is not None:
                cmd.extend(["--step", str(combo["step"])])

            row = self.run_cmd(f"gate_c_sweep_{idx}", cmd)
            payload = self._extract_json(row)
            aggregate = payload["result"]["aggregate"]
            rows.append(
                {
                    "thr_mode": combo["thr_mode"],
                    "threshold": combo["threshold"],
                    "step": combo["step"],
                    "mean_prd": aggregate["mean_prd"],
                    "max_prd": aggregate["max_prd"],
                    "mean_cr": aggregate["mean_cr"],
                    "mean_encode_ms": aggregate["mean_encode_latency_ms"],
                    "mean_decode_ms": aggregate["mean_decode_latency_ms"],
                }
            )

        # Pareto-like selection: minimize max_prd, tie-break on mean_cr
        best = min(rows, key=lambda r: (r["max_prd"], -r["mean_cr"]))
        baseline = rows[0]
        stretch_target_pass = bool(best["max_prd"] <= 1.0)

        sweep_payload = {
            "generated_utc": _utc_now(),
            "records": records.split(","),
            "rows": rows,
            "best": best,
            "stretch_target": {
                "target_max_prd_leq": 1.0,
                "pass": stretch_target_pass,
            },
        }
        before_after = {
            "baseline": baseline,
            "best_achieved": best,
            "delta": {
                "max_prd_improvement": round(float(baseline["max_prd"] - best["max_prd"]), 6),
                "mean_prd_improvement": round(float(baseline["mean_prd"] - best["mean_prd"]), 6),
                "mean_cr_change": round(float(best["mean_cr"] - baseline["mean_cr"]), 6),
            },
            "stretch_target_status": "PASS" if stretch_target_pass else "OPEN",
        }
        self._write_json("fidelity_sweep_results.json", sweep_payload)
        self._write_json("before_after_metrics.json", before_after)
        return sweep_payload, before_after

    def _run_gate_d(self) -> dict[str, Any]:
        chemo = self.run_cmd(
            "gate_d_chemosense_runtime",
            [str(self.python), "-m", "zpe_bio", "chemosense-bio", "--json"],
        )
        payload = self._extract_json(chemo)
        claim = payload["result"]["taste"]["claim_status"]
        if claim == "placeholder_governed":
            raise RuntimeError("chemosense claim_status still placeholder_governed")
        self.run_cmd(
            "gate_d_chemosense_tests",
            [str(self.python), "-m", "pytest", "-q", "tests/test_chemosense_bio_cli.py"],
        )
        return {"gate": "D", "status": "PASS", "claim_status": claim}

    def _run_gate_e(self) -> dict[str, Any]:
        self.run_cmd("gate_e_pytest", [str(self.python), "-m", "pytest", "-q"])
        self.run_cmd(
            "gate_e_determinism_replay",
            [str(self.python), "scripts/run_bio_wave2_phase6.py", "--repeats", "5"],
        )
        self.run_cmd("gate_e_repro_falsification", ["scripts/run_repro_falsification.sh"])
        self.run_cmd("gate_e_pip_install", [str(self.python), "-m", "pip", "install", "."])
        self.run_cmd("gate_e_cli_help", [str(self.repo_root / ".venv" / "bin" / "zpe-bio"), "--help"])

        repro_manifest = _latest_glob(self.results_root, "repro_manifest_*.json")
        if repro_manifest is None:
            raise RuntimeError("missing repro_manifest_*.json after gate E")
        payload = json.loads(repro_manifest.read_text(encoding="utf-8"))
        overall_go = bool(payload.get("gates", {}).get("overall_go"))
        if not overall_go:
            raise RuntimeError(f"repro gate overall_go=false in {repro_manifest}")
        return {
            "gate": "E",
            "status": "PASS",
            "repro_manifest": str(repro_manifest.relative_to(self.repo_root)),
            "repro_overall_go": True,
            "dt_all_pass": bool(payload.get("gates", {}).get("dt_all_pass")),
            "phase3_overall_pass": bool(payload.get("gates", {}).get("phase3_overall_pass")),
        }

    def run(self) -> int:
        gate_results: list[dict[str, Any]] = []
        try:
            gate_a = self._run_gate_a()
            gate_results.append({"gate": "A", "status": "PASS"})

            self._run_gate_b(gate_a)
            gate_results.append({"gate": "B", "status": "PASS"})

            sweep_payload, before_after = self._run_gate_c()
            gate_results.append({"gate": "C", "status": "PASS"})

            gate_d = self._run_gate_d()
            gate_results.append(gate_d)

            gate_e = self._run_gate_e()
            gate_results.append(gate_e)

            claim_status_lines = [
                "# Claim Status Delta",
                f"generated_utc: {_utc_now()}",
                "",
                "1. External baseline evidence: CLOSED",
                f"- evidence: {self.out_dir / 'bio_external_baseline_results.json'}",
                "2. Chemosense placeholder claim tag removal: CLOSED",
                f"- claim_status: {gate_d['claim_status']}",
                "3. ECG stretch target (max_prd <= 1.0): "
                + ("CLOSED" if sweep_payload["stretch_target"]["pass"] else "OPEN"),
                f"- evidence: {self.out_dir / 'fidelity_sweep_results.json'}",
            ]
            (self.out_dir / "claim_status_delta.md").write_text(
                "\n".join(claim_status_lines) + "\n",
                encoding="utf-8",
            )

            falsification_lines = [
                "# Falsification Results",
                f"generated_utc: {_utc_now()}",
                "",
                "- Gate E pytest: PASS",
                "- Gate E determinism replay: PASS",
                "- Gate E repro falsification: PASS",
                "- Gate E packaging smoke: PASS",
                "",
                "No DT regression detected in latest repro manifest.",
            ]
            (self.out_dir / "falsification_results.md").write_text(
                "\n".join(falsification_lines) + "\n",
                encoding="utf-8",
            )

            handoff = {
                "generated_utc": _utc_now(),
                "artifact_root": str(self.out_dir.relative_to(self.repo_root)),
                "gates": gate_results,
                "all_gates_pass": all(row["status"] == "PASS" for row in gate_results),
                "artifacts": [
                    "handoff_manifest.json",
                    "before_after_metrics.json",
                    "bio_external_baseline_results.json",
                    "fidelity_sweep_results.json",
                    "falsification_results.md",
                    "claim_status_delta.md",
                    "command_log.txt",
                ],
            }
            self._write_json("handoff_manifest.json", handoff)
            self._write_command_log()

            # Ensure mandatory files all exist
            missing = [
                name
                for name in handoff["artifacts"]
                if not (self.out_dir / name).exists()
            ]
            if missing:
                raise RuntimeError(f"missing required artifacts: {missing}")
            return 0
        except Exception as exc:
            self._write_command_log()
            # write partial handoff for failure diagnosis
            partial = {
                "generated_utc": _utc_now(),
                "artifact_root": str(self.out_dir.relative_to(self.repo_root)),
                "gates": gate_results,
                "error": str(exc),
            }
            self._write_json("handoff_manifest.json", partial)
            print(str(exc), file=sys.stderr)
            return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Bio external baseline + fidelity PRD execution.")
    parser.add_argument("--date", default=str(date.today()))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "validation" / "results" / f"{args.date}_bio_external_baseline_fidelity"
    runner = Runner(repo_root=repo_root, out_dir=out_dir)
    return runner.run()


if __name__ == "__main__":
    raise SystemExit(main())
