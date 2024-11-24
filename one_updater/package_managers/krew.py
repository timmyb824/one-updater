"""kubectl-krew package manager implementation."""
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
