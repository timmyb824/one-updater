"""pip package manager implementation."""

import json
import logging
import subprocess
from pathlib import Path

from .base import PackageManager


class PipManager(PackageManager):
    """Manager for pip packages."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.virtualenv = config.get("virtualenv")
        self.pyenv = config.get("pyenv")

    def is_available(self) -> bool:
        """Check if pip is available."""
        return self.run_command(["which", "pip"])

    def _get_pip_command(self) -> list[str]:
        """Get the correct pip command based on virtualenv/pyenv settings."""
        if self.virtualenv:
            return [str(Path(self.virtualenv) / "bin" / "pip")]
        return ["pip"]

    def _check_available(self, operation: str) -> bool:
        """Check if pip is available for the given operation."""
        if not self.is_available():
            logging.info(f"pip is not installed. Skipping {operation}.")
            return False
        return True

    def update(self) -> bool:
        """Update pip package lists.

        pip doesn't have a separate update operation, as it checks PyPI
        directly when installing or upgrading packages.
        """
        if not self._check_available("update"):
            return False
        # pip doesn't need a separate update operation
        return self.run_command(self.commands.get("update", []))

    def upgrade(self) -> bool:
        """Upgrade pip packages."""
        if not self._check_available("upgrade"):
            return False

        success = True
        pip_cmd = self._get_pip_command()

        try:
            if self.verbose:
                logging.info("Checking for outdated packages...")
            # Get list of outdated packages using JSON format
            result = subprocess.run(
                pip_cmd + ["list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )

            try:
                packages = json.loads(result.stdout)
                if not packages:
                    logging.info("No outdated packages found.")
                    return True

                if self.verbose:
                    package_names = [pkg["name"] for pkg in packages]
                    logging.info(
                        f"Found {len(packages)} outdated packages: {', '.join(package_names)}"
                    )

                # Upgrade each package
                for package in packages:
                    package_name = package["name"]
                    if self.verbose:
                        current_version = package.get("version", "unknown")
                        latest_version = package.get("latest_version", "unknown")
                        logging.info(
                            f"Upgrading {package_name} from {current_version} to {latest_version}..."
                        )

                    try:
                        upgrade_cmd = self.commands.get(
                            "upgrade", pip_cmd + ["install", "--upgrade"]
                        )
                        if not self.run_command(upgrade_cmd + [package_name]):
                            logging.error(f"Failed to upgrade {package_name}")
                            success = False
                    except Exception as e:
                        logging.error(f"Error upgrading {package_name}: {e}")
                        success = False

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON output: {e}")
                if self.verbose:
                    logging.error(f"Raw output: {result.stdout}")
                success = False

        except subprocess.CalledProcessError as e:
            logging.error(f"Error listing outdated packages: {e}")
            if e.stderr:
                logging.error(f"Error output: {e.stderr}")
            success = False
        except Exception as e:
            logging.error(f"Unexpected error during pip upgrade: {e}")
            success = False

        return success
