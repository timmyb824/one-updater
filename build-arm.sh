#!/bin/bash

set -e

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

handle_error() {
    echo "Error: $1"
    exit 1
}

if ! command_exists gh; then
    handle_error "GitHub CLI (gh) is not installed. Please install it first.\nVisit: https://cli.github.com/"
fi

if command_exists podman; then
    CONTAINER_TOOL="podman"
elif command_exists docker; then
    CONTAINER_TOOL="docker"
else
    handle_error "Neither Docker nor Podman is installed"
fi

echo "Using $CONTAINER_TOOL for building..."

mkdir -p dist

if [ "$CONTAINER_TOOL" = "docker" ]; then
    docker buildx create --use || handle_error "Failed to create Docker buildx builder"
fi

echo "Building ARM binary..."
if ! $CONTAINER_TOOL build --platform linux/arm64 -t localhost/one-updater-arm:latest -f Dockerfile.arm .; then
    handle_error "Failed to build ARM binary"
fi

echo "Creating temporary container..."
container_id=$($CONTAINER_TOOL create localhost/one-updater-arm:latest) || handle_error "Failed to create container"

echo "Extracting binary from container..."
$CONTAINER_TOOL cp $container_id:/app/dist/one-updater ./dist/one-updater-linux-arm64 || handle_error "Failed to copy binary from container"

echo "Cleaning up..."
$CONTAINER_TOOL rm $container_id || echo "Warning: Failed to remove container"

if [ ! -f "./dist/one-updater-linux-arm64" ]; then
    handle_error "Binary was not created successfully"
fi

echo "Build complete! Binary is available at ./dist/one-updater-linux-arm64"

if [ "$CONTAINER_TOOL" = "podman" ]; then
    echo -e "\nNote: If this is your first time building with Podman, you may need to run:"
    echo "podman machine ssh sudo rpm-ostree install qemu-user-static"
    echo "podman machine ssh sudo systemctl reboot"
fi

echo "Uploading ARM binary to GitHub release..."
if [ -f "./dist/one-updater-linux-arm64" ]; then
    if gh release upload latest ./dist/one-updater-linux-arm64 --clobber; then
        echo "Successfully uploaded binary to GitHub release"
        echo "Visit: https://github.com/timmyb824/one-updater/releases/tag/latest"
    else
        handle_error "Failed to upload binary to GitHub release.\nMake sure you're authenticated with GitHub CLI (run 'gh auth login')"
    fi
else
    handle_error "Binary file not found. Build may have failed."
fi
