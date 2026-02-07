#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  RAI SENTINEL - Installation Script"
echo "=========================================="
echo ""

# =============================================================================
# DEPENDENCY CHECKS
# =============================================================================

echo "Checking dependencies..."

MISSING_DEPS=()

if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi

if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    MISSING_DEPS+=("pip")
fi

if ! command -v systemctl &> /dev/null; then
    MISSING_DEPS+=("systemd")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo "Please install missing dependencies and try again."
    exit 1
fi

echo -e "${GREEN}✓ All dependencies found${NC}"
echo ""

# =============================================================================
# GET INSTALLATION DIRECTORY
# =============================================================================

INSTALL_DIR=$(pwd)
echo "Installation directory: $INSTALL_DIR"
echo ""

# =============================================================================
# USER INPUT WITH VALIDATION
# =============================================================================

# Check if .env exists and ask if user wants to update
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to update it? (y/n): " update_env
    if [ "$update_env" != "y" ]; then
        echo "Using existing .env file"
        source .env
        TG_TOKEN=${TG_TOKEN:-""}
        TG_CHAT_ID=${TG_CHAT_ID:-""}
        WALLET_ADDRESS=${WALLET_ADDRESS:-""}
        VALOPER_ADDRESS=${VALOPER_ADDRESS:-""}
        CONSADDR_ADDRESS=${CONSADDR_ADDRESS:-""}
    else
        TG_TOKEN=""
        TG_CHAT_ID=""
        WALLET_ADDRESS=""
        VALOPER_ADDRESS=""
        CONSADDR_ADDRESS=""
    fi
else
    TG_TOKEN=""
    TG_CHAT_ID=""
    WALLET_ADDRESS=""
    VALOPER_ADDRESS=""
    CONSADDR_ADDRESS=""
fi

