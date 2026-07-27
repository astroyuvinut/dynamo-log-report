"""
Verifier for dynamo/cross-compile-sqlite-cli.

Each test's docstring names the instruction.md success criterion it checks.
Input values are generated fresh at grade time so no hardcoded/stubbed
binary can fake the expected SUM.
"""
import os
import random
import subprocess
from pathlib import Path

import pytest

APP_DIR = Path("/app")
INPUT_CSV = APP_DIR / "input.csv"

TARGETS = {
    "x86_64-unknown-linux-gnu": {
        "path": APP_DIR / "target/x86_64-unknown-linux-gnu/release/app",
        "runner": lambda binpath, args: [str(binpath), *args],
    },
    "aarch64-unknown-linux-gnu": {
        "path": APP_DIR / "target/aarch64-unknown-linux-gnu/release/app",
        "runner": lambda binpath, args: ["qemu-aarch64-static", str(binpath), *args],
    },
    "armv7-unknown-linux-gnueabihf": {
        "path": APP_DIR / "target/armv7-unknown-linux-gnueabihf/release/app",
        "runner": lambda binpath, args: ["qemu-arm-static", str(binpath), *args],
    },
    "x86_64-pc-windows-gnu": {
        "path": APP_DIR / "target/x86_64-pc-windows-gnu/release/app.exe",
        "runner": lambda binpath, args: ["wine", str(binpath), *args],
    },
}


@pytest.fixture(scope="session")
def expected_sum():
    """Generate the grading input fresh (not known at build time) and
    return the correct sum, computed independently of any target binary."""
    random.seed()  # true per-run randomness, not a fixed seed
    values = [random.randint(1, 10_000) for _ in range(50)]
    INPUT_CSV.write_text("\n".join(str(v) for v in values) + "\n")
    return sum(values)


@pytest.mark.parametrize("triple", TARGETS.keys())
def test_binary_exists_and_matches_target(triple):
    """Criterion 1: all four binaries exist at the required paths."""
    info = TARGETS[triple]
    assert info["path"].exists(), f"missing binary for {triple}: {info['path']}"


@pytest.mark.parametrize("triple", TARGETS.keys())
def test_binary_produces_correct_sum(triple, expected_sum):
    """Criteria 2 and 3: each binary must load /app/input.csv and report
    the correct SUM via its real SQLite-backed code path. A stubbed or
    feature-disabled binary cannot know expected_sum in advance since the
    input is regenerated at grade time."""
    info = TARGETS[triple]
    binpath = info["path"]
    assert binpath.exists(), f"missing binary for {triple}"

    load_cmd = info["runner"](binpath, ["load", str(INPUT_CSV)])
    load_result = subprocess.run(load_cmd, capture_output=True, text=True, timeout=30)
    assert load_result.returncode == 0, f"{triple} load failed: {load_result.stderr}"
    assert "LOADED" in load_result.stdout

    sum_cmd = info["runner"](binpath, ["stats", "sum"])
    sum_result = subprocess.run(sum_cmd, capture_output=True, text=True, timeout=30)
    assert sum_result.returncode == 0, f"{triple} stats sum failed: {sum_result.stderr}"

    output = sum_result.stdout.strip()
    assert output == f"SUM={expected_sum}", (
        f"{triple}: expected SUM={expected_sum}, got '{output}' "
        f"(a stub/disabled-feature path would not know this value)"
    )
