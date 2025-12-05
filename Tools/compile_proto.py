#!/usr/bin/env python3
"""
Компиляция Protobuf схем в Python
"""

import subprocess
from pathlib import Path

def compile_proto_files():
    print("=" * 80)
    print("🔧 КОМПИЛЯЦИЯ PROTOBUF СХЕМ")
    print("=" * 80)
    print()
    
    proto_dir = Path("private-server/proto")
    output_dir = Path("private-server/src/protocol")
    
    # Создаем выходную директорию
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем __init__.py
    init_file = output_dir / "__init__.py"
    init_file.write_text("# Protocol Buffers generated code\n")
    
    proto_files = list(proto_dir.glob("*.proto"))
    
    if not proto_files:
        print("❌ .proto файлы не найдены!")
        return
    
    print(f"📁 Найдено .proto файлов: {len(proto_files)}")
    print()
    
    success = 0
    failed = 0
    
    for proto_file in proto_files:
        print(f"🔧 Компиляция: {proto_file.name}")
        
        try:
            # Используем grpc_tools.protoc
            import sys
            result = subprocess.run(
                [
                    sys.executable, "-m", "grpc_tools.protoc",
                    f"-I{proto_dir}",
                    f"--python_out={output_dir}",
                    str(proto_file)
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                output_file = output_dir / f"{proto_file.stem}_pb2.py"
                print(f"   ✅ Создан: {output_file.name}")
                success += 1
            else:
                print(f"   ❌ Ошибка: {result.stderr[:100]}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Исключение: {str(e)[:100]}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print(f"✅ Успешно: {success}")
    print(f"❌ Ошибок: {failed}")
    print("=" * 80)
    
    if success > 0:
        print("\n🎉 КОМПИЛЯЦИЯ ЗАВЕРШЕНА!")
        print(f"\nСгенерированные файлы в: {output_dir}")
        print("\nМожно использовать:")
        print("  from protocol import dr2_comm_pb2")
        print("  from protocol import dr2_logic_pb2")

if __name__ == "__main__":
    compile_proto_files()
