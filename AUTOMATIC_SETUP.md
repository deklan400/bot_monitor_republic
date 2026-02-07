# RAI Sentinel - Automatic Setup

## ✅ Otomatis Jalan

RAI Sentinel sudah dikonfigurasi untuk **jalan otomatis** via systemd timer.

### Systemd Timer

- **Service**: `rai-monitor.service`
- **Timer**: `rai-monitor.timer`
- **Interval**: Setiap **1 jam** (OnUnitActiveSec=1h)
- **On Boot**: Mulai 5 menit setelah boot (OnBootSec=5min)
- **Persistent**: True (catch up missed runs)

### Heartbeat (Full Info Report)

- **Interval**: Setiap **3 jam** (HEARTBEAT_HOURS=3)
- **Format**: Full Status Report dengan **SEMUA informasi lengkap**
- **Terlepas dari status**: Dikirim setiap 3 jam, baik status HEALTHY, WARNING, ALERT, atau FATAL
- **Isi Lengkap**: 
  - 📛 Moniker
  - 🔓 Status (BONDED/UNBONDING/UNBONDED)
  - 🔒/🔴 Jailed (Yes/No)
  - ⚰️/✅ Tombstoned (Yes/No)
  - ✅/⏳ Sync Status (OK/Catching Up)
  - 📊 Block Height
  - ⚠️ Missed Blocks
  - 💰 Wallet Balance
  - 🔐 Delegated Balance
  - 🎁 Rewards

### Cek Status

```bash
# Cek timer status
systemctl status rai-monitor.timer

# Cek service logs
journalctl -u rai-monitor.service -f

# Cek timer next run
systemctl list-timers rai-monitor.timer
```

### Manual Trigger

```bash
# Run manual (bypass heartbeat)
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force

# Run dengan charts
python monitor.py --force --send-charts
```

## Konfigurasi

Edit `.env` untuk customize:

```bash
HEARTBEAT_HOURS=3    # Heartbeat interval (jam)
```

## Flow Otomatis

```
1. Systemd timer trigger setiap 1 jam
   ↓
2. Run monitor.py
   ↓
3. Collect metrics
   ↓
4. Determine alert level
   ↓
5. Check heartbeat interval (3 jam)
   ↓
6. Send message:
   - Alert/Warning/Fatal → Segera (status alert)
   - Heartbeat time (setiap 3 jam) → Kirim FULL INFO REPORT (terlepas dari status)
```

## Informasi yang Dikirim

### Setiap 3 Jam (Full Info Report):
**Format**: `📊 RAI VALIDATOR — FULL STATUS REPORT`

Berisi **SEMUA informasi lengkap**, terlepas dari status:
- 📛 Moniker
- 🔓 Status (BONDED/UNBONDING/UNBONDED)
- 🔒/🔴 Jailed (Yes/No)
- ⚰️/✅ Tombstoned (Yes/No)
- ✅/⏳ Sync Status (OK/Catching Up)
- 📊 Block Height
- ⚠️ Missed Blocks
- 💰 Wallet Balance
- 🔐 Delegated Balance
- 🎁 Rewards

**Catatan**: Full info report dikirim setiap 3 jam, **terlepas dari status** (HEALTHY, WARNING, ALERT, atau FATAL).

### Segera (Status Alert):
- Alert level sesuai kondisi (HEALTHY/WARNING/ALERT/FATAL)
- Informasi relevan untuk alert tersebut
- **Tidak mengganggu** full info report setiap 3 jam

## Troubleshooting

### Timer Tidak Jalan

```bash
# Enable timer
sudo systemctl enable rai-monitor.timer
sudo systemctl start rai-monitor.timer

# Check status
systemctl status rai-monitor.timer
```

### Tidak Ada Message

```bash
# Check logs
journalctl -u rai-monitor.service -n 50

# Test manual
python monitor.py --force

# Check .env
cat .env | grep TG_TOKEN
cat .env | grep TG_CHAT_ID
```

### Ubah Interval

```bash
# Edit .env
nano .env
# Ubah HEARTBEAT_HOURS=3

# Restart timer (optional, akan reload otomatis)
sudo systemctl restart rai-monitor.timer
```

