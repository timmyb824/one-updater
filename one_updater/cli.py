#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from typing import Optional

import yaml
from rich.console import Console

from one_updater.package_managers.base import PackageManager
from one_updater.package_managers.registry import PackageManagerRegistry

console = Console()
error_console = Console(stderr=True)
logger = logging.getLogger(__name__)


def setup_logging(config: dict) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if config.get("verbose", False) else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)-8s %(message)s", force=True)


def get_default_config_path() -> str:
    """Get the default configuration file path."""
    return os.path.expanduser("~/.config/one-updater/config.yaml")


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from file."""
    if not config_path:
        config_path = get_default_config_path()

    logger.debug(f"Loading config from: {config_path}")

    if not os.path.exists(config_path):
        error_console.print(f"[red]Error: Config file not found: {config_path}[/red]")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            error_console.print(f"[red]Error: Invalid YAML in config file: {e}[/red]")
            sys.exit(1)


def init_config(config_path: str) -> None:
    """Initialize a new configuration file."""
    if os.path.exists(config_path):
        console.print(f"[yellow]Config file already exists at {config_path}[/yellow]")
        return

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Default configuration
    default_config = {
        "verbose": False,
        "logging": {"level": "INFO", "format": "%(message)s"},
        "package_managers": {
            "brew": {
                "enabled": True,
                "commands": {
                    "update": ["brew", "update"],
                    "upgrade": ["brew", "upgrade"],
                },
            },
            "apt": {
                "enabled": True,
                "commands": {
                    "update": ["sudo", "apt-get", "update"],
                    "upgrade": ["sudo", "apt", "upgrade", "-y"],
                },
            },
        },
    }

    # Write configuration
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(default_config, f, default_flow_style=False)

    console.print(f"[green]Created new config file at {config_path}[/green]")


def get_package_manager(name: str, config: dict) -> Optional[PackageManager]:
    """Get a package manager instance by name."""
    try:
        return PackageManagerRegistry.get_manager(name, config)
    except ValueError as e:
        error_console.print(f"[red]Error: {str(e)}[/red]")
        return None


def run_package_manager_action(
    name: str, cfg: dict, action_name: str, action_func, verbose: bool, status=None
) -> None:
    """Run a package manager action (update or upgrade) with proper console output."""
    if not cfg.get("enabled", True):
        return

    # Check if the command is configured
    commands = cfg.get("commands", {})
    if action_name not in commands:
        console.print(
            f"[yellow]! {name} does not have a {action_name} command configured[/yellow]"
        )
        return

    # Set verbose mode and status for this specific package manager
    cfg["verbose"] = verbose
    cfg["status"] = status

    logger.debug(f"Config for {name}: {cfg}")

    if pm := get_package_manager(name, cfg):
        # strip e at end of action_name if it exists
        action_name_without_e = action_name.title().rstrip("e")
        console.print(f"\n[bold blue]{action_name_without_e}ing {name}...[/bold blue]")
        if success := action_func(pm):
            console.print(f"[green]✓ {name} {action_name}d successfully[/green]")
        else:
            console.print(f"[red]✗ {name} {action_name} failed[/red]")


def list_managers(config: dict) -> None:
    """List all configured package managers."""
    package_managers = config.get("package_managers", {})
    if not package_managers:
        console.print("[yellow]No package managers configured[/yellow]")
        return

    console.print("\n[bold]Configured Package Managers:[/bold]")
    for name, cfg in package_managers.items():
        enabled = cfg.get("enabled", True)
        status = "[green]enabled[/green]" if enabled else "[red]disabled[/red]"
        console.print(f"  • {name}: {status}")


def update_managers(config: dict, managers: list[str], verbose: bool) -> None:
    """Update specified package managers."""
    package_managers = config.get("package_managers", {})

    # Filter package managers if specified
    if managers:
        if invalid_managers := [m for m in managers if m not in package_managers]:
            console.print(
                f"[red]Error: Invalid package manager(s): {', '.join(invalid_managers)}[/red]"
            )
            sys.exit(1)
        package_managers = {k: v for k, v in package_managers.items() if k in managers}

    # If no managers specified, use all enabled managers
    if not package_managers:
        console.print("[yellow]No package managers specified or enabled[/yellow]")
        return

    with console.status("[bold green]Updating package managers...") as status:
        for name, cfg in package_managers.items():
            run_package_manager_action(
                name, cfg, "update", lambda pm: pm.update(), verbose, status
            )


def upgrade_managers(config: dict, managers: list[str], verbose: bool) -> None:
    """Upgrade packages for specified package managers."""
    package_managers = config.get("package_managers", {})

    # Filter package managers if specified
    if managers:
        if invalid_managers := [m for m in managers if m not in package_managers]:
            console.print(
                f"[red]Error: Invalid package manager(s): {', '.join(invalid_managers)}[/red]"
            )
            sys.exit(1)
        package_managers = {k: v for k, v in package_managers.items() if k in managers}

    # If no managers specified, use all enabled managers
    if not package_managers:
        console.print("[yellow]No package managers specified or enabled[/yellow]")
        return

    with console.status("[bold green]Upgrading packages...") as status:
        for name, cfg in package_managers.items():
            run_package_manager_action(
                name, cfg, "upgrade", lambda pm: pm.upgrade(), verbose, status
            )


def show_version():
    """Show version information."""
    try:
        from importlib.metadata import version

        one_updater_version = version("one-updater")
        console.print(f"[blue]one-updater version {one_updater_version}[/blue]")
    except ImportError:
        console.print("[red]Error: Could not determine version[/red]")


def main():
    """Main entry point for the CLI."""
    description = """
