"""basher package manager implementation."""

import logging
import os
import subprocess
from typing import Optional

from .base import PackageManager


class BasherManager(PackageManager):
    """
    Basher package manager implementation.
    """

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

    def list_packages(self) -> Optional[list[str]]:
        """Return all basher-installed packages as user/package strings."""
        if not self.is_available():
            return None
        cellar = os.path.expanduser("~/.basher/cellar/packages")
        if not os.path.isdir(cellar):
            return []
        return [
            f"{user}/{pkg}"
            for user in os.listdir(cellar)
            if os.path.isdir(user_dir := os.path.join(cellar, user))
            for pkg in os.listdir(user_dir)
            if os.path.isdir(os.path.join(user_dir, pkg))
        ]

    def install_package(self, name: str) -> bool:
        """Install a basher package by user/package identifier."""
        if not self.is_available():
            return False
        return self.run_command(["basher", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a basher package is installed."""
        if "/" not in name:
            return False
        user, pkg = name.split("/", 1)
        path = os.path.expanduser(f"~/.basher/cellar/packages/{user}/{pkg}")
        return os.path.isdir(path)
