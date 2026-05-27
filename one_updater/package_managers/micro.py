"""micro-editor package manager implementation."""

from typing import Optional

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

    def list_packages(self) -> Optional[list[str]]:
        """Return all non-built-in installed micro plugins."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["micro", "-plugin", "list"])
        if not ok or not stdout:
            return []
        packages = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line or "(built-in)" in line:
                continue
            parts = line.split()
            if parts and parts[0] not in ("The", "following", "plugins"):
                packages.append(parts[0])
        return packages

    def install_package(self, name: str) -> bool:
        """Install a micro plugin by name."""
        if not self.is_available():
            return False
        return self.run_command(["micro", "-plugin", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a micro plugin is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