# Get Telegram Bot Token
while [ -z "$TG_TOKEN" ]; do
    read -p "Enter Telegram Bot Token: " TG_TOKEN
    if [ -z "$TG_TOKEN" ]; then
        echo -e "${RED}❌ Telegram Bot Token cannot be empty!${NC}"
    elif [[ ! "$TG_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        echo -e "${YELLOW}⚠️  Warning: Token format looks invalid (should be: number:alphanumeric)${NC}"
        read -p "Continue anyway? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            TG_TOKEN=""
        fi
    fi
done

# Get Telegram Chat ID
while [ -z "$TG_CHAT_ID" ]; do
    read -p "Enter Telegram Chat ID: " TG_CHAT_ID
    if [ -z "$TG_CHAT_ID" ]; then
        echo -e "${RED}❌ Telegram Chat ID cannot be empty!${NC}"
    elif [[ ! "$TG_CHAT_ID" =~ ^-?[0-9]+$ ]]; then
        echo -e "${YELLOW}⚠️  Warning: Chat ID should be numeric (can be negative for groups)${NC}"
        read -p "Continue anyway? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            TG_CHAT_ID=""
        fi
    fi
done

# Get Wallet Address
while [ -z "$WALLET_ADDRESS" ]; do
    read -p "Enter Wallet Address: " WALLET_ADDRESS
    if [ -z "$WALLET_ADDRESS" ]; then
        echo -e "${RED}❌ Wallet Address cannot be empty!${NC}"
    elif [[ ! "$WALLET_ADDRESS" =~ ^republic1 ]]; then
        echo -e "${YELLOW}⚠️  Warning: Wallet address should start with 'republic1'${NC}"
        read -p "Continue anyway? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            WALLET_ADDRESS=""
        fi
    fi
done

# Get Validator Operator Address
while [ -z "$VALOPER_ADDRESS" ]; do
    read -p "Enter Validator Operator Address (valoper): " VALOPER_ADDRESS
    if [ -z "$VALOPER_ADDRESS" ]; then
        echo -e "${RED}❌ Validator Operator Address cannot be empty!${NC}"
    elif [[ ! "$VALOPER_ADDRESS" =~ ^republicvaloper1 ]]; then
        echo -e "${YELLOW}⚠️  Warning: Validator address should start with 'republicvaloper1'${NC}"
        read -p "Continue anyway? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            VALOPER_ADDRESS=""
        fi
    fi
done

# Get Consensus Address (optional but recommended)
if [ -z "$CONSADDR_ADDRESS" ]; then
    read -p "Enter Consensus Address (consaddr) [optional]: " CONSADDR_ADDRESS
    if [ -n "$CONSADDR_ADDRESS" ] && [[ ! "$CONSADDR_ADDRESS" =~ ^republicvalcons1 ]]; then
        echo -e "${YELLOW}⚠️  Warning: Consensus address should start with 'republicvalcons1'${NC}"
        read -p "Continue anyway? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            CONSADDR_ADDRESS=""
        fi
    fi
fi

echo ""
echo -e "${GREEN}✓ Input validation complete${NC}"
echo ""

# =============================================================================
# CREATE .ENV FILE
# =============================================================================

echo "Creating .env file..."

cat > .env << EOF
# Telegram Configuration
TG_TOKEN=${TG_TOKEN}
TG_CHAT_ID=${TG_CHAT_ID}

# Validator Addresses
WALLET_ADDRESS=${WALLET_ADDRESS}
VALOPER_ADDRESS=${VALOPER_ADDRESS}
CONSADDR_ADDRESS=${CONSADDR_ADDRESS}

# Network Configuration
RPC_URL=http://localhost:26657
LCD_URL=http://localhost:1317
CHAIN_ID=republic_1-1

# Token Configuration
DENOM=arai
DECIMALS=18

# Monitoring Configuration
HEARTBEAT_HOURS=3
REWARD_DROP_PCT=5.0
STUCK_MINUTES=10

# Directory Configuration
DATA_DIR=./history
REPUBLIC_HOME=/root/.republicd
REPUBLICD_BINARY=republicd

# Bot Configuration
BOT_POLL_TIMEOUT=30
BOT_COOLDOWN_SECONDS=10
EOF

echo -e "${GREEN}✓ Created .env file${NC}"
echo ""

# =============================================================================
# PYTHON VIRTUAL ENVIRONMENT
# =============================================================================

echo "Setting up Python virtual environment..."

if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
    read -p "Recreate virtual environment? (y/n): " recreate_venv
    if [ "$recreate_venv" = "y" ]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies from requirements.txt..."

if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  requirements.txt not found, creating default...${NC}"
    cat > requirements.txt << EOF
requests>=2.31.0
python-dotenv>=1.0.0
matplotlib>=3.7.0
EOF
fi

pip install -r requirements.txt --quiet

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# =============================================================================
# CREATE DIRECTORIES AND FILES
# =============================================================================

# Create history directory
echo "Creating history directory..."
mkdir -p history
echo -e "${GREEN}✓ History directory created${NC}"

# Initialize history CSV if empty
if [ ! -f "history/history.csv" ] || [ ! -s "history/history.csv" ]; then
    echo "timestamp,height,validator_status,jailed,tombstoned,node_sync,missed_blocks,wallet_balance,delegated_balance,rewards" > history/history.csv
    echo -e "${GREEN}✓ History CSV initialized${NC}"
fi

# Initialize state.json if it doesn't exist
echo "Initializing state.json..."
if [ ! -f "history/state.json" ]; then
    cat > history/state.json << EOF
{
  "last_heartbeat": 0,
  "last_missed_blocks": 0,
  "last_height": 0,
  "last_status": "",
  "last_check": 0
}
EOF
    echo -e "${GREEN}✓ State file initialized${NC}"
fi

echo ""

# =============================================================================
# SYSTEMD SERVICES
# =============================================================================

echo "Installing systemd services..."

# Create rai-monitor.service
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

echo -e "${GREEN}✓ Created rai-monitor.service${NC}"

# Create rai-monitor.timer
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

echo -e "${GREEN}✓ Created rai-monitor.timer${NC}"

# Create rai-bot.service
sudo tee /etc/systemd/system/rai-bot.service > /dev/null << EOF
[Unit]
Description=RAI Sentinel Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/bot.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Created rai-bot.service${NC}"

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Systemd daemon reloaded${NC}"

# Enable and start services
echo ""
echo "Enabling and starting services..."

# Enable and start timer
sudo systemctl enable rai-monitor.timer
if sudo systemctl is-active --quiet rai-monitor.timer; then
    echo -e "${YELLOW}⚠️  rai-monitor.timer already running${NC}"
else
    sudo systemctl start rai-monitor.timer
    echo -e "${GREEN}✓ Started rai-monitor.timer${NC}"
fi

# Enable and start bot
sudo systemctl enable rai-bot.service
if sudo systemctl is-active --quiet rai-bot.service; then
    echo -e "${YELLOW}⚠️  rai-bot.service already running, restarting...${NC}"
    sudo systemctl restart rai-bot.service
else
    sudo systemctl start rai-bot.service
    echo -e "${GREEN}✓ Started rai-bot.service${NC}"
fi

echo ""

# =============================================================================
# INSTALLATION COMPLETE
# =============================================================================

echo "=========================================="
echo -e "${GREEN}  Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
echo ""
echo "Services status:"
echo "  Monitor timer: $(sudo systemctl is-active rai-monitor.timer)"
echo "  Bot service:   $(sudo systemctl is-active rai-bot.service)"
echo ""
echo "Useful commands:"
echo "  Timer status:  sudo systemctl status rai-monitor.timer"
echo "  Bot status:    sudo systemctl status rai-bot.service"
echo "  Monitor logs:  sudo journalctl -u rai-monitor.service -f"
echo "  Bot logs:      sudo journalctl -u rai-bot.service -f"
echo "  Stop timer:    sudo systemctl stop rai-monitor.timer"
echo "  Stop bot:      sudo systemctl stop rai-bot.service"
echo "  Restart bot:   sudo systemctl restart rai-bot.service"
echo ""
echo -e "${GREEN}Setup complete! The monitor will run every 1 hour.${NC}"
echo ""
