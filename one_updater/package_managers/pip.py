"""pip package manager implementation."""

import json
import logging
import os
import subprocess
from pathlib import Path

from .base import PackageManager


class PipManager(PackageManager):
    """Manager for pip packages."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.virtualenv = config.get("virtualenv")
        self.pyenv_versions = self._get_pyenv_versions(config)
        if self.virtualenv and self.pyenv_versions:
            logging.warning(
                "Both virtualenv and pyenv_versions specified. Using virtualenv."
            )

    def _get_pyenv_versions(self, config: dict) -> list[str]:
        """Get list of pyenv versions from config."""
        pyenv_version = config.get("pyenv_version")
        if isinstance(pyenv_version, list):
            return pyenv_version
        elif isinstance(pyenv_version, str):
            return [pyenv_version] if pyenv_version else []
        return []

    def is_available(self) -> bool:
        """Check if pip is available in any specified environment."""
        if self.virtualenv:
            return self._check_virtualenv()
        elif self.pyenv_versions:
            return any(self._check_pyenv(version) for version in self.pyenv_versions)
        return self.run_command(["pip", "--version"])

    def _check_virtualenv(self) -> bool:
        """Check if virtualenv is available and valid."""
        pip_path = str(Path(self.virtualenv) / "bin" / "pip")
        if not os.path.exists(pip_path):
            logging.error(f"Virtualenv pip not found at: {pip_path}")
            return False
        if self.verbose:
            logging.info(f"Using virtualenv pip: {pip_path}")
        return True

    def _check_pyenv(self, version: str) -> bool:
        # sourcery skip: extract-method
        """Check if pyenv is available and the specified version exists."""
        try:
            # Check if pyenv is installed and get root
            result = subprocess.run(
                ["pyenv", "root"], capture_output=True, text=True, check=True
            )
            pyenv_root = result.stdout.strip()
            if not pyenv_root:
                logging.error("Could not determine pyenv root")
                return False

            # Check if version exists
            version_path = os.path.join(pyenv_root, "versions", version)
            if not os.path.exists(version_path):
                logging.error(f"pyenv version {version} not found at {version_path}")
                return False

            if self.verbose:
                logging.info(f"Found pyenv version at: {version_path}")
            return True

        except subprocess.CalledProcessError as e:
            logging.error(f"Error checking pyenv: {e}")
            if self.verbose and e.stderr:
                logging.error(f"Error output: {e.stderr}")
            return False

    def _get_pip_commands(self) -> list[list[str]]:
        """Get all pip commands based on virtualenv/pyenv settings."""
        if self.virtualenv:
            pip_path = str(Path(self.virtualenv) / "bin" / "pip")
            if not os.path.exists(pip_path):
                logging.error(f"Virtualenv pip not found at: {pip_path}")
                return [["pip"]]  # Fallback to system pip
            if self.verbose:
                logging.info(f"Using virtualenv pip: {pip_path}")
            return [[pip_path]]
        elif self.pyenv_versions:
            try:
                # Get pyenv root
                if self.verbose:
                    logging.info("Getting pyenv root directory...")
                result = subprocess.run(
                    ["pyenv", "root"], capture_output=True, text=True, check=True
                )
                pyenv_root = result.stdout.strip()
                if self.verbose:
                    logging.info(f"Found pyenv root at: {pyenv_root}")

                # Get pip path for each version
                commands = []
                for version in self.pyenv_versions:
                    if self._check_pyenv(version):
                        pip_path = os.path.join(
                            pyenv_root, "versions", version, "bin", "pip"
                        )
                        if self.verbose:
                            logging.info(
                                f"Using pip from pyenv version {version}: {pip_path}"
                            )
                        commands.append([pip_path])

                if not commands and self.verbose:
                    logging.warning(
                        "No valid pyenv versions found, falling back to system pip"
                    )
                return commands or [
                    ["pip"]
                ]  # Fallback to system pip if no valid versions
            except subprocess.CalledProcessError as e:
                logging.error(f"Error getting pyenv root: {e}")
                if self.verbose and e.stderr:
                    logging.error(f"Error output: {e.stderr}")
                return [["pip"]]
        if self.verbose:
            logging.info("Using system pip")
        return [["pip"]]

    def update(self) -> bool:
        """Update pip package lists.

        pip doesn't have a separate update operation, as it checks PyPI
        directly when installing or upgrading packages.
        """
        if not self.is_available():
            return False
        # pip doesn't need a separate update operation
        return all(
            self.run_command(self.commands.get("update", []))
            for _ in self._get_pip_commands()
        )

    def upgrade(self) -> bool:
        """Upgrade pip packages in all specified environments."""
        if not self.is_available():
            return False

        success = True
        for pip_cmd in self._get_pip_commands():
            if not self._upgrade_environment(pip_cmd):
                success = False

        return success

    def _upgrade_environment(self, pip_cmd: list[str]) -> bool:
        """Upgrade packages in a specific pip environment."""
        if not pip_cmd:
            return False

        try:
            if self.verbose:
                logging.info(
                    f"Checking for outdated packages using: {' '.join(pip_cmd)}"
                )
            # Get list of outdated packages using JSON format
            result = subprocess.run(
                pip_cmd + ["list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )

            try:
                packages = json.loads(result.stdout)
                if self.verbose:
                    logging.info(f"Raw outdated packages output: {result.stdout}")
                if not packages:
                    if self.verbose:
                        logging.info("No outdated packages found in JSON response")
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

                    # Get base upgrade command or use default pip install --upgrade
                    upgrade_cmd = self.commands.get("upgrade", []) or pip_cmd + [
                        "install",
                        "--upgrade",
                    ]

                    # Add package name to the command
                    package_cmd = upgrade_cmd + [package_name]
                    if self.verbose:
                        logging.info(
                            f"Running upgrade command: {' '.join(package_cmd)}"
                        )

                    result = subprocess.run(
                        package_cmd,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode != 0:
                        logging.error(
                            f"Failed to upgrade {package_name}: {result.stderr}"
                        )
                        return False
                    elif self.verbose:
                        logging.info(f"Upgrade output: {result.stdout}")

                return True

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse pip output as JSON: {e}")
                if self.verbose:
                    logging.error(f"Raw output was: {result.stdout}")
                return False

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to check for outdated packages: {e}")
            if self.verbose and e.stderr:
                logging.error(f"Error output: {e.stderr}")
            return False
