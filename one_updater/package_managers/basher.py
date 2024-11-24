"""basher package manager implementation."""

import logging
import subprocess

from .base import PackageManager


class BasherManager(PackageManager):
    def is_available(self) -> bool:
        return self.run_command(["which", "basher"])

    def update(self) -> bool:
        """Update Homebrew package lists."""
        if not self.is_available():
            return False
        return self.run_command(
            self.commands.get("update", ["bash", "-c", "cd ~/.basher && git pull"])
        )

    def upgrade(self) -> bool:
        if not self.is_available():
            logging.info("basher is not installed. Skipping.")
            return False

        success = True
        try:
            result = subprocess.run(
                ["basher", "outdated"], capture_output=True, text=True, check=True
            )
            outdated_packages = (
                result.stdout.strip().split("\n") if result.stdout else []
            )
            upgrade_command = self.commands.get("upgrade", ["basher", "upgrade"])
            for package in outdated_packages:
                cmd = upgrade_command + [package]
                success &= self.run_command(cmd)
        except subprocess.CalledProcessError:
            logging.error("Failed to get outdated basher packages")
            success = False
        return success
