# RAI Sentinel

Production-ready Cosmos SDK validator monitor for RAI chain.

## Features

- ✅ Real-time validator status monitoring (BONDED/UNBONDING/UNBONDED)
- ✅ Jailed & tombstoned detection
- ✅ Node sync status monitoring
- ✅ Missed blocks tracking
- ✅ Telegram alerts (send-only, no bot commands)
- ✅ Heartbeat messages
- ✅ History tracking with CSV
- ✅ PNG charts (optional)

## Installation

### 1. Clone Repository

```bash
cd /opt
git clone https://github.com/deklan400/bot_monitor_republic.git rai-sentinel
cd rai-sentinel
```

### 2. Run Install Script

```bash
chmod +x install.sh
./install.sh
```

The script will:
- Ask for Telegram Bot Token
- Ask for Telegram Chat ID
- Ask for VALOPER address
- Ask for Wallet address
- Ask for Chain ID (optional)
- Create Python virtual environment
- Install dependencies
- Create .env file
- Setup systemd services
- Enable and start timer

### 3. Verify Installation

```bash
# Check timer status
systemctl status rai-monitor.timer

# Check logs
journalctl -u rai-monitor.service -f
```

## Configuration

Edit `.env` file to customize:

```bash
nano .env
```

### Required Variables

- `TG_TOKEN` - Telegram Bot Token from @BotFather
- `TG_CHAT_ID` - Telegram Chat ID
- `VALOPER` - Validator operator address (republicvaloper1...)
- `WALLET` - Wallet address (republic1...)

### Optional Variables

- `CHAIN_ID` - Chain ID (default: empty)
- `REPUBLIC_HOME` - republicd home directory (default: /root/.republicd)
- `DENOM` - Token denomination (default: arai)
- `DECIMALS` - Token decimals (default: 18)
- `HEARTBEAT_HOURS` - Hours between heartbeat (default: 6)
- `REWARD_DROP_PCT` - Reward drop threshold (default: 5)
- `STUCK_MINUTES` - Minutes before considering stuck (default: 10)

## Alert Levels

### 🟢 HEALTHY
- Status: BONDED
- Jailed: No
- Tombstoned: No
- Node: Not catching up

### 🟡 WARNING
- Status: UNBONDING
- OR Node: Catching up

### 🔴 ALERT
- Jailed: Yes
- OR Missed blocks increasing

### ☠️ FATAL
- Tombstoned: Yes (permanent, cannot recover)

## Recovery Steps

### If Jailed

1. Check why validator was jailed
2. Wait for jail period to expire
3. Unjail validator:
   ```bash
   republicd tx slashing unjail --from <key-name> --chain-id <chain-id>
   ```

### If Tombstoned

⚠️ **WARNING**: Tombstoned validators cannot be recovered. The validator is permanently slashed and cannot rejoin the network.

## Manual Testing

```bash
# Test monitor
cd /opt/rai-sentinel
source venv/bin/activate
python monitor.py --force

# Test with charts
python monitor.py --force --send-charts
```

## Troubleshooting

### Validator Status Shows UNKNOWN

1. Verify VALOPER address is correct:
   ```bash
   republicd query staking validator <VALOPER> -o json
   ```

2. Check if validator exists:
   ```bash
   republicd query staking validators | grep <VALOPER>
   ```

3. Verify .env file has correct VALOPER:
   ```bash
   cat .env | grep VALOPER
   ```

### No Telegram Messages

1. Check Telegram token:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   ```

2. Check Chat ID:
   - Send message to bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`

3. Check logs:
   ```bash
   journalctl -u rai-monitor.service -n 50
   ```

### Node Not Responding

1. Check if republicd is running:
   ```bash
   systemctl status republicd
   ```

2. Test RPC:
   ```bash
   curl http://localhost:26657/status
   ```

3. Update RPC_URL in .env if needed

## Service Management

```bash
# Start timer
systemctl start rai-monitor.timer

# Stop timer
systemctl stop rai-monitor.timer

# Check status
systemctl status rai-monitor.timer

# View logs
journalctl -u rai-monitor.service -f
```

## Files

- `monitor.py` - Main monitoring script
- `install.sh` - Installation script
- `.env` - Configuration file (create from .env.example)
- `history/history.csv` - Historical data
- `history/state.json` - State tracking
- `history/*.png` - Generated charts

## License

MIT
