#!/bin/bash
# Quick Start Script untuk VPS
# Run sebagai root

set -e

echo "=========================================="
echo "  RAI SENTINEL - Quick Start"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
apt update -qq
apt install -y python3 python3-pip python3-venv git

# Create directory
echo "Creating installation directory..."
mkdir -p /opt/rai-sentinel
cd /opt/rai-sentinel

echo ""
echo "=========================================="
echo "  Next Steps:"
echo "=========================================="
echo ""
echo "1. Upload semua project files ke /opt/rai-sentinel"
echo "   (atau clone dari git repo)"
echo ""
echo "2. Make install.sh executable:"
echo "   chmod +x /opt/rai-sentinel/install.sh"
echo ""
echo "3. Run install script:"
echo "   cd /opt/rai-sentinel"
echo "   ./install.sh"
echo ""
echo "=========================================="


