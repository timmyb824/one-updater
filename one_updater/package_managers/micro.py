"""micro-editor package manager implementation."""

from .base import PackageManager


class MicroEditorManager(PackageManager):
    """Manager for micro-editor packages."""

    def is_available(self) -> bool:
        """Check if micro is available."""
        return self.run_command(["which", "micro"])

    def update(self) -> bool:
        """Update micro-editor package lists."""
        if not self.is_available():
            return False
        return self.run_command(
            self.commands.get("update", ["micro", "-plugin", "update"])
        )

    def upgrade(self) -> bool:
        """Upgrade micro-editor packages."""
        if not self.is_available():
            return False
        # Micro editor's plugin update command handles both update and upgrade
        return self.run_command(
            self.commands.get("upgrade", ["micro", "-plugin", "update"])
        )
