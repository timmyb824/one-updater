"""gh-cli package manager implementation."""
from .base import PackageManager


class GhCliManager(PackageManager):
    """Manager for GitHub CLI."""

    def is_available(self) -> bool:
        """Check if gh is available."""
        return self.run_command(["which", "gh"])

    def update(self) -> bool:
        """Update GitHub CLI."""
        if not self.is_available():
            return False
        return self.run_command(
            self.commands.get("update", ["gh", "extension", "upgrade", "--all"])
        )

    def upgrade(self) -> bool:
        """Upgrade GitHub CLI extensions."""
        if not self.is_available():
            return False
        return self.run_command(
            self.commands.get("upgrade", ["gh", "extension", "upgrade", "--all"])
        )
