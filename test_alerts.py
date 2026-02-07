#!/usr/bin/env python3
"""
Test script untuk semua alert levels
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import functions from monitor.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor import (
    format_healthy_message,
    format_warning_message,
    format_alert_message,
    format_fatal_message,
    send_telegram_message,
    format_balance
)

load_dotenv()

def test_healthy():
    """Test HEALTHY alert"""
    print("=" * 60)
    print("TEST 1: HEALTHY ALERT")
    print("=" * 60)
    
    metrics = {
        'validator_status': 'BONDED',
        'jailed': False,
        'tombstoned': False,
        'height': 174065,
        'catching_up': False,
        'missed_blocks': 0,
        'wallet_balance': 1208000000000000000,  # 12.08 RAI (18 decimals)
        'delegated_balance': 4982000000000000000,  # 49.82 RAI
        'rewards': 0,
    }
    
    message = format_healthy_message(metrics)
    print(message)
    print()
    
    # Ask to send
    send = input("Kirim ke Telegram? (y/n): ").strip().lower()
    if send == 'y':
        if send_telegram_message(message):
            print("✓ HEALTHY message sent!")
        else:
            print("✗ Failed to send")
    print()


def test_warning_unbonding():
    """Test WARNING - UNBONDING"""
    print("=" * 60)
    print("TEST 2: WARNING - UNBONDING")
    print("=" * 60)
    
    metrics = {
        'validator_status': 'UNBONDING',
        'jailed': False,
        'catching_up': False,
        'height': 174065,
    }
    
    message = format_warning_message(metrics)
    print(message)
    print()
    
    send = input("Kirim ke Telegram? (y/n): ").strip().lower()
    if send == 'y':
        if send_telegram_message(message):
            print("✓ WARNING (UNBONDING) message sent!")
        else:
            print("✗ Failed to send")
    print()


def test_warning_catching_up():
    """Test WARNING - Catching Up"""
    print("=" * 60)
    print("TEST 3: WARNING - CATCHING UP")
    print("=" * 60)
    
    metrics = {
        'validator_status': 'BONDED',
        'jailed': False,
        'catching_up': True,
        'height': 95000,
    }
    
    message = format_warning_message(metrics)
    print(message)
    print()
    
    send = input("Kirim ke Telegram? (y/n): ").strip().lower()
    if send == 'y':
        if send_telegram_message(message):
            print("✓ WARNING (Catching Up) message sent!")
        else:
            print("✗ Failed to send")
    print()


def test_alert_jailed():
    """Test ALERT - Jailed"""
    print("=" * 60)
    print("TEST 4: ALERT - JAILED")
    print("=" * 60)
    
    metrics = {
        'validator_status': 'BONDED',
        'jailed': True,
        'missed_blocks': 102,
    }
    
    message = format_alert_message(metrics)
    print(message)
    print()
    
    send = input("Kirim ke Telegram? (y/n): ").strip().lower()
    if send == 'y':
        if send_telegram_message(message):
            print("✓ ALERT (Jailed) message sent!")
        else:
            print("✗ Failed to send")
    print()


def test_alert_missed_blocks():
    """Test ALERT - Missed Blocks"""
    print("=" * 60)
    print("TEST 5: ALERT - MISSED BLOCKS")
    print("=" * 60)
    
    metrics = {
        'validator_status': 'BONDED',
        'jailed': False,
        'missed_blocks': 50,
    }
    
    message = format_alert_message(metrics)
    print(message)
    print()
    
    send = input("Kirim ke Telegram? (y/n): ").strip().lower()
    if send == 'y':
        if send_telegram_message(message):
            print("✓ ALERT (Missed Blocks) message sent!")
        else:
            print("✗ Failed to send")
    print()


def test_fatal_tombstoned():
    """Test FATAL - Tombstoned"""
    print("=" * 60)
    print("TEST 6: FATAL - TOMBSTONED")
    print("=" * 60)
    
    metrics = {
        'validator_status': 'UNBONDED',
        'tombstoned': True,
    }
    
    message = format_fatal_message(metrics)
    print(message)
    print()
    
    send = input("Kirim ke Telegram? (y/n): ").strip().lower()
    if send == 'y':
        if send_telegram_message(message):
            print("✓ FATAL (Tombstoned) message sent!")
        else:
            print("✗ Failed to send")
    print()


def show_all_preview():
    """Show all alerts in preview mode (no send)"""
    print("=" * 60)
    print("PREVIEW ALL ALERT LEVELS")
    print("=" * 60)
    print()
    
    # HEALTHY
    metrics_healthy = {
        'validator_status': 'BONDED',
        'jailed': False,
        'tombstoned': False,
        'height': 174065,
        'catching_up': False,
        'missed_blocks': 0,
        'wallet_balance': 1208000000000000000,
        'delegated_balance': 4982000000000000000,
        'rewards': 0,
    }
    print("1. HEALTHY:")
    print(format_healthy_message(metrics_healthy))
    print("\n" + "-" * 60 + "\n")
    
    # WARNING - UNBONDING
    metrics_warning_unbonding = {
        'validator_status': 'UNBONDING',
        'jailed': False,
        'catching_up': False,
        'height': 174065,
    }
    print("2. WARNING - UNBONDING:")
    print(format_warning_message(metrics_warning_unbonding))
    print("\n" + "-" * 60 + "\n")
    
    # WARNING - CATCHING UP
    metrics_warning_sync = {
        'validator_status': 'BONDED',
        'jailed': False,
        'catching_up': True,
        'height': 95000,
    }
    print("3. WARNING - CATCHING UP:")
    print(format_warning_message(metrics_warning_sync))
    print("\n" + "-" * 60 + "\n")
    
    # ALERT - JAILED
    metrics_alert_jailed = {
        'validator_status': 'BONDED',
        'jailed': True,
        'missed_blocks': 102,
    }
    print("4. ALERT - JAILED:")
    print(format_alert_message(metrics_alert_jailed))
    print("\n" + "-" * 60 + "\n")
    
    # ALERT - MISSED BLOCKS
    metrics_alert_missed = {
        'validator_status': 'BONDED',
        'jailed': False,
        'missed_blocks': 50,
    }
    print("5. ALERT - MISSED BLOCKS:")
    print(format_alert_message(metrics_alert_missed))
    print("\n" + "-" * 60 + "\n")
    
    # FATAL
    metrics_fatal = {
        'validator_status': 'UNBONDED',
        'tombstoned': True,
    }
    print("6. FATAL - TOMBSTONED:")
    print(format_fatal_message(metrics_fatal))
    print()


def main():
    """Main test menu"""
    print("\n" + "=" * 60)
    print("  RAI SENTINEL - ALERT TEST SUITE")
    print("=" * 60)
    print()
    print("Alert Levels:")
    print("  1. 🟢 HEALTHY - BONDED, not jailed, synced")
    print("  2. 🟡 WARNING - UNBONDING")
    print("  3. 🟡 WARNING - Catching Up")
    print("  4. 🔴 ALERT - Jailed")
    print("  5. 🔴 ALERT - Missed Blocks")
    print("  6. ☠️  FATAL - Tombstoned")
    print("  7. Preview All (no send)")
    print("  0. Exit")
    print()
    
    while True:
        choice = input("Pilih test (0-7): ").strip()
        
        if choice == '0':
            print("Exit")
            break
        elif choice == '1':
            test_healthy()
        elif choice == '2':
            test_warning_unbonding()
        elif choice == '3':
            test_warning_catching_up()
        elif choice == '4':
            test_alert_jailed()
        elif choice == '5':
            test_alert_missed_blocks()
        elif choice == '6':
            test_fatal_tombstoned()
        elif choice == '7':
            show_all_preview()
        else:
            print("Invalid choice!")
        print()


if __name__ == '__main__':
    main()

