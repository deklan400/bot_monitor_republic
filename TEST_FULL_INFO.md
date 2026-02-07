# Test Full Info Report

## Cara Test Full Info Report

### 1. Test Manual dengan Force Flag

```bash
cd /opt/rai-sentinel
source venv/bin/activate

# Test full info report (bypass heartbeat interval)
python monitor.py --force
```

Ini akan:
- Collect semua metrics
- Kirim full info report langsung (bypass 3 jam interval)
- Juga kirim alert status jika ada

### 2. Test Hanya Full Info (Simulasi Heartbeat)

Edit state.json untuk simulasi heartbeat:

```bash
cd /opt/rai-sentinel

# Backup state dulu
cp history/state.json history/state.json.backup

# Edit state.json - set last_heartbeat ke waktu lama lalu
python3 << EOF
import json
import time

with open('history/state.json', 'r') as f:
    state = json.load(f)

# Set last_heartbeat ke 4 jam lalu (lebih dari 3 jam)
state['last_heartbeat'] = time.time() - (4 * 3600)

with open('history/state.json', 'w') as f:
    json.dump(state, f, indent=2)

print("✓ State updated - last_heartbeat set to 4 hours ago")
EOF

# Run monitor (akan trigger heartbeat)
python monitor.py
```

### 3. Test dengan Script Khusus

Buat script test:

```bash
cat > test_full_info.py << 'EOF'
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

print("=" * 60)
print("TEST FULL INFO REPORT")
print("=" * 60)
print()

# Collect metrics
print("Collecting metrics...")
metrics = collect_metrics()
print("✓ Metrics collected")
print()

# Format full info message
print("Formatting full info message...")
message = format_full_info_message(metrics)
print("✓ Message formatted")
print()

# Preview
print("=" * 60)
print("PREVIEW:")
print("=" * 60)
print(message)
print()

# Ask to send
send = input("Kirim ke Telegram? (y/n): ").strip().lower()
if send == 'y':
    print("\nSending to Telegram...")
    if send_telegram_message(message):
        print("✓ Full info report sent!")
    else:
        print("✗ Failed to send")
else:
    print("Skipped sending")
EOF

chmod +x test_full_info.py
python test_full_info.py
```

### 4. Test Real-Time (Tunggu 3 Jam)

```bash
# Cek timer status
systemctl status rai-monitor.timer

# Monitor logs real-time
journalctl -u rai-monitor.service -f

# Tunggu 3 jam, full info report akan terkirim otomatis
```

### 5. Test dengan Mengubah Interval (Quick Test)

Edit `.env` untuk test cepat:

```bash
nano .env
# Ubah: HEARTBEAT_HOURS=0.05  # 3 menit (untuk test cepat)

# Restart timer
sudo systemctl restart rai-monitor.timer

# Monitor logs
journalctl -u rai-monitor.service -f

# Tunggu 3 menit, full info report akan terkirim
# Jangan lupa kembalikan ke 3 jam setelah test!
```

### 6. Test dengan Python Script Langsung

```bash
cd /opt/rai-sentinel
source venv/bin/activate

python3 << 'PYEOF'
from monitor import collect_metrics, format_full_info_message, send_telegram_message

# Collect
metrics = collect_metrics()

# Format
message = format_full_info_message(metrics)

# Preview
print(message)
print("\n" + "="*60)

# Send
send = input("Kirim? (y/n): ")
if send.lower() == 'y':
    send_telegram_message(message)
    print("✓ Sent!")
PYEOF
```

## Verifikasi

### Cek State

```bash
# Cek last_heartbeat
cat history/state.json | grep last_heartbeat

# Atau format lebih readable
python3 -c "import json; from datetime import datetime; state = json.load(open('history/state.json')); print('Last heartbeat:', datetime.fromtimestamp(state.get('last_heartbeat', 0)))"
```

### Cek Logs

```bash
# Cek logs terakhir
journalctl -u rai-monitor.service -n 20

# Filter untuk "FULL STATUS REPORT"
journalctl -u rai-monitor.service | grep -i "full status"
```

## Troubleshooting

### Full Info Tidak Terkirim

1. **Cek state.json**:
   ```bash
   cat history/state.json
   ```

2. **Cek interval**:
   ```bash
   cat .env | grep HEARTBEAT_HOURS
   ```

3. **Test manual**:
   ```bash
   python monitor.py --force
   ```

4. **Cek Telegram token**:
   ```bash
   curl "https://api.telegram.org/bot$(grep TG_TOKEN .env | cut -d= -f2)/getMe"
   ```

### Reset Heartbeat

```bash
# Reset heartbeat (force next run)
python3 << EOF
import json
import time

with open('history/state.json', 'r') as f:
    state = json.load(f)

state['last_heartbeat'] = 0  # Reset

with open('history/state.json', 'w') as f:
    json.dump(state, f, indent=2)

print("✓ Heartbeat reset")
EOF

# Run monitor
python monitor.py
```

## Quick Test Command

```bash
# One-liner test
cd /opt/rai-sentinel && source venv/bin/activate && python monitor.py --force
```

