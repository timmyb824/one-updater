# One Updater

A flexible package manager updater that helps you keep all your development tools up to date.

## Features

- Update multiple package managers with a single command
- Configure which package managers to update
- Support for virtual environments and pyenv for Python packages
- Beautiful command-line interface with rich formatting
- Extensible architecture for adding new package managers

## Supported Package Managers

- Homebrew
- pip (with virtualenv/pyenv support)
- npm
- cargo
- gem
- pipx
- More coming soon!

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/one-update.git
cd one-update
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Update all enabled package managers:

```bash
python -m one_update.cli update
```

Update specific package managers:

```bash
python -m one_update.cli update -m homebrew -m pip
```

List configured package managers:

```bash
python -m one_update.cli list-managers
```

### Configuration

The tool uses a YAML configuration file (`config.yaml`) to specify package manager settings. You can:

1. Enable/disable specific package managers
2. Configure virtualenv/pyenv for Python packages
3. Customize update commands
4. Configure logging

Example configuration:

```yaml
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
```

## Contributing

Contributions are welcome! Feel free to:

1. Add support for new package managers
2. Improve error handling and logging
3. Add new features
4. Fix bugs

## License

MIT License
