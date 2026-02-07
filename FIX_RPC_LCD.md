# FIX RPC/LCD CONNECTION ISSUE

## Problem
LCD connection refused di localhost:1317

## Solution Steps

### 1. Check if republicd is running
```bash
ps aux | grep republicd
```

### 2. Check RPC endpoint
```bash
curl http://localhost:26657/status
```

### 3. Check LCD endpoint
```bash
curl http://localhost:1317/cosmos/staking/v1beta1/validators
```

### 4. Find correct RPC/LCD URLs
Jika localhost tidak jalan, cari URL yang benar:
- Check republicd config
- Atau gunakan public RPC/LCD

### 5. Update .env file
Edit RPC_URL dan LCD_URL di .env

