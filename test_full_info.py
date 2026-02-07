#!/usr/bin/env python3
"""Test script untuk full info report"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor import (
    collect_metrics,
    format_full_info_message,
    send_telegram_message
)

load_dotenv()

def main():
    print("=" * 60)
    print("TEST FULL INFO REPORT")
    print("=" * 60)
    print()
    
    # Collect metrics
    print("📊 Collecting metrics...")
    try:
        metrics = collect_metrics()
        print("✓ Metrics collected")
        print()
    except Exception as e:
        print(f"✗ Error collecting metrics: {e}")
        sys.exit(1)
    
    # Format full info message
    print("📝 Formatting full info message...")
    try:
        message = format_full_info_message(metrics)
        print("✓ Message formatted")
        print()
    except Exception as e:
        print(f"✗ Error formatting message: {e}")
        sys.exit(1)
    
    # Preview
    print("=" * 60)
    print("PREVIEW:")
    print("=" * 60)
    print(message)
    print()
    print("=" * 60)
    print()
    
    # Ask to send
    send = input("Kirim ke Telegram? (y/n): ").strip().lower()
    if send == 'y':
        print()
        print("📤 Sending to Telegram...")
        try:
            if send_telegram_message(message):
                print("✓ Full info report sent successfully!")
            else:
                print("✗ Failed to send message")
        except Exception as e:
            print(f"✗ Error sending: {e}")
    else:
        print("Skipped sending")

if __name__ == '__main__':
    main()

