# Provident Energy Integration for Home Assistant

This integration allows you to monitor your utility usage data from Provident Energy in Home Assistant.

## Features

- Monitor electricity usage
- Monitor gas usage
- Monitor water usage
- Automatic data updates every hour
- Manual refresh option

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Click the "+ Explore & Download Repositories" button
4. Search for "Provident Energy"
5. Click "Download"
6. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/provident_energy` directory to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "+ Add Integration"
3. Search for "Provident Energy"
4. Follow the configuration steps:
   - Enter your Provident Energy username
   - Enter your Provident Energy password
   - (Optional) Enter your account ID if you have multiple accounts

## Sensors

This integration provides the following sensors:

- **Electricity Usage**: Total electricity usage in kWh
- **Gas Usage**: Total gas usage in cubic meters
- **Water Usage**: Total water usage in cubic meters

## Services

- **provident_energy.refresh_data**: Manually refresh data from the Provident Energy API

## Troubleshooting

- If you encounter authentication issues, verify your username and password
- For other issues, check the Home Assistant logs for more information

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Development with DevContainers

This project includes a devcontainer configuration for easy development and testing:

### Using VS Code

1. Install [VS Code](https://code.visualstudio.com/), [Docker](https://www.docker.com/products/docker-desktop), and the [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Clone this repository
3. Open the repository in VS Code
4. When prompted, click "Reopen in Container" or run the "Remote-Containers: Reopen in Container" command
5. VS Code will build the container and open the project inside it

### Using PyCharm

1. Install [PyCharm Professional](https://www.jetbrains.com/pycharm/) (required for remote debugging) and [Docker](https://www.docker.com/products/docker-desktop)
2. Clone this repository
3. Open the repository in PyCharm
4. Set up the Docker-based remote interpreter:
   - Go to File > Settings > Project > Python Interpreter
   - Click the gear icon and select "Add..."
   - Choose "Docker Compose" from the left menu
   - Select the docker-compose.yml file (or create one based on the devcontainer configuration)
   - Click "OK" to create the interpreter
5. Configure remote debugging:
   - Create a new Run/Debug Configuration (Run > Edit Configurations...)
   - Add a new "Python Debug Server" configuration
   - Set the host to localhost and port to 5678 (the default debugpy port)
   - Apply the changes

The devcontainer includes all necessary dependencies and tools for development, including debugpy for PyCharm remote debugging. See the `.devcontainer/README.md` file for more detailed instructions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
