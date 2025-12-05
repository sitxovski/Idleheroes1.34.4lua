#!/usr/bin/env python3
"""
Анализ Lua байткода для понимания формата
"""

import struct
from pathlib import Path

def analyze_lua_header(filepath):
    """Анализ заголовка Lua файла"""
    
    with open(filepath, 'rb') as f:
        data = f.read(100)
    
    print("=" * 80)
    print(f"📁 Файл: {filepath.name}")
    print("=" * 80)
    print()
    
    # Заголовок Lua
    print("🔍 ЗАГОЛОВОК:")
    print(f"  Сигнатура: {data[0:4].hex()} ({data[0:4]})")
    
    if data[0:4] != b'\x1bLua':
        print("  ❌ Неправильная сигнатура!")
        return
    
    print(f"  Версия: {data[4]:02x}")
    print(f"  Формат: {data[5]:02x}")
    print(f"  Endianness: {data[6]:02x}")
    print(f"  sizeof(int): {data[7]:02x}")
    print(f"  sizeof(size_t): {data[8]:02x}")
    print(f"  sizeof(Instruction): {data[9]:02x}")
    print(f"  sizeof(lua_Number): {data[10]:02x}")
    print(f"  Integral flag: {data[11]:02x}")
    print()
    
    # Hex dump первых 100 байт
    print("📊 HEX DUMP (первые 100 байт):")
    for i in range(0, min(100, len(data)), 16):
        hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"  {i:04x}: {hex_part:<48} {ascii_part}")
    print()
    
    # Сравнение с стандартным Lua 5.1
    print("🔬 СРАВНЕНИЕ СО СТАНДАРТНЫМ LUA 5.1:")
    
    standard_lua51 = {
        'signature': b'\x1bLua',
        'version': 0x51,  # Lua 5.1
        'format': 0x00,
        'endianness': 0x01,
        'sizeof_int': 0x04,
        'sizeof_size_t': 0x04,  # или 0x08 на 64-bit
        'sizeof_instruction': 0x04,
        'sizeof_number': 0x08,
        'integral': 0x00
    }
    
    differences = []
    
    if data[4] != standard_lua51['version']:
        differences.append(f"  ⚠️ Версия: {data[4]:02x} (стандарт: {standard_lua51['version']:02x})")
    
    if data[5] != standard_lua51['format']:
        differences.append(f"  ⚠️ Формат: {data[5]:02x} (стандарт: {standard_lua51['format']:02x})")
    
    if data[8] != standard_lua51['sizeof_size_t'] and data[8] != 0x08:
        differences.append(f"  ⚠️ sizeof(size_t): {data[8]:02x}")
    
    if differences:
        print("  НАЙДЕНЫ ОТЛИЧИЯ:")
        for diff in differences:
            print(diff)
    else:
        print("  ✅ Заголовок соответствует стандарту Lua 5.1")
    print()
    
    # Попытка прочитать chunk
    print("📦 CHUNK INFO:")
    try:
        pos = 12  # После заголовка
        
        # Source name
        size = struct.unpack('<I', data[pos:pos+4])[0]
        pos += 4
        print(f"  Source name size: {size}")
        
        if size > 0 and pos + size <= len(data):
            source = data[pos:pos+size-1].decode('utf-8', errors='replace')
            print(f"  Source name: {source}")
            pos += size
        
        # Line defined
        if pos + 4 <= len(data):
            line_defined = struct.unpack('<I', data[pos:pos+4])[0]
            print(f"  Line defined: {line_defined}")
            pos += 4
        
        # Last line defined
        if pos + 4 <= len(data):
            last_line = struct.unpack('<I', data[pos:pos+4])[0]
            print(f"  Last line defined: {last_line}")
            pos += 4
        
        # Num upvalues
        if pos + 1 <= len(data):
            num_upvalues = data[pos]
            print(f"  Num upvalues: {num_upvalues}")
            pos += 1
        
        # Num parameters
        if pos + 1 <= len(data):
            num_params = data[pos]
            print(f"  Num parameters: {num_params}")
            pos += 1
        
        # Is vararg
        if pos + 1 <= len(data):
            is_vararg = data[pos]
            print(f"  Is vararg: {is_vararg}")
            pos += 1
        
        # Max stack size
        if pos + 1 <= len(data):
            max_stack = data[pos]
            print(f"  Max stack size: {max_stack}")
            pos += 1
            
    except Exception as e:
        print(f"  ❌ Ошибка парсинга: {e}")
    
    print()

def main():
    print("=" * 80)
    print("🔬 АНАЛИЗ LUA БАЙТКОДА COCOS2D-X")
    print("=" * 80)
    print()
    
    # Анализируем несколько файлов
    base_path = Path("decrypted_lua_FINAL")
    
    test_files = [
        "version.lua",
        "app/config/hero.lua",
        "app/common/eventManager.lua",
    ]
    
    for test_file in test_files:
        filepath = base_path / test_file
        if filepath.exists():
            analyze_lua_header(filepath)
            print()
        else:
            print(f"❌ Файл не найден: {filepath}")
            print()
    
    print("=" * 80)
    print("💡 ВЫВОДЫ:")
    print("=" * 80)
    print()
    print("На основе анализа можно:")
    print("1. Определить точную версию Lua")
    print("2. Найти модификации формата")
    print("3. Написать парсер байткода")
    print("4. Создать декомпилятор")

if __name__ == "__main__":
    main()
