#!/usr/bin/env python3
"""
RAI Sentinel - Validator Monitor
Python 3.10+ required
"""

import os
import sys
import json
import csv
import time
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv
import tempfile
import shutil

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Required environment variables
REQUIRED_VARS = {
    'TG_TOKEN': os.getenv('TG_TOKEN'),
    'TG_CHAT_ID': os.getenv('TG_CHAT_ID'),
    'WALLET_ADDRESS': os.getenv('WALLET_ADDRESS'),
    'VALOPER_ADDRESS': os.getenv('VALOPER_ADDRESS'),
    'CONSADDR_ADDRESS': os.getenv('CONSADDR_ADDRESS'),
}

# Optional environment variables with defaults
RPC_URL = os.getenv('RPC_URL', 'http://localhost:26657')
LCD_URL = os.getenv('LCD_URL', 'http://localhost:1317')
CHAIN_ID = os.getenv('CHAIN_ID', '')
DENOM = os.getenv('DENOM', 'arai')
DECIMALS = int(os.getenv('DECIMALS', '18'))
HEARTBEAT_HOURS = float(os.getenv('HEARTBEAT_HOURS', '3'))
DATA_DIR = Path(os.getenv('DATA_DIR', './history'))
REPUBLIC_HOME = Path(os.getenv('REPUBLIC_HOME', '/root/.republicd'))
REPUBLICD_BINARY = os.getenv('REPUBLICD_BINARY', 'republicd')

# Retry configuration
RPC_RETRY_ATTEMPTS = 3
RPC_RETRY_BASE_DELAY = 1  # seconds

# Paths
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / 'state.json'
HISTORY_CSV = DATA_DIR / 'history.csv'

# =============================================================================
# VALIDATION
# =============================================================================

def validate_config() -> bool:
    """Fail-fast validation of required environment variables"""
    missing = [var for var, value in REQUIRED_VARS.items() if not value]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Please set all required variables in .env file", file=sys.stderr)
        return False
    return True


# =============================================================================
# UTILITIES
# =============================================================================

def log_error(msg: str) -> None:
    """Log error to stderr"""
    print(f"[ERROR] {msg}", file=sys.stderr)


def atomic_write_json(filepath: Path, data: Dict[str, Any]) -> bool:
    """Atomically write JSON file"""
    try:
        # Write to temp file first
        temp_file = filepath.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        # Atomic move
        shutil.move(str(temp_file), str(filepath))
        return True
    except Exception as e:
        log_error(f"Failed to write state file: {e}")
        return False


