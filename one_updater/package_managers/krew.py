"""kubectl-krew package manager implementation."""

from typing import Optional

from .base import PackageManager


class KubectlKrewManager(PackageManager):
    """Manager for kubectl-krew packages."""

    def is_available(self) -> bool:
        """Check if kubectl-krew is available."""
        return self.run_command(["which", "kubectl-krew"])

    def update(self) -> bool:
        """Update kubectl-krew package lists."""
        if not self.is_available():
            return False
        return self.run_command(
            self.commands.get("update", ["kubectl", "krew", "update"])
        )

    def upgrade(self) -> bool:
        """Upgrade kubectl-krew packages."""
        if not self.is_available():
            return False
        return self.run_command(
            self.commands.get("upgrade", ["kubectl", "krew", "upgrade"])
        )

    def list_packages(self) -> Optional[list[str]]:
        """Return all installed krew plugin names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["kubectl", "krew", "list"])
        if not ok or not stdout:
            return []
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    def install_package(self, name: str) -> bool:
        """Install a krew plugin by name."""
        if not self.is_available():
            return False
        return self.run_command(["kubectl", "krew", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a krew plugin is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
