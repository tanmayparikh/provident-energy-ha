# Development Container for Provident Energy Home Assistant Integration

This directory contains configuration files for setting up a development container environment for the Provident Energy Home Assistant Integration.

## Contents

- `devcontainer.json`: Configuration for the development container
- `Dockerfile`: Definition of the Docker image used for development
- `entrypoint.sh`: Script that runs when the container starts

## Using with VS Code

VS Code can automatically detect and use the devcontainer configuration:

1. Install the [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the repository in VS Code
3. When prompted, click "Reopen in Container" or run the "Remote-Containers: Reopen in Container" command
4. VS Code will build the container and open the project inside it

## Using with PyCharm Professional

PyCharm Professional can use the devcontainer for development and debugging:

### Setting Up the Docker Interpreter

1. Create a `docker-compose.yml` file in the root of the project with the following content:

```yaml
version: '3'
services:
  devcontainer:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - .:/workspaces/provident-energy-ha
    environment:
      - PYTHONPATH=/workspaces/provident-energy-ha
    ports:
      - "5678:5678"  # For debugpy
      - "8123:8123"  # For Home Assistant
    network_mode: host
    command: sleep infinity
```

2. In PyCharm, go to File > Settings > Project > Python Interpreter
3. Click the gear icon and select "Add..."
4. Choose "Docker Compose" from the left menu
5. Configure the interpreter:
   - Server: Select your Docker server (or create a new one)
   - Configuration file(s): Select the docker-compose.yml file you created
   - Service: Select "devcontainer"
   - Python interpreter path: /usr/local/bin/python
6. Click "OK" to create the interpreter

### Setting Up Remote Debugging

1. Add the following code at the beginning of the file you want to debug:

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()
```

2. Create a new Run/Debug Configuration:
   - Go to Run > Edit Configurations...
   - Click the "+" button and select "Python Debug Server"
   - Set the host to "localhost" and port to "5678"
   - Name the configuration (e.g., "Remote Debug")
   - Click "OK" to save

3. Start your application in the container
4. In PyCharm, click the debug icon next to your "Remote Debug" configuration
5. PyCharm will connect to the debugpy server running in the container

## Debugging Home Assistant Custom Components

### Using the Example Debug Script

We've included an example script to help you get started with debugging:

1. In the container, run the example script:

```bash
cd /workspaces/provident-energy-ha
python .devcontainer/debug_example.py
```

2. The script will pause and wait for a debugger to attach
3. In PyCharm, start your "Python Debug Server" configuration
4. The script will continue execution once the debugger is attached
5. You can set breakpoints in PyCharm and debug as normal

### Debugging within Home Assistant

To debug the custom component within Home Assistant:

1. Start Home Assistant in the container:

```bash
cd /workspaces/provident-energy-ha
hass -c ./config
```

2. In your component code, add debugpy statements where needed:

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

3. Connect with PyCharm as described above

## Troubleshooting

- **Port conflicts**: If you encounter port conflicts, you can change the ports in the docker-compose.yml file and update your debug configuration accordingly.
- **Connection issues**: Make sure your firewall allows connections to the debug port.
- **Container not starting**: Check Docker logs for any errors during container startup.
