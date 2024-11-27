"""DNF package manager implementation."""
import logging
from typing import List, Optional

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
