import logging
import os
import subprocess

from .base import PackageManager


class GoManager(PackageManager):
    """Manager for Go packages."""

    # Special case mappings for known tools that need specific module paths
    SPECIAL_CASES: dict[str, str] = {
        "staticcheck": "honnef.co/go/tools/cmd/staticcheck",
    }

    def is_available(self) -> bool:
        """Check if Go is installed."""
        return self.run_command(["which", "go"])

    def update(self) -> bool:
        """Go itself doesn't need updating, that's handled by the system package manager."""
        return True

    def upgrade(self) -> bool:
        """Upgrade all globally installed Go packages."""
        if not self.is_available():
            logging.info("go is not installed. Skipping.")
            return False

        success = True
        try:
            # First try to get GOPATH
            result = subprocess.run(
                ["go", "env", "GOPATH"],
                capture_output=True,
                text=True,
                check=True,
            )
            gopath = result.stdout.strip() or os.path.expanduser(
                "~/go"
            )  # Default GOPATH
            logging.info(f"Using GOPATH: {gopath}")

            # Get list of binaries in GOPATH/bin
            bin_dir = os.path.join(gopath, "bin")
            if not os.path.exists(bin_dir):
                logging.info(f"No Go binaries found in {bin_dir}")
                return True

            binaries = [
                binary
                for binary in os.listdir(bin_dir)
                if not binary.startswith(".")
                and os.path.isfile(os.path.join(bin_dir, binary))
            ]
            if not binaries:
                logging.info("No Go binaries found to update")
                return True

            logging.info(f"Found Go binaries: {', '.join(binaries)}")

            # For each binary, try to find its package and update it
            for binary in binaries:
                try:
                    # Use go version -m to get module info
                    binary_path = os.path.join(bin_dir, binary)
                    logging.info(f"Getting module info for: {binary}")
                    result = subprocess.run(
                        ["go", "version", "-m", binary_path],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    logging.debug(f"Module info output:\n{result.stdout}")

                    # Check special cases first
                    if binary in self.SPECIAL_CASES:
                        module_path = self.SPECIAL_CASES[binary]
                        logging.info(
                            f"Using special case path for {binary}: {module_path}"
                        )
                    else:
                        module_path = next(
                            (
                                line.strip().split("\t")[1]
                                for line in result.stdout.split("\n")
                                if line.strip().startswith("mod\t")
                            ),
                            None,
                        )

                    if module_path:
                        logging.info(f"Found module path: {module_path}")
                        # Install latest version using direct subprocess call
                        try:
                            logging.info(f"Attempting to update {module_path}")
                            result = subprocess.run(
                                ["go", "install", f"{module_path}@latest"],
                                capture_output=True,
                                text=True,
                                check=True,
                            )
                            # Check if there was meaningful stderr output
                            if result.stderr and not (
                                "go: downloading" in result.stderr
                                or "go: found" in result.stderr
                            ):
                                logging.error(
                                    f"Error updating {module_path}: {result.stderr}"
                                )
                                success = False
                            else:
                                if result.stdout:
                                    logging.info(f"Update output: {result.stdout}")
                                if result.stderr:
                                    logging.info(f"Update info: {result.stderr}")
                        except subprocess.CalledProcessError as e:
                            logging.error(f"Failed to update {module_path}: {e.stderr}")
                            success = False
                    else:
                        logging.warning(
                            f"Could not determine package for binary: {binary}"
                        )
                except subprocess.CalledProcessError as e:
                    logging.warning(
                        f"Failed to get module info for {binary}: {e.stderr}"
                    )
                    success = False

        except subprocess.CalledProcessError as e:
            logging.error(f"Error during Go package updates: {e}")
            success = False

        return success
