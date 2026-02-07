# ENABLE LCD/REST API DI REPUBLICD

## Problem
LCD (REST API) tidak running di port 1317. Hanya RPC yang running.

## Solution: Enable API Server

### Step 1: Edit republicd config

```bash
# Edit config.toml
nano ~/.republicd/config/app.toml
```

### Step 2: Enable API Server

Cari section `[api]` dan pastikan:

```toml
[api]

# Enable defines if the API server should be enabled.
enable = true

# Address defines the API server to listen on.
address = "tcp://0.0.0.0:1317"

# MaxOpenConnections defines the number of maximum open connections.
max-open-connections = 1000

# RPCReadTimeout defines the Tendermint RPC read timeout (in seconds).
rpc-read-timeout = 10

# RPCTimeout defines the Tendermint RPC write timeout (in seconds).
rpc-write-timeout = 10

# EnableUnsafeCORS defines if CORS should be enabled (unsafe - use it at your own risk).
enable-unsafe-cors = false
```

**Atau jika tidak ada section [api], tambahkan di akhir file.**

### Step 3: Restart republicd

```bash
systemctl restart republicd

# Wait a few seconds
sleep 5

# Check status
systemctl status republicd
```

### Step 4: Verify LCD is running

```bash
# Check port
ss -tlnp | grep 1317

# Test LCD
curl http://localhost:1317/cosmos/staking/v1beta1/validators
```

### Step 5: Test monitor again

```bash
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force
```

---

## Alternative: Use republicd query commands

Jika tidak bisa enable API server, monitor sudah punya fallback ke republicd subprocess commands.

