#!/usr/bin/env python3
"""
RAI Sentinel - Production Validator Monitor
Cosmos SDK validator monitoring for RAI chain
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
    'VALOPER': os.getenv('VALOPER'),
    'WALLET': os.getenv('WALLET'),
}

# Optional with defaults
REPUBLIC_HOME = Path(os.getenv('REPUBLIC_HOME', '/root/.republicd'))
CHAIN_ID = os.getenv('CHAIN_ID', '')
DENOM = os.getenv('DENOM', 'arai')
DECIMALS = int(os.getenv('DECIMALS', '18'))
HEARTBEAT_HOURS = float(os.getenv('HEARTBEAT_HOURS', '3'))
REWARD_DROP_PCT = float(os.getenv('REWARD_DROP_PCT', '5'))
STUCK_MINUTES = int(os.getenv('STUCK_MINUTES', '10'))
REPUBLICD_BINARY = os.getenv('REPUBLICD_BINARY', 'republicd')

# Paths
HISTORY_DIR = Path('history')
HISTORY_DIR.mkdir(exist_ok=True)
HISTORY_CSV = HISTORY_DIR / 'history.csv'
REWARDS_CHART = HISTORY_DIR / 'rewards.png'
MISSED_BLOCKS_CHART = HISTORY_DIR / 'missed_blocks.png'
STATE_FILE = HISTORY_DIR / 'state.json'

# RPC endpoint
RPC_URL = os.getenv('RPC_URL', 'http://localhost:26657')

# Retry config
RPC_RETRY_ATTEMPTS = 3
RPC_RETRY_DELAY = 2

# =============================================================================
# VALIDATION
# =============================================================================

def validate_config() -> bool:
    """Validate all required environment variables"""
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
        temp_file = filepath.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        shutil.move(str(temp_file), str(filepath))
        return True
    except Exception as e:
        log_error(f"Failed to write state: {e}")
        return False


def load_state() -> Dict[str, Any]:
    """Load state from JSON"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        log_error(f"Failed to load state: {e}")
    return {}


def save_state(state: Dict[str, Any]) -> None:
    """Save state atomically"""
    atomic_write_json(STATE_FILE, state)


def map_bond_status(status: str) -> str:
    """Map Cosmos SDK bond status to human readable - CRITICAL FUNCTION"""
    if not status:
        return "UNKNOWN"
    
    # Direct mapping
    status_map = {
        "BOND_STATUS_BONDED": "BONDED",
        "BOND_STATUS_UNBONDING": "UNBONDING",
        "BOND_STATUS_UNBONDED": "UNBONDED",
    }
    
    mapped = status_map.get(status)
    if mapped:
        return mapped
    
    # Already mapped
    if status in ["BONDED", "UNBONDING", "UNBONDED"]:
        return status
    
    # Try removing prefix
    if status.startswith("BOND_STATUS_"):
        return status.replace("BOND_STATUS_", "")
    
    return "UNKNOWN"


# =============================================================================
# TELEGRAM
# =============================================================================

