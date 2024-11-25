import importlib.resources as resources
import logging
import os
import shutil
import sys
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.logging import RichHandler

from one_updater.package_managers.base import PackageManager
from one_updater.package_managers.registry import PackageManagerRegistry

console = Console()


def setup_logging(config: dict):
    """Setup logging configuration."""
    logging.basicConfig(
        level=config.get("logging", {}).get("level", "INFO"),
        format=config.get("logging", {}).get("format", "%(message)s"),
        handlers=[RichHandler(console=console)],
    )


def get_default_config_path():
    """Get the default config path."""
    config_dir = os.path.expanduser("~/.config/one-updater")
    return os.path.join(config_dir, "config.yaml")


def load_config(config_path: Optional[str] = None):
    """Load configuration from file.

    Args:
        config_path: Optional path to config file. If not provided,
                    uses default location (~/.config/one-updater/config.yaml)

    Returns:
        dict: Loaded configuration
    """
    config_path = config_path or get_default_config_path()

    if not os.path.exists(config_path):
        console.print(
            f"[red]Config file not found: {config_path}\nRun 'one-updater init' to create a new configuration file.[/red]"
        )
        sys.exit(1)

    try:
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error loading config file: {e}[/red]")
        return {}


def init_config(config_path: Optional[str] = None):
    """Initialize a new configuration file.

    Args:
        config_path: Optional path to create config file. If not provided,
                    uses default location (~/.config/one-updater/config.yaml)
    """
    if not config_path:
        raise ValueError("config_path must be provided")

    config_dir = os.path.dirname(config_path)

    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Don't overwrite existing config
    if os.path.exists(config_path):
        console.print(
            f"[blue]Configuration file already exists at {config_path}[/blue]"
        )
        return

    # Copy default config to user's config directory
    default_config = resources.files("one_updater").joinpath(
        "configs/default_config.yaml"
    )
    with resources.as_file(default_config) as default_config_path:
        shutil.copy(default_config_path, config_path)
        console.print(f"[green]Configuration file created at {config_path}[/green]")
        if config_path != get_default_config_path():
            console.print(
                "[yellow]You used a custom config file path. Remember to use the same --config (or -c) flag when running other commands.[/yellow]"
            )


def get_package_manager(name: str, config: dict) -> Optional[PackageManager]:
    """Get a package manager instance by name."""
    try:
        return PackageManagerRegistry.get_manager(name, config)
    except ValueError as e:
        logging.warning(str(e))
        return None


def run_package_manager_action(
    name: str, cfg: dict, action_name: str, action_func, verbose: bool
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

    # Set verbose mode for this specific package manager
    cfg["verbose"] = verbose

    if pm := get_package_manager(name, cfg):
        # strip e at end of action_name if it exists
        action_name_without_e = action_name.title().rstrip("e")
        console.print(f"\n[bold blue]{action_name_without_e}ing {name}...[/bold blue]")
        if success := action_func(pm):
            console.print(f"[green]✓ {name} {action_name}d successfully[/green]")
        else:
            console.print(f"[red]✗ {name} {action_name} failed[/red]")


def common_options(f):
    """Common options for all commands."""
    f = click.option(
        "--config",
        "-c",
        help="Path to config file (default: ~/.config/one-updater/config.yaml)",
        default=None,
    )(f)
    return f


@click.group()
@common_options
@click.pass_context
def cli(ctx, config):
    """One Update - Update all your package managers with one command."""
    ctx.ensure_object(dict)
    # Convert relative path to absolute path if config is provided
    if config:
        config = os.path.abspath(config)
    ctx.obj["config_path"] = config or get_default_config_path()

    if ctx.invoked_subcommand == "init":
        return

    if not os.path.exists(ctx.obj["config_path"]):
        console.print(
            f"[red]Config file not found at {ctx.obj['config_path']}\n"
            "Run 'one-updater init' to create a new configuration file.[/red]"
        )
        sys.exit(1)

    ctx.obj["config"] = load_config(ctx.obj["config_path"])
    setup_logging(ctx.obj["config"])


@cli.command("init", help="Initialize a new configuration file")
@common_options
def init(config):
    """Initialize a new configuration file."""
    # Use the provided config path or default
    config_path = os.path.abspath(config) if config else get_default_config_path()
    try:
        init_config(config_path)
    except Exception as e:
        console.print(f"[red]Error initializing config file: {e}[/red]")
        sys.exit(1)


@cli.command("version", help="Show version information")
@common_options
def show_version(config):
    """Show version information."""
    try:
        from importlib.metadata import version

        one_updater_version = version("one-updater")
        print(f"one-updater version {one_updater_version}")
    except ImportError:
        print("importlib.metadata not found")


@cli.command()
@common_options
@click.option(
    "--manager", "-m", multiple=True, help="Specific package manager(s) to update"
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show verbose output from package managers"
)
@click.pass_context
def update(ctx, config, manager, verbose):
    """Update package manager indices/registries."""
    config = ctx.obj.get("config", {})
    package_managers = config.get("package_managers", {})

    # Filter package managers if specified
    if manager:
        # Check for requested managers that don't exist in config
        for m in manager:
            if m not in package_managers:
                logging.warning(f"Package manager '{m}' is not defined in config")
        package_managers = {k: v for k, v in package_managers.items() if k in manager}

    with console.status("[bold green]Updating package managers...") as status:
        for name, cfg in package_managers.items():
            run_package_manager_action(
                name, cfg, "update", lambda pm: pm.update(), verbose
            )


@cli.command()
@common_options
@click.option(
    "--manager", "-m", multiple=True, help="Specific package manager(s) to upgrade"
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show verbose output from package managers"
)
@click.pass_context
def upgrade(ctx, config, manager, verbose):
    """Upgrade all packages for specified package managers."""
    config = ctx.obj.get("config", {})
    package_managers = config.get("package_managers", {})

    # Filter package managers if specified
    if manager:
        # Check for requested managers that don't exist in config
        for m in manager:
            if m not in package_managers:
                logging.warning(f"Package manager '{m}' is not defined in config")
        package_managers = {k: v for k, v in package_managers.items() if k in manager}

    with console.status("[bold green]Upgrading packages...") as status:
        for name, cfg in package_managers.items():
            run_package_manager_action(
                name, cfg, "upgrade", lambda pm: pm.upgrade(), verbose
            )


@cli.command()
@common_options
@click.pass_context
def list_managers(ctx, config):
    """List all configured package managers and their status."""
    config = ctx.obj.get("config", {})
    package_managers = config.get("package_managers", {})

    console.print("\n[bold]Configured Package Managers:[/bold]")
    for name, cfg in package_managers.items():
        enabled = cfg.get("enabled", True)
        status = "[green]enabled[/green]" if enabled else "[red]disabled[/red]"
        console.print(f"  • {name}: {status}")


if __name__ == "__main__":
    cli(obj={})  # pylint: disable=no-value-for-parameter
