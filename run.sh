#!/usr/bin/env sh

install_uv() {
    # Check if the 'uv' binary is installed
    if ! command -v uv &> /dev/null; then
        echo "'uv' is not installed. Installing..."
        # Run the installation command
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Add the installation path to the $PATH
        export PATH=$HOME/.local/bin:$PATH
        echo "'uv' installed and PATH updated."
    else
        # echo "'uv' is already installed."
        return
    fi
}

install_curl() {
  if command -v curl &> /dev/null; then
    echo "curl is already installed."
    return 0
  fi

  if [ -f /etc/debian_version ]; then
    # Debian or Ubuntu
    apt-get update
    apt-get install -y curl
  elif [ -f /etc/alpine-release ]; then
    # Alpine Linux
    apk update
    apk add curl
  elif [ -f /etc/redhat-release ]; then
    # RHEL, CentOS, or Fedora
    yum install -y curl
  else
    echo "Unsupported distribution. Please install curl manually."
    return 1
  fi

  echo "curl has been successfully installed."
}

install_python3() {
  if command -v python3 &> /dev/null; then
    echo "Python3 is already installed."
    return 0
  fi

  if [ -f /etc/debian_version ]; then
    # Debian or Ubuntu
    apt-get update
    apt-get install -y python3
  elif [ -f /etc/alpine-release ]; then
    # Alpine Linux
    apk update
    apk add python3
  elif [ -f /etc/redhat-release ]; then
    # RHEL, CentOS, or Fedora
    yum install -y python3
  else
    echo "Unsupported distribution. Please install Python3 manually."
    return 1
  fi

  echo "Python3 has been successfully installed."
}

install_dev_deps() {
  if [ "$(arch)" = "aarch64" ] || [ -n "${INSTALL_DEV_DEPS:-1}" ]; then
    echo "Install dependencies for ARM64"
    yum install -y python3-devel gcc kernel-devel kernel-headers make diffutils file
  fi
}
install_dev_deps
install_curl
install_uv
install_python3

uv tool run --isolated --with . pyinfra @local pysetmeup.setups.basicdev
