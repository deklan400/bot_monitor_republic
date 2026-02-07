# FIX LCD CONNECTION ISSUE

## Problem Analysis
- ✅ RPC running: `127.0.0.1:26657` (OK)
- ❌ LCD not running: port 1317 tidak ada yang listen
- republicd hanya expose RPC, tidak expose REST API (LCD)

## Solution Options

### Option 1: Enable API Server di republicd (Recommended)
Edit config.toml untuk enable API server

### Option 2: Use RPC untuk semua query
Modify monitor.py untuk pakai RPC saja (tapi RPC tidak support semua query)

### Option 3: Use public LCD endpoint
Jika ada public LCD untuk testnet

Mari kita cek config republicd dulu.

