#!/usr/bin/env python3
"""
Извлечение маппинга ID сообщений из Lua файлов
"""

from pathlib import Path
from extract_protobuf_schema import extract_constants_from_lua

def extract_message_mapping():
    """Извлечь маппинг ID -> тип сообщения"""
    
    print("=" * 80)
    print("🔍 ИЗВЛЕЧЕНИЕ МАППИНГА ID СООБЩЕНИЙ")
    print("=" * 80)
    print()
    
    # Ищем файлы с маппингом
    protocol_files = [
        Path("decrypted_lua_FINAL/app/protocol/dr2_comm_pb.lua"),
        Path("decrypted_lua_FINAL/app/protocol/dr2_logic_pb.lua"),
        Path("decrypted_lua_FINAL/app/protocol/protocol.lua"),
        Path("decrypted_lua_FINAL/app/protocol/protocolId.lua"),
    ]
    
    message_ids = {}
    
    for proto_file in protocol_files:
        if not proto_file.exists():
            continue
        
        print(f"📁 Анализ: {proto_file.name}")
        
        constants = extract_constants_from_lua(proto_file)
        
        # Ищем паттерны ID
        for i, const in enumerate(constants):
            if isinstance(const, str) and const:
                # Ищем числа рядом со строками
                if i + 1 < len(constants) and isinstance(constants[i + 1], (int, float)):
                    msg_id = int(constants[i + 1])
                    message_ids[msg_id] = const
                    print(f"  {msg_id}: {const}")
        
        print()
    
    # Сохраняем маппинг
    output_file = Path("private-server/src/protocol/message_ids.py")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""\nМаппинг ID сообщений Protobuf\nАвтоматически извлечено из Lua файлов\n"""\n\n')
        f.write('MESSAGE_IDS = {\n')
        for msg_id, msg_name in sorted(message_ids.items()):
            f.write(f'    {msg_id}: "{msg_name}",\n')
        f.write('}\n\n')
        f.write('# Обратный маппинг\n')
        f.write('MESSAGE_NAMES = {\n')
        for msg_id, msg_name in sorted(message_ids.items()):
            f.write(f'    "{msg_name}": {msg_id},\n')
        f.write('}\n')
    
    print("=" * 80)
    print(f"✅ Найдено {len(message_ids)} маппингов")
    print(f"✅ Сохранено: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    extract_message_mapping()