def send_telegram_message(text: str) -> bool:
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{REQUIRED_VARS['TG_TOKEN']}/sendMessage"
        payload = {
            'chat_id': REQUIRED_VARS['TG_CHAT_ID'],
            'text': text
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        log_error(f"Failed to send Telegram: {e}")
        return False


def send_telegram_photo(photo_path: Path, caption: str = "") -> bool:
    """Send photo to Telegram"""
    try:
        if not photo_path.exists():
            return False
        url = f"https://api.telegram.org/bot{REQUIRED_VARS['TG_TOKEN']}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': REQUIRED_VARS['TG_CHAT_ID'], 'caption': caption}
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            return True
    except Exception as e:
        log_error(f"Failed to send photo: {e}")
        return False


# =============================================================================
# RPC CALLS
# =============================================================================

def rpc_call(endpoint: str) -> Optional[Dict[str, Any]]:
    """Make RPC call with retry"""
    for attempt in range(RPC_RETRY_ATTEMPTS):
        try:
            url = f"{RPC_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < RPC_RETRY_ATTEMPTS - 1:
                time.sleep(RPC_RETRY_DELAY * (attempt + 1))
                continue
            log_error(f"RPC call failed {endpoint}: {e}")
            return None
    return None


# =============================================================================
# REPUBLICD QUERIES
# =============================================================================

def republicd_query(command: list) -> Optional[str]:
    """Execute republicd query command"""
    try:
        cmd = [REPUBLICD_BINARY] + command
        if CHAIN_ID:
            cmd.extend(['--chain-id', CHAIN_ID])
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
            log_error(f"republicd failed: {' '.join(cmd)} - {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        log_error(f"republicd timeout: {' '.join(command)}")
        return None
    except Exception as e:
        log_error(f"republicd error: {e}")
        return None


# =============================================================================
# DATA COLLECTION
# =============================================================================

def get_node_status() -> Optional[Dict[str, Any]]:
    """Get node status from RPC"""
    result = rpc_call('/status')
    if result and 'result' in result:
        return result['result']
    return None


def get_validator_info() -> Optional[Dict[str, Any]]:
    """Get validator info - CRITICAL: Must use VALOPER address"""
    valoper = REQUIRED_VARS.get('VALOPER')
    if not valoper:
        log_error("VALOPER not configured")
        return None
    
    # Query validator using VALOPER address
    output = republicd_query(['query', 'staking', 'validator', valoper, '--output', 'json'])
    if not output:
        log_error(f"republicd query returned empty for validator: {valoper}")
        return None
    
    try:
        if isinstance(output, str):
            response_data = json.loads(output)
        else:
            response_data = output
        
        if not isinstance(response_data, dict):
            log_error(f"Validator query returned non-dict: {type(response_data)}")
            return None
        
        # Handle nested structure: response may be {"validator": {...}} or direct validator object
        if 'validator' in response_data:
            validator_data = response_data['validator']
        else:
            validator_data = response_data
        
        if not isinstance(validator_data, dict):
            log_error(f"Validator data is not a dict: {type(validator_data)}")
            return None
        
        # Extract raw status - check multiple possible keys
        raw_status = validator_data.get('status') or validator_data.get('Status') or 'UNKNOWN'
        
        # Map status
        mapped_status = map_bond_status(raw_status)
        
        # Extract other fields
        jailed = validator_data.get('jailed', False)
        tombstoned = validator_data.get('tombstoned', False)
        operator_address = validator_data.get('operator_address', valoper)
        
        # Extract moniker from description
        description = validator_data.get('description', {})
        if isinstance(description, dict):
            moniker = description.get('moniker', 'Unknown')
        else:
            moniker = 'Unknown'
        
        return {
            'status': mapped_status,
            'jailed': jailed,
            'tombstoned': tombstoned,
            'operator_address': operator_address,
            'moniker': moniker,
            **validator_data
        }
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse validator JSON: {e}")
        log_error(f"Raw output (first 500 chars): {str(output)[:500]}")
    except Exception as e:
        log_error(f"Failed to process validator data: {e}")
        import traceback
        log_error(traceback.format_exc())
    
    return None


def get_signing_info() -> Optional[Dict[str, Any]]:
    """Get signing info for missed blocks and tombstoned status"""
    # Get validator pubkey first
    validator = get_validator_info()
    if not validator:
        return None
    
    # Try to get consensus address from validator
    consensus_pubkey = validator.get('consensus_pubkey', {})
    if not consensus_pubkey:
        return None
    
    # Query slashing signing-info
    # Note: May need consensus address, try with operator address first
    valoper = REQUIRED_VARS.get('VALOPER')
    try:
        output = republicd_query(['query', 'slashing', 'signing-info', valoper, '--output', 'json'])
        if output:
            if isinstance(output, str):
                return json.loads(output)
            return output
    except Exception as e:
        log_error(f"Failed to get signing info: {e}")
    
    return None


def get_wallet_balance() -> int:
    """Get wallet balance"""
    wallet = REQUIRED_VARS.get('WALLET')
    if not wallet:
        return 0
    
    output = republicd_query(['query', 'bank', 'balances', wallet, '--output', 'json'])
    if not output:
        return 0
    
    try:
        if isinstance(output, str):
            result = json.loads(output)
        else:
            result = output
        
        if isinstance(result, dict) and 'balances' in result:
            for balance in result['balances']:
                if isinstance(balance, dict) and balance.get('denom') == DENOM:
                    try:
                        return int(balance.get('amount', '0'))
                    except (ValueError, TypeError):
                        return 0
    except Exception as e:
        log_error(f"Failed to parse balance: {e}")
    
    return 0


def get_delegated_balance() -> int:
    """Get delegated balance"""
    wallet = REQUIRED_VARS.get('WALLET')
    if not wallet:
        return 0
    
    output = republicd_query(['query', 'staking', 'delegations', wallet, '--output', 'json'])
    if not output:
        return 0
    
    try:
        if isinstance(output, str):
            result = json.loads(output)
        else:
            result = output
        
        total = 0
        if isinstance(result, dict):
            delegations = result.get('delegation_responses', [])
            for delegation in delegations:
                if isinstance(delegation, dict):
                    balance = delegation.get('balance', {})
                    if isinstance(balance, dict) and balance.get('denom') == DENOM:
                        try:
                            total += int(balance.get('amount', '0'))
                        except (ValueError, TypeError):
                            continue
        return total
    except Exception as e:
        log_error(f"Failed to parse delegations: {e}")
    
    return 0


def get_rewards() -> int:
    """Get pending rewards"""
    wallet = REQUIRED_VARS.get('WALLET')
    if not wallet:
        return 0
    
    output = republicd_query(['query', 'distribution', 'rewards', wallet, '--output', 'json'])
    if not output:
        return 0
    
    try:
        if isinstance(output, str):
            result = json.loads(output)
        else:
            result = output
        
        total = 0
        if isinstance(result, dict):
            rewards_list = result.get('total', [])
            for reward in rewards_list:
                if isinstance(reward, dict) and reward.get('denom') == DENOM:
                    amount = reward.get('amount', '0')
                    try:
                        if isinstance(amount, str):
                            amount = amount.split('.')[0]
                        total += int(amount)
                    except (ValueError, TypeError):
                        continue
        return total
    except Exception as e:
        log_error(f"Failed to parse rewards: {e}")
    
    return 0


def format_balance(amount: int) -> str:
    """Format balance with decimals"""
    if amount == 0:
        return "0.00"
    balance = amount / (10 ** DECIMALS)
    return f"{balance:.2f}"


# =============================================================================
# MONITORING LOGIC
# =============================================================================

def collect_metrics() -> Dict[str, Any]:
    """Collect all monitoring metrics"""
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'height': 0,
        'catching_up': True,
        'validator_status': 'UNKNOWN',
        'jailed': False,
        'tombstoned': False,
        'missed_blocks': 0,
        'wallet_balance': 0,
        'delegated_balance': 0,
        'rewards': 0,
        'moniker': 'Unknown',
    }
    
    # Node status
    node_status = get_node_status()
    if node_status:
        sync_info = node_status.get('sync_info', {})
        metrics['catching_up'] = sync_info.get('catching_up', True)
        try:
            metrics['height'] = int(sync_info.get('latest_block_height', 0))
        except (ValueError, TypeError):
            metrics['height'] = 0
    
    # Validator info - CRITICAL
    validator = get_validator_info()
    if validator:
        # Status should already be mapped in get_validator_info()
        mapped_status = validator.get('status', 'UNKNOWN')
        # Double-check mapping (defensive)
        if mapped_status and mapped_status not in ['BONDED', 'UNBONDING', 'UNBONDED']:
            # If somehow not mapped, try to map it
            mapped_status = map_bond_status(mapped_status)
        
        metrics['validator_status'] = mapped_status
        metrics['jailed'] = validator.get('jailed', False)
        metrics['tombstoned'] = validator.get('tombstoned', False)
        metrics['moniker'] = validator.get('moniker', 'Unknown')
        
        # Debug logging
        if mapped_status == 'UNKNOWN':
            log_error(f"WARNING: Validator status is UNKNOWN. Raw validator data: {json.dumps(validator, indent=2)[:500]}")
    else:
        log_error("CRITICAL: Failed to get validator info - status will be UNKNOWN")
        log_error(f"VALOPER configured: {REQUIRED_VARS.get('VALOPER', 'NOT SET')}")
    
    # Signing info (for missed blocks and tombstoned)
    signing_info = get_signing_info()
    if signing_info:
        try:
            missed = signing_info.get('missed_blocks_counter', '0')
            metrics['missed_blocks'] = int(missed)
        except (ValueError, TypeError):
            metrics['missed_blocks'] = 0
        
        # Check tombstoned from signing info if not set
        if not metrics['tombstoned']:
            metrics['tombstoned'] = signing_info.get('tombstoned', False)
    
    # Balances
    metrics['wallet_balance'] = get_wallet_balance()
    metrics['delegated_balance'] = get_delegated_balance()
    metrics['rewards'] = get_rewards()
    
    return metrics


def determine_alert_level(metrics: Dict[str, Any], state: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Determine alert level: HEALTHY, WARNING, ALERT, FATAL
    Returns: (level, should_send)
    """
    status = metrics.get('validator_status', 'UNKNOWN')
    jailed = metrics.get('jailed', False)
    tombstoned = metrics.get('tombstoned', False)
    catching_up = metrics.get('catching_up', True)
    
    # FATAL: Tombstoned
    if tombstoned:
        return 'FATAL', True
    
    # ALERT: Jailed
    if jailed:
        return 'ALERT', True
    
    # ALERT: Missed blocks increasing
    last_missed = state.get('last_missed_blocks', 0)
    current_missed = metrics.get('missed_blocks', 0)
    if current_missed > last_missed:
        return 'ALERT', True
    
    # WARNING: UNBONDING
    if status == 'UNBONDING':
        return 'WARNING', True
    
    # WARNING: Catching up
    if catching_up:
        return 'WARNING', True
    
    # HEALTHY: BONDED, not jailed, not catching up
    if status == 'BONDED' and not jailed and not catching_up:
        return 'HEALTHY', False
    
    # Default to WARNING if status unclear
    return 'WARNING', True


def should_send_heartbeat(state: Dict[str, Any]) -> bool:
    """Check if heartbeat should be sent"""
    last_heartbeat = state.get('last_heartbeat', 0)
    if last_heartbeat == 0:
        return True
    
    hours_since = (time.time() - last_heartbeat) / 3600
    return hours_since >= HEARTBEAT_HOURS


# =============================================================================
# TELEGRAM MESSAGE FORMATTING
# =============================================================================

def format_healthy_message(metrics: Dict[str, Any]) -> str:
    """Format HEALTHY status message"""
    moniker = metrics.get('moniker', 'Unknown')
    status = metrics.get('validator_status', 'UNKNOWN')
    height = metrics.get('height', 0)
    missed = metrics.get('missed_blocks', 0)
    
    message = f"🟢 RAI VALIDATOR STATUS — HEALTHY\n"
    message += f"📛 Moniker: {moniker}\n\n"
    message += "Validator:\n"
    message += f" • 🔓 Status : {status}\n"
    message += f" • 🔒 Jailed : No\n"
    message += f" • ⚰️  Tombstoned : No\n\n"
    message += "Node:\n"
    message += f" • ✅ Sync   : OK\n"
    message += f" • 📊 Height : {height:,}\n"
    message += f" • ⚠️  Missed : {missed}\n\n"
    message += "Balance:\n"
    message += f" • 💰 Wallet    : {format_balance(metrics.get('wallet_balance', 0))} RAI\n"
    message += f" • 🔐 Delegated : {format_balance(metrics.get('delegated_balance', 0))} RAI\n"
    message += f" • 🎁 Rewards   : {format_balance(metrics.get('rewards', 0))} RAI\n\n"
    
    wib_time = datetime.utcnow() + timedelta(hours=7)
    message += f"🕒 {wib_time.strftime('%Y-%m-%d %H:%M')} WIB"
    
    return message


def format_warning_message(metrics: Dict[str, Any]) -> str:
    """Format WARNING status message"""
    moniker = metrics.get('moniker', 'Unknown')
    status = metrics.get('validator_status', 'UNKNOWN')
    catching_up = metrics.get('catching_up', True)
    height = metrics.get('height', 0)
    
    message = f"🟡 RAI VALIDATOR WARNING\n"
    message += f"📛 Moniker: {moniker}\n\n"
    message += "Validator:\n"
    message += f" • 🔓 Status : {status}\n"
    message += f" • 🔒 Jailed : No\n\n"
    message += "Node:\n"
    sync_text = "Catching Up" if catching_up else "OK"
    sync_emoji = "⏳" if catching_up else "✅"
    message += f" • {sync_emoji} Sync   : {sync_text}\n"
    message += f" • 📊 Height : {height:,}\n\n"
    
    wib_time = datetime.utcnow() + timedelta(hours=7)
    message += f"🕒 Detected: {wib_time.strftime('%Y-%m-%d %H:%M')} WIB"
    
    return message


def format_alert_message(metrics: Dict[str, Any]) -> str:
    """Format ALERT status message"""
    moniker = metrics.get('moniker', 'Unknown')
    status = metrics.get('validator_status', 'UNKNOWN')
    jailed = metrics.get('jailed', False)
    missed = metrics.get('missed_blocks', 0)
    
    if jailed:
        message = f"🔴 RAI VALIDATOR ALERT — JAILED\n"
    else:
        message = f"🔴 RAI VALIDATOR ALERT\n"
    
    message += f"📛 Moniker: {moniker}\n\n"
    message += "Validator:\n"
    message += f" • 🔓 Status : {status}\n"
    jailed_emoji = "🔴" if jailed else "🔒"
    message += f" • {jailed_emoji} Jailed : {'YES' if jailed else 'No'}\n\n"
    message += "Node:\n"
    message += f" • 🛑 Sync   : STOPPED\n"
    message += f" • ⚠️  Missed : {missed} blocks\n\n"
    
    wib_time = datetime.utcnow() + timedelta(hours=7)
    message += f"🕒 Detected: {wib_time.strftime('%Y-%m-%d %H:%M')} WIB"
    
    return message


def format_full_info_message(metrics: Dict[str, Any]) -> str:
    """Format FULL INFO message - semua informasi lengkap"""
    moniker = metrics.get('moniker', 'Unknown')
    status = metrics.get('validator_status', 'UNKNOWN')
    jailed = metrics.get('jailed', False)
    tombstoned = metrics.get('tombstoned', False)
    catching_up = metrics.get('catching_up', True)
    height = metrics.get('height', 0)
    missed = metrics.get('missed_blocks', 0)
    
    message = f"📊 RAI VALIDATOR — FULL STATUS REPORT\n"
    message += f"📛 Moniker: {moniker}\n\n"
    message += "Validator:\n"
    message += f" • 🔓 Status : {status}\n"
    jailed_emoji = "🔴" if jailed else "🔒"
    message += f" • {jailed_emoji} Jailed : {'YES' if jailed else 'No'}\n"
    tombstoned_emoji = "⚰️" if tombstoned else "✅"
    message += f" • {tombstoned_emoji} Tombstoned : {'YES' if tombstoned else 'No'}\n\n"
    message += "Node:\n"
    if catching_up:
        sync_emoji = "⏳"
        sync_text = "Catching Up"
    else:
        sync_emoji = "✅"
        sync_text = "OK"
    message += f" • {sync_emoji} Sync   : {sync_text}\n"
    message += f" • 📊 Height : {height:,}\n"
    message += f" • ⚠️  Missed : {missed} blocks\n\n"
    message += "Balance:\n"
    message += f" • 💰 Wallet    : {format_balance(metrics.get('wallet_balance', 0))} RAI\n"
    message += f" • 🔐 Delegated : {format_balance(metrics.get('delegated_balance', 0))} RAI\n"
    message += f" • 🎁 Rewards   : {format_balance(metrics.get('rewards', 0))} RAI\n\n"
    
    wib_time = datetime.utcnow() + timedelta(hours=7)
    message += f"🕒 {wib_time.strftime('%Y-%m-%d %H:%M')} WIB"
    
    return message


def format_fatal_message(metrics: Dict[str, Any]) -> str:
    """Format FATAL status message"""
    moniker = metrics.get('moniker', 'Unknown')
    status = metrics.get('validator_status', 'UNKNOWN')
    
    message = f"☠️ RAI VALIDATOR FATAL — TOMBSTONED\n"
    message += f"📛 Moniker: {moniker}\n\n"
    message += "Validator:\n"
    message += f" • ⚰️  Tombstoned : YES\n"
    message += f" • 🔓 Status     : {status}\n\n"
    message += "🚨 Validator permanently slashed\n"
    message += "Recovery impossible\n\n"
    
    wib_time = datetime.utcnow() + timedelta(hours=7)
    message += f"🕒 Detected: {wib_time.strftime('%Y-%m-%d %H:%M')} WIB"
    
    return message


def format_status_message(metrics: Dict[str, Any], level: str) -> str:
    """Format status message based on alert level"""
    if level == 'HEALTHY':
        return format_healthy_message(metrics)
    elif level == 'WARNING':
        return format_warning_message(metrics)
    elif level == 'ALERT':
        return format_alert_message(metrics)
    elif level == 'FATAL':
        return format_fatal_message(metrics)
    else:
        return format_healthy_message(metrics)


# =============================================================================
# HISTORY & CHARTS
# =============================================================================

def append_history(metrics: Dict[str, Any]) -> None:
    """Append metrics to history CSV"""
    try:
        file_exists = HISTORY_CSV.exists() and HISTORY_CSV.stat().st_size > 0
        
        with open(HISTORY_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    'timestamp', 'height', 'catching_up', 'missed_blocks',
                    'rewards', 'balance', 'delegated'
                ])
            writer.writerow([
                metrics['timestamp'],
                metrics['height'],
                metrics['catching_up'],
                metrics['missed_blocks'],
                metrics['rewards'],
                metrics['wallet_balance'],
                metrics['delegated_balance']
            ])
    except Exception as e:
        log_error(f"Failed to append history: {e}")


def generate_charts() -> None:
    """Generate PNG charts"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from datetime import datetime, timedelta
        
        if not HISTORY_CSV.exists():
            return
        
        # Read last 24 hours
        timestamps = []
        rewards = []
        missed_deltas = []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        last_missed = 0
        
        with open(HISTORY_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ts = datetime.fromisoformat(row['timestamp'])
                    if ts < cutoff_time:
                        continue
                    
                    timestamps.append(ts)
                    rewards.append(float(row['rewards']) / (10 ** DECIMALS))
                    
                    current_missed = int(row['missed_blocks'])
                    missed_deltas.append(current_missed - last_missed)
                    last_missed = current_missed
                except Exception:
                    continue
        
        if len(timestamps) < 2:
            return
        
        # Rewards chart
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, rewards, 'b-', linewidth=2)
        plt.title('Rewards (Last 24h)', fontsize=14, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Rewards (RAI)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(REWARDS_CHART, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Missed blocks chart (delta)
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, missed_deltas, 'r-', linewidth=2)
        plt.title('Missed Blocks Delta (Last 24h)', fontsize=14, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Missed Blocks (Delta)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(MISSED_BLOCKS_CHART, dpi=100, bbox_inches='tight')
        plt.close()
        
    except ImportError:
        log_error("matplotlib not available, skipping charts")
    except Exception as e:
        log_error(f"Failed to generate charts: {e}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main monitoring function"""
    # Validate config
    if not validate_config():
        sys.exit(1)
    
    # Check for flags
    send_charts = '--send-charts' in sys.argv
    force_send = '--force' in sys.argv
    
    # Load state
    state = load_state()
    
    # Collect metrics
    metrics = collect_metrics()
    
    # Determine alert level
    level, should_alert = determine_alert_level(metrics, state)
    
    # Check if status changed (untuk alert status)
    last_status = state.get('last_status', None)
    status_changed = (last_status is None) or (level != last_status)
    
    # Check heartbeat (untuk full info report)
    should_heartbeat = should_send_heartbeat(state)
    
    # Send alert status HANYA untuk ALERT dan FATAL (kritikal)
    # WARNING tidak perlu alert terpisah, cukup di full info report
    # Full info report adalah alert utama setiap 3 jam
    # Force send juga hanya untuk ALERT dan FATAL, bukan WARNING
    if (force_send and level in ['ALERT', 'FATAL']) or (level in ['ALERT', 'FATAL'] and status_changed):
        message = format_status_message(metrics, level)
        send_telegram_message(message)
        
        # Send charts if requested or alert/fatal
        if send_charts or level in ['ALERT', 'FATAL']:
            generate_charts()
            if REWARDS_CHART.exists():
                send_telegram_photo(REWARDS_CHART, "Rewards History (24h)")
            if MISSED_BLOCKS_CHART.exists():
                send_telegram_photo(MISSED_BLOCKS_CHART, "Missed Blocks Delta (24h)")
    
    # Send full info report every HEARTBEAT_HOURS (terlepas dari status)
    # Ini adalah alert utama yang selalu dikirim setiap 3 jam
    # Berisi semua info termasuk WARNING jika ada
    if should_heartbeat:
        full_info_message = format_full_info_message(metrics)
        send_telegram_message(full_info_message)
        state['last_heartbeat'] = time.time()
    
    # Update state
    state['last_missed_blocks'] = metrics.get('missed_blocks', 0)
    state['last_height'] = metrics.get('height', 0)
    state['last_status'] = level
    state['last_check'] = time.time()
    
    # Save state
    save_state(state)
    
    # Append history
    append_history(metrics)


if __name__ == '__main__':
    main()
