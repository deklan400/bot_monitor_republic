# Environment Variables Validation Rules

## Overview
This document describes validation rules for all environment variables used by RAI Sentinel monitor.

---

## 🔴 REQUIRED VARIABLES (No Defaults)

### `TG_TOKEN`
**Type:** String  
**Format:** `{bot_id}:{bot_secret}`  
**Validation Rules:**
- Must not be empty
- Must contain exactly one colon (`:`) separator
- Part before colon: Must be numeric (bot ID)
- Part after colon: Must be alphanumeric (A-Z, a-z, 0-9), length 35-45 characters
- Total length: Typically 45-55 characters

**Valid Examples:**
```
123456789:ABCDEFghijklmnopQRSTUVwxyz1234567890
987654321:AbCdEfGhIjKlMnOpQrStUvWxYz123456789
```

**Invalid Examples:**
```
123456789 (missing colon)
:ABCDEFghijklmnopQRSTUVwxyz (missing bot ID)
123456789: (missing secret)
123456789:ABC DEF (contains space)
```

---

### `TG_CHAT_ID`
**Type:** String (numeric)  
**Format:** Integer as string (can be negative)  
**Validation Rules:**
- Must not be empty
- Must be numeric (digits only, optional leading minus)
- For private chats: Positive integer (e.g., `123456789`)
- For groups: Negative integer (e.g., `-1001234567890`)
- Length: Typically 9-14 digits

**Valid Examples:**
```
123456789
-1001234567890
987654321
```

**Invalid Examples:**
```
abc123 (non-numeric)
123.456 (decimal)
+123456789 (plus sign not allowed)
```

---

### `WALLET_ADDRESS`
**Type:** String  
**Format:** Bech32 address  
**Validation Rules:**
- Must start with `republic1` prefix
- Must be valid bech32 encoding
- Length: 42-45 characters (after prefix)
- Characters: Lowercase letters and numbers (bech32 alphabet)
- Must pass bech32 checksum validation

**Valid Examples:**
```
republic1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
republic1qwertyuiopasdfghjklzxcvbnm1234567890
```

**Invalid Examples:**
```
republic1 (too short)
cosmos1abc123... (wrong prefix)
republic1ABC123... (uppercase not allowed in bech32)
republic1abc123... (invalid checksum)
```

---

### `VALOPER_ADDRESS`
**Type:** String  
**Format:** Bech32 validator operator address  
**Validation Rules:**
- Must start with `republicvaloper1` prefix
- Must be valid bech32 encoding
- Length: 50-53 characters total
- Characters: Lowercase letters and numbers (bech32 alphabet)
- Must pass bech32 checksum validation

**Valid Examples:**
```
republicvaloper1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
republicvaloper1qwertyuiopasdfghjklzxcvbnm1234567890
```

**Invalid Examples:**
```
republicvaloper1 (too short)
republicvaloper (missing '1' prefix)
republicvaloper1ABC... (uppercase)
republicvaloper1abc... (invalid checksum)
```

---

### `CONSADDR_ADDRESS`
**Type:** String  
**Format:** Bech32 consensus address  
**Validation Rules:**
- Must start with `republicvalcons1` prefix
- Must be valid bech32 encoding
- Length: 50-53 characters total
- Characters: Lowercase letters and numbers (bech32 alphabet)
- Must pass bech32 checksum validation

**Valid Examples:**
```
republicvalcons1abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
republicvalcons1qwertyuiopasdfghjklzxcvbnm1234567890
```

**Invalid Examples:**
```
republicvalcons1 (too short)
republicvalcons (missing '1' prefix)
republicvalcons1ABC... (uppercase)
republicvalcons1abc... (invalid checksum)
```

---

## 🟡 OPTIONAL VARIABLES (Have Defaults)

### `RPC_URL`
**Type:** String (URL)  
**Default:** `http://localhost:26657`  
**Validation Rules:**
- Must be valid URL
- Must start with `http://` or `https://`
- Must include port number
- Port must be valid (1-65535)
- Should be reachable (validation can check connectivity)

**Valid Examples:**
```
http://localhost:26657
https://rpc.republicchain.io:443
http://192.168.1.100:26657
```

**Invalid Examples:**
```
localhost:26657 (missing protocol)
http://localhost (missing port)
http://localhost:99999 (invalid port)
ftp://localhost:26657 (wrong protocol)
```

---

### `LCD_URL`
**Type:** String (URL)  
**Default:** `http://localhost:1317`  
**Validation Rules:**
- Must be valid URL
- Must start with `http://` or `https://`
- Must include port number
- Port must be valid (1-65535)
- Should be reachable (validation can check connectivity)

