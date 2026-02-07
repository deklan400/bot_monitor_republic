# TUTORIAL LENGKAP - DEPLOY DENGAN GIT
**Step-by-step guide menggunakan Git untuk deploy RAI Sentinel ke VPS**

---

## 📋 PRASYARAT

### Di Local Machine (Windows/Mac/Linux)
- ✅ Git sudah terinstall
- ✅ Akses ke GitHub/GitLab/Bitbucket (atau git server lain)
- ✅ Semua file project sudah siap

### Di VPS
- ✅ SSH access sebagai root
- ✅ Git sudah terinstall
- ✅ Python 3.10+ sudah terinstall

---

## 🚀 LANGKAH 1: SETUP GIT REPOSITORY

### Opsi A: Buat Repository Baru di GitHub

1. **Login ke GitHub**
   - Buka https://github.com
   - Login dengan akun Anda

2. **Create New Repository**
   - Klik tombol "+" di kanan atas
   - Pilih "New repository"
   - Nama: `rai-sentinel` (atau nama lain)
   - Visibility: Private (recommended) atau Public
   - Jangan centang "Initialize with README"
   - Klik "Create repository"

3. **Copy Repository URL**
   - Setelah repo dibuat, copy URL
   - Format: `https://github.com/username/rai-sentinel.git`
   - atau: `git@github.com:username/rai-sentinel.git` (SSH)

---

### Opsi B: Gunakan Repository yang Sudah Ada

Jika sudah punya repo, skip langkah ini dan langsung ke Langkah 2.

---

## 🚀 LANGKAH 2: INITIALIZE GIT DI LOCAL

### Di Local Machine (folder project)

```bash
# Masuk ke folder project
cd /path/to/bot_monitor_republic

# Initialize git (jika belum)
git init

# Add .gitignore (penting!)
cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# History & State
history/*.json
history/*.png
history/*.csv
!history/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF

# Add semua file
git add .

# Commit pertama
git commit -m "Initial commit: RAI Sentinel validator monitor"

# Add remote repository
git remote add origin https://github.com/username/rai-sentinel.git
# atau pakai SSH: git remote add origin git@github.com:username/rai-sentinel.git

# Push ke GitHub
git branch -M main
git push -u origin main
```

**Catatan**: 
- Ganti `username/rai-sentinel` dengan repo URL Anda
- Jika pakai SSH, pastikan SSH key sudah setup di GitHub

---

## 🚀 LANGKAH 3: DEPLOY KE VPS

### Step 1: Login ke VPS

```bash
ssh root@your-vps-ip
# atau
ssh root@your-vps-domain
```

---

### Step 2: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv git

# Verify
python3 --version  # Harus 3.10+
git --version
```

---

### Step 3: Clone Repository

```bash
# Clone repository ke /opt/rai-sentinel
cd /opt
git clone https://github.com/username/rai-sentinel.git
# atau pakai SSH: git clone git@github.com:username/rai-sentinel.git

# Masuk ke directory
cd rai-sentinel

# Verify files
ls -la
# Harus ada: install.sh, monitor.py, bot.py, requirements.txt, dll
```

**Jika pakai Private Repository dengan HTTPS:**
```bash
# Akan diminta username & password
# Atau lebih baik pakai Personal Access Token:
# 1. GitHub → Settings → Developer settings → Personal access tokens
# 2. Generate token dengan repo access
# 3. Pakai token sebagai password saat clone
```

**Jika pakai SSH:**
```bash
# Pastikan SSH key sudah di-setup di VPS
# Copy SSH key ke GitHub: Settings → SSH and GPG keys
ssh-keygen -t ed25519 -C "vps@rai-sentinel"
cat ~/.ssh/id_ed25519.pub
# Copy output ke GitHub
```

---

### Step 4: Run Install Script

```bash
cd /opt/rai-sentinel

# Make executable
chmod +x install.sh

# Run install
./install.sh
```

**Input yang diminta:**
- Telegram Bot Token
- Telegram Chat ID
- Wallet Address
- Validator Operator Address
- Consensus Address (optional)

---

### Step 5: Verify Installation

```bash
# Check services
systemctl status rai-monitor.timer
systemctl status rai-bot.service

# Check logs
journalctl -u rai-monitor.service -n 20
journalctl -u rai-bot.service -n 20
```

---

## 🔄 LANGKAH 4: UPDATE CODE (SETELAH PERUBAHAN)

### Di Local Machine

```bash
# Masuk ke folder project
cd /path/to/bot_monitor_republic

# Edit files sesuai kebutuhan
# ...

# Commit changes
git add .
git commit -m "Update: description of changes"

# Push ke GitHub
git push origin main
```

---

### Di VPS (Pull Update)

```bash
# Masuk ke directory
cd /opt/rai-sentinel

# Pull latest changes
git pull origin main

# Restart services (jika ada perubahan code)
systemctl restart rai-monitor.timer
systemctl restart rai-bot.service

