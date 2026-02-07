#!/bin/bash
# Setup Git Repository Script
# Run di local machine (bukan di VPS)

set -e

echo "=========================================="
echo "  RAI SENTINEL - Git Setup"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if already a git repo
if [ -d ".git" ]; then
    echo "⚠️  Git repository already initialized"
    read -p "Continue anyway? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        exit 0
    fi
fi

# Initialize git
echo "Initializing git repository..."
git init

# Create .gitignore if not exists
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# History & State
history/*.json
history/*.png
history/*.csv
!history/.gitkeep

# Charts
*.png
*.jpg
*.jpeg
!systemd/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary
*.tmp
*.bak
EOF
    echo "✓ .gitignore created"
else
    echo "✓ .gitignore already exists"
fi

# Add all files
echo "Adding files to git..."
git add .

# Initial commit
echo "Creating initial commit..."
git commit -m "Initial commit: RAI Sentinel validator monitor"

echo ""
echo "=========================================="
echo "  Git Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create repository on GitHub/GitLab"
echo "2. Add remote:"
echo "   git remote add origin https://github.com/username/rai-sentinel.git"
echo "3. Push to remote:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Or if using SSH:"
echo "   git remote add origin git@github.com:username/rai-sentinel.git"
echo "   git push -u origin main"
echo ""

