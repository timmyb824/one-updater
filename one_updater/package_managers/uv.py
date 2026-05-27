"""uv package manager implementation."""

from typing import Optional

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

    def list_packages(self) -> Optional[list[str]]:
        """Return all uv tool package names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["uv", "tool", "list"])
        if not ok or not stdout:
            return []
        return [
            line.split()[0]
            for line in stdout.splitlines()
            if line and not line.startswith(" ") and not line.startswith("-")
        ]

    def install_package(self, name: str) -> bool:
        """Install a uv tool package by name."""
        if not self.is_available():
            return False
        return self.run_command(["uv", "tool", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a uv tool package is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
