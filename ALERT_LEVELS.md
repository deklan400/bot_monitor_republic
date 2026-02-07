# RAI Sentinel - Alert Levels

## 📊 Alert Level Overview

RAI Sentinel memiliki **4 alert levels** dengan kondisi trigger yang berbeda:

---

## 🟢 HEALTHY

**Kondisi:**
- Validator status: **BONDED**
- Jailed: **No**
- Tombstoned: **No**
- Node: **Not catching up** (synced)

**Kapan dikirim:**
- Heartbeat setiap `HEARTBEAT_HOURS` (default: 6 jam)
- Tidak dikirim saat alert/warning

**Format Message:**
```
🟢 RAI VALIDATOR STATUS — HEALTHY

Validator:
 • Status : BONDED
 • Jailed : No
 • Tombstoned : No

Node:
 • Sync   : OK
 • Height : 174,065
 • Missed : 0

Balance:
 • Wallet    : 12.08 RAI
 • Delegated : 49.82 RAI
 • Rewards   : 0.00 RAI

🕒 2026-02-07 10:08 WIB
```

---

## 🟡 WARNING

**Kondisi (salah satu):**
1. Validator status: **UNBONDING**
2. Node: **Catching up** (not synced)

**Kapan dikirim:**
- Segera saat kondisi terdeteksi
- Bypass heartbeat

**Format Message:**
```
🟡 RAI VALIDATOR WARNING

Validator:
 • Status : UNBONDING
 • Jailed : No

Node:
 • Sync   : Catching Up
 • Height : 95,102

🕒 Detected: 2026-02-06 22:20 WIB
```

---

## 🔴 ALERT

**Kondisi (salah satu):**
1. Validator: **Jailed = YES**
2. **Missed blocks increasing** (current > last)

**Kapan dikirim:**
- Segera saat kondisi terdeteksi
- Bypass heartbeat

**Format Message (Jailed):**
```
🔴 RAI VALIDATOR ALERT — JAILED

Validator:
 • Status : BONDED
 • Jailed : YES

Node:
 • Sync   : STOPPED
 • Missed : 102 blocks

🕒 Detected: 2026-02-06 22:31 WIB
```

**Format Message (Missed Blocks):**
```
🔴 RAI VALIDATOR ALERT

Validator:
 • Status : BONDED
 • Jailed : No

Node:
 • Sync   : STOPPED
 • Missed : 50 blocks

🕒 Detected: 2026-02-06 22:31 WIB
```

---

## ☠️ FATAL

**Kondisi:**
- Validator: **Tombstoned = YES**

**Kapan dikirim:**
- Segera saat kondisi terdeteksi
- Bypass heartbeat

**Catatan:**
- ⚠️ **Tombstoned = PERMANENT**
- Validator tidak bisa recover
- Validator permanently slashed

**Format Message:**
```
☠️ RAI VALIDATOR FATAL — TOMBSTONED

Validator:
 • Tombstoned : YES
 • Status     : UNBONDED

🚨 Validator permanently slashed
Recovery impossible

🕒 Detected: 2026-02-06 22:45 WIB
```

---

## Alert Priority

1. **FATAL** (highest) - Tombstoned
2. **ALERT** - Jailed / Missed blocks
3. **WARNING** - UNBONDING / Catching up
4. **HEALTHY** (lowest) - Normal status

Alert dengan priority lebih tinggi akan **override** alert yang lebih rendah.

---

## Testing Alerts

Gunakan `test_alerts.py` untuk test semua alert levels:

```bash
cd /opt/rai-sentinel
source venv/bin/activate
python test_alerts.py
```

Menu:
- `1` - Test HEALTHY
- `2` - Test WARNING (UNBONDING)
- `3` - Test WARNING (Catching Up)
- `4` - Test ALERT (Jailed)
- `5` - Test ALERT (Missed Blocks)
- `6` - Test FATAL (Tombstoned)
- `7` - Preview All (no send)
- `0` - Exit

---

## Alert Logic Flow

```
1. Collect metrics
   ↓
2. Determine alert level
   ├─ Tombstoned? → FATAL
   ├─ Jailed? → ALERT
   ├─ Missed blocks increasing? → ALERT
   ├─ UNBONDING? → WARNING
   ├─ Catching up? → WARNING
   └─ BONDED + OK? → HEALTHY
   ↓
3. Check if should send
   ├─ Alert/Warning/Fatal? → Send immediately
   └─ Healthy? → Check heartbeat interval
   ↓
4. Format & send message
```

---

## Configuration

Edit `.env` untuk customize:

```bash
HEARTBEAT_HOURS=6      # Heartbeat interval (hours)
REWARD_DROP_PCT=5      # Reward drop threshold (%)
STUCK_MINUTES=10       # Height stuck threshold (minutes)
```