# Check logs untuk memastikan tidak ada error
journalctl -u rai-monitor.service -n 20
journalctl -u rai-bot.service -n 20
```

---

## 🔐 LANGKAH 5: SETUP SSH KEY (RECOMMENDED)

### Generate SSH Key di VPS

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "vps-rai-sentinel"
# Tekan Enter untuk default location
# Tekan Enter untuk no passphrase (atau set passphrase untuk lebih aman)

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

### Add SSH Key ke GitHub

1. **Copy output dari command di atas**
2. **Login ke GitHub**
3. **Settings → SSH and GPG keys**
4. **New SSH key**
5. **Paste public key**
6. **Save**

### Test SSH Connection

```bash
# Test connection
ssh -T git@github.com
# Should output: "Hi username! You've successfully authenticated..."
```

### Clone dengan SSH (setelah setup)

```bash
# Clone pakai SSH (lebih aman, tidak perlu password)
cd /opt
rm -rf rai-sentinel  # Hapus yang lama jika ada
git clone git@github.com:username/rai-sentinel.git
cd rai-sentinel
```

---

## 📝 WORKFLOW HARIAN

### Update Code

```bash
# 1. Edit di local
# 2. Commit & push
git add .
git commit -m "Fix: description"
git push

# 3. Di VPS, pull & restart
cd /opt/rai-sentinel
git pull
systemctl restart rai-monitor.timer
systemctl restart rai-bot.service
```

### Check Status

```bash
# Check git status di VPS
cd /opt/rai-sentinel
git status

# Check if up to date
git fetch
git status
```

### Rollback (jika perlu)

```bash
# Di VPS, rollback ke commit sebelumnya
cd /opt/rai-sentinel
git log --oneline  # Lihat commit history
git reset --hard <commit-hash>  # Rollback ke commit tertentu
systemctl restart rai-monitor.timer
systemctl restart rai-bot.service
```

---

## 🔧 TROUBLESHOOTING

### Problem: Git pull meminta password terus

**Solusi**: Setup SSH key (lihat Langkah 5)

```bash
# Atau pakai credential helper
git config --global credential.helper store
# Setelah itu, masukkan username & password sekali
```

### Problem: Conflict saat pull

```bash
# Backup dulu
cp -r /opt/rai-sentinel /opt/rai-sentinel-backup

# Stash local changes (jika ada)
cd /opt/rai-sentinel
git stash

# Pull
git pull origin main

# Apply stash jika perlu
git stash pop
```

### Problem: .env file ter-overwrite

**Solusi**: Pastikan .env ada di .gitignore

```bash
# Check .gitignore
cat .gitignore | grep .env

# Jika tidak ada, tambahkan
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push
```

### Problem: File tidak ter-track

```bash
# Check git status
git status

# Add file yang belum ter-track
git add <filename>
git commit -m "Add missing file"
git push
```

---

## 📋 CHECKLIST DEPLOY

### Setup Git Repository
- [ ] Buat repo di GitHub/GitLab
- [ ] Initialize git di local
- [ ] Buat .gitignore
- [ ] Commit & push pertama

### Deploy ke VPS
- [ ] Install dependencies di VPS
- [ ] Clone repository
- [ ] Run install.sh
- [ ] Input semua config
- [ ] Verify services running

### Setup SSH (Optional tapi Recommended)
- [ ] Generate SSH key di VPS
- [ ] Add SSH key ke GitHub
- [ ] Test SSH connection
- [ ] Re-clone dengan SSH

### Post-Deploy
- [ ] Test monitor: `python monitor.py --force`
- [ ] Test bot: Kirim `/status` ke bot
- [ ] Check logs: `journalctl -u rai-monitor.service -f`
- [ ] Verify timer: `systemctl status rai-monitor.timer`

---

## 🎯 BEST PRACTICES

### 1. Branch Strategy (Optional)

```bash
# Buat branch untuk development
git checkout -b develop

# Work di develop branch
# ...

# Merge ke main saat ready
git checkout main
git merge develop
git push
```

### 2. Commit Messages

```bash
# Gunakan format yang jelas
git commit -m "Fix: false alerts saat RPC down"
git commit -m "Add: Telegram rate limiting"
git commit -m "Update: timer interval ke 1 hour"
```

### 3. Tagging Releases

```bash
# Tag untuk release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Di VPS, checkout tag tertentu
git checkout v1.0.0
```

### 4. Backup .env

```bash
# Backup .env file (jangan commit ke git!)
# Simpan di tempat aman atau password manager
cat /opt/rai-sentinel/.env > ~/rai-sentinel-env-backup.txt
```

---

## 📞 QUICK REFERENCE

### Git Commands

```bash
# Status
git status

# Add files
git add .
git add <file>

# Commit
git commit -m "message"

# Push
git push origin main

# Pull
git pull origin main

# Log
git log --oneline

# Diff
git diff

# Reset (hati-hati!)
git reset --hard HEAD
```

### VPS Commands

```bash
# Pull update
cd /opt/rai-sentinel && git pull

# Restart services
systemctl restart rai-monitor.timer
systemctl restart rai-bot.service

# Check logs
journalctl -u rai-monitor.service -f
journalctl -u rai-bot.service -f
```

---

## ✅ SELESAI!

Setelah semua langkah, Anda akan punya:
- ✅ Git repository setup
- ✅ Code ter-deploy di VPS
- ✅ Services running otomatis
- ✅ Easy update via git pull

**Happy deploying!** 🚀

