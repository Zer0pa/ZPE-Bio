"""
DT-6: RAM Budget Test
PRD: §2.1 | INV-RAM | REQ-EMBED-1
PASS CONDITION: Embedded static RAM sections (.data + .bss + .uninit) < 32 KB
EXIT CODE: 0 = PASS, 1 = FAIL

Host-side method: cross-compile thumb target and parse section sizes.
"""
import subprocess
import re
import sys
from pathlib import Path

MAX_RAM_BYTES = 32 * 1024
SECTIONS = (".data", ".bss", ".uninit")


def parse_section_sizes(output: str) -> dict[str, int]:
    sizes = {name: 0 for name in SECTIONS}
    for line in output.splitlines():
        m = re.match(r"^\s*(\.[A-Za-z0-9_]+)\s+([0-9]+)\b", line)
        if not m:
            continue
        sec = m.group(1)
        if sec in sizes:
            sizes[sec] = int(m.group(2))
    return sizes


def main() -> None:
    print("Executing DT-6: RAM Budget (Embedded Section Audit)...")
    print("-" * 60)

    repo_root = Path(__file__).resolve().parents[2]
    embedded_dir = repo_root / "embedded" / "nrf5340"

    build_cmd = [
        "cargo", "build", "--release", "--target", "thumbv8m.main-none-eabi",
    ]
    size_cmd = [
        "cargo", "size", "--release", "--target", "thumbv8m.main-none-eabi", "--", "-A",
    ]

    try:
        build = subprocess.run(
            build_cmd,
            cwd=embedded_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if build.returncode != 0:
            print("FAIL: Embedded release build failed")
            print(build.stdout[-1200:])
            print(build.stderr[-1200:])
            sys.exit(1)

        sized = subprocess.run(
            size_cmd,
            cwd=embedded_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if sized.returncode != 0:
            print("FAIL: `cargo size` failed")
            print(sized.stdout[-1200:])
            print(sized.stderr[-1200:])
            sys.exit(1)
    except Exception as exc:
        print(f"FAIL: Could not execute embedded RAM audit ({exc})")
        sys.exit(1)

    sizes = parse_section_sizes(sized.stdout)
    static_ram = sum(sizes.values())

    print(f".data:   {sizes['.data']} bytes")
    print(f".bss:    {sizes['.bss']} bytes")
    print(f".uninit: {sizes['.uninit']} bytes")
    print(f"Static RAM total: {static_ram} bytes")
    print(f"Budget:           {MAX_RAM_BYTES} bytes")

    if static_ram <= MAX_RAM_BYTES:
        print("PASS: Embedded static RAM is within 32 KB")
        sys.exit(0)

    print("FAIL: Embedded static RAM exceeds 32 KB")
    sys.exit(1)


if __name__ == "__main__":
    main()
