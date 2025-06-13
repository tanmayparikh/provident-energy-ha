#!/bin/bash
set -e

# Print message
echo "Initializing development container for Provident Energy Home Assistant Integration"

# Set up Python path for development
export PYTHONPATH=/workspaces/provident-energy-ha:$PYTHONPATH

# Install the component in development mode if not already installed
if [ ! -f "/workspaces/provident-energy-ha/.installed" ]; then
    echo "Installing component in development mode..."
    cd /workspaces/provident-energy-ha
    pip install -e .
    touch /workspaces/provident-energy-ha/.installed
fi

# Set up debugpy for PyCharm remote debugging
echo "Setting up debugpy for PyCharm remote debugging..."
# Default debugpy port is 5678
export DEBUGPY_PORT=${DEBUGPY_PORT:-5678}
echo "debugpy will listen on port $DEBUGPY_PORT"

# Execute the command passed to docker
exec "$@"