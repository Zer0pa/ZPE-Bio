"""
DT-13: Cross-Platform Parity
PRD: §2.1 | INV-DET
PASS CONDITION: Python and Rust outputs are byte-identical
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import subprocess
import sys
from pathlib import Path

def main():
    print("Executing DT-13: Cross-Platform Parity (Host-Side Audit)...")
    print("-" * 60)
    
    repo_root = Path(__file__).resolve().parents[2]
    parity_test = repo_root / "tests" / "test_parity.py"
    rust_core_dir = repo_root / "core" / "rust"
    
    try:
        parity = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(parity_test), "-rs"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if parity.returncode != 0:
            print("FAIL: Parity mismatch detected ❌")
            print(parity.stdout)
            print(parity.stderr)
            sys.exit(1)
        if "skipped" in parity.stdout.lower():
            print("FAIL: Parity test was skipped (Rust dynamic library missing) ❌")
            print(parity.stdout)
            sys.exit(1)

        print("Host parity verified (Python vs Rust FFI).")

        arm_check = subprocess.run(
            [
                "cargo",
                "check",
                "--release",
                "--target",
                "thumbv8m.main-none-eabi",
                "--no-default-features",
                "--features",
                "embedded",
            ],
            capture_output=True,
            text=True,
            cwd=rust_core_dir,
        )
        if arm_check.returncode != 0:
            print("FAIL: Rust core did not compile for ARM target ❌")
            print(arm_check.stdout[-2000:])
            print(arm_check.stderr[-2000:])
            sys.exit(1)

        print("PASS: Cross-platform parity + ARM compile audit passed ✅")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Could not run parity test — {e} ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