One Update - Update all your package managers with one command

A simple tool to manage multiple package managers from a single interface.
Updates and upgrades can be performed on all or selected package managers.

Examples:
  %(prog)s init                     Create a new configuration file
  %(prog)s list-managers           List all configured package managers
  %(prog)s update -m brew pip      Update only brew and pip
  %(prog)s upgrade                 Upgrade all enabled package managers
  %(prog)s -h                      Show this help message
"""

    epilog = """
For more information and examples, visit:
https://github.com/timmyb824/one-updater
"""

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="available commands",
        help="command help",
        metavar="COMMAND",
    )

    # Common arguments for all commands
    common_parser = argparse.ArgumentParser(add_help=False)
    common_group = common_parser.add_argument_group("common options")
    common_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable verbose output (overrides config file setting)",
    )
    common_group.add_argument(
        "-c",
        "--config",
        metavar="PATH",
        help="path to config file (default: ~/.config/one-updater/config.yaml)",
    )

    # Manager selection arguments for update/upgrade commands
    manager_parser = argparse.ArgumentParser(add_help=False)
    manager_group = manager_parser.add_argument_group("manager selection")
    manager_group.add_argument(
        "-m",
        "--manager",
        metavar="NAME",
        action="append",
        help="specific package manager(s) to process (can be specified multiple times)",
    )

    # Add subcommands with detailed help
    init_help = """
    Initialize a new configuration file with default settings.
    If no config path is provided, creates ~/.config/one-updater/config.yaml
    """
    subparsers.add_parser(
        "init",
        help="initialize a new configuration file",
        description=init_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common_parser],
    )

    list_help = """
    List all package managers and their current status.
    Shows whether each manager is enabled or disabled.
    Use -v for detailed configuration information.
    """
    subparsers.add_parser(
        "list-managers",
        help="list all configured package managers",
        description=list_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common_parser],
    )

    update_help = """
    Update package manager indices/registries.
    If no managers are specified, updates all enabled managers.
    Use -m to specify specific managers to update.
    """
    subparsers.add_parser(
        "update",
        help="update package manager indices",
        description=update_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common_parser, manager_parser],
    )

    upgrade_help = """
    Upgrade packages for specified package managers.
    If no managers are specified, upgrades all enabled managers.
    Use -m to specify specific managers to upgrade.
    """
    subparsers.add_parser(
        "upgrade",
        help="upgrade packages for package managers",
        description=upgrade_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common_parser, manager_parser],
    )

    version_help = """
    Show version information.
    """
    subparsers.add_parser(
        "version",
        help="show version information",
        description=version_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common_parser],
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Handle version command before loading config
        if args.command == "version":
            show_version()
            return

        # Set up initial logging based on command line verbose flag
        setup_logging({"verbose": args.verbose})
        logger.debug(f"Command line arguments: {args}")

        # Load config file if needed
        if args.command != "init":
            config_path = os.path.abspath(
                os.path.expanduser(args.config or get_default_config_path())
            )
            config = load_config(config_path)

            # Command line verbose flag overrides config file
            if args.verbose:
                config["verbose"] = True
                setup_logging(config)

            logger.debug(f"Loaded config from {config_path}")
            logger.debug(f"Config contents: {config}")

        # Execute command
        if args.command == "init":
            config_path = os.path.abspath(
                os.path.expanduser(args.config or get_default_config_path())
            )
            init_config(config_path)
        elif args.command == "list-managers":
            list_managers(config)
        elif args.command == "update":
            update_managers(config, args.manager, args.verbose)
        elif args.command == "upgrade":
            upgrade_managers(config, args.manager, args.verbose)
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        error_console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
