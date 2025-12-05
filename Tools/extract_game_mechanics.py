#!/usr/bin/env python3
"""
Извлечение игровых механик и формул из Lua файлов
"""

import json
from pathlib import Path
from extract_protobuf_schema import extract_constants_from_lua


def analyze_damage_formulas(lua_dir: Path):
    """Анализ формул расчета урона"""
    
    print("🗡️ АНАЛИЗ ФОРМУЛ УРОНА")
    print("=" * 80)
    
    # Ищем файлы с боевой логикой
    fight_files = [
        lua_dir / "app" / "fight" / "fight.lua",
        lua_dir / "app" / "fight" / "damage.lua",
        lua_dir / "app" / "fight" / "skill.lua",
        lua_dir / "app" / "config" / "skill.lua",
    ]
    
    damage_data = {}
    
    for fight_file in fight_files:
        if not fight_file.exists():
            continue
        
        print(f"\n📁 Анализ: {fight_file.name}")
        print("-" * 80)
        
        constants = extract_constants_from_lua(fight_file)
        
        # Ищем ключевые слова для урона
        damage_keywords = ['damage', 'atk', 'attack', 'hurt', 'dmg', 'crit', 'armor', 'def']
        
        found_formulas = []
        for i, const in enumerate(constants):
            if isinstance(const, str) and any(kw in const.lower() for kw in damage_keywords):
                # Собираем контекст
                context = []
                for j in range(max(0, i-2), min(len(constants), i+3)):
                    if constants[j] is not None:
                        context.append(str(constants[j]))
                
                found_formulas.append({
                    'keyword': const,
                    'context': context
                })
        
        if found_formulas:
            print(f"Найдено формул: {len(found_formulas)}")
            for formula in found_formulas[:10]:  # Первые 10
                print(f"  - {formula['keyword']}: {formula['context'][:5]}")
            
            damage_data[fight_file.name] = found_formulas
    
    return damage_data


def analyze_summon_rates(lua_dir: Path):
    """Анализ шансов призыва героев"""
    
    print("\n\n🎲 АНАЛИЗ ШАНСОВ ПРИЗЫВА")
    print("=" * 80)
    
    # Ищем файлы с призывом
    summon_files = [
        lua_dir / "app" / "config" / "summon.lua",
        lua_dir / "app" / "config" / "gacha.lua",
        lua_dir / "app" / "config" / "heroic.lua",
        lua_dir / "app" / "config" / "prophet.lua",
    ]
    
    summon_data = {}
    
    for summon_file in summon_files:
        if not summon_file.exists():
            continue
        
        print(f"\n📁 Анализ: {summon_file.name}")
        print("-" * 80)
        
        constants = extract_constants_from_lua(summon_file)
        
        # Ищем проценты и вероятности
        rates = []
        for i, const in enumerate(constants):
            # Ищем числа от 0 до 100 (вероятности в процентах)
            if isinstance(const, (int, float)) and 0 < const <= 100:
                context = []
                # Собираем контекст
                for j in range(max(0, i-3), min(len(constants), i+2)):
                    if constants[j] is not None:
                        context.append(str(constants[j]))
                
                rates.append({
                    'rate': const,
                    'context': context
                })
            
            # Ищем ключевые слова
            if isinstance(const, str) and any(kw in const.lower() for kw in ['rate', 'chance', 'prob', 'weight']):
                if i + 1 < len(constants) and isinstance(constants[i + 1], (int, float)):
                    rates.append({
                        'type': const,
                        'value': constants[i + 1]
                    })
        
        if rates:
            print(f"Найдено вероятностей: {len(rates)}")
            for rate in rates[:15]:  # Первые 15
                if 'type' in rate:
                    print(f"  - {rate['type']}: {rate['value']}")
                else:
                    print(f"  - {rate['rate']}%: {rate['context'][:3]}")
            
            summon_data[summon_file.name] = rates
    
    return summon_data


