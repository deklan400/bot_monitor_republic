#!/bin/bash

set -e

echo "=========================================="
echo "  RAI SENTINEL - Installation"
echo "=========================================="
echo ""

# Check dependencies
MISSING_DEPS=()
if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi
if ! command -v systemctl &> /dev/null; then
    MISSING_DEPS+=("systemd")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "ERROR: Missing dependencies: ${MISSING_DEPS[*]}"
    exit 1
fi

INSTALL_DIR=$(pwd)
echo "Installation directory: $INSTALL_DIR"
echo ""

# Get user input
echo "Enter configuration values:"
echo ""

read -p "Telegram Bot Token: " TG_TOKEN
read -p "Telegram Chat ID: " TG_CHAT_ID
read -p "Validator Operator Address (VALOPER): " VALOPER
read -p "Wallet Address: " WALLET
read -p "Chain ID [optional]: " CHAIN_ID

# Validate inputs
if [ -z "$TG_TOKEN" ] || [ -z "$TG_CHAT_ID" ] || [ -z "$VALOPER" ] || [ -z "$WALLET" ]; then
    echo "ERROR: Required fields cannot be empty"
    exit 1
fi

echo ""
echo "Creating .env file..."

# Create .env from .env.example
if [ -f ".env.example" ]; then
    cp .env.example .env
else
    touch .env
fi

# Update .env with user values
cat > .env << EOF
TG_TOKEN=${TG_TOKEN}
TG_CHAT_ID=${TG_CHAT_ID}

REPUBLIC_HOME=/root/.republicd
CHAIN_ID=${CHAIN_ID}

VALOPER=${VALOPER}
WALLET=${WALLET}

DENOM=arai
DECIMALS=18

HEARTBEAT_HOURS=3
REWARD_DROP_PCT=5
STUCK_MINUTES=10
EOF

echo "✓ .env file created"
echo ""

# Python venv
echo "Setting up Python environment..."
if [ -d "venv" ]; then
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "✓ Python environment ready"
echo ""

# Create directories
mkdir -p history systemd

# Initialize history CSV
if [ ! -f "history/history.csv" ]; then
    echo "timestamp,height,catching_up,missed_blocks,rewards,balance,delegated" > history/history.csv
fi

echo "✓ Directories created"
echo ""

# Systemd services
echo "Installing systemd services..."

sudo tee /etc/systemd/system/rai-monitor.service > /dev/null << EOF
[Unit]
Description=RAI Validator Monitor
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/monitor.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/rai-monitor.timer > /dev/null << EOF
[Unit]
Description=RAI Validator Monitor Timer
Requires=rai-monitor.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
Persistent=true
AccuracySec=1s

[Install]
WantedBy=timers.target
EOF

echo "✓ Systemd services created"
echo ""

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable rai-monitor.timer
sudo systemctl start rai-monitor.timer

echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "Monitor will run every 1 hour"
echo "Check status: systemctl status rai-monitor.timer"
echo ""
