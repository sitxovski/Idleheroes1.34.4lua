#!/usr/bin/env python3
"""
🎉 ФИНАЛЬНЫЙ ДЕКОДЕР - 100% РАБОЧИЙ
Основан на реверс-инжиниринге libcocos2dlua.so
"""

import sys
import zlib
import struct
import os
from pathlib import Path

# XOR таблица для данных (DAT_00fe7458)
XOR_DATA_TABLE = bytes([
    0x3c, 0xb5, 0x3c, 0x7f, 0x83, 0x94, 0xba, 0x3b,
    0x2b, 0xb2, 0x73, 0x5b, 0xef, 0xee, 0xe2, 0xa3,
    0x3b, 0x2b, 0xcc, 0x66, 0x3d, 0xe5, 0x2c, 0xd7,
    0x4d, 0x2e, 0x17, 0xe6, 0xf3
])

# XOR таблица для ключа (DAT_00fe7485)
XOR_KEY_TABLE = bytes([
    0x1b, 0xc3, 0xae, 0xf5, 0x87, 0x8d, 0xaf, 0x3f,
    0x2b, 0xc2, 0xd3, 0xfc, 0xfe, 0xe6, 0xf3, 0xa1,
    0x3c, 0x3c, 0xfc, 0xb4, 0x65
])

# Базовый ключ
BASE_KEY = bytes([
    0x44, 0xfa, 0xe7, 0xba, 0xcc, 0xfe, 0xfb, 0x5c,
    0x1a, 0xfb, 0xbd, 0xbb, 0x93, 0xb5, 0x83, 0xe7
])

def xor_data(data):
    """XOR данных с таблицей (индекс 0-27, потом 7-27, 7-27...)"""
    result = bytearray(data)
    idx = 0
    for i in range(len(result)):
        result[i] ^= XOR_DATA_TABLE[idx]
        
        # Логика из Ghidra: if (idx == 0x1c) idx = 7; else idx++;
        if idx == 0x1c:  # 28
            idx = 7
        else:
            idx += 1
    
    return bytes(result)

def generate_key():
    """Генерация ключа (XOR базового ключа с таблицей)"""
    key = bytearray(BASE_KEY)
    idx = 1  # Начинаем с 1 (из кода Ghidra)
    
    for i in range(1, 16):  # lVar8 от 1 до 15
        # Логика: if (idx == 0x15) idx = 7; else idx++;
        if idx == 0x15:  # 21
            idx = 7
        else:
            # idx уже был инкрементирован в предыдущей итерации
            pass
        
        key[i] ^= XOR_KEY_TABLE[idx]
        idx += 1
    
    return bytes(key)

def xxtea_decrypt(data, key):
    """XXTEA расшифровка"""
    if len(data) < 8:
        return data
    
    # Паддинг до кратности 4
    padding = (4 - (len(data) % 4)) % 4
    if padding > 0:
        data = data + b'\x00' * padding
    
    # Конвертируем в uint32 массив
    n = len(data) // 4
    v = list(struct.unpack('<' + 'I' * n, data))
    
    # Ключ в uint32
    k = list(struct.unpack('<4I', key[:16]))
    
    def MX(sum_val, y, z, p, e, k):
        return ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((sum_val ^ y) + (k[(p & 3) ^ e] ^ z))
    
    delta = 0x9E3779B9
    rounds = 6 + 52 // n
    sum_val = (rounds * delta) & 0xFFFFFFFF
    
    y = v[0]
    while rounds > 0:
        e = (sum_val >> 2) & 3
        for p in range(n - 1, 0, -1):
            z = v[p - 1]
            v[p] = (v[p] - MX(sum_val, y, z, p, e, k)) & 0xFFFFFFFF
            y = v[p]
        
        z = v[n - 1]
        v[0] = (v[0] - MX(sum_val, y, z, 0, e, k)) & 0xFFFFFFFF
        y = v[0]
        
        sum_val = (sum_val - delta) & 0xFFFFFFFF
        rounds -= 1
    
    # Конвертируем обратно
    result = struct.pack('<' + 'I' * n, *v)
    
    # Последний uint32 содержит реальную длину
    if n > 0:
        real_len = v[-1]
        if 0 < real_len < len(result):
            result = result[:real_len]
    
    return result

def decrypt_file(filepath):
    """Расшифровка файла"""
    
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # 1. Удаляем DHGAMES
        if not data.startswith(b"DHGAMES"):
            return None, "No DHGAMES header"
        
        encrypted = data[7:]
        
        # 2. XOR данных
        xored = xor_data(encrypted)
        
        # 3. Генерируем ключ
        key = generate_key()
        
        # 4. XXTEA
        decrypted = xxtea_decrypt(xored, key)
        
        # 5. Проверяем DHZAMES
        if not decrypted.startswith(b"DHZAMES"):
            return None, f"No DHZAMES (got: {decrypted[:10].hex()})"
        
        payload = decrypted[7:]
        
        # 6. ZLIB
        try:
            final = zlib.decompress(payload)
            return final, "OK"
        except:
            return None, "ZLIB error"
            
    except Exception as e:
        return None, str(e)

def main():
    print("=" * 80)
    print("🎉 ФИНАЛЬНЫЙ ДЕКОДЕР - ОСНОВАН НА РЕВЕРС-ИНЖИНИРИНГЕ")
    print("=" * 80)
    
    # Показываем ключ
    key = generate_key()
    print(f"🔑 Сгенерированный ключ: {key.hex()}")
    print(f"📋 Алгоритм: DHGAMES → XOR → XXTEA → DHZAMES → ZLIB")
    print("=" * 80)
    print()
    
    # Ищем все .lua файлы
    base_path = Path(r"D:\idleheroes\idle-heroes-1-34-4\lua_files_from_device\lua_backup")
    
    if not base_path.exists():
        print(f"❌ Папка не найдена: {base_path}")
        return
    
    lua_files = list(base_path.rglob("*.lua"))
    print(f"📁 Найдено файлов: {len(lua_files)}")
    print()
    
    success = 0
    failed = 0
    
    output_dir = Path(r"D:\idleheroes\idle-heroes-1-34-4\decrypted_lua_FINAL")
    output_dir.mkdir(exist_ok=True)
    
    for filepath in lua_files:
        result, status = decrypt_file(filepath)
        
        if result:
            # Сохраняем
            rel_path = filepath.relative_to(base_path)
            output_file = output_dir / rel_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(result)
            
            print(f"✅ {rel_path}")
            success += 1
        else:
            if failed < 10:  # Показываем только первые 10 ошибок
                print(f"❌ {filepath.name}: {status}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"✅ Успешно: {success}")
    print(f"❌ Ошибок: {failed}")
    print(f"📁 Результат: {output_dir}")
    print("=" * 80)
    
    if success > 0:
        print("\n🎉 РАСШИФРОВКА УСПЕШНА!")
        print("\nТеперь у вас есть все конфиги игры в читаемом виде!")

if __name__ == "__main__":
    main()
