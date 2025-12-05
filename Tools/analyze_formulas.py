#!/usr/bin/env python3
"""
Детальный анализ формул и механик
"""

import json
from pathlib import Path

def analyze_game_mechanics():
    """Анализ извлеченных механик"""
    
    print("=" * 80)
    print("📊 ДЕТАЛЬНЫЙ АНАЛИЗ ИГРОВЫХ МЕХАНИК")
    print("=" * 80)
    print()
    
    mechanics_file = Path("private-server/data/game_mechanics.json")
    
    if not mechanics_file.exists():
        print("❌ Файл game_mechanics.json не найден")
        return
    
    with open(mechanics_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Анализ формул урона
    print("🗡️ ФОРМУЛЫ УРОНА")
    print("=" * 80)
    
    damage_formulas = data.get('damage_formulas', {})
    for file_name, formulas in damage_formulas.items():
        print(f"\n📁 {file_name}")
        print("-" * 80)
        
        # Группируем по типам
        formula_types = {}
        for formula in formulas:
            keyword = formula['keyword']
            if keyword not in formula_types:
                formula_types[keyword] = []
            formula_types[keyword].append(formula)
        
        print(f"Найдено типов формул: {len(formula_types)}")
        
        # Показываем ключевые формулы
        key_formulas = ['hurt', 'damage', 'atk', 'crit', 'armor', 'def']
        for key in key_formulas:
            if key in formula_types:
                print(f"\n{key.upper()}:")
                for f in formula_types[key][:3]:
                    print(f"  Context: {' → '.join(f['context'][:5])}")
    
    # Анализ шансов призыва
    print("\n\n🎲 ШАНСЫ ПРИЗЫВА")
    print("=" * 80)
    
    summon_rates = data.get('summon_rates', {})
    if summon_rates:
        for file_name, rates in summon_rates.items():
            print(f"\n📁 {file_name}")
            print("-" * 80)
            
            # Группируем по значениям
            rate_groups = {}
            for rate in rates:
                if 'type' in rate:
                    print(f"  {rate['type']}: {rate['value']}")
                elif 'rate' in rate:
                    r = rate['rate']
                    if r not in rate_groups:
                        rate_groups[r] = []
                    rate_groups[r].append(rate)
            
            if rate_groups:
                print("\nРаспределение вероятностей:")
                for r in sorted(rate_groups.keys()):
                    print(f"  {r}%: {len(rate_groups[r])} случаев")
    else:
        print("⚠️ Данные о призыве не найдены в стандартных файлах")
        print("💡 Попробуем найти в других конфигах...")
    
    # Анализ характеристик героев
    print("\n\n📈 ХАРАКТЕРИСТИКИ ГЕРОЕВ")
    print("=" * 80)
    
    hero_stats = data.get('hero_stats', {})
    print(f"Всего героев: {len(hero_stats)}")
    
    # Статистика по характеристикам
    stat_counts = {}
    for hero_id, stats in hero_stats.items():
        for stat_name in stats.keys():
            if stat_name not in stat_counts:
                stat_counts[stat_name] = 0
            stat_counts[stat_name] += 1
    
    print("\nНайденные характеристики:")
    for stat_name, count in sorted(stat_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {stat_name}: {count} героев")
    
    # Анализ механик навыков
    print("\n\n⚔️ МЕХАНИКИ НАВЫКОВ")
    print("=" * 80)
    
    skills = data.get('skill_mechanics', {})
    print(f"Всего навыков: {len(skills)}")
    
    # Типы эффектов
    effect_counts = {}
    for skill_id, skill_data in skills.items():
        for effect_name in skill_data.keys():
            if effect_name != 'id':
                if effect_name not in effect_counts:
                    effect_counts[effect_name] = 0
                effect_counts[effect_name] += 1
    
    if effect_counts:
        print("\nТипы эффектов:")
        for effect, count in sorted(effect_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {effect}: {count} навыков")
    
    # Создаем сводку
    print("\n\n" + "=" * 80)
    print("📋 СВОДКА")
    print("=" * 80)
    
    summary = {
        'total_damage_formulas': sum(len(f) for f in damage_formulas.values()),
        'total_heroes': len(hero_stats),
        'total_skills': len(skills),
        'hero_stats_types': len(stat_counts),
        'skill_effect_types': len(effect_counts)
    }
    
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Сохраняем сводку
    summary_file = Path("private-server/data/mechanics_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Сводка сохранена: {summary_file}")
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("  1. Формулы урона найдены - можно реализовать боевую систему")
    print("  2. Характеристики героев извлечены - можно создать систему героев")
    print("  3. Механики навыков доступны - можно реализовать систему навыков")
    print("  4. Для шансов призыва - проверьте файлы gacha/summon в декомпилированных данных")


if __name__ == "__main__":
    analyze_game_mechanics()
