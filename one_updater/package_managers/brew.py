"""Homebrew package manager implementation."""

import subprocess
import sys
from typing import Optional

from .base import PackageManager


class HomebrewManager(PackageManager):
    """Manager for Homebrew packages."""

    def is_available(self) -> bool:
        """Check if Homebrew is installed."""
        return self.run_command(["which", "brew"])

    def update(self) -> bool:
        """Update Homebrew package lists."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["brew", "update"]))

    def upgrade(self) -> bool:
        """Upgrade Homebrew packages."""
        if not self.is_available():
            return False

        # Use direct terminal connection for upgrade since it might need password input
        command = self.commands.get("upgrade", ["brew", "upgrade"])

        if self._status:
            # Pause the status spinner for potential password prompts
            self._status.stop()

        try:
            result = subprocess.run(
                command,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True,
            )
            success = True
        except subprocess.CalledProcessError:
            success = False

        if self._status:
            # Resume the status spinner
            self._status.start()

        return success

    def list_packages(self) -> Optional[list[str]]:
        """Return all installed Homebrew formulae and casks."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["brew", "list", "--formula"])
        formulae = stdout.splitlines() if ok and stdout else []
        ok, stdout, _ = self.run_command_with_output(["brew", "list", "--cask"])
        casks = stdout.splitlines() if ok and stdout else []
        return formulae + casks

    def install_package(self, name: str) -> bool:
        """Install a Homebrew formula or cask by name."""
        if not self.is_available():
            return False
        return self.run_command(["brew", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a Homebrew package is installed."""
        ok, _, _ = self.run_command_with_output(["brew", "list", name])
        return ok
