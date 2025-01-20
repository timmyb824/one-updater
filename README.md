# One Updater

A flexible package manager updater that helps you keep all your development tools up to date.

## Features

- Update multiple package managers with a single command
- Configure which package managers to update
- Support for virtual environments and pyenv for Python packages
- Beautiful command-line interface with rich formatting and logging
- Cross-platform support
- Extensible architecture for adding new package managers

## Supported Package Managers

- Homebrew
- pip (with virtualenv/pyenv support)
- npm
- cargo
- gem
- pipx
- pacman
- dnf
- flatpak
- pkgx
- vagrant-plugins
- micro editor plugins
- tldr pages
- go packages
- apt
- More coming soon!

## Installation

Install from PyPI:

```bash
pip install one-updater
```

To upgrade to the latest version:

```bash
pip install --upgrade one-updater
```

Use one of the pre-built executables in `one_updater/bin` e.g.:

```bash
sudo cp one-updater-linux /usr/local/bin/one-updater
sudo chmod +x /usr/local/bin/one-updater
```

## Usage

### Basic Usage

Update all enabled package managers:

```bash
one-updater update
```

Update specific package managers:

```bash
one-updater update -m homebrew -m pip
```

List configured package managers:

```bash
one-updater list-managers
```

Initialize a new configuration file:

```bash
one-updater init
```

### Configuration

The tool uses a YAML configuration file (default: `~/.config/one-updater/config.yaml`) to specify package manager settings. You can:

1. Enable/disable specific package managers
2. Configure virtualenv/pyenv for Python packages
3. Customize update commands
4. Configure logging and verbosity

Example configuration:

```yaml
verbose: true
logging:
  level: "INFO"
  format: "%(message)s"

package_managers:
  homebrew:
    enabled: true
    commands:
      update: ["brew", "update"]
      upgrade: ["brew", "upgrade"]

  pip:
    enabled: true
    virtualenv: "/path/to/virtualenv" # Optional
    pyenv: "3.11.0" # Optional
    commands:
      update: ["pip", "install", "--upgrade", "pip"]
      upgrade: ["pip", "list", "--outdated", "--format=json"]
```

## Contributing

Contributions are welcome! Feel free to:

1. Add support for new package managers
2. Improve error handling and logging
3. Add new features
4. Fix bugs
5. Improve documentation

Please ensure your changes pass the test suite and code quality checks:

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Run code formatting
poetry run black .
```

## License

MIT License
