"""vagrant package manager implementation."""

from .base import PackageManager


class VagrantPluginManager(PackageManager):
    """Manager for vagrant packages."""

    def is_available(self) -> bool:
        """Check if vagrant is available."""
        return self.run_command(["which", "vagrant"])

    def update(self) -> bool:
        if not self.is_available():
            return False
        return self.run_command(["vagrant", "plugin", "update"])

    def upgrade(self) -> bool:
        if not self.is_available():
            return False
        return self.run_command(["vagrant", "plugin", "update"])
