"""Flatpak package manager implementation."""

import logging

from .base import PackageManager


class FlatpakManager(PackageManager):
    """Package manager for Flatpak applications."""

    def __init__(self, config: dict):
        """Initialize Flatpak package manager.

        Args:
            config: Configuration dictionary for the package manager
        """
        super().__init__(config)

    def _check_available(self, operation: str) -> bool:
        """Check if Flatpak is available and the operation is supported.

        Args:
            operation: The operation to check for (update/upgrade)

        Returns:
            bool: True if available, False otherwise
        """
        if operation not in self.commands:
            if self.verbose:
                logging.warning(f"Operation {operation} not configured for Flatpak")
            return False

        # Check if flatpak is installed
        return self.run_command(["which", "flatpak"])

    def is_available(self) -> bool:
        """Check if Flatpak is available on the system.

        Returns:
            bool: True if Flatpak is available, False otherwise
        """
        # Check if flatpak is installed
        if not self.run_command(["which", "flatpak"]):
            if self.verbose:
                logging.warning("Flatpak is not installed")
            return False
        return True

    def update(self) -> bool:
        """Update Flatpak package lists.

        Note: Flatpak doesn't require a separate update operation,
        but we keep the method for consistency.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_available("update"):
            return False

        return self.run_command(self.commands.get("update", []))

    def upgrade(self) -> bool:
        """Upgrade all Flatpak applications.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_available("upgrade"):
            return False

        return self.run_command(self.commands["upgrade"])
