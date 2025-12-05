#!/usr/bin/env python3
"""
Восстановление .proto файлов из извлеченных данных
"""

import re
from pathlib import Path
from extract_protobuf_schema import extract_constants_from_lua

def reconstruct_proto_from_lua(filepath):
    """Восстановить .proto файл из Lua байткода"""
    
    constants = extract_constants_from_lua(filepath)
    
    # Фильтруем только строки
    strings = [c for c in constants if isinstance(c, str) and c]
    
    # Группируем по сообщениям
    messages = {}
    current_message = None
    
    for i, s in enumerate(strings):
        # Ищем паттерн: MESSAGE_NAME, затем MESSAGE_NAME_FIELD_FIELD
        if s and '_FIELD' not in s and s.isupper() and len(s) > 3:
            # Это может быть имя сообщения
            # Проверяем следующие строки на наличие полей
            fields = []
            j = i + 1
            while j < len(strings) and strings[j].startswith(s + '_') and '_FIELD' in strings[j]:
                field_name = strings[j].replace(s + '_', '').replace('_FIELD', '').lower()
                fields.append(field_name)
                j += 1
            
            if fields:
                # Преобразуем имя сообщения
                msg_name = ''.join(word.capitalize() for word in s.split('_'))
                messages[msg_name] = fields
    
    return messages

def generate_proto_file(messages, package_name, output_file):
    """Генерация .proto файла"""
    
    lines = []
    lines.append('syntax = "proto3";')
    lines.append('')
    lines.append(f'package {package_name};')
    lines.append('')
    
    for msg_name, fields in sorted(messages.items()):
        lines.append(f'message {msg_name} {{')
        
        for i, field in enumerate(fields, 1):
            # Определяем тип поля (пока все string, потом уточним)
            field_type = 'string'
            
            # Эвристика для определения типа
            if 'id' in field.lower() or field.endswith('_id'):
                field_type = 'int64'
            elif 'count' in field.lower() or 'num' in field.lower():
                field_type = 'int32'
            elif 'flag' in field.lower() or 'is_' in field.lower():
                field_type = 'bool'
            elif 'time' in field.lower() or 'ts' in field.lower():
                field_type = 'int64'
            elif 'list' in field.lower() or field.endswith('s'):
                field_type = f'repeated string'
            
            lines.append(f'  {field_type} {field} = {i};')
        
        lines.append('}')
        lines.append('')
    
    # Сохраняем
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return len(messages)

def main():
    print("=" * 80)
    print("🔧 ВОССТАНОВЛЕНИЕ .PROTO ФАЙЛОВ")
    print("=" * 80)
    print()
    
    proto_files = [
        {
            'input': Path("decrypted_lua_FINAL/app/protocol/dr2_comm_pb.lua"),
            'output': Path("private-server/proto/dr2_comm.proto"),
            'package': 'dr2.comm'
        },
        {
            'input': Path("decrypted_lua_FINAL/app/protocol/dr2_logic_pb.lua"),
            'output': Path("private-server/proto/dr2_logic.proto"),
            'package': 'dr2.logic'
        },
    ]
    
    total_messages = 0
    
    for proto_info in proto_files:
        input_file = proto_info['input']
        output_file = proto_info['output']
        package = proto_info['package']
        
        if not input_file.exists():
            print(f"❌ Файл не найден: {input_file}")
            continue
        
        print(f"📁 Обработка: {input_file.name}")
        
        # Восстанавливаем сообщения
        messages = reconstruct_proto_from_lua(input_file)
        
        print(f"   Найдено сообщений: {len(messages)}")
        
        # Создаем директорию
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Генерируем .proto файл
        count = generate_proto_file(messages, package, output_file)
        
        print(f"   ✅ Сохранено: {output_file}")
        print(f"   Сообщений в файле: {count}")
        print()
        
        total_messages += count
    
    print("=" * 80)
    print(f"✅ Восстановлено {total_messages} сообщений")
    print("=" * 80)
    print()
    print("💡 Следующие шаги:")
    print("1. Проверить сгенерированные .proto файлы")
    print("2. Уточнить типы полей на основе анализа")
    print("3. Скомпилировать .proto файлы")
    print("4. Использовать в сервере")

if __name__ == "__main__":
    main()
