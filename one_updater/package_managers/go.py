"""Go package manager implementation."""

import logging
import os
import subprocess

from .base import PackageManager


class GoManager(PackageManager):
    """Manager for Go packages."""

    # Known special cases where the install path differs from the module path
    SPECIAL_CASES = {
        "staticcheck": "honnef.co/go/tools/cmd/staticcheck",
        "kube-linter": "golang.stackrox.io/kube-linter/cmd/kube-linter",
        "yamlfmt": "github.com/google/yamlfmt/cmd/yamlfmt",
    }

    def __init__(self, config: dict):
        """Initialize the Go package manager."""
        super().__init__(config)
        logging.debug(f"GoManager initialized with config: {config}")

    def is_available(self) -> bool:
        """Check if Go is installed."""
        return self.run_command(["which", "go"])

    def update(self) -> bool:
        """Go itself doesn't need updating, that's handled by the system package manager."""
        logging.info("Go itself doesn't need updating. Skipping.")
        return True

    def _try_install_package(
        self, binary: str, package_path: str, is_retry: bool = False
    ) -> bool:
        # sourcery skip: extract-duplicate-method, invert-any-all, swap-nested-ifs
        """Try to install a Go package, handling common errors."""
        if self.verbose:
            logging.info(f"Attempting to install {package_path}")

        # For special cases, use the path directly without any manipulation
        if binary in self.SPECIAL_CASES:
            package_path = self.SPECIAL_CASES[binary]
            if self.verbose:
                logging.info(f"Using special case path for {binary}: {package_path}")

        success, stdout, stderr = self.run_command_with_output(
            ["go", "install", f"{package_path}@latest"]
        )

        if success:
            if stdout and self.verbose:
                logging.info(f"Install output: {stdout}")
            if (
                stderr
                and self.verbose
                and not any(x in stderr for x in ["go: downloading", "go: found"])
            ):
                logging.info(f"Install info: {stderr}")
            return True

        # Handle common error cases
        if stderr:
            stderr = stderr.replace("\n", " ")  # Normalize error message

            # Case 1: Package not found at root module path
            if "does not contain package" in stderr and not is_retry:
                # Try with /cmd/{binary} suffix if not already a cmd path
                if "/cmd/" not in package_path:
                    cmd_path = f"{package_path}/cmd/{binary}"
                    if self.verbose:
                        logging.info(f"Package not found at root, trying {cmd_path}")
                    return self._try_install_package(binary, cmd_path, True)
                # Try just the module path if cmd path didn't work
                elif package_path.endswith(f"/cmd/{binary}"):
                    base_path = package_path.replace(f"/cmd/{binary}", "")
                    if self.verbose:
                        logging.info(
                            f"Package not found at cmd path, trying base path: {base_path}"
                        )
                    return self._try_install_package(binary, base_path, True)

            # Case 2: Build constraints exclude files
            elif "build constraints exclude all Go files" in stderr:
                if not is_retry and "tools" in package_path:
                    cmd_path = f"{package_path}/cmd/{binary}"
                    if self.verbose:
                        logging.info(
                            f"Build constraints exclude files, trying {cmd_path}"
                        )
                    return self._try_install_package(binary, cmd_path, True)

        logging.error(f"Failed to install {package_path}: {stderr}")
        return False

    def upgrade(self) -> bool:
        """Upgrade all globally installed Go packages."""
        if not self.is_available():
            if self.verbose:
                logging.info("go is not installed. Skipping upgrade.")
            return False

        success = True
        try:
            # Get GOPATH
            result = subprocess.run(
                ["go", "env", "GOPATH"],
                capture_output=True,
                text=True,
                check=True,
            )
            gopath = result.stdout.strip() or os.path.expanduser("~/go")
            if self.verbose:
                logging.info(f"Using GOPATH: {gopath}")

            # Get list of binaries in GOPATH/bin
            bin_dir = os.path.join(gopath, "bin")
            if not os.path.exists(bin_dir):
                if self.verbose:
                    logging.info(f"No Go binaries found in {bin_dir}")
                return True

            binaries = [
                binary
                for binary in os.listdir(bin_dir)
                if not binary.startswith(".")
                and os.path.isfile(os.path.join(bin_dir, binary))
            ]

            if not binaries:
                if self.verbose:
                    logging.info("No Go binaries found to upgrade")
                return True

            if self.verbose:
                logging.info(f"Found Go binaries: {', '.join(binaries)}")

            # For each binary, try to find its package and update it
            for binary in binaries:
                try:
                    if self.verbose:
                        logging.info(f"Processing binary: {binary}")
                    # Check for special cases first
                    if binary in self.SPECIAL_CASES:
                        package_path = self.SPECIAL_CASES[binary]
                        if self.verbose:
                            logging.info(
                                f"Using special case path for {binary}: {package_path}"
                            )
                        success, stdout, stderr = self.run_command_with_output(
                            ["go", "install", f"{package_path}@latest"]
                        )
                        if not success:
                            logging.error(f"Failed to update {package_path}: {stderr}")
                            success = False
                        continue

                    # For non-special cases, get module info
                    binary_path = os.path.join(bin_dir, binary)
                    if self.verbose:
                        logging.info(f"Getting module info for: {binary}")
                    result = subprocess.run(
                        ["go", "version", "-m", binary_path],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    if self.verbose:
                        logging.debug(f"Module info output:\n{result.stdout}")

                    if module_path := next(
                        (
                            line.strip().split("\t")[1]
                            for line in result.stdout.split("\n")
                            if line.strip().startswith("mod\t")
                        ),
                        None,
                    ):
                        if self.verbose:
                            logging.info(f"Found module path: {module_path}")
                        if not self._try_install_package(binary, module_path):
                            success = False
                    else:
                        if self.verbose:
                            logging.warning(
                                f"Could not determine package for binary: {binary}"
                            )
                        # Try using binary name as a last resort
                        if not self._try_install_package(binary, binary):
                            success = False

                except subprocess.CalledProcessError as e:
                    logging.warning(
                        f"Failed to get module info for {binary}: {e.stderr}"
                    )
                    success = False

        except subprocess.CalledProcessError as e:
            logging.error(f"Error during Go package updates: {e}")
            success = False

        return success
