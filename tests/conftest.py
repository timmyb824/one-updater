"""Pytest configuration for one-updater tests."""

import logging
import os

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Set up logging for tests."""
    # Save original handlers
    root_handlers = logging.root.handlers[:]
    logger = logging.getLogger("one-updater")
    logger_handlers = logger.handlers[:]

    # Create a test handler for our logger
    logger.handlers = []
    test_handler = logging.StreamHandler()
    test_handler.setLevel(logging.DEBUG)
    logger.addHandler(test_handler)
    logger.setLevel(logging.DEBUG)

    yield

    # Restore original handlers
    logging.root.handlers = root_handlers
    logger.handlers = logger_handlers


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_config_path():
    """Get the path to the test configuration file."""
    return os.path.join(os.path.dirname(__file__), "test_config.yaml")
