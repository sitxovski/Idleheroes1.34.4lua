"""
Генератор SQL для импорта ВСЕХ игровых данных в PostgreSQL
"""

import json
from pathlib import Path


def escape_sql_string(s):
    """Экранирование строк для SQL"""
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"


def generate_hero_imports():
    """Генерация INSERT для всех героев"""
    hero_file = Path("data/game_configs/hero.json")
    
    if not hero_file.exists():
        print(f"❌ Файл {hero_file} не найден")
        return []
    
    with open(hero_file, 'r', encoding='utf-8') as f:
        heroes = json.load(f)
    
    inserts = []
    inserts.append("-- Импорт всех героев из игры")
    inserts.append("INSERT INTO hero_data (hero_id, name, quality, base_atk, base_hp, base_armor, base_speed, grow_atk, grow_hp, grow_armor, grow_speed) VALUES")
    
    values = []
    for hero_id, hero_data in heroes.items():
        # Извлекаем данные
        name = hero_data.get('name', f'Hero_{hero_id}')
        quality = hero_data.get('quality', 1)
        
        # Базовые характеристики
        base_atk = hero_data.get('base_atk', 100)
        base_hp = hero_data.get('base_hp', 1000)
        base_armor = hero_data.get('base_armor', 50)
        base_speed = hero_data.get('base_speed', 100)
        
        # Рост характеристик
        grow_atk = hero_data.get('grow_atk', 5)
        grow_hp = hero_data.get('grow_hp', 50)
        grow_armor = hero_data.get('grow_armor', 2.5)
        grow_speed = hero_data.get('grow_speed', 1)
        
        value = f"({hero_id}, {escape_sql_string(name)}, {quality}, {base_atk}, {base_hp}, {base_armor}, {base_speed}, {grow_atk}, {grow_hp}, {grow_armor}, {grow_speed})"
        values.append(value)
    
    inserts.append(",\n".join(values))
    inserts.append("ON CONFLICT (hero_id) DO NOTHING;")
    inserts.append("")
    
    return inserts


def generate_item_imports():
    """Генерация INSERT для всех предметов"""
    item_file = Path("data/game_configs/item.json")
    
    if not item_file.exists():
        print(f"❌ Файл {item_file} не найден")
        return []
    
    with open(item_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    inserts = []
    inserts.append("-- Импорт всех предметов из игры")
    inserts.append("INSERT INTO item_data (item_id, name, item_type, quality, stack_size, value) VALUES")
    
    values = []
    for item_id, item_data in items.items():
        name = item_data.get('name', f'Item_{item_id}')
        item_type = item_data.get('type', 'material')
        quality = item_data.get('quality', 1)
        stack_size = item_data.get('stack_size', 1)
        value = item_data.get('value', 100)
        
        value_str = f"({item_id}, {escape_sql_string(name)}, {escape_sql_string(item_type)}, {quality}, {stack_size}, {value})"
        values.append(value_str)
    
    inserts.append(",\n".join(values))
    inserts.append("ON CONFLICT (item_id) DO NOTHING;")
    inserts.append("")
    
    return inserts


def generate_import_sql():
    """Генерация полного SQL файла импорта"""
    
    print("🔄 Генерация SQL для импорта игровых данных...")
    print("=" * 80)
    
    sql_lines = []
    
    # Заголовок
    sql_lines.append("-- Автоматически сгенерированный SQL для импорта игровых данных")
    sql_lines.append("-- Idle Heroes 1.34.4")
    sql_lines.append("-- Сгенерировано: " + str(Path(__file__).stat().st_mtime))
    sql_lines.append("")
    sql_lines.append("SET client_encoding = 'UTF8';")
    sql_lines.append("SET standard_conforming_strings = on;")
    sql_lines.append("")
    
    # Импорт героев
    print("📦 Импорт героев...")
    hero_inserts = generate_hero_imports()
    if hero_inserts:
        sql_lines.extend(hero_inserts)
        print(f"✅ Героев: {len([l for l in hero_inserts if l.startswith('(')])} записей")
    
    # Импорт предметов
    print("📦 Импорт предметов...")
    item_inserts = generate_item_imports()
    if item_inserts:
        sql_lines.extend(item_inserts)
        print(f"✅ Предметов: {len([l for l in item_inserts if l.startswith('(')])} записей")
    
    # Тестовые данные
    sql_lines.append("-- Тестовые пользователи")
    sql_lines.append("INSERT INTO users (username, password_hash, email) VALUES")
    sql_lines.append("('test', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.hsEqFTqHqUbe', 'test@test.com'),")
    sql_lines.append("('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.hsEqFTqHqUbe', 'admin@test.com')")
    sql_lines.append("ON CONFLICT (username) DO NOTHING;")
    sql_lines.append("")
    
    # Добавляем героев тестовому пользователю
    sql_lines.append("-- Тестовые герои для пользователя test")
    sql_lines.append("INSERT INTO user_heroes (user_id, hero_id, level, star) ")
    sql_lines.append("SELECT 1, hero_id, 1, 1 FROM hero_data WHERE hero_id IN (1001, 1002, 1003, 1004, 1005)")
    sql_lines.append("ON CONFLICT DO NOTHING;")
    sql_lines.append("")
    
    # Добавляем предметы тестовому пользователю
    sql_lines.append("-- Тестовые предметы для пользователя test")
    sql_lines.append("INSERT INTO user_inventory (user_id, item_id, quantity) ")
    sql_lines.append("SELECT 1, item_id, 10 FROM item_data WHERE item_id IN (2001, 2002, 2003, 2004, 2005)")
    sql_lines.append("ON CONFLICT DO NOTHING;")
    sql_lines.append("")
    
    # Статистика
    sql_lines.append("-- Статистика импорта")
    sql_lines.append("SELECT 'Импорт завершен!' AS status;")
    sql_lines.append("SELECT COUNT(*) AS hero_count FROM hero_data;")
    sql_lines.append("SELECT COUNT(*) AS item_count FROM item_data;")
    sql_lines.append("SELECT COUNT(*) AS user_count FROM users;")
    
    # Сохраняем в файл
    output_file = Path("network/import_game_data.sql")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print("=" * 80)
    print(f"✅ SQL файл сохранен: {output_file}")
    print(f"📊 Размер файла: {output_file.stat().st_size / 1024:.2f} KB")
    print()
    print("🚀 Для импорта запустите:")
    print("   docker-compose up -d")
    print()


if __name__ == "__main__":
    generate_import_sql()
