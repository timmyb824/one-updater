"""cargo package manager implementation."""

import logging
import subprocess

from .base import PackageManager


class CargoManager(PackageManager):
    """Manager for cargo packages."""

    def is_available(self) -> bool:
        """Check if cargo is available."""
        return self.run_command(["which", "cargo"])

    def update(self) -> bool:
        """Update cargo package lists."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["rustup", "update"]))

    def upgrade(self) -> bool:
        """Upgrade cargo packages."""
        if not self.is_available():
            logging.info("cargo is not installed. Skipping.")
            return False

        success = True
        # First update rustup
        success &= self.run_command(self.commands.get("update", ["rustup", "update"]))

        # Check if upgrade command is configured (even if empty list)
        if "upgrade" not in self.commands:
            logging.info("cargo upgrade command not configured. Skipping.")
            return success

        # Get list of installed packages
        try:
            result = subprocess.run(
                ["cargo", "install", "--list"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Parse output to get package names
            # Output format is like:
            # package-name v1.2.3:
            #     package-name
            packages = []
            for line in result.stdout.split("\n"):
                if ":" in line:  # This line contains a package name
                    package = line.split(" ")[0].strip()
                    packages.append(package)

            # Update each package
            for package in packages:
                if self.verbose:
                    logging.info(f"Updating cargo package: {package}")
                success &= self.run_command(["cargo", "install", package])

        except subprocess.CalledProcessError:
            logging.error("Failed to list cargo packages")
            success = False

        return success
