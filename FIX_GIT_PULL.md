# Fix Git Pull Conflict

## Problem
```
error: Your local changes to the following files would be overwritten by merge:
        install.sh
```

## Solusi Cepat

### Opsi 1: Stash (Rekomendasi - Simpan perubahan lokal)

```bash
# Simpan perubahan lokal
git stash

# Pull update
git pull origin main

# Lihat perubahan yang di-stash (optional)
git stash show -p

# Jika perlu restore perubahan lokal
git stash pop
```

### Opsi 2: Discard Local Changes (Jika tidak penting)

```bash
# Backup dulu (optional)
cp install.sh install.sh.backup

# Discard local changes
git checkout -- install.sh

# Pull update
git pull origin main
```

### Opsi 3: Commit Local Changes

```bash
# Commit perubahan lokal
git add install.sh
git commit -m "Local changes to install.sh"

# Pull dengan merge
git pull origin main

# Jika ada conflict, resolve manual
```

## Langkah Lengkap (Rekomendasi)

```bash
cd /opt/rai-sentinel

# 1. Stash perubahan lokal
git stash save "Local install.sh modifications"

# 2. Pull update
git pull origin main

# 3. Update dependencies jika ada perubahan
source venv/bin/activate
pip install -r requirements.txt --quiet

# 4. Reload systemd jika service berubah
sudo systemctl daemon-reload

# 5. (Optional) Lihat apa yang di-stash
git stash show -p

# 6. (Optional) Restore jika perlu
git stash pop
```

## Setelah Pull Berhasil

```bash
# Test monitor
python monitor.py --force

# Cek timer
systemctl status rai-monitor.timer

# Update .env jika perlu (untuk HEARTBEAT_HOURS=3)
nano .env
```

