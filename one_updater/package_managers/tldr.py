"""tldr package manager implementation."""

from .base import PackageManager


class TldrManager(PackageManager):
    """Manager for tldr pages."""

    def is_available(self) -> bool:
        """Check if tldr is available."""
        return self.run_command(["which", "tldr"])

    def update(self) -> bool:
        """Update tldr pages cache."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["tldr", "--update"]))

    def upgrade(self) -> bool:
        """Upgrade tldr pages cache."""
        if not self.is_available():
            return False
        # tldr --update handles both update and upgrade
        return self.run_command(self.commands.get("upgrade", ["tldr", "--update"]))
