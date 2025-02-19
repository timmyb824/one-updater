"""uv package manager implementation."""

from .base import PackageManager


class UvManager(PackageManager):
    """Manager for uv pages."""

    def is_available(self) -> bool:
        """Check if uv is available."""
        return self.run_command(["which", "uv"])

    def update(self) -> bool:
        """Update uv itself."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["uv", "self", "update"]))

    def upgrade(self) -> bool:
        """Upgrade uv tool packages."""
        if not self.is_available():
            return False
        # uv tool upgrade --all handles both update and upgrade
        return self.run_command(
            self.commands.get("upgrade", ["uv", "tool", "upgrade", "--all"])
        )
