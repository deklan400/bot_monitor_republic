# Telegram Message Templates

## 1. HEALTHY

```
🟢 RAI VALIDATOR STATUS — HEALTHY

Validator:
• Moniker  : {MONIKER}
• Status   : BONDED
• Jailed   : No
• Tombstoned : No

Node:
• Height   : {HEIGHT:,}
• Missed   : {MISSED_BLOCKS}

Balance:
• Wallet    : {WALLET_BALANCE} RAI
• Delegated : {DELEGATED_BALANCE} RAI
• Rewards   : {REWARDS_BALANCE} RAI

⏱ {TIMESTAMP} UTC
```

## 2. WARNING (Unbonding or Catching Up)

```
🟡 RAI VALIDATOR STATUS — WARNING

Validator:
• Moniker  : {MONIKER}
• Status   : {STATUS}
• Jailed   : No
• Tombstoned : No

Node:
• Height   : {HEIGHT:,}
• Sync     : {SYNC_STATUS}
• Missed   : {MISSED_BLOCKS}

Balance:
• Wallet    : {WALLET_BALANCE} RAI
• Delegated : {DELEGATED_BALANCE} RAI
• Rewards   : {REWARDS_BALANCE} RAI

⏱ {TIMESTAMP} UTC
```

## 3. ALERT (Jailed or Missed Blocks)

```
🔴 RAI VALIDATOR STATUS — ALERT

Validator:
• Moniker  : {MONIKER}
• Status   : {STATUS}
• Jailed   : {JAILED_STATUS}
• Tombstoned : No

Node:
• Height   : {HEIGHT:,}
• Missed   : {MISSED_BLOCKS} {MISSED_CHANGE}

Balance:
• Wallet    : {WALLET_BALANCE} RAI
• Delegated : {DELEGATED_BALANCE} RAI
• Rewards   : {REWARDS_BALANCE} RAI

⏱ {TIMESTAMP} UTC
```

## 4. FATAL (Tombstoned)

```
⚫ RAI VALIDATOR STATUS — FATAL

Validator:
• Moniker  : {MONIKER}
• Status   : {STATUS}
• Jailed   : {JAILED_STATUS}
• Tombstoned : Yes

Node:
• Height   : {HEIGHT:,}
• Missed   : {MISSED_BLOCKS}

Balance:
• Wallet    : {WALLET_BALANCE} RAI
• Delegated : {DELEGATED_BALANCE} RAI
• Rewards   : {REWARDS_BALANCE} RAI

⏱ {TIMESTAMP} UTC
```

---

## Template Variables

- `{MONIKER}` - Validator moniker name
- `{STATUS}` - BONDED / UNBONDING / UNBONDED
- `{HEIGHT}` - Latest block height (integer)
- `{MISSED_BLOCKS}` - Missed blocks count (integer)
- `{MISSED_CHANGE}` - Optional: "(+X)" if increased
- `{SYNC_STATUS}` - "SYNCING" or "OK"
- `{JAILED_STATUS}` - "Yes" or "No"
- `{WALLET_BALANCE}` - Formatted balance (2 decimals)
- `{DELEGATED_BALANCE}` - Formatted balance (2 decimals)
- `{REWARDS_BALANCE}` - Formatted balance (2 decimals)
- `{TIMESTAMP}` - ISO format: "YYYY-MM-DD HH:MM:SS UTC"

---

## Example Outputs

### HEALTHY Example:
```
🟢 RAI VALIDATOR STATUS — HEALTHY

Validator:
• Moniker  : MyValidator
• Status   : BONDED
• Jailed   : No
• Tombstoned : No

Node:
• Height   : 1,234,567
• Missed   : 0

Balance:
• Wallet    : 11.99 RAI
• Delegated : 39.60 RAI
• Rewards   : 0.12 RAI

⏱ 2024-01-15 14:30:45 UTC
```

### WARNING Example (Catching Up):
```
🟡 RAI VALIDATOR STATUS — WARNING

Validator:
• Moniker  : MyValidator
• Status   : BONDED
• Jailed   : No
• Tombstoned : No

Node:
• Height   : 1,234,567
• Sync     : SYNCING
• Missed   : 0

Balance:
• Wallet    : 11.99 RAI
• Delegated : 39.60 RAI
• Rewards   : 0.12 RAI

⏱ 2024-01-15 14:30:45 UTC
```

### ALERT Example (Jailed):
```
🔴 RAI VALIDATOR STATUS — ALERT

Validator:
• Moniker  : MyValidator
• Status   : BONDED
• Jailed   : Yes
• Tombstoned : No

Node:
• Height   : 1,234,567
• Missed   : 5

Balance:
• Wallet    : 11.99 RAI
• Delegated : 39.60 RAI
• Rewards   : 0.12 RAI

⏱ 2024-01-15 14:30:45 UTC
```

### FATAL Example:
```
⚫ RAI VALIDATOR STATUS — FATAL

Validator:
• Moniker  : MyValidator
• Status   : BONDED
• Jailed   : Yes
• Tombstoned : Yes

Node:
• Height   : 1,234,567
• Missed   : 10

Balance:
• Wallet    : 11.99 RAI
• Delegated : 39.60 RAI
• Rewards   : 0.12 RAI

⏱ 2024-01-15 14:30:45 UTC
```


