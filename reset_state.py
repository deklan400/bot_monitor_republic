#!/usr/bin/env python3
"""Reset state.json untuk test"""

import json
from pathlib import Path

STATE_FILE = Path('history/state.json')

if STATE_FILE.exists():
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    print("Current state:")
    print(json.dumps(state, indent=2))
    print()
    
    # Reset last_status
    if 'last_status' in state:
        old_status = state['last_status']
        state['last_status'] = None
        print(f"✓ Reset last_status: {old_status} → None")
    
    # Reset last_heartbeat untuk test cepat
    if 'last_heartbeat' in state:
        old_heartbeat = state['last_heartbeat']
        state['last_heartbeat'] = 0
        print(f"✓ Reset last_heartbeat: {old_heartbeat} → 0")
    
    # Save
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    print()
    print("✓ State reset complete")
else:
    print("State file not found")

