# DEPLOY KE VPS - RAI SENTINEL
**Guide lengkap untuk install di VPS sebagai root**

---

## 📋 PRASYARAT

### 1. Akses VPS
- ✅ SSH access sebagai root
- ✅ VPS sudah install Python 3.10+
- ✅ VPS sudah install systemd
- ✅ VPS sudah install git (optional)

### 2. Persiapan
- ✅ Telegram Bot Token dari @BotFather
- ✅ Telegram Chat ID (kirim pesan ke bot, lalu cek di https://api.telegram.org/bot<TOKEN>/getUpdates)
- ✅ Wallet Address (republic1...)
- ✅ Validator Operator Address (republicvaloper1...)
- ✅ Consensus Address (republicvalcons1...)

---

## 🚀 LANGKAH-LANGKAH DEPLOY

### STEP 1: Login ke VPS

```bash
ssh root@your-vps-ip
```

---

### STEP 2: Install Dependencies (jika belum ada)

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3 dan pip
apt install -y python3 python3-pip python3-venv

# Install git (untuk clone repo, atau bisa upload manual)
apt install -y git

# Verify Python version (harus 3.10+)
python3 --version
```

---

### STEP 3: Clone atau Upload Project

**Opsi A: Clone dari Git (jika ada repo)**
```bash
cd /opt
git clone <your-repo-url> rai-sentinel
cd rai-sentinel
```

**Opsi B: Upload Manual**
```bash
# Buat directory
mkdir -p /opt/rai-sentinel
cd /opt/rai-sentinel

# Upload semua file ke /opt/rai-sentinel menggunakan:
# - SCP: scp -r * root@vps-ip:/opt/rai-sentinel/
# - SFTP: upload semua file
# - atau gunakan wget/curl jika file ada di server lain
```

---

### STEP 4: Set Permissions

```bash
cd /opt/rai-sentinel

# Make install.sh executable
chmod +x install.sh

# Verify files exist
ls -la
# Should show: install.sh, monitor.py, bot.py, requirements.txt, etc.
```

---

### STEP 5: Run Install Script

```bash
# Run install script
./install.sh
```

**Script akan:**
1. ✅ Check dependencies
2. ✅ Ask for input:
   - Telegram Bot Token
   - Telegram Chat ID
   - Wallet Address
   - Validator Operator Address
   - Consensus Address (optional)
3. ✅ Create Python venv
4. ✅ Install dependencies
5. ✅ Create .env file
6. ✅ Setup history directory
7. ✅ Initialize state.json
8. ✅ Install systemd services
9. ✅ Enable & start services

**Contoh input:**
```
Enter Telegram Bot Token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
Enter Telegram Chat ID: 123456789
Enter Wallet Address: republic1abc123...
Enter Validator Operator Address (valoper): republicvaloper1abc123...
Enter Consensus Address (consaddr) [optional]: republicvalcons1abc123...
```

---

### STEP 6: Verify Installation

```bash
# Check timer status
systemctl status rai-monitor.timer

# Check bot service status
systemctl status rai-bot.service

# Check if timer is enabled
systemctl is-enabled rai-monitor.timer
# Should output: enabled

# Check if bot is enabled
systemctl is-enabled rai-bot.service
# Should output: enabled
```

---

### STEP 7: Test Monitor (Optional)

```bash
# Test monitor manually
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force

# Should send message to Telegram
```

---

### STEP 8: Check Logs

```bash
# Monitor logs
journalctl -u rai-monitor.service -f

# Bot logs
journalctl -u rai-bot.service -f

# Check for errors
journalctl -u rai-monitor.service --since "10 minutes ago" | grep ERROR
journalctl -u rai-bot.service --since "10 minutes ago" | grep ERROR
```

---

## 🔧 TROUBLESHOOTING

### Problem: Timer tidak jalan

```bash
# Check timer status
systemctl status rai-monitor.timer

# Check if timer is active
systemctl is-active rai-monitor.timer

# Restart timer
systemctl restart rai-monitor.timer

# Check timer list
systemctl list-timers | grep rai-monitor
```

### Problem: Bot tidak jalan

```bash
# Check bot status
systemctl status rai-bot.service

# Check logs
journalctl -u rai-bot.service -n 50

# Restart bot
systemctl restart rai-bot.service
```

### Problem: Monitor tidak kirim Telegram

```bash
# Check .env file
cat /opt/rai-sentinel/.env | grep TG_TOKEN
cat /opt/rai-sentinel/.env | grep TG_CHAT_ID

# Test Telegram API manually
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Run monitor manually dengan debug
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force
```

### Problem: RPC connection failed

```bash
# Check if republicd is running
ps aux | grep republicd

# Check RPC endpoint
curl http://localhost:26657/status

# Check LCD endpoint
curl http://localhost:1317/cosmos/staking/v1beta1/validators

# Update .env if RPC/LCD URL berbeda
nano /opt/rai-sentinel/.env
# Edit RPC_URL dan LCD_URL jika perlu
```

---

## 📝 USEFUL COMMANDS

### Service Management

```bash
# Stop monitor timer
systemctl stop rai-monitor.timer

# Start monitor timer
systemctl start rai-monitor.timer

# Restart bot
systemctl restart rai-bot.service

# Stop bot
systemctl stop rai-bot.service

# Disable services (jika perlu uninstall)
systemctl disable rai-monitor.timer
systemctl disable rai-bot.service
```

### Logs

```bash
# Monitor logs (real-time)
journalctl -u rai-monitor.service -f

# Bot logs (real-time)
journalctl -u rai-bot.service -f

# Last 100 lines
journalctl -u rai-monitor.service -n 100

# Logs since today
journalctl -u rai-monitor.service --since today

# Logs with errors only
journalctl -u rai-monitor.service | grep -i error
```

### Manual Testing

```bash
# Test monitor
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force

# Test bot (akan run terus, Ctrl+C untuk stop)
python bot.py

# Test Telegram bot command
# Kirim /status atau /help ke bot di Telegram
```

### Update Code

```bash
# Jika update code
cd /opt/rai-sentinel

# Pull latest (jika pakai git)
git pull

# Atau upload file baru

# Restart services
systemctl restart rai-monitor.timer
systemctl restart rai-bot.service
```

---

## ✅ VERIFICATION CHECKLIST

Setelah install, pastikan:

- [ ] Timer status: `systemctl status rai-monitor.timer` → active
- [ ] Bot status: `systemctl status rai-bot.service` → active
- [ ] Timer enabled: `systemctl is-enabled rai-monitor.timer` → enabled
- [ ] Bot enabled: `systemctl is-enabled rai-bot.service` → enabled
- [ ] .env file exists: `ls -la /opt/rai-sentinel/.env`
- [ ] State file exists: `ls -la /opt/rai-sentinel/history/state.json`
- [ ] History CSV exists: `ls -la /opt/rai-sentinel/history/history.csv`
- [ ] Test monitor: `python monitor.py --force` → kirim Telegram
- [ ] Test bot: Kirim `/status` ke bot → dapat response

---

## 🎯 NEXT STEPS

1. ✅ Monitor akan jalan otomatis setiap 1 jam
2. ✅ Bot siap menerima command `/status` dan `/help`
3. ✅ Alerts akan dikirim otomatis jika ada masalah
4. ✅ Heartbeat dikirim setiap 3 jam (jika sehat)

**Setup selesai! Monitor sudah aktif.** 🚀

---

## 📞 SUPPORT

Jika ada masalah:
1. Check logs: `journalctl -u rai-monitor.service -f`
2. Check .env file: `cat /opt/rai-sentinel/.env`
3. Test manual: `python monitor.py --force`
4. Check systemd: `systemctl status rai-monitor.timer`


