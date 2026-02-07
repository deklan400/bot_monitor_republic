# TUTORIAL DEPLOY LENGKAP - RAI SENTINEL
**Step-by-step guide lengkap dari awal sampai selesai**

---

## 📋 DAFTAR ISI

1. [Persiapan](#1-persiapan)
2. [Setup di Local Machine](#2-setup-di-local-machine)
3. [Persiapan VPS](#3-persiapan-vps)
4. [Deploy ke VPS](#4-deploy-ke-vps)
5. [Konfigurasi](#5-konfigurasi)
6. [Verifikasi](#6-verifikasi)
7. [Testing](#7-testing)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. PERSIAPAN

### 1.1 Persiapan Data yang Diperlukan

Sebelum mulai, siapkan data berikut:

#### A. Telegram Bot Token
1. Buka Telegram, cari **@BotFather**
2. Kirim command: `/newbot`
3. Ikuti instruksi:
   - Masukkan nama bot (contoh: "RAI Validator Monitor")
   - Masukkan username bot (contoh: "rai_validator_bot")
4. BotFather akan memberikan **Token**
   - Format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890`
   - **SIMPAN TOKEN INI!**

#### B. Telegram Chat ID
1. Kirim pesan ke bot yang baru dibuat
2. Buka browser, kunjungi:
   ```
   https://api.telegram.org/bot<TOKEN_ANDA>/getUpdates
   ```
   Ganti `<TOKEN_ANDA>` dengan token dari BotFather
3. Cari `"chat":{"id":` di response JSON
4. Angka setelah `"id":` adalah **Chat ID**
   - Contoh: `123456789` atau `-1001234567890` (untuk group)
   - **SIMPAN CHAT ID INI!**

#### C. Validator Addresses
Siapkan 3 alamat:

1. **Wallet Address**
   - Format: `republic1...`
   - Contoh: `republic1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

2. **Validator Operator Address (valoper)**
   - Format: `republicvaloper1...`
   - Contoh: `republicvaloper1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

3. **Consensus Address (consaddr)**
   - Format: `republicvalcons1...`
   - Contoh: `republicvalcons1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

**Cara mendapatkan:**
```bash
# Di VPS validator, jalankan:
republicd keys show <key-name> --bech val
republicd keys show <key-name> --bech acc
republicd tendermint show-address
```

---

## 2. SETUP DI LOCAL MACHINE

### 2.1 Clone Repository

```bash
# Buka terminal/command prompt
# Masuk ke directory yang diinginkan
cd ~/Documents  # atau directory lain

# Clone repository
git clone https://github.com/deklan400/bot_monitor_republic.git rai-sentinel

# Masuk ke folder
cd rai-sentinel

# Verify files
ls -la
# Harus ada: monitor.py, bot.py, install.sh, dll
```

**Atau jika sudah punya folder project:**
```bash
cd /path/to/bot_monitor_republic
git pull origin main
```

---

### 2.2 Verify Files

Pastikan file-file penting ada:

```bash
# Core files
ls monitor.py bot.py install.sh requirements.txt

# Systemd files
ls systemd/

# Documentation
ls *.md
```

---

## 3. PERSIAPAN VPS

### 3.1 Login ke VPS

```bash
# Login via SSH
ssh root@your-vps-ip
# atau
ssh root@your-vps-domain.com

# Jika pakai key file:
ssh -i /path/to/key.pem root@your-vps-ip
```

**Contoh:**
```bash
ssh root@192.168.1.100
# atau
ssh root@validator.example.com
```

---

### 3.2 Update System

```bash
# Update package list
apt update

# Upgrade system
apt upgrade -y

# Reboot jika diperlukan (setelah upgrade besar)
# reboot
```

---

### 3.3 Install Dependencies

```bash
# Install Python 3 dan pip
apt install -y python3 python3-pip python3-venv

# Install Git
apt install -y git

# Install tools lainnya (optional tapi recommended)
apt install -y curl wget nano

# Verify installations
python3 --version  # Harus 3.10 atau lebih tinggi
git --version
```

**Output yang diharapkan:**
```
Python 3.10.x atau lebih tinggi
git version 2.x.x
```

---

### 3.4 Verify Republicd Running (Optional)

```bash
# Check if republicd is running
ps aux | grep republicd

# Check RPC endpoint
curl http://localhost:26657/status

# Check LCD endpoint
curl http://localhost:1317/cosmos/staking/v1beta1/validators
```

**Jika RPC/LCD tidak di localhost, catat URL-nya untuk nanti.**

---

## 4. DEPLOY KE VPS

### 4.1 Clone Repository ke VPS

```bash
# Masuk ke /opt
cd /opt

# Clone repository
git clone https://github.com/deklan400/bot_monitor_republic.git rai-sentinel

# Masuk ke directory
cd rai-sentinel

# Verify files
ls -la
```

**Output:**
```
total XX
drwxr-xr-x  .git
-rw-r--r--  monitor.py
-rw-r--r--  bot.py
-rw-r--r--  install.sh
-rw-r--r--  requirements.txt
...
```

---

### 4.2 Make Install Script Executable

```bash
# Make install.sh executable
chmod +x install.sh

# Verify
ls -l install.sh
# Harus ada 'x' di permissions: -rwxr-xr-x
```

---

### 4.3 Run Install Script

```bash
# Run install script
./install.sh
```

**Script akan:**
1. Check dependencies
2. Tanya input (lihat bagian 4.4)
3. Setup Python venv
4. Install dependencies
5. Create .env file
6. Setup systemd services
7. Enable & start services

---

### 4.4 Input Data Saat Install

Saat script berjalan, Anda akan diminta input:

#### A. Telegram Bot Token
```
Enter Telegram Bot Token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
```
**Paste token dari BotFather**

#### B. Telegram Chat ID
```
Enter Telegram Chat ID: 123456789
```
**Masukkan Chat ID yang sudah didapat**

#### C. Wallet Address
```
Enter Wallet Address: republic1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```
**Masukkan wallet address**

#### D. Validator Operator Address
```
Enter Validator Operator Address (valoper): republicvaloper1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```
**Masukkan valoper address**

#### E. Consensus Address (Optional)
```
Enter Consensus Address (consaddr) [optional]: republicvalcons1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```
**Masukkan consaddr (bisa dikosongkan, tapi recommended)**

---

### 4.5 Tunggu Install Selesai

Script akan:
- ✅ Create Python virtual environment
- ✅ Install dependencies (requests, python-dotenv, matplotlib)
- ✅ Create .env file
- ✅ Create history directory
- ✅ Initialize state.json
- ✅ Install systemd services
- ✅ Enable & start services

**Waktu install: ~2-5 menit**

---

## 5. KONFIGURASI

### 5.1 Verify .env File

```bash
# Check .env file
cat /opt/rai-sentinel/.env

# Verify semua variabel sudah terisi
grep -E "TG_TOKEN|TG_CHAT_ID|WALLET_ADDRESS|VALOPER_ADDRESS" /opt/rai-sentinel/.env
```

**Pastikan tidak ada yang kosong!**

---

### 5.2 Edit .env (Jika Perlu)

Jika RPC/LCD tidak di localhost:

```bash
# Edit .env
nano /opt/rai-sentinel/.env

# Edit baris:
# RPC_URL=http://localhost:26657
# LCD_URL=http://localhost:1317
# Ganti dengan URL yang benar

# Save: Ctrl+O, Enter, Ctrl+X
```

**Contoh jika RPC di server lain:**
```bash
RPC_URL=http://rpc.republicchain.io:26657
LCD_URL=http://lcd.republicchain.io:1317
```

---

### 5.3 Verify Systemd Services

```bash
# Check timer status
systemctl status rai-monitor.timer

# Check bot service status
systemctl status rai-bot.service

# Check if enabled
systemctl is-enabled rai-monitor.timer
systemctl is-enabled rai-bot.service
# Harus output: "enabled"
```

---

## 6. VERIFIKASI

### 6.1 Check Services Running

```bash
# Check timer
systemctl is-active rai-monitor.timer
# Harus output: "active"

# Check bot
systemctl is-active rai-bot.service
# Harus output: "active"
```

---

### 6.2 Check Logs

```bash
# Monitor logs (real-time)
journalctl -u rai-monitor.service -f

# Bot logs (real-time)
journalctl -u rai-bot.service -f

# Last 50 lines
journalctl -u rai-monitor.service -n 50
journalctl -u rai-bot.service -n 50
```

**Tekan Ctrl+C untuk keluar dari follow mode**

---

### 6.3 Check Files Created

```bash
# Check .env
ls -la /opt/rai-sentinel/.env

# Check history directory
ls -la /opt/rai-sentinel/history/

# Check state.json
cat /opt/rai-sentinel/history/state.json

# Check history.csv
head -5 /opt/rai-sentinel/history/history.csv
```

---

### 6.4 Check Timer Schedule

```bash
# List all timers
systemctl list-timers

# Filter rai-monitor
systemctl list-timers | grep rai-monitor

# Output akan menunjukkan next run time
```

---

## 7. TESTING

### 7.1 Test Monitor Manual

```bash
# Masuk ke directory
cd /opt/rai-sentinel

# Activate virtual environment
source venv/bin/activate

# Run monitor dengan --force (akan kirim status langsung)
python monitor.py --force
```

**Expected:**
- ✅ Tidak ada error
- ✅ Mengirim message ke Telegram
- ✅ Message berisi status validator

**Check Telegram, harus ada message status!**

---

### 7.2 Test Bot Commands

#### A. Test /help
1. Buka Telegram
2. Cari bot Anda
3. Kirim: `/help`
4. **Expected:** Bot reply dengan help message

#### B. Test /status
1. Kirim: `/status`
2. **Expected:** 
   - Bot reply: "🔄 Running validator check..."
   - Kemudian kirim status message
   - Lalu reply: "✅ Status check completed"

**Note:** Ada cooldown 10 detik antar /status command

---

### 7.3 Test Timer (Tunggu 1 Jam)

Timer akan jalan otomatis setiap 1 jam. Untuk test cepat:

```bash
# Trigger timer manual (untuk testing)
systemctl start rai-monitor.service

# Check logs
journalctl -u rai-monitor.service -n 20
```

---

### 7.4 Verify Alerts Work

Untuk test alert (jika ada masalah):
- Jika validator jailed → harus dapat ALERT
- Jika validator tombstoned → harus dapat FATAL
- Jika node catching up → harus dapat WARNING

---

## 8. TROUBLESHOOTING

### 8.1 Problem: Timer Tidak Jalan

```bash
# Check status
systemctl status rai-monitor.timer

# Check if enabled
systemctl is-enabled rai-monitor.timer

# Enable jika belum
systemctl enable rai-monitor.timer

# Start timer
systemctl start rai-monitor.timer

# Check timer list
systemctl list-timers | grep rai-monitor
```

---

### 8.2 Problem: Bot Tidak Jalan

```bash
# Check status
systemctl status rai-bot.service

# Check logs
journalctl -u rai-bot.service -n 50

# Restart bot
systemctl restart rai-bot.service

# Check lagi
systemctl status rai-bot.service
```

**Common issues:**
- Telegram token salah → check .env
- Network issue → check internet connection
- Python error → check logs

---

### 8.3 Problem: Monitor Tidak Kirim Telegram

```bash
# Check .env
cat /opt/rai-sentinel/.env | grep TG_TOKEN
cat /opt/rai-sentinel/.env | grep TG_CHAT_ID

# Test Telegram API
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
# Ganti <YOUR_TOKEN> dengan token Anda

# Run monitor manual dengan debug
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force
```

**Check output untuk error messages**

---

### 8.4 Problem: RPC Connection Failed

```bash
# Check if republicd running
ps aux | grep republicd

# Test RPC endpoint
curl http://localhost:26657/status

# Test LCD endpoint
curl http://localhost:1317/cosmos/staking/v1beta1/validators

# Edit .env jika URL berbeda
nano /opt/rai-sentinel/.env
# Edit RPC_URL dan LCD_URL
```

---

### 8.5 Problem: Permission Denied

```bash
# Check permissions
ls -la /opt/rai-sentinel/

# Fix permissions
chmod +x /opt/rai-sentinel/install.sh
chmod +x /opt/rai-sentinel/monitor.py
chmod +x /opt/rai-sentinel/bot.py

# Check venv permissions
ls -la /opt/rai-sentinel/venv/bin/python
```

---

### 8.6 Problem: Python Module Not Found

```bash
# Reinstall dependencies
cd /opt/rai-sentinel
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Verify
pip list | grep requests
pip list | grep python-dotenv
pip list | grep matplotlib
```

---

### 8.7 Problem: Services Keep Restarting

```bash
# Check logs untuk error
journalctl -u rai-bot.service -n 100 | grep -i error

# Check systemd status
systemctl status rai-bot.service

# Disable restart untuk debugging
# Edit: /etc/systemd/system/rai-bot.service
# Comment: Restart=always
# Reload: systemctl daemon-reload
```

---

## 9. MAINTENANCE

### 9.1 Update Code

```bash
# Di VPS
cd /opt/rai-sentinel

# Pull latest code
git pull origin main

# Restart services
systemctl restart rai-monitor.timer
systemctl restart rai-bot.service

# Check logs
journalctl -u rai-monitor.service -n 20
journalctl -u rai-bot.service -n 20
```

---

### 9.2 Check Logs Regularly

```bash
# Check errors
journalctl -u rai-monitor.service --since "1 day ago" | grep -i error
journalctl -u rai-bot.service --since "1 day ago" | grep -i error

# Check last 24 hours activity
journalctl -u rai-monitor.service --since "24 hours ago"
```

---

### 9.3 Backup .env File

```bash
# Backup .env (penting!)
cp /opt/rai-sentinel/.env ~/rai-sentinel-env-backup-$(date +%Y%m%d).txt

# Atau simpan di tempat aman
# Jangan commit .env ke git!
```

---

### 9.4 Monitor Disk Space

```bash
# Check disk usage
df -h

# Check history.csv size
du -sh /opt/rai-sentinel/history/

# History.csv tumbuh ~1KB per hour (~9MB per year)
# Bisa di-rotate jika perlu
```

---

## 10. CHECKLIST FINAL

Setelah deploy, pastikan:

- [ ] Timer status: `active` dan `enabled`
- [ ] Bot service: `active` dan `enabled`
- [ ] .env file: semua variabel terisi
- [ ] Test monitor: `python monitor.py --force` → kirim Telegram
- [ ] Test bot: `/status` → dapat response
- [ ] Test bot: `/help` → dapat response
- [ ] Logs: tidak ada error
- [ ] Timer: next run time terlihat di `systemctl list-timers`

---

## 11. QUICK REFERENCE

### Service Management

```bash
# Start/Stop/Restart Timer
systemctl start rai-monitor.timer
systemctl stop rai-monitor.timer
systemctl restart rai-monitor.timer

# Start/Stop/Restart Bot
systemctl start rai-bot.service
systemctl stop rai-bot.service
systemctl restart rai-bot.service

# Enable/Disable
systemctl enable rai-monitor.timer
systemctl disable rai-monitor.timer
```

### Logs

```bash
# Follow logs
journalctl -u rai-monitor.service -f
journalctl -u rai-bot.service -f

# Last N lines
journalctl -u rai-monitor.service -n 50

# Since time
journalctl -u rai-monitor.service --since "1 hour ago"
journalctl -u rai-monitor.service --since today
```

### Manual Testing

```bash
# Test monitor
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force

# Test bot (Ctrl+C to stop)
python bot.py
```

---

## ✅ SELESAI!

Setelah semua langkah, Anda punya:
- ✅ Monitor running otomatis setiap 1 jam
- ✅ Bot siap menerima commands
- ✅ Alerts otomatis jika ada masalah
- ✅ Heartbeat setiap 3 jam (jika sehat)

**Monitor sudah aktif dan siap digunakan!** 🚀

---

## 📞 SUPPORT

Jika ada masalah:
1. Check logs: `journalctl -u rai-monitor.service -f`
2. Check .env: `cat /opt/rai-sentinel/.env`
3. Test manual: `python monitor.py --force`
4. Check systemd: `systemctl status rai-monitor.timer`

**Happy monitoring!** 📊

