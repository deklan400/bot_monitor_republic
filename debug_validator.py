#!/usr/bin/env python3
"""
Debug script untuk test query validator
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()

VALOPER = os.getenv('VALOPER')
CHAIN_ID = os.getenv('CHAIN_ID', '')
REPUBLICD_BINARY = os.getenv('REPUBLICD_BINARY', 'republicd')

print("=" * 60)
print("DEBUG VALIDATOR QUERY")
print("=" * 60)
print(f"VALOPER: {VALOPER}")
print(f"CHAIN_ID: {CHAIN_ID}")
print(f"BINARY: {REPUBLICD_BINARY}")
print()

if not VALOPER:
    print("ERROR: VALOPER not set in .env")
    sys.exit(1)

# Query validator
print("Querying validator...")
cmd = [REPUBLICD_BINARY, 'query', 'staking', 'validator', VALOPER, '--output', 'json']
if CHAIN_ID:
    cmd.extend(['--chain-id', CHAIN_ID])

print(f"Command: {' '.join(cmd)}")
print()

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    print(f"Return code: {result.returncode}")
    print()
    
    if result.returncode != 0:
        print("ERROR:")
        print(result.stderr)
        sys.exit(1)
    
    # Parse JSON
    try:
        data = json.loads(result.stdout)
        print("=" * 60)
        print("VALIDATOR DATA:")
        print("=" * 60)
        print(json.dumps(data, indent=2))
        print()
        
        # Check status
        status = data.get('status')
        print("=" * 60)
        print("STATUS EXTRACTION:")
        print("=" * 60)
        print(f"Raw status: {status}")
        print(f"Status type: {type(status)}")
        print()
        
        # Check all keys
        print("All keys in response:")
        for key in data.keys():
            print(f"  - {key}: {type(data[key])}")
        
    except json.JSONDecodeError as e:
        print("ERROR: Failed to parse JSON")
        print(f"Error: {e}")
        print()
        print("Raw output:")
        print(result.stdout[:1000])
        
except subprocess.TimeoutExpired:
    print("ERROR: Query timeout")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

