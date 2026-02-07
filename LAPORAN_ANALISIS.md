# LAPORAN ANALISIS - RAI SENTINEL MONITOR

## ✅ YANG SUDAH BENAR

1. ✅ Struktur file sesuai requirement
2. ✅ Semua fitur utama sudah diimplementasi
3. ✅ Systemd service & timer sudah dibuat
4. ✅ History CSV dan chart generation ada
5. ✅ Alert mechanism sudah ada

---

## ❌ MASALAH KRITIS YANG PERLU DIPERBAIKI

### 1. **TG_TOKEN BISA None - CRASH RISK**
**Lokasi:** `monitor.py` line 52-53
**Masalah:**
```python
TG_TOKEN = os.getenv('TG_TOKEN')  # Bisa None
TG_API_URL = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage'  # Akan jadi "botNone"
```
**Dampak:** Script akan crash saat kirim Telegram jika TG_TOKEN tidak di-set
**Solusi:** Validasi env vars di awal atau buat TG_API_URL di dalam function

---

### 2. **DOUBLE SEND MESSAGE PADA ALERT**
**Lokasi:** `monitor.py` line 432-485
**Masalah:**
- Saat ada alert (jailed/unbonded/stuck), sudah kirim message di line 434, 442, 450, 459, 467
- Tapi di line 474-478, kalau `is_alert=True`, akan kirim lagi message yang sama
**Dampak:** User dapat 2x message yang sama saat ada alert
**Solusi:** Jangan kirim heartbeat message jika sudah ada alert yang dikirim

---

### 3. **NAMA FILE .env.example SALAH**
**Lokasi:** Root directory
**Masalah:** 
- Requirement minta: `.env.example`
- Yang dibuat: `env.example` (tanpa titik di depan)
**Dampak:** Tidak sesuai spesifikasi
**Solusi:** Rename ke `.env.example`

---

### 4. **HARDCODED PATH DI SYSTEMD FILES**
**Lokasi:** `systemd/rai-monitor.service` line 8-10
**Masalah:**
```ini
WorkingDirectory=/root/rai-sentinel
ExecStart=/root/rai-sentinel/venv/bin/python /root/rai-sentinel/monitor.py
```
**Dampak:** 
- Install.sh pakai `$(pwd)` tapi systemd files hardcoded `/root/rai-sentinel`
- Tidak fleksibel jika install di lokasi lain
**Solusi:** Install.sh harus replace path di systemd files dengan `$(pwd)`

---

### 5. **CHECK_HEIGHT_STUCK LOGIC BUG**
**Lokasi:** `monitor.py` line 222-242
**Masalah:**
- Jika height berubah, harus update time juga
- Tapi logic saat ini: kalau height sama dengan last, cek stuck. Kalau beda, update height & time, return False
- **MASALAH:** Kalau height berubah, time di-update di line 238-239, tapi ini terjadi SETELAH return False di line 236
- Jadi kalau height berubah, time tidak ter-update dengan benar
**Dampak:** Stuck detection bisa salah
**Solusi:** Perbaiki flow logic

---

### 6. **GET_REWARDS() POTENTIAL ERROR**
**Lokasi:** `monitor.py` line 184-197, khususnya line 193
**Masalah:**
```python
total += int(reward['amount'].split('.')[0])
```
**Dampak:** 
- Jika format `amount` bukan string (misal sudah int), akan error
- Jika format berbeda (misal scientific notation), bisa error
**Solusi:** Handle berbagai format amount dengan lebih robust

---

### 7. **DATETIME.FROMISOFORMAT() BISA ERROR**
**Lokasi:** `monitor.py` line 351
**Masalah:**
```python
ts = datetime.fromisoformat(row['timestamp'])
```
**Dampak:** 
- Jika format timestamp di CSV berbeda (misal dari timezone lain), bisa error
- Python < 3.7 tidak support `fromisoformat()`
**Solusi:** Gunakan parser yang lebih robust atau handle exception

---

### 8. **MISSING VALIDATION ENV VARS**
**Lokasi:** `monitor.py` line 25-29
**Masalah:** Tidak ada validasi apakah env vars penting (TG_TOKEN, TG_CHAT_ID, WALLET, VALOPER, CONSADDR) sudah di-set
**Dampak:** Script bisa crash dengan error yang tidak jelas
**Solusi:** Validasi di awal main() atau saat load env

---

### 9. **INSTALL.SH TIDAK VALIDASI INPUT**
**Lokasi:** `install.sh` line 11-15
**Masalah:** Tidak ada validasi apakah input kosong atau format salah
**Dampak:** Bisa create .env dengan value kosong
**Solusi:** Tambah validasi input

---

