#!/bin/bash
# Update and upgrade system packages
apt update -y
apt upgrade -y

# Install system dependencies
apt install -y python3-full python3-pip python3-venv git wget curl

# Download and extract the latest MiniZinc release
LATEST_MINIZINC_VERSION=$(curl -s https://api.github.com/repos/MiniZinc/MiniZincIDE/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
wget "https://github.com/MiniZinc/MiniZincIDE/releases/download/${LATEST_MINIZINC_VERSION}/MiniZincIDE-${LATEST_MINIZINC_VERSION}-bundle-linux-x86_64.tgz"
mkdir -p "$HOME/minizinc"
tar -xvzf "MiniZincIDE-${LATEST_MINIZINC_VERSION}-bundle-linux-x86_64.tgz" -C "$HOME/minizinc" --strip-components=1
rm "MiniZincIDE-${LATEST_MINIZINC_VERSION}-bundle-linux-x86_64.tgz"

# Create a wrapper script to call MiniZinc with proper LD_LIBRARY_PATH
echo '#!/bin/bash' > /usr/local/bin/minizinc
echo "exec env LD_LIBRARY_PATH=\$HOME/minizinc/lib:\$LD_LIBRARY_PATH \$HOME/minizinc/bin/minizinc \"\$@\"" >> /usr/local/bin/minizinc
chmod +x /usr/local/bin/minizinc

# Create a Python virtual environment
python3 -m venv "$HOME/zerovenv"
source "$HOME/zerovenv/bin/activate"

# Install Python packages
pip install --upgrade pip
pip install minizinc