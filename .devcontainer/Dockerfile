FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
        wget \
        unzip \
        libffi-dev \
        libjpeg-dev \
        libpng-dev \
        libssl-dev \
        libudev-dev \
        zlib1g-dev \
        libavcodec-dev \
        libavdevice-dev \
        libavfilter-dev \
        libavformat-dev \
        libavutil-dev \
        libswscale-dev \
        libswresample-dev \
        ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up Home Assistant development environment
RUN pip install --no-cache-dir \
    homeassistant \
    pytest \
    pytest-cov \
    pytest-homeassistant-custom-component \
    black \
    flake8 \
    pylint \
    mypy \
    pydocstyle \
    pre-commit \
    debugpy

# Set up PyCharm debugging
RUN pip install --no-cache-dir pydevd-pycharm

# Create a non-root user to use if preferred
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && mkdir -p /home/$USERNAME/.vscode-server /home/$USERNAME/.vscode-server-insiders \
    && chown -R $USER_UID:$USER_GID /home/$USERNAME

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Set up working directory
WORKDIR /workspaces/provident-energy-ha

# Add a script to be executed every time the container starts
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]