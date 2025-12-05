#!/usr/bin/env python3
"""
Извлечение Protobuf схем из Lua байткода
"""

import struct
from pathlib import Path

def extract_constants_from_lua(filepath):
    """Извлечь все константы из Lua файла"""
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    if not data.startswith(b'\x1bLua'):
        return []
    
    pos = 12  # Пропускаем заголовок
    
    def read_int():
        nonlocal pos
        val = struct.unpack('<I', data[pos:pos+4])[0]
        pos += 4
        return val
    
    def read_byte():
        nonlocal pos
        b = data[pos]
        pos += 1
        return b
    
    def read_string():
        nonlocal pos
        size = read_int()
        if size == 0:
            return ""
        s = data[pos:pos+size-1].decode('utf-8', errors='replace')
        pos += size
        return s
    
    # Source
    read_string()
    
    # Line info
    read_int()  # line defined
    read_int()  # last line
    
    # Function info
    read_byte()  # upvalues
    read_byte()  # params
    read_byte()  # vararg
    read_byte()  # stack
    
    # Code
    num_inst = read_int()
    for i in range(num_inst):
        read_int()
    
    # Constants
    num_const = read_int()
    constants = []
    
    for i in range(num_const):
        const_type = read_byte()
        
        if const_type == 0:  # nil
            constants.append(None)
        elif const_type == 1:  # boolean
            val = read_byte()
            constants.append(bool(val))
        elif const_type == 3:  # number
            val = struct.unpack('<d', data[pos:pos+8])[0]
            pos += 8
            constants.append(val)
        elif const_type == 4:  # string
            val = read_string()
            constants.append(val)
    
    return constants

def analyze_protobuf_file(filepath):
    """Анализ Protobuf Lua файла"""
    
    constants = extract_constants_from_lua(filepath)
    
    # Фильтруем только строки
    strings = [c for c in constants if isinstance(c, str) and c]
    
    return strings

def main():
    print("=" * 80)
    print("🔍 ИЗВЛЕЧЕНИЕ PROTOBUF СХЕМ")
    print("=" * 80)
    print()
    
    # Ищем Protobuf файлы
    proto_files = [
        Path("decrypted_lua_FINAL/app/protocol/dr2_comm_pb.lua"),
        Path("decrypted_lua_FINAL/app/protocol/dr2_logic_pb.lua"),
    ]
    
    all_messages = {}
    
    for proto_file in proto_files:
        if not proto_file.exists():
            print(f"❌ Файл не найден: {proto_file}")
            continue
        
        print(f"📁 Анализ: {proto_file.name}")
        print("-" * 80)
        
        strings = analyze_protobuf_file(proto_file)
        
        print(f"Найдено строк: {len(strings)}")
        print()
        
        # Ищем паттерны Protobuf
        messages = []
        fields = []
        
        for s in strings:
            # Сообщения обычно начинаются с заглавной буквы
            if s and s[0].isupper() and not '.' in s and len(s) > 2:
                messages.append(s)
            # Поля обычно с маленькой буквы
            elif s and s[0].islower() and not '.' in s and len(s) > 2:
                fields.append(s)
        
        print(f"Возможные сообщения ({len(messages)}):")
        for msg in messages[:20]:  # Первые 20
            print(f"  - {msg}")
        
        if len(messages) > 20:
            print(f"  ... и еще {len(messages) - 20}")
        
        print()
        print(f"Возможные поля ({len(fields)}):")
        for field in fields[:20]:  # Первые 20
            print(f"  - {field}")
        
        if len(fields) > 20:
            print(f"  ... и еще {len(fields) - 20}")
        
        print()
        
        all_messages[proto_file.name] = {
            'messages': messages,
            'fields': fields,
            'all_strings': strings
        }
    
    # Сохраняем результаты
    output_file = Path("protobuf_schema_extracted.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for filename, data in all_messages.items():
            f.write(f"{'=' * 80}\n")
            f.write(f"Файл: {filename}\n")
            f.write(f"{'=' * 80}\n\n")
            
            f.write(f"Сообщения ({len(data['messages'])}):\n")
            for msg in data['messages']:
                f.write(f"  {msg}\n")
            
            f.write(f"\nПоля ({len(data['fields'])}):\n")
            for field in data['fields']:
                f.write(f"  {field}\n")
            
            f.write(f"\nВсе строки ({len(data['all_strings'])}):\n")
            for s in data['all_strings']:
                f.write(f"  {s}\n")
            
            f.write("\n\n")
    
    print("=" * 80)
    print(f"✅ Результаты сохранены: {output_file}")
    print("=" * 80)
    print()
    print("💡 Следующий шаг: Восстановить .proto файлы на основе найденных данных")

if __name__ == "__main__":
    main()