def load_state() -> Dict[str, Any]:
    """Load state from JSON file"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        log_error(f"Failed to load state: {e}")
    return {}


def save_state(state: Dict[str, Any]) -> None:
    """Save state to JSON file atomically"""
    atomic_write_json(STATE_FILE, state)


# =============================================================================
# TELEGRAM
# =============================================================================

# Telegram rate limiting
_last_telegram_send = 0
_telegram_min_interval = 1  # Minimum 1 second between sends

def send_telegram_message(text: str) -> bool:
    """Send message to Telegram with rate limiting"""
    global _last_telegram_send
    
    # Rate limiting: ensure minimum interval between sends
    current_time = time.time()
    time_since_last = current_time - _last_telegram_send
    if time_since_last < _telegram_min_interval:
        time.sleep(_telegram_min_interval - time_since_last)
    
    try:
        url = f"https://api.telegram.org/bot{REQUIRED_VARS['TG_TOKEN']}/sendMessage"
        payload = {
            'chat_id': REQUIRED_VARS['TG_CHAT_ID'],
            'text': text
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        _last_telegram_send = time.time()
        return True
    except Exception as e:
        log_error(f"Failed to send Telegram message: {e}")
        return False


# =============================================================================
# RPC/LCD CALLS WITH RETRY
# =============================================================================

def rpc_call(endpoint: str, retry_attempts: int = RPC_RETRY_ATTEMPTS) -> Optional[Dict[str, Any]]:
    """Make RPC call with retry and backoff"""
    for attempt in range(retry_attempts):
        try:
            url = f"{RPC_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < retry_attempts - 1:
                delay = RPC_RETRY_BASE_DELAY * (2 ** attempt)
                time.sleep(delay)
                continue
            log_error(f"RPC call failed {endpoint} after {retry_attempts} attempts: {e}")
            return None
    return None


def lcd_call(endpoint: str, retry_attempts: int = RPC_RETRY_ATTEMPTS) -> Optional[Dict[str, Any]]:
    """Make LCD call with retry and backoff"""
    for attempt in range(retry_attempts):
        try:
            url = f"{LCD_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < retry_attempts - 1:
                delay = RPC_RETRY_BASE_DELAY * (2 ** attempt)
                time.sleep(delay)
                continue
            log_error(f"LCD call failed {endpoint} after {retry_attempts} attempts: {e}")
            return None
    return None


# =============================================================================
# REPUBLICD SUBPROCESS CALLS
# =============================================================================

def republicd_query(command: list) -> Optional[str]:
    """Execute republicd query command via subprocess"""
    try:
        cmd = [REPUBLICD_BINARY] + command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPUBLIC_HOME) if REPUBLIC_HOME.exists() else None
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            log_error(f"republicd command failed: {' '.join(cmd)} - {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        log_error(f"republicd command timeout: {' '.join(command)}")
        return None
    except Exception as e:
        log_error(f"republicd subprocess error: {e}")
        return None


# =============================================================================
# DATA COLLECTION
# =============================================================================

def get_node_status() -> Optional[Dict[str, Any]]:
    """Get node status from RPC or republicd subprocess"""
    # Try RPC first
    result = rpc_call('/status')
    if result and 'result' in result:
        return result['result']
    
    # Fallback to republicd subprocess
    try:
        output = republicd_query(['status'])
        if output:
            return json.loads(output)
    except Exception:
        pass
    
    return None


def get_validator_info() -> Optional[Dict[str, Any]]:
    """Get validator information from LCD or republicd subprocess"""
    # Try LCD first
    endpoint = f"/cosmos/staking/v1beta1/validators/{REQUIRED_VARS['VALOPER_ADDRESS']}"
    result = lcd_call(endpoint)
    if result and 'validator' in result:
        return result['validator']
    
    # Fallback to republicd subprocess (if LCD not available)
    try:
        output = republicd_query(['query', 'staking', 'validator', REQUIRED_VARS['VALOPER_ADDRESS'], '--output', 'json'])
        if output:
            validator_data = json.loads(output)
            # Convert republicd output format to LCD format
            if validator_data:
                return {
                    'status': validator_data.get('status', 'UNKNOWN'),
                    'jailed': validator_data.get('jailed', False),
                    'tombstoned': validator_data.get('tombstoned', False),
                    **validator_data
                }
    except Exception as e:
        log_error(f"republicd query fallback failed: {e}")
    
    return None


def get_signing_info() -> Optional[Dict[str, Any]]:
    """Get validator signing info from LCD"""
    endpoint = f"/cosmos/slashing/v1beta1/validators/{REQUIRED_VARS['CONSADDR_ADDRESS']}/signing_infos"
    result = lcd_call(endpoint)
    if result and 'val_signing_info' in result:
        return result['val_signing_info']
    return None


def get_wallet_balance() -> int:
    """Get wallet balance"""
    # Try LCD first
    endpoint = f"/cosmos/bank/v1beta1/balances/{REQUIRED_VARS['WALLET_ADDRESS']}"
    result = lcd_call(endpoint)
    if result and 'balances' in result:
        for balance in result['balances']:
            if balance['denom'] == DENOM:
                try:
                    return int(balance['amount'])
                except (ValueError, TypeError):
                    return 0
    
    # Fallback to republicd subprocess
    try:
        output = republicd_query(['query', 'bank', 'balances', REQUIRED_VARS['WALLET_ADDRESS'], '--output', 'json'])
        if output:
            result = json.loads(output)
            if 'balances' in result:
                for balance in result['balances']:
                    if balance.get('denom') == DENOM:
                        try:
                            return int(balance.get('amount', '0'))
                        except (ValueError, TypeError):
                            return 0
    except Exception as e:
        log_error(f"republicd balance query failed: {e}")
    
    return 0


def get_delegated_balance() -> int:
    """Get delegated balance"""
    # Try LCD first
    endpoint = f"/cosmos/staking/v1beta1/delegations/{REQUIRED_VARS['WALLET_ADDRESS']}"
    result = lcd_call(endpoint)
    total = 0
    if result and 'delegation_responses' in result:
        for delegation in result['delegation_responses']:
            if 'balance' in delegation and delegation['balance']['denom'] == DENOM:
                try:
                    total += int(delegation['balance']['amount'])
                except (ValueError, TypeError):
                    continue
        if total > 0:
            return total
    
    # Fallback to republicd subprocess
    try:
        output = republicd_query(['query', 'staking', 'delegations', REQUIRED_VARS['WALLET_ADDRESS'], '--output', 'json'])
        if output:
            result = json.loads(output)
            if 'delegation_responses' in result:
                for delegation in result['delegation_responses']:
                    if 'balance' in delegation and delegation['balance'].get('denom') == DENOM:
                        try:
                            total += int(delegation['balance'].get('amount', '0'))
                        except (ValueError, TypeError):
                            continue
    except Exception as e:
        log_error(f"republicd delegations query failed: {e}")
    
    return total


def get_rewards() -> int:
    """Get pending rewards"""
    # Try LCD first
    endpoint = f"/cosmos/distribution/v1beta1/delegators/{REQUIRED_VARS['WALLET_ADDRESS']}/rewards"
    result = lcd_call(endpoint)
    total = 0
    if result and 'total' in result:
        for reward in result['total']:
            if reward['denom'] == DENOM:
                amount = reward.get('amount', '0')
                try:
                    if isinstance(amount, str):
                        # Remove decimal part if present
                        amount = amount.split('.')[0]
                    total += int(amount)
                except (ValueError, TypeError):
                    continue
        if total > 0:
            return total
    
    # Fallback to republicd subprocess
    try:
        output = republicd_query(['query', 'distribution', 'rewards', REQUIRED_VARS['WALLET_ADDRESS'], '--output', 'json'])
        if output:
            result = json.loads(output)
            if 'total' in result:
                for reward in result['total']:
                    if reward.get('denom') == DENOM:
                        amount = reward.get('amount', '0')
                        try:
                            if isinstance(amount, str):
                                amount = amount.split('.')[0]
                            total += int(amount)
                        except (ValueError, TypeError):
                            continue
    except Exception as e:
        log_error(f"republicd rewards query failed: {e}")
    
    return total


def format_balance(amount: int) -> str:
    """Format balance to human readable"""
    if amount == 0:
        return "0.00"
    balance = amount / (10 ** DECIMALS)
    return f"{balance:.2f}"


# =============================================================================
# MONITORING LOGIC
# =============================================================================

def collect_metrics() -> Dict[str, Any]:
    """Collect all monitoring metrics - always returns dict, never None"""
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'node_sync': None,
        'height': 0,
        'validator_status': 'UNKNOWN',
        'jailed': False,
        'tombstoned': False,
        'missed_blocks': 0,
        'wallet_balance': 0,
        'delegated_balance': 0,
        'rewards': 0,
    }
    
    # Get node status
    node_status = get_node_status()
    if node_status:
        sync_info = node_status.get('sync_info', {})
        metrics['node_sync'] = sync_info.get('catching_up', True)
        try:
            metrics['height'] = int(sync_info.get('latest_block_height', 0))
        except (ValueError, TypeError):
            metrics['height'] = 0
    
    # Get validator info
    validator = get_validator_info()
    if validator:
        metrics['validator_status'] = validator.get('status', 'UNKNOWN')
        metrics['jailed'] = validator.get('jailed', False)
        metrics['tombstoned'] = validator.get('tombstoned', False)
    
    # Get signing info (missed blocks)
    signing_info = get_signing_info()
    if signing_info:
        try:
            missed = signing_info.get('missed_blocks_counter', '0')
            metrics['missed_blocks'] = int(missed)
        except (ValueError, TypeError):
            metrics['missed_blocks'] = 0
    
    # Get balances
    metrics['wallet_balance'] = get_wallet_balance()
    metrics['delegated_balance'] = get_delegated_balance()
    metrics['rewards'] = get_rewards()
    
    return metrics


def determine_status(metrics: Dict[str, Any], state: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Determine status level: HEALTHY, WARNING, ALERT, FATAL
    Returns: (status_level, should_send_message)
    """
    # Check if RPC data is available (prevent false alerts when RPC is down)
    node_sync = metrics.get('node_sync')
    height = metrics.get('height', 0)
    val_status = metrics.get('validator_status', 'UNKNOWN')
    
    # If critical data is missing, don't alert (RPC might be down)
    if node_sync is None and height == 0 and val_status == 'UNKNOWN':
        # RPC appears to be down, don't send false alerts
        return 'HEALTHY', False
    
    # FATAL: Tombstoned
    if metrics.get('tombstoned', False):
        return 'FATAL', True
    
    # ALERT: Jailed OR missed blocks increased
    if metrics.get('jailed', False):
        return 'ALERT', True
    
    # Check missed blocks increase (only if we have valid data)
    if height > 0:  # Only check if we have valid height
        last_missed = state.get('last_missed_blocks', 0)
        current_missed = metrics.get('missed_blocks', 0)
        if current_missed > last_missed:
            return 'ALERT', True
    
    # WARNING: Unbonding OR catching up
    if val_status in ['BOND_STATUS_UNBONDING', 'UNBONDING']:
        return 'WARNING', True
    
    # Only check node_sync if we have valid data
    if node_sync is not None and node_sync:  # catching_up = True
        return 'WARNING', True
    
    # HEALTHY: Everything OK
    return 'HEALTHY', False


