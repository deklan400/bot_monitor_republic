#!/usr/bin/env python3
"""
RAI Sentinel - Simple Telegram Bot
Python 3.10+ required

Simple mode:
- Only responds to /status and /help
- No buttons, keyboards, or charts
- Uses requests library only
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Required environment variables
REQUIRED_VARS = {
    'TG_TOKEN': os.getenv('TG_TOKEN'),
    'TG_CHAT_ID': os.getenv('TG_CHAT_ID'),
}

# Optional
BOT_POLL_TIMEOUT = int(os.getenv('BOT_POLL_TIMEOUT', '30'))
BOT_COOLDOWN_SECONDS = int(os.getenv('BOT_COOLDOWN_SECONDS', '10'))
MONITOR_SCRIPT = Path(__file__).parent / 'monitor.py'

# Telegram API
TG_API_BASE = f"https://api.telegram.org/bot{REQUIRED_VARS.get('TG_TOKEN', '')}"

# State
last_command_time = {}
cooldown_per_chat = {}
CLEANUP_INTERVAL = 3600  # Cleanup old entries every hour
last_cleanup = 0


# =============================================================================
# VALIDATION
# =============================================================================

def validate_config() -> bool:
    """Validate required environment variables"""
    missing = [var for var, value in REQUIRED_VARS.items() if not value]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        return False
    
    # Validate Telegram token format
    token = REQUIRED_VARS['TG_TOKEN']
    if ':' not in token or len(token) < 20:
        print("ERROR: Invalid Telegram token format", file=sys.stderr)
        return False
    
    # Check if monitor.py exists
    if not MONITOR_SCRIPT.exists():
        print(f"ERROR: Monitor script not found: {MONITOR_SCRIPT}", file=sys.stderr)
        return False
    
    return True


def test_telegram_api() -> bool:
    """Test Telegram API connectivity"""
    try:
        url = f"{TG_API_BASE}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('ok'):
            bot_info = data.get('result', {})
            print(f"Bot connected: @{bot_info.get('username', 'unknown')}")
            return True
        return False
    except Exception as e:
        print(f"ERROR: Failed to connect to Telegram API: {e}", file=sys.stderr)
        return False


# =============================================================================
# TELEGRAM API
# =============================================================================

def send_message(chat_id: str, text: str) -> bool:
    """Send message to Telegram chat"""
    try:
        url = f"{TG_API_BASE}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"ERROR: Failed to send message: {e}", file=sys.stderr)
        return False


def get_updates(offset: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Get updates from Telegram"""
    try:
        url = f"{TG_API_BASE}/getUpdates"
        params = {
            'timeout': BOT_POLL_TIMEOUT,
            'allowed_updates': ['message']
        }
        if offset:
            params['offset'] = offset
        
        response = requests.get(url, params=params, timeout=BOT_POLL_TIMEOUT + 5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"ERROR: Failed to get updates: {e}", file=sys.stderr)
        return None


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

def handle_help(chat_id: str) -> None:
    """Handle /help command"""
    message = """🤖 RAI Sentinel Bot

Commands:
/status - Run validator monitor and get current status
/help   - Show this help message

The bot monitors your RAI validator and sends alerts via Telegram.

For status updates, use /status command."""
    
    send_message(chat_id, message)


def cleanup_old_entries():
    """Clean up old entries from last_command_time to prevent memory leak"""
    global last_cleanup, last_command_time
    current_time = time.time()
    
    # Only cleanup once per hour
    if current_time - last_cleanup < CLEANUP_INTERVAL:
        return
    
    # Remove entries older than 24 hours
    cutoff_time = current_time - 86400  # 24 hours
    old_keys = [k for k, v in last_command_time.items() if v < cutoff_time]
    for k in old_keys:
        del last_command_time[k]
    
    last_cleanup = current_time


def handle_status(chat_id: str) -> bool:
    """Handle /status command - run monitor.py --force"""
    # Cleanup old entries periodically
    cleanup_old_entries()
    
    # Check cooldown
    chat_id_int = int(chat_id) if chat_id.lstrip('-').isdigit() else hash(chat_id)
    current_time = time.time()
    
    if chat_id_int in last_command_time:
        time_since = current_time - last_command_time[chat_id_int]
        if time_since < BOT_COOLDOWN_SECONDS:
            remaining = int(BOT_COOLDOWN_SECONDS - time_since)
            send_message(chat_id, f"⏳ Please wait {remaining} seconds before requesting status again.")
            return False
    
    # Update last command time
    last_command_time[chat_id_int] = current_time
    
    # Send acknowledgment
    send_message(chat_id, "🔄 Running validator check... Please wait.")
    
    # Run monitor.py with --force flag
    try:
        cmd = [sys.executable, str(MONITOR_SCRIPT), '--force']
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(MONITOR_SCRIPT.parent)
        )
        
        if result.returncode == 0:
            # Monitor script should send the status message itself
            # Just confirm here
            send_message(chat_id, "✅ Status check completed. Check the status message above.")
        else:
            error_msg = result.stderr[:500] if result.stderr else "Unknown error"
            send_message(chat_id, f"❌ Status check failed:\n{error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        send_message(chat_id, "⏱️ Status check timed out. Please try again later.")
        return False
    except Exception as e:
        send_message(chat_id, f"❌ Error running status check: {str(e)[:200]}")
        return False
    
    return True


def handle_unknown_command(chat_id: str, command: str) -> None:
    """Handle unknown commands"""
    message = f"❓ Unknown command: {command}\n\nUse /help to see available commands."
    send_message(chat_id, message)


# =============================================================================
# MESSAGE PROCESSING
# =============================================================================

def process_message(message: Dict[str, Any]) -> None:
    """Process incoming message"""
    chat = message.get('chat', {})
    chat_id = str(chat.get('id'))
    text = message.get('text', '').strip()
    
    # Only process commands
    if not text.startswith('/'):
        return
    
    # Parse command
    parts = text.split()
    command = parts[0].lower()
    
    # Handle commands
    if command == '/help':
        handle_help(chat_id)
    elif command == '/status':
        handle_status(chat_id)
    else:
        handle_unknown_command(chat_id, command)


# =============================================================================
# MAIN LOOP
# =============================================================================

def main():
    """Main bot loop"""
    # Validate configuration
    if not validate_config():
        print("Configuration validation failed. Exiting.", file=sys.stderr)
        sys.exit(1)
    
    # Test Telegram API
    if not test_telegram_api():
        print("Telegram API test failed. Exiting.", file=sys.stderr)
        sys.exit(1)
    
    print("Bot started. Listening for commands...")
    print(f"Commands: /status, /help")
    print(f"Cooldown: {BOT_COOLDOWN_SECONDS} seconds between /status commands")
    print("Press Ctrl+C to stop")
    
    last_update_id = None
    
    try:
        while True:
            # Get updates
            updates = get_updates(last_update_id)
            
            if not updates or not updates.get('ok'):
                time.sleep(5)
                continue
            
            # Process updates
            for update in updates.get('result', []):
                update_id = update.get('update_id')
                
                # Update offset
                if last_update_id is None or update_id > last_update_id:
                    last_update_id = update_id + 1
                
                # Process message
                message = update.get('message')
                if message:
                    process_message(message)
            
            # Small delay to prevent tight loop
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

