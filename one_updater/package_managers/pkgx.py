"""pkgx package manager implementation."""

from .base import PackageManager


class PkgxManager(PackageManager):
    """Manager for pkgx packages."""

    def is_available(self) -> bool:
        """Check if pkgx is available."""
        return self.run_command(["which", "pkgx"])

    def update(self) -> bool:
        """Update npm package lists."""
        if not self.is_available():
            return False
        return self.run_command(
            self.commands.get("update", ["pkgx", "mash", "pkgx/cache", "upgrade"])
        )

    def upgrade(self) -> bool:
        """Upgrade npm packages."""
        if not self.is_available():
            return False
        # npm update -g handles both update and upgrade
        return self.run_command(
            self.commands.get("upgrade", ["pkgx", "mash", "pkgx/cache", "upgrade"])
        )
