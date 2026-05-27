"""DNF package manager implementation."""

import logging
from typing import Optional

from .base import PackageManager


class DnfManager(PackageManager):
    """Package manager for RHEL/Fedora systems using DNF."""

    def __init__(self, config: dict):
        """Initialize DNF package manager.

        Args:
            config: Configuration dictionary for the package manager
        """
        super().__init__(config)

    def _check_available(self, operation: str) -> bool:
        """Check if DNF is available and the operation is supported.

        Args:
            operation: The operation to check for (update/upgrade)

        Returns:
            bool: True if available, False otherwise
        """
        if operation not in self.commands:
            if self.verbose:
                logging.warning(f"Operation {operation} not configured for DNF")
            return False

        # Check if dnf is installed
        return self.run_command(["which", "dnf"])

    def is_available(self) -> bool:
        """Check if DNF is available on the system.

        Returns:
            bool: True if DNF is available, False otherwise
        """
        # Check if dnf is installed
        if not self.run_command(["which", "dnf"]):
            if self.verbose:
                logging.warning("DNF is not installed")
            return False
        return True

    def update(self) -> bool:
        """Update DNF package lists.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_available("update"):
            return False

        return self.run_command(self.commands["update"])

    def upgrade(self) -> bool:
        """Upgrade all packages managed by DNF.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_available("upgrade"):
            return False

        return self.run_command(self.commands["upgrade"])

    def list_packages(self) -> Optional[list[str]]:
        """Return all explicitly installed DNF package names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(
            ["dnf", "repoquery", "--installed", "--qf", "%{name}"]
        )
        if not ok or not stdout:
            return []
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    def install_package(self, name: str) -> bool:
        """Install a DNF package by name."""
        if not self.is_available():
            return False
        return self.run_command(["sudo", "dnf", "install", "-y", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a DNF package is installed."""
        ok, _, _ = self.run_command_with_output(["dnf", "list", "installed", name])
        return ok