def analyze_hero_stats(lua_dir: Path):
    """Анализ характеристик героев и формул роста"""
    
    print("\n\n📈 АНАЛИЗ ХАРАКТЕРИСТИК ГЕРОЕВ")
    print("=" * 80)
    
    hero_file = lua_dir / "app" / "config" / "hero.lua"
    
    if not hero_file.exists():
        print("❌ Файл hero.lua не найден")
        return {}
    
    constants = extract_constants_from_lua(hero_file)
    
    # Ищем характеристики
    stat_keywords = ['baseAtk', 'baseHp', 'baseArm', 'baseSpd', 'growAtk', 'growHp', 'growArm', 'growSpd']
    
    hero_stats = {}
    current_hero_id = None
    current_stats = {}
    
    for i, const in enumerate(constants):
        # Ищем ID героя (обычно большие числа)
        if isinstance(const, (int, float)) and 1000 <= const < 10000:
            if current_hero_id and current_stats:
                hero_stats[current_hero_id] = current_stats
            current_hero_id = int(const)
            current_stats = {'id': current_hero_id}
        
        # Ищем характеристики
        if isinstance(const, str) and const in stat_keywords:
            if i + 1 < len(constants) and isinstance(constants[i + 1], (int, float)):
                current_stats[const] = constants[i + 1]
        
        # Ищем имя
        if isinstance(const, str) and const == 'name':
            if i + 1 < len(constants) and isinstance(constants[i + 1], str):
                current_stats['name'] = constants[i + 1]
    
    # Добавляем последнего героя
    if current_hero_id and current_stats:
        hero_stats[current_hero_id] = current_stats
    
    print(f"Найдено героев с характеристиками: {len(hero_stats)}")
    
    # Показываем примеры
    print("\nПримеры героев:")
    for hero_id, stats in list(hero_stats.items())[:5]:
        print(f"\nГерой {hero_id}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    return hero_stats


def analyze_skill_mechanics(lua_dir: Path):
    """Анализ механик навыков"""
    
    print("\n\n⚔️ АНАЛИЗ МЕХАНИК НАВЫКОВ")
    print("=" * 80)
    
    skill_file = lua_dir / "app" / "config" / "skill.lua"
    
    if not skill_file.exists():
        print("❌ Файл skill.lua не найден")
        return {}
    
    constants = extract_constants_from_lua(skill_file)
    
    # Ищем типы навыков и эффекты
    skill_keywords = ['damage', 'heal', 'buff', 'debuff', 'stun', 'silence', 'dot', 'shield']
    
    skills = {}
    current_skill_id = None
    current_skill = {}
    
    for i, const in enumerate(constants):
        # ID навыка
        if isinstance(const, (int, float)) and 10000 <= const < 999999:
            if current_skill_id and current_skill:
                skills[current_skill_id] = current_skill
            current_skill_id = int(const)
            current_skill = {'id': current_skill_id}
        
        # Ищем эффекты
        if isinstance(const, str):
            for keyword in skill_keywords:
                if keyword in const.lower():
                    if i + 1 < len(constants):
                        current_skill[keyword] = constants[i + 1]
    
    if current_skill_id and current_skill:
        skills[current_skill_id] = current_skill
    
    print(f"Найдено навыков: {len(skills)}")
    
    # Показываем примеры
    print("\nПримеры навыков:")
    for skill_id, skill_data in list(skills.items())[:5]:
        print(f"\nНавык {skill_id}:")
        for key, value in skill_data.items():
            print(f"  {key}: {value}")
    
    return skills


def main():
    print("=" * 80)
    print("🎮 ИЗВЛЕЧЕНИЕ ИГРОВЫХ МЕХАНИК")
    print("=" * 80)
    print()
    
    lua_dir = Path("decrypted_lua_FINAL")
    
    if not lua_dir.exists():
        print("❌ Директория decrypted_lua_FINAL не найдена")
        return
    
    # Анализируем все механики
    results = {
        'damage_formulas': analyze_damage_formulas(lua_dir),
        'summon_rates': analyze_summon_rates(lua_dir),
        'hero_stats': analyze_hero_stats(lua_dir),
        'skill_mechanics': analyze_skill_mechanics(lua_dir)
    }
    
    # Сохраняем результаты
    output_file = Path("private-server/data/game_mechanics.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n\n" + "=" * 80)
    print("✅ АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 80)
    print(f"\n📁 Результаты сохранены: {output_file}")
    print("\n💡 Теперь у вас есть:")
    print("  - Формулы расчета урона")
    print("  - Шансы призыва героев")
    print("  - Характеристики героев")
    print("  - Механики навыков")


if __name__ == "__main__":
    main()