**Valid Examples:**
```
http://localhost:1317
https://lcd.republicchain.io:443
http://192.168.1.100:1317
```

**Invalid Examples:**
```
localhost:1317 (missing protocol)
http://localhost (missing port)
http://localhost:99999 (invalid port)
```

---

### `CHAIN_ID`
**Type:** String  
**Default:** None (optional)  
**Validation Rules:**
- Must be non-empty string if provided
- Typically lowercase with hyphens or underscores
- Length: Usually 5-30 characters
- No special characters except hyphens and underscores

**Valid Examples:**
```
republic_1-1
republic-testnet-1
republic-mainnet
```

**Invalid Examples:**
```
 (empty string if provided)
REPUBLIC_1-1 (uppercase, though some chains use it)
republic@1-1 (invalid character)
```

---

### `DENOM`
**Type:** String  
**Default:** `arai`  
**Validation Rules:**
- Must be non-empty string
- Typically lowercase
- Length: Usually 3-10 characters
- Alphanumeric, may include hyphens

**Valid Examples:**
```
arai
urai
stake
atom
```

**Invalid Examples:**
```
 (empty)
ARAI (uppercase, though some chains use it)
ar ai (spaces)
```

---

### `DECIMALS`
**Type:** Integer  
**Default:** `18`  
**Validation Rules:**
- Must be positive integer
- Typical values: 6, 9, 18
- Range: 1-30 (practical limit)

**Valid Examples:**
```
6
9
18
```

**Invalid Examples:**
```
0 (zero)
-1 (negative)
18.5 (decimal)
abc (non-numeric)
```

---

### `HEARTBEAT_HOURS`
**Type:** Float/Integer  
**Default:** `3`  
**Validation Rules:**
- Must be positive number
- Recommended range: 1-24 hours
- Can be float for sub-hour intervals (e.g., 0.5 for 30 minutes)

**Valid Examples:**
```
1
3
6
12
24
0.5
1.5
```

**Invalid Examples:**
```
0 (zero)
-1 (negative)
25 (too high, though technically valid)
abc (non-numeric)
```

---

### `REWARD_DROP_PCT`
**Type:** Float  
**Default:** `5.0`  
**Validation Rules:**
- Must be positive number
- Recommended range: 1.0-50.0
- Can be decimal (e.g., 2.5)

**Valid Examples:**
```
1.0
5.0
10.0
25.5
```

**Invalid Examples:**
```
0 (zero)
-1.0 (negative)
100.0 (too high, though technically valid)
abc (non-numeric)
```

---

### `STUCK_MINUTES`
**Type:** Integer  
**Default:** `10`  
**Validation Rules:**
- Must be positive integer
- Recommended range: 5-30 minutes
- Should be less than block time * 10 (for safety)

**Valid Examples:**
```
5
10
15
30
```

**Invalid Examples:**
```
0 (zero)
-1 (negative)
1 (too low, will trigger false positives)
abc (non-numeric)
```

---

### `DATA_DIR`
**Type:** String (Path)  
**Default:** `./history`  
**Validation Rules:**
- Must be valid path (absolute or relative)
- Directory must exist or be creatable
- Should have write permissions
- Can be relative (to script location) or absolute

**Valid Examples:**
```
./history
/root/rai-sentinel/history
/var/lib/rai-sentinel
history
```

**Invalid Examples:**
```
 (empty)
/root/nonexistent/path (if not creatable)
/proc/sys (system directory, no write access)
```

---

### `REPUBLIC_HOME`
**Type:** String (Path)  
**Default:** `/root/.republicd`  
**Validation Rules:**
- Must be valid absolute path
- Directory should exist (for reference)
- Used for locating config files

**Valid Examples:**
```
/root/.republicd
/home/user/.republicd
/opt/republic/.republicd
```

**Invalid Examples:**
```
 (empty if absolute path required)
./republicd (relative path, should be absolute)
```

---

## Validation Implementation

### Recommended Validation Order:
1. **Format Check**: Validate structure (regex, length, characters)
2. **Type Check**: Ensure correct data type (int, float, string)
3. **Range Check**: Validate numeric ranges
4. **Checksum Check**: For bech32 addresses, validate checksum
5. **Connectivity Check**: For URLs, optionally test reachability
6. **File System Check**: For paths, check existence/permissions

### Error Handling:
- Missing required variables: **FATAL ERROR** - Exit immediately
- Invalid format: **FATAL ERROR** - Exit with clear error message
- Invalid range: **WARNING** - Use default or exit with warning
- Optional variables: Use defaults if missing or invalid

---

## Testing Validation

You can test validation using:
```bash
# Check .env file
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('TG_TOKEN:', 'SET' if os.getenv('TG_TOKEN') else 'MISSING')"
```


