import logging
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


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error loading config file: {e}[/red]")
        return {}


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


@click.group()
@click.option("--config", "-c", default="config.yaml", help="Path to config file")
@click.pass_context
def cli(ctx, config):
    """One Update - Update all your package managers with one command."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)
    setup_logging(ctx.obj["config"])


@cli.command("version")
def show_version():
    try:
        from importlib.metadata import (  # pylint: disable=import-outside-toplevel
            version,
        )

        one_updater_version = version("one-updater")
        print(f"one-updater version {one_updater_version}")
    except ImportError:
        print("importlib.metadata not found")


@cli.command()
@click.option(
    "--manager", "-m", multiple=True, help="Specific package manager(s) to update"
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show verbose output from package managers"
)
@click.pass_context
def update(ctx, manager, verbose):
    """Update package manager indices/registries."""
    config = ctx.obj["config"]
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
@click.option(
    "--manager", "-m", multiple=True, help="Specific package manager(s) to upgrade"
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show verbose output from package managers"
)
@click.pass_context
def upgrade(ctx, manager, verbose):
    """Upgrade all packages for specified package managers."""
    config = ctx.obj["config"]
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
@click.pass_context
def list_managers(ctx):
    """List all configured package managers and their status."""
    config = ctx.obj["config"]
    package_managers = config.get("package_managers", {})

    console.print("\n[bold]Configured Package Managers:[/bold]")
    for name, cfg in package_managers.items():
        enabled = cfg.get("enabled", True)
        status = "[green]enabled[/green]" if enabled else "[red]disabled[/red]"
        console.print(f"  • {name}: {status}")


if __name__ == "__main__":
    cli(obj={})
