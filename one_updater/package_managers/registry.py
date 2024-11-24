"""Registry for package managers."""

from .apt import AptManager
from .base import PackageManager
from .basher import BasherManager
from .brew import HomebrewManager
from .cargo import CargoManager
from .gem import GemManager
from .ghcli import GhCliManager
from .go import GoManager
from .krew import KubectlKrewManager
from .micro import MicroEditorManager
from .npm import NpmManager
from .pip import PipManager
from .pipx import PipxManager
from .pkgx import PkgxManager
from .snap import SnapManager
from .tldr import TldrManager
from .vagrant import VagrantPluginManager


class PackageManagerRegistry:
    """Registry for package managers."""

    _managers: dict[str, type[PackageManager]] = {
        "apt": AptManager,
        "basher": BasherManager,
        "brew": HomebrewManager,
        "cargo": CargoManager,
        "gem": GemManager,
        "gh-cli": GhCliManager,
        "go": GoManager,
        "krew": KubectlKrewManager,
        "micro": MicroEditorManager,
        "npm": NpmManager,
        "pip": PipManager,
        "pipx": PipxManager,
        "pkgx": PkgxManager,
        "snap": SnapManager,
        "tldr": TldrManager,
        "vagrant": VagrantPluginManager,
    }

    @classmethod
    def get_manager(cls, name: str, config: dict) -> PackageManager:
        """Get a package manager instance by name."""
        if name not in cls._managers:
            raise ValueError(f"Unknown package manager: {name}")
        return cls._managers[name](config)
