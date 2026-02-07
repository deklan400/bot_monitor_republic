# Fix Git Pull Conflict

## Problem
```
error: Your local changes to the following files would be overwritten by merge:
        install.sh
```

## Solusi

### Opsi 1: Stash Local Changes (Rekomendasi)

```bash
# Simpan perubahan lokal dulu
git stash

# Pull update
git pull origin main

# Lihat apa yang di-stash (optional)
git stash show -p

# Jika perlu restore perubahan lokal
git stash pop
```

### Opsi 2: Commit Local Changes

```bash
# Commit perubahan lokal
git add install.sh
git commit -m "Local changes to install.sh"

# Pull dengan merge
git pull origin main

# Jika ada conflict, resolve manual
```

### Opsi 3: Discard Local Changes (Hati-hati!)

```bash
# Backup dulu
cp install.sh install.sh.backup

# Discard local changes
git checkout -- install.sh

# Pull update
git pull origin main

# Jika perlu, compare dengan backup
diff install.sh install.sh.backup
```

### Opsi 4: Reset Hard (Hanya jika local changes tidak penting)

```bash
# WARNING: Ini akan menghapus semua local changes!
git reset --hard origin/main
git pull origin main
```

## Rekomendasi untuk VPS

Karena di VPS biasanya install.sh sudah dimodifikasi untuk path lokal, gunakan **Opsi 1 (Stash)**:

```bash
cd /opt/rai-sentinel

# Stash perubahan
git stash save "Local install.sh modifications"

# Pull update
git pull origin main

# Lihat apa yang berbeda
git stash show -p

# Jika perlu, apply kembali perubahan lokal
git stash pop
```

Setelah itu, jika ada konflik, resolve manual dengan:
```bash
nano install.sh
```

