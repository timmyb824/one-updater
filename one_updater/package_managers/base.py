import logging
import subprocess
from abc import ABC, abstractmethod
from typing import Optional


class PackageManager(ABC):
    """Base class for all package managers."""

    def __init__(self, config: dict):
        """Initialize the package manager with its configuration."""
        self.config = config
        self.enabled = config.get("enabled", True)
        self.commands = config.get("commands", {})
        self.verbose = config.get("verbose", False)

    def run_command(self, command: list[str]) -> bool:
        """Run a command and return True if it succeeded."""
        if not command:
            return True

        try:
            if self.verbose:
                logging.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                logging.info(
                    f"INFO - stdout from {' '.join(command)}:\n{result.stdout}"
                )
            return True
        except subprocess.CalledProcessError as e:
            if self.verbose:
                logging.error(f"Command failed with exit code {e.returncode}")
                if e.stdout:
                    logging.error(f"stdout: {e.stdout}")
                if e.stderr:
                    logging.error(f"stderr: {e.stderr}")
            if e.stdout:
                logging.error(f"ERROR - stdout from {' '.join(command)}:\n{e.stdout}")
            if e.stderr:
                logging.error(f"ERROR - stderr from {' '.join(command)}:\n{e.stderr}")
            return False

    def run_command_with_output(
        self, command: list[str]
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr

    def _check_available(self, operation: str) -> bool:
        """Check if package manager is available and log if not.

        Args:
            operation: Name of the operation being attempted (e.g., 'update', 'upgrade')

        Returns:
            bool: True if available, False if not
        """
        if not self.is_available():
            manager_name = self.__class__.__name__.replace("Manager", "").lower()
            logging.info(f"{manager_name} is not available. Skipping {operation}.")
            return False
        return True

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this package manager is available on the system."""
        pass

    @abstractmethod
    def update(self) -> bool:
        """Update package lists/indices."""
        pass

    @abstractmethod
    def upgrade(self) -> bool:
        """Upgrade installed packages."""
        pass
