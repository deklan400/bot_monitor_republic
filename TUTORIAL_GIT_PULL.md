# Tutorial Deploy RAI Sentinel via Git Pull

## Langkah 1: Clone Repository (Pertama Kali)

```bash
# Login ke VPS sebagai root
ssh root@your-vps-ip

# Clone repository
cd /opt
git clone https://github.com/deklan400/bot_monitor_republic.git rai-sentinel
cd rai-sentinel
```

## Langkah 2: Install Pertama Kali

```bash
# Buat executable
chmod +x install.sh

# Jalankan install script
./install.sh
```

Script akan menanyakan:
- **Telegram Bot Token** → Masukkan token dari @BotFather
- **Telegram Chat ID** → Masukkan chat ID
- **Validator Operator Address (VALOPER)** → Masukkan `republicvaloper1...`
- **Wallet Address** → Masukkan `republic1...`
- **Chain ID** → Masukkan chain ID (optional)

## Langkah 3: Update dari Git (Jika Ada Perubahan)

```bash
# Masuk ke directory
cd /opt/rai-sentinel

# Pull perubahan terbaru
git pull origin main

# Jika ada perubahan di monitor.py atau requirements.txt
# Aktifkan venv dan update dependencies
source venv/bin/activate
pip install -r requirements.txt --quiet

# Reload systemd jika ada perubahan service files
sudo systemctl daemon-reload
sudo systemctl restart rai-monitor.timer
```

## Langkah 4: Jika Ada File Baru atau Config Kurang

### A. Jika .env Kurang Variable

```bash
# Edit .env manual
nano .env

# Atau jalankan install.sh lagi (idempotent, aman di-run ulang)
./install.sh
```

### B. Jika Ada Dependencies Baru

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### C. Jika Systemd Service Berubah

```bash
# Copy service files ke systemd
sudo cp systemd/rai-monitor.service /etc/systemd/system/
sudo cp systemd/rai-monitor.timer /etc/systemd/system/

# Reload dan restart
sudo systemctl daemon-reload
sudo systemctl restart rai-monitor.timer
sudo systemctl status rai-monitor.timer
```

## Langkah 5: Verifikasi

```bash
# Cek timer status
systemctl status rai-monitor.timer

# Cek service logs
journalctl -u rai-monitor.service -f

# Test manual
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force
```

## Workflow Update Harian

```bash
# Quick update script
cd /opt/rai-sentinel
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --quiet
sudo systemctl daemon-reload
sudo systemctl restart rai-monitor.timer
```

## Troubleshooting

### Jika Git Pull Error

```bash
# Backup dulu
cp -r /opt/rai-sentinel /opt/rai-sentinel.backup

# Reset jika ada conflict
cd /opt/rai-sentinel
git fetch origin
git reset --hard origin/main
```

### Jika Install Script Error

```bash
# Cek apakah .env sudah ada
cat .env

# Jika belum, buat manual atau run install.sh lagi
./install.sh
```

### Jika Monitor Tidak Jalan

```bash
# Cek logs
journalctl -u rai-monitor.service -n 50

# Test manual
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force

# Cek .env
cat .env | grep -E "TG_TOKEN|TG_CHAT_ID|VALOPER|WALLET"
```

## Checklist Update

- [ ] `git pull origin main`
- [ ] `pip install -r requirements.txt` (jika ada perubahan)
- [ ] `systemctl daemon-reload` (jika service berubah)
- [ ] `systemctl restart rai-monitor.timer`
- [ ] Test manual: `python monitor.py --force`
- [ ] Cek logs: `journalctl -u rai-monitor.service -f`

## Catatan Penting

1. **install.sh idempotent** → Aman di-run ulang, tidak akan overwrite .env yang sudah ada
2. **Backup .env** → Selalu backup sebelum update besar
3. **Test dulu** → Selalu test dengan `--force` sebelum deploy
4. **Cek logs** → Monitor logs setelah update

