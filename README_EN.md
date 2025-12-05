# Idle Heroes 1.34.4 - Python Tools Collection

Complete toolkit for reverse engineering, decompilation, and analysis of Idle Heroes version 1.34.4.

## 📋 Table of Contents

- [Decryption Tools](#-decryption-tools)
- [Decompilation Tools](#-decompilation-tools)
- [Analysis Tools](#-analysis-tools)
- [Data Extraction Tools](#-data-extraction-tools)
- [Protobuf Tools](#-protobuf-tools)
- [Database Tools](#-database-tools)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)

---

## 🔓 Decryption Tools

### decrypt_ULTIMATE.py

**Purpose:** Final decoder for decrypting encrypted Lua files from the game.

**Algorithm:**
```
DHGAMES → XOR → XXTEA → DHZAMES → ZLIB → Decrypted Lua
```

**Technical Details:**
- Based on reverse engineering of `libcocos2dlua.so`
- Uses XOR tables from native library
- XXTEA decryption with custom key
- DHZAMES signature verification
- Final ZLIB decompression

**Usage:**
```bash
python decrypt_ULTIMATE.py
```

**Input:**
- Encrypted `.lua` files from `lua_backup/`

**Output:**
- Decrypted bytecode files in `decrypted_lua_FINAL/`

**Key Functions:**
- `xor_data()` - XOR data decryption
- `generate_key()` - XXTEA key generation
- `xxtea_decrypt()` - XXTEA decryption
- `decrypt_file()` - Complete decryption chain

---

## 🔨 Decompilation Tools

### improved_lua_decompiler.py

**Purpose:** Advanced Lua 5.1 bytecode decompiler to readable source code.

**Features:**
- ✅ All 38 Lua 5.1 opcodes (shuffled in Idle Heroes)
- ✅ Variable name recovery from debug info
- ✅ Proper scope handling
- ✅ Control structures (if/while/for)
- ✅ All operations (arithmetic, comparisons, loops)
- ✅ Memory optimization for large files

**Usage:**
```bash
python improved_lua_decompiler.py
```

**Architecture:**
```python
class ImprovedLuaDecompiler:
    - read_function()      # Read function from bytecode
    - decode_instruction() # Decode opcode
    - decompile_code()     # Decompile code
    - analyze_control_flow() # Analyze control structures
```

**Opcodes (Shuffled):**
- `0x00` = SUB (subtraction)
- `0x01` = LOADK (load constant)
- `0x06` = CALL (function call)
- `0x1c` = MOVE (register copy)
- `0x1a` = RETURN (return)
- And more (full list in code)

---

### advanced_decompiler.py

**Purpose:** Basic Lua 5.1 decompiler with readable code recovery.

**Features:**
- Lua header parsing
- Constant extraction (strings, numbers, booleans)
- Instruction decoding
- Nested function recovery
- Debug info comments

**Usage:**
```python
from advanced_decompiler import decompile_file

code, status = decompile_file("file.lua")
if code:
    print(code)
```

**Output Structure:**
```lua
-- Function: @source.lua
-- Lines: 1-100
-- Parameters: 2, Vararg: false

-- Code:
var0 = K0  -- "constant_value"
var1 = var0 + 10
return var1

-- Constants:
-- [0] "constant_value"
-- [1] 10
```

---

### decompile_all_advanced.py

**Purpose:** Mass decompilation of all Lua files.

**Usage:**
```bash
python decompile_all_advanced.py
```

**Process:**
1. Scans `decrypted_lua_FINAL/`
2. Decompiles each `.lua` file
3. Saves to `decompiled_lua_READABLE/`
4. Shows progress and statistics

**Output:**
```
[1/500] ✅ app/config/hero.lua
[2/500] ✅ app/config/item.lua
...
✅ Success: 495
❌ Errors: 5
```

---

## 🔍 Analysis Tools

### analyze_bytecode.py

**Purpose:** Detailed analysis of Lua bytecode structure.

**Analyzes:**
- Lua header (signature, version, format)
- Data type sizes
- Endianness
- Hex dump of first bytes
- Comparison with standard Lua 5.1
- Function information

**Usage:**
```bash
python analyze_bytecode.py
```

**Example Output:**
```
📁 File: hero.lua
═══════════════════════════════════════════════════════════════════════════════

🔍 HEADER:
  Signature: 1b4c7561 (b'\x1bLua')
  Version: 51
  Format: 00
  sizeof(int): 04
  sizeof(size_t): 04
  sizeof(Instruction): 04
  sizeof(lua_Number): 08

🔬 COMPARISON WITH STANDARD LUA 5.1:
  ✅ Header matches standard
```

---

### analyze_formulas.py

**Purpose:** Detailed analysis of game formulas and mechanics.

**Analyzes:**
- 🗡️ Damage calculation formulas
- 🎲 Hero summon rates
- 👤 Hero statistics
- ⚔️ Skill mechanics

**Usage:**
```bash
python analyze_formulas.py
```

**Requires:** Prior execution of `extract_game_mechanics.py`

**Output:**
```
🗡️ DAMAGE FORMULAS
═══════════════════════════════════════════════════════════════════════════════
📁 fight.lua
Found formula types: 15

DAMAGE:
  Context: atk → * → 1.5 → - → armor
  Context: base_damage → + → crit_bonus

🎲 SUMMON RATES
═══════════════════════════════════════════════════════════════════════════════
Probability distribution:
  0.5%: 5-star heroes
  3%: 4-star heroes
  20%: 3-star heroes
```

---

## 📦 Data Extraction Tools

### extract_game_data.py

**Purpose:** Extract game data from decompiled Lua files.

**Extracts:**
- `hero.lua` → Hero data
- `item.lua` → Item data
- `skill.lua` → Skill data
- `buff.lua` → Buff data
- `activity.lua` → Activity data
- `shop.lua` → Shop data

**Usage:**
```bash
python extract_game_data.py
```

**Output:**
- JSON files in `private-server/data/game_configs/`

**Example Structure:**
```json
{
  "1001": {
    "id": 1001,
    "name": "Norma",
    "quality": 3,
    "base_atk": 150,
    "base_hp": 2000
  }
}
```

---

### extract_game_mechanics.py

**Purpose:** Extract game mechanics and formulas.

**Extracts:**
- Damage calculation formulas
- Hero summon rates
- Hero statistics
- Skill mechanics

**Usage:**
```bash
python extract_game_mechanics.py
```

**Output:**
- `private-server/data/game_mechanics.json`

**Structure:**
```json
{
  "damage_formulas": {
    "fight.lua": [
      {
        "keyword": "damage",
        "context": ["atk", "*", "1.5", "-", "armor"]
      }
    ]
  },
  "summon_rates": {...},
  "hero_stats": {...},
  "skill_mechanics": {...}
}
```

---

### extract_summon_rates.py

**Purpose:** Detailed extraction of hero summon rates.

**Analyzes:**
- Gacha/summon files
- Summon pools
- Rarity probabilities
- Hero distribution

**Usage:**
```bash
python extract_summon_rates.py
```

**Typical Rates:**
```
Common (1-star): ~60-70%
Uncommon (2-star): ~20-25%
Rare (3-star): ~8-12%
Epic (4-star): ~3-5%
Legendary (5-star): ~1-2%
```

---

### extract_message_ids.py

**Purpose:** Extract Protobuf message ID mapping.

**Usage:**
```bash
python extract_message_ids.py
```

**Output:**
- `private-server/src/protocol/message_ids.py`

**Example:**
```python
MESSAGE_IDS = {
    1001: "LoginRequest",
    1002: "LoginResponse",
    2001: "GetHeroListRequest",
    2002: "GetHeroListResponse",
}

MESSAGE_NAMES = {
    "LoginRequest": 1001,
    "LoginResponse": 1002,
}
```

---

## 🔧 Protobuf Tools

### extract_protobuf_schema.py

**Purpose:** Extract Protobuf schemas from Lua bytecode.

**Process:**
1. Parse Lua bytecode
2. Extract all string constants
3. Filter by Protobuf patterns
4. Group messages and fields

**Usage:**
```bash
python extract_protobuf_schema.py
```

**Output:**
- `protobuf_schema_extracted.txt`

**Patterns:**
- Messages: start with uppercase letter
- Fields: start with lowercase letter
- No dots in name

---

### reconstruct_proto.py

**Purpose:** Reconstruct .proto files from extracted data.

**Process:**
1. Analyze extracted constants
2. Group by messages
3. Determine field types (heuristics)
4. Generate .proto files

**Usage:**
```bash
python reconstruct_proto.py
```

**Output:**
- `private-server/proto/dr2_comm.proto`
- `private-server/proto/dr2_logic.proto`

**Example .proto:**
```protobuf
syntax = "proto3";

package dr2.comm;

message LoginRequest {
  string username = 1;
  string password = 2;
  int64 timestamp = 3;
}

message LoginResponse {
  int32 code = 1;
  string message = 2;
  int64 user_id = 3;
  string session_token = 4;
}
```

**Type Heuristics:**
- `*_id`, `id` → `int64`
- `count`, `num` → `int32`
- `flag`, `is_*` → `bool`
- `time`, `ts` → `int64`
- `*list`, `*s` → `repeated`

---

### compile_proto.py

**Purpose:** Compile Protobuf schemas to Python code.

**Usage:**
```bash
python compile_proto.py
```

**Requirements:**
```bash
pip install grpcio-tools
```

**Process:**
1. Scans `private-server/proto/*.proto`
2. Compiles via `grpc_tools.protoc`
3. Generates `*_pb2.py` files
4. Creates `__init__.py`

**Output:**
- `private-server/src/protocol/dr2_comm_pb2.py`
- `private-server/src/protocol/dr2_logic_pb2.py`

**Usage in Code:**
```python
from protocol import dr2_comm_pb2

request = dr2_comm_pb2.LoginRequest()
request.username = "test"
request.password = "test123"
```

---

## 🗄️ Database Tools

### generate_import_sql.py

**Purpose:** Generate SQL for importing game data into PostgreSQL.

**Generates:**
- INSERT for all heroes
- INSERT for all items
- Test users
- Test data

**Usage:**
```bash
python generate_import_sql.py
```

**Output:**
- `network/import_game_data.sql`

**Example SQL:**
```sql
-- Import all heroes from game
INSERT INTO hero_data (hero_id, name, quality, base_atk, base_hp, base_armor, base_speed, grow_atk, grow_hp, grow_armor, grow_speed) VALUES
(1001, 'Norma', 3, 150, 2000, 50, 100, 5, 50, 2.5, 1),
(1002, 'Starlight', 5, 300, 5000, 100, 120, 10, 100, 5, 2)
ON CONFLICT (hero_id) DO NOTHING;

-- Test users
INSERT INTO users (username, password_hash, email) VALUES
('test', '$2b$12$...', 'test@test.com')
ON CONFLICT (username) DO NOTHING;
```

**Import to Database:**
```bash
docker-compose up -d
psql -U postgres -d idleheroes < network/import_game_data.sql
```

---

## 📋 Requirements

### Python Version
```
Python 3.8+
```

### Dependencies
```bash
# Built-in libraries
# struct
# pathlib
# json
# os
# sys

# Protobuf
pip install protobuf
pip install grpcio-tools

# Database (optional)
pip install psycopg2-binary

# Utilities
pip install colorama
```

### Install All Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### Complete Processing Pipeline

#### 1. Decrypt Lua Files
```bash
python decrypt_ULTIMATE.py
```
**Result:** `decrypted_lua_FINAL/` with decrypted bytecode

#### 2. Decompile to Readable Code
```bash
python decompile_all_advanced.py
```
**Result:** `decompiled_lua_READABLE/` with source code

#### 3. Analyze Bytecode (Optional)
```bash
python analyze_bytecode.py
```

#### 4. Extract Game Data
```bash
python extract_game_data.py
python extract_game_mechanics.py
python extract_summon_rates.py
```
**Result:** JSON files in `private-server/data/`

#### 5. Analyze Formulas
```bash
python analyze_formulas.py
```

#### 6. Work with Protobuf
```bash
# Extract schemas
python extract_protobuf_schema.py

# Reconstruct .proto
python reconstruct_proto.py

# Extract message IDs
python extract_message_ids.py

# Compile to Python
python compile_proto.py
```
**Result:** Python modules for protocol work

#### 7. Generate SQL for Database
```bash
python generate_import_sql.py
```
**Result:** `network/import_game_data.sql`

---

## 📁 Directory Structure

```
Tools/
├── decrypt_ULTIMATE.py              # Lua decryption
├── improved_lua_decompiler.py       # Advanced decompiler
├── advanced_decompiler.py           # Basic decompiler
├── decompile_all_advanced.py        # Mass decompilation
├── analyze_bytecode.py              # Bytecode analysis
├── analyze_formulas.py              # Formula analysis
├── extract_game_data.py             # Data extraction
├── extract_game_mechanics.py        # Mechanics extraction
├── extract_summon_rates.py          # Rate extraction
├── extract_message_ids.py           # Message ID extraction
├── extract_protobuf_schema.py       # Protobuf extraction
├── reconstruct_proto.py             # .proto reconstruction
├── compile_proto.py                 # Protobuf compilation
└── generate_import_sql.py           # SQL generation

Input:
lua_backup/                          # Encrypted Lua files

Output:
decrypted_lua_FINAL/                 # Decrypted bytecode
decompiled_lua_READABLE/             # Decompiled code
private-server/
├── data/
│   ├── game_configs/                # JSON with game data
│   ├── game_mechanics.json          # Game mechanics
│   └── summon_rates.json            # Summon rates
├── proto/                           # .proto files
└── src/
    └── protocol/                    # Compiled Python modules
network/
└── import_game_data.sql             # SQL for import
```

---

## 🔬 Technical Details

### Lua Encryption Format

```
Original file
    ↓
[DHGAMES signature]
    ↓
[XOR with data table]
    ↓
[XXTEA encryption]
    ↓
[DHZAMES signature]
    ↓
[ZLIB compression]
    ↓
Encrypted file
```

### Lua 5.1 Bytecode Structure

```
[Header 12 bytes]
  - Signature: 0x1B 'L' 'u' 'a'
  - Version: 0x51
  - Format: 0x00
  - Endianness: 0x01
  - sizeof(int): 0x04
  - sizeof(size_t): 0x04/0x08
  - sizeof(Instruction): 0x04
  - sizeof(lua_Number): 0x08
  - Integral flag: 0x00

[Function]
  - Source name (string)
  - Line defined (int)
  - Last line defined (int)
  - Num upvalues (byte)
  - Num parameters (byte)
  - Is vararg (byte)
  - Max stack size (byte)
  
  [Code]
    - Num instructions (int)
    - Instructions[] (int[])
  
  [Constants]
    - Num constants (int)
    - Constants[] (type + value)
  
  [Prototypes]
    - Num prototypes (int)
    - Prototypes[] (Function[])
  
  [Debug info]
    - Line info[]
    - Local vars[]
    - Upvalue names[]
```

### Lua 5.1 Opcodes (Shuffled)

Idle Heroes uses **shuffled opcodes** (non-standard):

| Opcode | Standard | Idle Heroes | Description |
|--------|----------|-------------|-------------|
| 0x00   | MOVE     | SUB         | Subtraction |
| 0x01   | LOADK    | LOADK       | Load constant |
| 0x06   | LOADBOOL | CALL        | Function call |
| 0x1c   | VARARG   | MOVE        | Register copy |
| 0x1a   | CLOSE    | RETURN      | Return |

**Full mapping in `improved_lua_decompiler.py`**

---

## 💡 Tips and Recommendations

### Memory Optimization

When working with large files:
```python
import gc

# After processing file
del large_data
gc.collect()
```

### Error Handling

Always check results:
```python
code, status = decompile_file(filepath)
if code:
    # Success
    process(code)
else:
    # Error
    print(f"Error: {status}")
```

### Parallel Processing

To speed up mass processing:
```python
from multiprocessing import Pool

with Pool(4) as pool:
    results = pool.map(process_file, files)
```

---

## 🐛 Troubleshooting

### Error: "Not Lua bytecode"
**Cause:** File not decrypted or corrupted  
**Solution:** Run `decrypt_ULTIMATE.py`

### Error: "No DHZAMES"
**Cause:** Wrong decryption key  
**Solution:** Check XOR tables in `decrypt_ULTIMATE.py`

### Error: "ZLIB error"
**Cause:** Data corrupted after XXTEA  
**Solution:** Check XXTEA algorithm

### Error: "protoc not found"
**Cause:** grpcio-tools not installed  
**Solution:** `pip install grpcio-tools`

---

## 📊 Project Statistics

### Files
- **Python scripts:** 14
- **Lines of code:** ~3500
- **Functions:** ~80

### Supported Formats
- Lua 5.1 bytecode (encrypted and decrypted)
- Protobuf schemas
- JSON data
- SQL scripts

### Extractable Data
- Heroes: ~200+
- Items: ~500+
- Skills: ~300+
- Protobuf messages: ~100+

---

## 🤝 Contributing

These tools are created for:
- Reverse engineering Idle Heroes game
- Creating private server
- Studying game mechanics
- Game modification

---

## ⚠️ Disclaimer

These tools are intended **for educational purposes only** and studying game mechanics. Use for commercial purposes or copyright infringement is prohibited.

---

## 📝 License

Tools are provided "as is" without any warranties.

---

## 📞 Contact

For questions and suggestions, create an Issue in the repository.

Discrord: @sitxovski


---

**Last Update:** December 2025  
**Game Version:** Idle Heroes 1.34.4  
**Status:** Fully functional tools ✅