### 10. **RPC/LCD ERROR HANDLING TIDAK KONSISTEN**
**Lokasi:** `monitor.py` line 93-114
**Masalah:**
- `get_rpc()` dan `get_lcd()` return None jika error
- Tapi di `main()`, jika validator/node_status None, langsung exit
- Tidak ada retry mechanism
**Dampak:** Satu kali network hiccup = script exit
**Solusi:** Tambah retry dengan backoff atau handle lebih graceful

---

## ⚠️ MASALAH MINOR / PERBAIKAN DISARANKAN

### 11. **HEARTBEAT LOGIC**
**Lokasi:** `monitor.py` line 261-275, 474
**Masalah:**
- `should_send_heartbeat()` update file di dalam function
- Tapi kalau ada alert, heartbeat juga dikirim (line 474: `or is_alert`)
- Ini berarti setiap alert = reset heartbeat timer
**Dampak:** Heartbeat bisa lebih sering dari yang diharapkan
**Solusi:** Pisahkan logic: alert tidak reset heartbeat timer

---

### 12. **CHART GENERATION HANYA JIKA >= 2 DATA POINTS**
**Lokasi:** `monitor.py` line 358
**Masalah:** 
- Chart hanya generate jika ada >= 2 timestamps
- Tapi tidak ada notifikasi ke user bahwa chart belum bisa dibuat
**Dampak:** User tidak tahu kenapa chart tidak muncul
**Solusi:** Bisa skip dengan silent, atau log info

---

### 13. **MISSED BLOCKS COUNTER BISA RESET**
**Lokasi:** `monitor.py` line 200-211
**Masalah:**
- `missed_blocks_counter` dari API bisa reset setelah unbonding period
- Chart akan menunjukkan nilai yang tidak akurat untuk historical
**Dampak:** Chart missed blocks bisa misleading
**Solusi:** Simpan cumulative atau delta per run

---

### 14. **REWARD DROP CHECK BISA FALSE POSITIVE**
**Lokasi:** `monitor.py` line 245-258
**Masalah:**
- Jika user claim rewards, `current_rewards` akan drop drastis
- Ini akan trigger alert "reward drop"
**Dampak:** False positive alert
**Solusi:** Handle case dimana reward drop karena claim (cek transaction history atau threshold lebih tinggi)

---

### 15. **FORMAT MESSAGE TIDAK 100% SESUAI SPEC**
**Lokasi:** `monitor.py` line 298-312
**Masalah:**
- Spec minta format exact dengan bullet points
- Current format sudah mirip tapi spacing bisa berbeda
- Timestamp format: spec minta "Timestamp (WIB)" tapi current "⏱ {timestamp}"
**Dampak:** Tidak 100% sesuai requirement
**Solusi:** Match exact format dari spec

---

### 16. **NO LOGGING TO FILE**
**Lokasi:** Seluruh `monitor.py`
**Masalah:** Hanya log error ke stderr, tidak ada log file
**Dampak:** Sulit debug jika run via systemd
**Solusi:** Tambah file logging (optional)

---

### 17. **INSTALL.SH TIDAK CHECK DEPENDENCIES**
**Lokasi:** `install.sh`
**Masalah:** Tidak check apakah python3, pip, systemd sudah terinstall
**Dampak:** Install bisa gagal dengan error yang tidak jelas
**Solusi:** Tambah dependency check

---

### 18. **HISTORY CSV BISA CORRUPT**
**Lokasi:** `monitor.py` line 317-333
**Masalah:** Tidak ada lock mechanism saat write CSV
**Dampak:** Jika 2 instance run bersamaan, CSV bisa corrupt
**Solusi:** Tambah file lock (optional, karena systemd timer biasanya aman)

---

## 📋 RINGKASAN PRIORITAS

### **PRIORITAS TINGGI (Harus Fix):**
1. TG_TOKEN validation (crash risk)
2. Double send message pada alert
3. Nama file .env.example
4. Hardcoded path di systemd
5. Check_height_stuck logic bug
6. Missing validation env vars

### **PRIORITAS SEDANG (Sebaiknya Fix):**
7. Get_rewards() error handling
8. Datetime parsing robustness
9. Install.sh input validation
10. RPC/LCD retry mechanism
11. Heartbeat logic improvement

### **PRIORITAS RENDAH (Nice to Have):**
12. Chart generation notification
13. Missed blocks counter handling
14. Reward drop false positive
15. Format message exact match
16. File logging
17. Install.sh dependency check
18. CSV corruption prevention

---

## ✅ KESIMPULAN

**Status:** Code sudah 80% siap, tapi ada beberapa bug kritis yang harus diperbaiki sebelum production.

**Yang paling urgent:**
- Fix TG_TOKEN None issue (akan crash)
- Fix double message send
- Fix systemd path hardcoding
- Fix height stuck detection logic

Setelah fix ini, code sudah cukup stabil untuk digunakan.


