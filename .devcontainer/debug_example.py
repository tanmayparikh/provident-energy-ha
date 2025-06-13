"""
Example script for debugging the Provident Energy component.

This script demonstrates how to use debugpy to debug the component.
To use this script:
1. Run it in the container
2. Connect to it from PyCharm using the Python Debug Server configuration
"""
import os
import sys
import debugpy
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

# Add the repository root to the Python path
sys.path.insert(0, "/workspaces/provident-energy-ha")

# Enable remote debugging
_LOGGER.info("Starting debugpy server on 0.0.0.0:5678")
debugpy.listen(("0.0.0.0", 5678))
_LOGGER.info("Waiting for debugger to attach...")
debugpy.wait_for_client()
_LOGGER.info("Debugger attached!")

# Import the component
from custom_components.provident_energy.api import ProvidentEnergyAPI
from custom_components.provident_energy.const import DOMAIN

# Example usage
def main():
    """Run example code for debugging."""
    _LOGGER.info("Starting Provident Energy API example")
    
    # You can set breakpoints in this function or in the API code
    username = os.environ.get("PROVIDENT_USERNAME", "test_user")
    password = os.environ.get("PROVIDENT_PASSWORD", "test_password")
    
    _LOGGER.info(f"Creating API client for user: {username}")
    api = ProvidentEnergyAPI(username, password)
    
    # This is where you would set a breakpoint
    _LOGGER.info("Attempting to login")
    login_result = api.login()
    _LOGGER.info(f"Login result: {login_result}")
    
    # More example code here
    _LOGGER.info("Example completed")

if __name__ == "__main__":
    main()