def should_send_heartbeat(state: Dict[str, Any]) -> bool:
    """Check if heartbeat should be sent"""
    last_heartbeat = state.get('last_heartbeat', 0)
    if last_heartbeat == 0:
        return True
    
    hours_since = (time.time() - last_heartbeat) / 3600
    return hours_since >= HEARTBEAT_HOURS


def format_status_message(metrics: Dict[str, Any], status: str) -> str:
    """Format status message for Telegram"""
    # Status emoji
    emoji_map = {
        'HEALTHY': '🟢',
        'WARNING': '🟡',
        'ALERT': '🔴',
        'FATAL': '⚫'
    }
    emoji = emoji_map.get(status, '⚪')
    
    # Status text
    status_text = status
    
    # Validator status
    val_status = metrics.get('validator_status', 'UNKNOWN')
    val_status_map = {
        'BOND_STATUS_BONDED': 'BONDED',
        'BOND_STATUS_UNBONDING': 'UNBONDING',
        'BOND_STATUS_UNBONDED': 'UNBONDED'
    }
    val_status_display = val_status_map.get(val_status, val_status.replace('BOND_STATUS_', ''))
    
    # Format timestamp (WIB = UTC+7)
    wib_time = datetime.utcnow() + timedelta(hours=7)
    timestamp = wib_time.strftime("%Y-%m-%d %H:%M:%S WIB")
    
    # Build message
    message = f"{emoji} RAI VALIDATOR STATUS — {status_text}\n\n"
    
    message += "Validator:\n"
    message += f"• Status  : {val_status_display}\n"
    message += f"• Jailed  : {'Yes' if metrics.get('jailed') else 'No'}\n"
    if metrics.get('tombstoned'):
        message += f"• Tombstoned : Yes\n"
    
    message += "\nNode:\n"
    sync_status = "SYNCING" if metrics.get('node_sync', True) else "OK"
    message += f"• Sync    : {sync_status}\n"
    message += f"• Height  : {metrics.get('height', 0):,}\n"
    message += f"• Missed  : {metrics.get('missed_blocks', 0)}\n"
    
    message += "\nBalance:\n"
    message += f"• Wallet    : {format_balance(metrics.get('wallet_balance', 0))} RAI\n"
    message += f"• Delegated : {format_balance(metrics.get('delegated_balance', 0))} RAI\n"
    message += f"• Rewards   : {format_balance(metrics.get('rewards', 0))} RAI\n"
    
    message += f"\n⏱ {timestamp}"
    
    return message


