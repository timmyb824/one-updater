"""gh-cli package manager implementation."""

from typing import Optional

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

    def list_packages(self) -> Optional[list[str]]:
        """Return all installed gh extension owner/repo identifiers."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["gh", "extension", "list"])
        if not ok or not stdout:
            return []
        packages = []
        for line in stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                packages.append(parts[1])  # owner/repo is second field
        return packages

    def install_package(self, name: str) -> bool:
        """Install a gh extension by owner/repo identifier."""
        if not self.is_available():
            return False
        return self.run_command(["gh", "extension", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a gh extension is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
