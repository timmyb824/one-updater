"""Pacman package manager implementation."""

import logging
from typing import Optional

from .base import PackageManager


class PacmanManager(PackageManager):
    """Package manager for Arch Linux systems using Pacman."""

    def __init__(self, config: dict):
        """Initialize Pacman package manager.

        Args:
            config: Configuration dictionary for the package manager
        """
        super().__init__(config)

    def _check_available(self, operation: str) -> bool:
        """Check if Pacman is available and the operation is supported.

        Args:
            operation: The operation to check for (update/upgrade)

        Returns:
            bool: True if available, False otherwise
        """
        if operation not in self.commands:
            if self.verbose:
                logging.warning(f"Operation {operation} not configured for Pacman")
            return False

        # Check if pacman is installed
        return self.run_command(["which", "pacman"])

    def is_available(self) -> bool:
        """Check if Pacman is available on the system.

        Returns:
            bool: True if Pacman is available, False otherwise
        """
        # Check if pacman is installed
        if not self.run_command(["which", "pacman"]):
            if self.verbose:
                logging.warning("Pacman is not installed")
            return False
        return True

    def update(self) -> bool:
        """Update Pacman package database.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_available("update"):
            return False

        # Sync package databases
        return self.run_command(self.commands["update"])

    def upgrade(self) -> bool:
        """Upgrade all packages managed by Pacman.

        Note: Pacman can combine update and upgrade with -Syu,
        but we keep them separate for consistency with other package managers.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_available("upgrade"):
            return False

        return self.run_command(self.commands["upgrade"])

    def list_packages(self) -> Optional[list[str]]:
        """Return all explicitly installed Pacman package names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["pacman", "-Qqe"])
        if not ok or not stdout:
            return []
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    def install_package(self, name: str) -> bool:
        """Install a Pacman package by name."""
        if not self.is_available():
            return False
        return self.run_command(["sudo", "pacman", "-S", "--noconfirm", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a Pacman package is installed."""
        ok, _, _ = self.run_command_with_output(["pacman", "-Q", name])
        return ok
