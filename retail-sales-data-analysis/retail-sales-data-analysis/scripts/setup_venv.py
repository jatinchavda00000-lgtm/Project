# ============================================
# Retail Sales Data Analysis
# File: scripts/setup_venv.py
# Purpose: Cross-platform virtual environment setup helper
# ============================================

"""
Cross-platform virtual environment setup script.

Works on Windows, Linux, and macOS. Creates a virtual environment,
installs dependencies, and prints activation instructions.

Usage:
    python scripts/setup_venv.py
    python scripts/setup_venv.py --name myenv
    python scripts/setup_venv.py --no-install
    python scripts/setup_venv.py --force

Note:
    - No API is used anywhere in this project.
    - Requires Python 3.10+.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# ============================================
# PROJECT PATHS
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"


# ============================================
# HELPERS
# ============================================

def is_windows() -> bool:
    """True if running on Windows."""
    return os.name == "nt"


def venv_python(venv_dir: Path) -> Path:
    """Return the path to the venv's python executable."""
    if is_windows():
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_pip(venv_dir: Path) -> Path:
    """Return the path to the venv's pip executable."""
    if is_windows():
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def print_section(title: str) -> None:
    """Print a section header."""
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_activation_instructions(venv_dir: Path) -> None:
    """Print activation commands for Windows and Unix."""
    print()
    print("-" * 60)
    print("ACTIVATE THE ENVIRONMENT")
    print("-" * 60)

    if is_windows():
        print("  PowerShell :")
        print(f"    {venv_dir}\\Scripts\\Activate.ps1")
        print()
        print("  CMD :")
        print(f"    {venv_dir}\\Scripts\\activate.bat")
    else:
        print("  Bash / Zsh :")
        print(f"    source {venv_dir}/bin/activate")

    print()
    print("-" * 60)
    print("DEACTIVATE")
    print("-" * 60)
    print("  deactivate")
    print()


def check_python_version() -> None:
    """Ensure Python 3.10+ is being used."""
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 10):
        print(f"[ERROR] Python 3.10+ required. Found: {major}.{minor}")
        sys.exit(1)
    print(f"  Python version : {major}.{minor}")


# ============================================
# CORE STEPS
# ============================================

def create_venv(venv_dir: Path, force: bool = False) -> bool:
    """
    Create a virtual environment.

    Returns True if a new venv was created, False if it already existed
    and force was not set.
    """
    if venv_dir.exists():
        if not force:
            print(f"  [SKIP] Virtual env already exists: {venv_dir}")
            print(f"         Use --force to recreate it.")
            return False
        print(f"  [FORCE] Removing existing venv: {venv_dir}")
        shutil.rmtree(venv_dir, ignore_errors=True)

    print(f"  Creating venv: {venv_dir}")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "venv", str(venv_dir)]
        )
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed to create venv: {e}")
        sys.exit(1)

    print(f"  [OK] Created: {venv_dir}")
    return True


def upgrade_pip(venv_dir: Path) -> None:
    """Upgrade pip inside the virtual environment."""
    pip_exe = venv_pip(venv_dir)
    if not pip_exe.exists():
        print(f"  [WARN] pip not found at {pip_exe}. Skipping upgrade.")
        return

    print("  Upgrading pip...")
    try:
        subprocess.check_call(
            [str(pip_exe), "install", "--upgrade", "pip"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("  [OK] pip upgraded.")
    except subprocess.CalledProcessError:
        print("  [WARN] pip upgrade failed. Continuing anyway.")


def install_requirements(venv_dir: Path) -> None:
    """Install requirements.txt inside the virtual environment."""
    if not REQUIREMENTS_FILE.exists():
        print(f"  [ERROR] requirements.txt not found: {REQUIREMENTS_FILE}")
        sys.exit(1)

    pip_exe = venv_pip(venv_dir)
    if not pip_exe.exists():
        print(f"  [ERROR] pip not found in venv: {pip_exe}")
        sys.exit(1)

    print(f"  Installing from: {REQUIREMENTS_FILE.name}")
    try:
        subprocess.check_call(
            [str(pip_exe), "install", "-r", str(REQUIREMENTS_FILE)]
        )
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Dependency install failed: {e}")
        sys.exit(1)

    print("  [OK] All dependencies installed.")


def verify_install(venv_dir: Path) -> None:
    """Verify critical packages are importable."""
    python_exe = venv_python(venv_dir)
    if not python_exe.exists():
        print(f"  [WARN] Python not found in venv: {python_exe}")
        return

    packages = ["pandas", "numpy", "matplotlib", "seaborn", "sqlalchemy"]
    print("  Verifying packages...")

    for pkg in packages:
        try:
            subprocess.check_call(
                [str(python_exe), "-c", f"import {pkg}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"    [OK] {pkg}")
        except subprocess.CalledProcessError:
            print(f"    [MISSING] {pkg}")


# ============================================
# ARGUMENTS
# ============================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set up a virtual environment for the project."
    )
    parser.add_argument(
        "--name",
        type=str,
        default="venv",
        help="Virtual environment folder name (default: venv).",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Create the venv but do not install requirements.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate the venv if it already exists.",
    )
    return parser.parse_args()


# ============================================
# MAIN
# ============================================

def main() -> int:
    args = parse_args()
    venv_dir = PROJECT_ROOT / args.name

    print_section("VIRTUAL ENVIRONMENT SETUP")
    print(f"  Project root : {PROJECT_ROOT}")
    print(f"  Venv dir     : {venv_dir}")
    print(f"  OS           : {'Windows' if is_windows() else 'Unix-like'}")
    check_python_version()

    # Step 1 — create
    print_section("STEP 1 — CREATE VIRTUAL ENVIRONMENT")
    created = create_venv(venv_dir, force=args.force)

    if not created and not venv_dir.exists():
        print("  [ERROR] Venv not available. Aborting.")
        return 1

    # Step 2 — upgrade pip
    print_section("STEP 2 — UPGRADE PIP")
    upgrade_pip(venv_dir)

    # Step 3 — install
    if args.no_install:
        print_section("STEP 3 — INSTALL DEPENDENCIES (SKIPPED)")
        print("  --no-install flag set.")
    else:
        print_section("STEP 3 — INSTALL DEPENDENCIES")
        install_requirements(venv_dir)

    # Step 4 — verify
    print_section("STEP 4 — VERIFY INSTALLATION")
    verify_install(venv_dir)

    # Step 5 — instructions
    print_section("STEP 5 — NEXT STEPS")
    print_activation_instructions(venv_dir)
    print("After activation, run:")
    print("    python scripts/run_pipeline.py")
    print()
    print("=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())