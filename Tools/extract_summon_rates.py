#!/usr/bin/env python3
"""
Извлечение шансов призыва героев из gacha файлов
"""

import json
from pathlib import Path
from extract_protobuf_schema import extract_constants_from_lua


def analyze_gacha_file(filepath: Path):
    """Анализ файла gacha"""
    
    print(f"\n📁 Анализ: {filepath.name}")
    print("-" * 80)
    
    constants = extract_constants_from_lua(filepath)
    
    rates = []
    pools = {}
    current_pool = None
    
    for i, const in enumerate(constants):
        # Ищем ID пула
        if isinstance(const, (int, float)) and 1000 <= const < 100000:
            current_pool = int(const)
            if current_pool not in pools:
                pools[current_pool] = {
                    'id': current_pool,
                    'rates': [],
                    'heroes': []
                }
        
        # Ищем ключевые слова для вероятностей
        if isinstance(const, str):
            keywords = ['rate', 'weight', 'prob', 'chance', 'percent']
            if any(kw in const.lower() for kw in keywords):
                # Следующее значение может быть вероятностью
                if i + 1 < len(constants):
                    next_val = constants[i + 1]
                    if isinstance(next_val, (int, float)):
                        rate_info = {
                            'type': const,
                            'value': next_val,
                            'pool': current_pool
                        }
                        rates.append(rate_info)
                        
                        if current_pool and current_pool in pools:
                            pools[current_pool]['rates'].append(rate_info)
        
        # Ищем проценты (числа от 0.001 до 100)
        if isinstance(const, (int, float)) and 0.001 <= const <= 100:
            # Проверяем контекст
            context = []
            for j in range(max(0, i-2), min(len(constants), i+3)):
                if constants[j] is not None:
                    context.append(str(constants[j]))
            
            # Если это похоже на процент
            if any(str(c).replace('.', '').isdigit() for c in context):
                rate_info = {
                    'value': const,
                    'context': context,
                    'pool': current_pool
                }
                rates.append(rate_info)
    
    return rates, pools


def main():
    print("=" * 80)
    print("🎲 ИЗВЛЕЧЕНИЕ ШАНСОВ ПРИЗЫВА ГЕРОЕВ")
    print("=" * 80)
    
    lua_dir = Path("decrypted_lua_FINAL")
    
    # Файлы gacha
    gacha_files = [
        lua_dir / "app/config/collectgacha.lua",
        lua_dir / "app/config/showgacha.lua",
        lua_dir / "app/config/spacegacha.lua",
    ]
    
    all_rates = {}
    all_pools = {}
    
    for gacha_file in gacha_files:
        if not gacha_file.exists():
            print(f"⚠️ Файл не найден: {gacha_file.name}")
            continue
        
        rates, pools = analyze_gacha_file(gacha_file)
        
        all_rates[gacha_file.name] = rates
        all_pools[gacha_file.name] = pools
        
        print(f"Найдено вероятностей: {len(rates)}")
        print(f"Найдено пулов: {len(pools)}")
        
        # Показываем примеры
        if rates:
            print("\nПримеры вероятностей:")
            for rate in rates[:10]:
                if 'type' in rate:
                    print(f"  {rate['type']}: {rate['value']} (пул: {rate.get('pool', 'N/A')})")
                else:
                    print(f"  {rate['value']}% - {rate.get('context', [])[:3]}")
    
    # Анализ hero.json для редкости
    print("\n\n📊 АНАЛИЗ РЕДКОСТИ ГЕРОЕВ")
    print("=" * 80)
    
    hero_file = Path("private-server/data/game_configs/hero.json")
    if hero_file.exists():
        with open(hero_file, 'r', encoding='utf-8') as f:
            heroes = json.load(f)
        
        # Группируем по редкости
        rarity_groups = {}
        for hero_id, hero_data in heroes.items():
            qlt = hero_data.get('qlt', 0)
            if qlt not in rarity_groups:
                rarity_groups[qlt] = []
            rarity_groups[qlt].append(hero_id)
        
        print("\nРаспределение героев по редкости:")
        for qlt in sorted(rarity_groups.keys()):
            count = len(rarity_groups[qlt])
            print(f"  Качество {qlt}: {count} героев")
        
        # Типичные шансы по редкости (из опыта с gacha играми)
        typical_rates = {
            1: "Common (обычный): ~60-70%",
            2: "Uncommon (необычный): ~20-25%",
            3: "Rare (редкий): ~8-12%",
            4: "Epic (эпический): ~3-5%",
            5: "Legendary (легендарный): ~1-2%"
        }
        
        print("\nТипичные шансы призыва (стандарт для gacha):")
        for qlt, desc in typical_rates.items():
            if qlt in rarity_groups:
                print(f"  {desc}")
    
    # Сохраняем результаты
    output_file = Path("private-server/data/summon_rates.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    result = {
        'gacha_files': all_rates,
        'pools': all_pools,
        'rarity_distribution': {
            str(qlt): len(heroes) 
            for qlt, heroes in rarity_groups.items()
        } if hero_file.exists() else {}
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("\n\n" + "=" * 80)
    print("✅ АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 80)
    print(f"\n📁 Результаты сохранены: {output_file}")
    
    # Итоговая статистика
    total_rates = sum(len(rates) for rates in all_rates.values())
    total_pools = sum(len(pools) for pools in all_pools.values())
    
    print(f"\n📊 Статистика:")
    print(f"  Всего вероятностей найдено: {total_rates}")
    print(f"  Всего пулов призыва: {total_pools}")
    print(f"  Файлов проанализировано: {len(gacha_files)}")
    
    print("\n💡 Рекомендации:")
    print("  1. Проверьте summon_rates.json для деталей")
    print("  2. Типичные шансы gacha игр применимы")
    print("  3. Можно настроить свои шансы для приватного сервера")


if __name__ == "__main__":
    main()
