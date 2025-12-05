#!/usr/bin/env python3
"""
Извлечение игровых данных из декомпилированных Lua файлов
"""

import json
from pathlib import Path
from extract_protobuf_schema import extract_constants_from_lua

def extract_config_data(config_file):
    """Извлечь данные из конфиг файла"""
    
    constants = extract_constants_from_lua(config_file)
    
    # Группируем данные
    data = {}
    current_id = None
    current_obj = {}
    
    for i, const in enumerate(constants):
        if isinstance(const, (int, float)) and const > 1000:
            # Возможно это ID
            if current_id and current_obj:
                data[current_id] = current_obj
            current_id = int(const)
            current_obj = {'id': current_id}
        elif isinstance(const, str) and const:
            # Это может быть имя поля
            if i + 1 < len(constants):
                next_val = constants[i + 1]
                if isinstance(next_val, (str, int, float)):
                    current_obj[const] = next_val
    
    if current_id and current_obj:
        data[current_id] = current_obj
    
    return data

def main():
    print("=" * 80)
    print("🎮 ИЗВЛЕЧЕНИЕ ИГРОВЫХ ДАННЫХ")
    print("=" * 80)
    print()
    
    config_dir = Path("decrypted_lua_FINAL/app/config")
    output_dir = Path("private-server/data/game_configs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Важные конфиги
    important_configs = [
        'hero.lua',
        'item.lua',
        'skill.lua',
        'buff.lua',
        'activity.lua',
        'shop.lua',
    ]
    
    total_extracted = 0
    
    for config_name in important_configs:
        config_file = config_dir / config_name
        
        if not config_file.exists():
            print(f"❌ Не найден: {config_name}")
            continue
        
        print(f"📁 Обработка: {config_name}")
        
        data = extract_config_data(config_file)
        
        if data:
            output_file = output_dir / config_name.replace('.lua', '.json')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Извлечено записей: {len(data)}")
            print(f"   ✅ Сохранено: {output_file.name}")
            total_extracted += len(data)
        else:
            print(f"   ⚠️ Данные не найдены")
        
        print()
    
    print("=" * 80)
    print(f"✅ Всего извлечено: {total_extracted} записей")
    print(f"✅ Сохранено в: {output_dir}")
    print("=" * 80)
    print()
    print("💡 Теперь можно использовать эти данные в сервере!")

if __name__ == "__main__":
    main()
