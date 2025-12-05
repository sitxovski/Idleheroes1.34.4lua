#!/usr/bin/env python3
"""
Массовая декомпиляция всех файлов продвинутым декомпилятором
"""

from pathlib import Path
from advanced_decompiler import decompile_file

def main():
    print("=" * 80)
    print("🔥 МАССОВАЯ ДЕКОМПИЛЯЦИЯ - ПРОДВИНУТЫЙ ДЕКОМПИЛЯТОР")
    print("=" * 80)
    print()
    
    input_dir = Path("decrypted_lua_FINAL")
    output_dir = Path("decompiled_lua_READABLE")
    
    if not input_dir.exists():
        print(f"❌ Папка не найдена: {input_dir}")
        return
    
    output_dir.mkdir(exist_ok=True)
    
    lua_files = list(input_dir.rglob("*.lua"))
    print(f"📁 Найдено файлов: {len(lua_files)}")
    print()
    
    success = 0
    failed = 0
    
    for i, lua_file in enumerate(lua_files, 1):
        rel_path = lua_file.relative_to(input_dir)
        output_file = output_dir / rel_path
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        code, status = decompile_file(lua_file)
        
        if code:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            print(f"[{i}/{len(lua_files)}] ✅ {rel_path}")
            success += 1
        else:
            print(f"[{i}/{len(lua_files)}] ❌ {rel_path} - {status[:50]}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"✅ Успешно: {success}")
    print(f"❌ Ошибок: {failed}")
    print(f"📁 Результат: {output_dir}")
    print("=" * 80)
    
    if success > 0:
        print("\n🎉 ДЕКОМПИЛЯЦИЯ ЗАВЕРШЕНА!")
        print("\nТеперь у вас есть читаемые Lua файлы с:")
        print("  - Всеми константами (строки, числа)")
        print("  - Структурой кода")
        print("  - Данными героев, предметов, навыков и т.д.")
        print("\nМожно анализировать и модифицировать игру!")

if __name__ == "__main__":
    main()