def append_history(metrics: Dict[str, Any]) -> None:
    """Append metrics to history CSV"""
    try:
        file_exists = HISTORY_CSV.exists() and HISTORY_CSV.stat().st_size > 0
        
        with open(HISTORY_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    'timestamp', 'height', 'validator_status', 'jailed', 'tombstoned',
                    'node_sync', 'missed_blocks', 'wallet_balance', 'delegated_balance', 'rewards'
                ])
            writer.writerow([
                metrics['timestamp'],
                metrics['height'],
                metrics['validator_status'],
                metrics['jailed'],
                metrics['tombstoned'],
                metrics['node_sync'],
                metrics['missed_blocks'],
                metrics['wallet_balance'],
                metrics['delegated_balance'],
                metrics['rewards']
            ])
    except Exception as e:
        log_error(f"Failed to append history: {e}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main monitoring function"""
    # Check for --force flag
    force_mode = '--force' in sys.argv
    
    # Fail-fast validation
    if not validate_config():
        sys.exit(1)
    
    # Load state
    state = load_state()
    
    # Collect metrics (never crash on errors, always returns dict)
    metrics = collect_metrics()
    
    # Determine status
    status, should_alert = determine_status(metrics, state)
    
    # Check heartbeat
    should_heartbeat = should_send_heartbeat(state)
    
    # Send message if needed (force mode always sends)
    if force_mode or should_alert or (status == 'HEALTHY' and should_heartbeat):
        message = format_status_message(metrics, status)
        send_telegram_message(message)
        
        # Update heartbeat time if sent (unless forced)
        if not force_mode and status == 'HEALTHY' and should_heartbeat:
            state['last_heartbeat'] = time.time()
    
    # Update state
    state['last_missed_blocks'] = metrics.get('missed_blocks', 0)
    state['last_height'] = metrics.get('height', 0)
    state['last_status'] = status
    state['last_check'] = time.time()
    
    # Save state atomically
    save_state(state)
    
    # Append to history
    append_history(metrics)


if __name__ == '__main__':
    main()
