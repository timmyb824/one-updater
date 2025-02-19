"""Test fixtures for one-updater."""

import os

import pytest
import yaml


@pytest.fixture
def test_config_path(tmp_path):
    """Create a temporary test configuration file."""
    config_path = tmp_path / "test_config.yaml"

    test_config = {
        "package_managers": {
            "brew": {
                "enabled": True,
                "commands": {
                    "update": ["brew", "update"],
                    "upgrade": ["brew", "upgrade"],
                },
            },
            "pip": {
                "enabled": True,
                "commands": {
                    "update": ["pip", "install", "--upgrade", "pip"],
                    "upgrade": [],
                },
            },
        }
    }

    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(test_config, f)

    return str(config_path)
