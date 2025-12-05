#!/usr/bin/env python3
"""
Продвинутый декомпилятор Lua 5.1
Восстанавливает читаемый исходный код
"""

import struct
from pathlib import Path
from typing import List, Dict, Any

class LuaDecompiler:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        
    def read_byte(self):
        b = self.data[self.pos]
        self.pos += 1
        return b
    
    def read_int(self):
        val = struct.unpack('<I', self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return val
    
    def read_number(self):
        val = struct.unpack('<d', self.data[self.pos:self.pos+8])[0]
        self.pos += 8
        return val
    
    def read_string(self):
        size = self.read_int()
        if size == 0:
            return ""
        s = self.data[self.pos:self.pos+size-1].decode('utf-8', errors='replace')
        self.pos += size
        return s
    
    def decompile(self):
        # Пропускаем заголовок
        self.pos = 12
        return self.read_function(0)
    
    def read_function(self, level):
        indent = "  " * level
        
        # Source name
        source = self.read_string()
        
        # Line info
        line_defined = self.read_int()
        last_line_defined = self.read_int()
        
        # Function info
        num_upvalues = self.read_byte()
        num_params = self.read_byte()
        is_vararg = self.read_byte()
        max_stack_size = self.read_byte()
        
        # Code
        num_instructions = self.read_int()
        instructions = []
        for i in range(num_instructions):
            inst = self.read_int()
            instructions.append(self.decode_instruction(inst))
        
        # Constants
        num_constants = self.read_int()
        constants = []
        for i in range(num_constants):
            const_type = self.read_byte()
            
            if const_type == 0:  # nil
                constants.append(None)
            elif const_type == 1:  # boolean
                val = self.read_byte()
                constants.append(bool(val))
            elif const_type == 3:  # number
                val = self.read_number()
                constants.append(val)
            elif const_type == 4:  # string
                val = self.read_string()
                constants.append(val)
        
        # Prototypes
        num_protos = self.read_int()
        protos = []
        for i in range(num_protos):
            protos.append(self.read_function(level + 1))
        
        # Line info (debug)
        num_lines = self.read_int()
        for i in range(num_lines):
            self.read_int()
        
        # Locals (debug)
        num_locals = self.read_int()
        locals_info = []
        for i in range(num_locals):
            name = self.read_string()
            startpc = self.read_int()
            endpc = self.read_int()
            locals_info.append((name, startpc, endpc))
        
        # Upvalues (debug)
        num_upvalue_names = self.read_int()
        for i in range(num_upvalue_names):
            self.read_string()
        
        # Генерируем код
        return self.generate_lua_code(instructions, constants, protos, locals_info, num_params, is_vararg, indent)
    
    def decode_instruction(self, inst):
        opcode = inst & 0x3F
        a = (inst >> 6) & 0xFF
        c = (inst >> 14) & 0x1FF
        b = (inst >> 23) & 0x1FF
        bx = (inst >> 14) & 0x3FFFF
        sbx = bx - 131071
        
        return {
            'opcode': opcode,
            'a': a,
            'b': b,
            'c': c,
            'bx': bx,
            'sbx': sbx
        }
    
    def generate_lua_code(self, instructions, constants, protos, locals_info, num_params, is_vararg, indent=""):
        """Генерация читаемого Lua кода из инструкций"""
        
        lines = []
        registers = {}  # Отслеживание значений в регистрах
        
        # Параметры функции
        if num_params > 0:
            params = [f"arg{i}" for i in range(num_params)]
            if is_vararg:
                params.append("...")
            lines.append(f"{indent}function({', '.join(params)})")
        
        for i, inst in enumerate(instructions):
            op = inst['opcode']
            a, b, c, bx, sbx = inst['a'], inst['b'], inst['c'], inst['bx'], inst['sbx']
            
            # MOVE - копирование регистра
            if op == 0:
                registers[a] = registers.get(b, f"R{b}")
            
            # LOADK - загрузка константы
            elif op == 1:
                if bx < len(constants):
                    const = constants[bx]
                    if isinstance(const, str):
                        registers[a] = f'"{const}"'
                        lines.append(f'{indent}local var{a} = "{const}"')
                    elif isinstance(const, (int, float)):
                        registers[a] = str(const)
                        lines.append(f'{indent}local var{a} = {const}')
                    elif const is None:
                        registers[a] = "nil"
                        lines.append(f'{indent}local var{a} = nil')
            
            # LOADBOOL - загрузка boolean
            elif op == 2:
                registers[a] = "true" if b != 0 else "false"
                lines.append(f'{indent}local var{a} = {registers[a]}')
            
            # LOADNIL - загрузка nil
            elif op == 3:
                for r in range(a, b + 1):
                    registers[r] = "nil"
                lines.append(f'{indent}local var{a} = nil')
            
            # GETGLOBAL - получение глобальной переменной
            elif op == 5:
                if bx < len(constants):
                    name = constants[bx]
                    registers[a] = name
                    lines.append(f'{indent}local var{a} = {name}')
            
            # SETGLOBAL - установка глобальной переменной
            elif op == 7:
                if bx < len(constants):
                    name = constants[bx]
                    value = registers.get(a, f"var{a}")
                    lines.append(f'{indent}{name} = {value}')
            
            # NEWTABLE - создание таблицы
            elif op == 10:
                registers[a] = "{}"
                lines.append(f'{indent}local var{a} = {{}}')
            
            # SETTABLE - установка значения в таблицу
            elif op == 9:
                table = registers.get(a, f"var{a}")
                key = self.get_rk_value(b, registers, constants)
                value = self.get_rk_value(c, registers, constants)
                lines.append(f'{indent}{table}[{key}] = {value}')
            
            # GETTABLE - получение значения из таблицы
            elif op == 6:
                table = registers.get(b, f"var{b}")
                key = self.get_rk_value(c, registers, constants)
                registers[a] = f"{table}[{key}]"
                lines.append(f'{indent}local var{a} = {table}[{key}]')
            
            # CALL - вызов функции
            elif op == 28:
                func = registers.get(a, f"var{a}")
                args = []
                if b > 1:
                    for j in range(1, b):
                        args.append(registers.get(a + j, f"var{a + j}"))
                
                call_str = f"{func}({', '.join(args)})"
                
                if c > 1:  # Есть возвращаемые значения
                    lines.append(f'{indent}local var{a} = {call_str}')
                    registers[a] = call_str
                else:
                    lines.append(f'{indent}{call_str}')
            
            # RETURN - возврат значений
            elif op == 30:
                if b == 0:
                    lines.append(f'{indent}return')
                elif b == 1:
                    lines.append(f'{indent}return')
                elif b == 2:
                    value = registers.get(a, f"var{a}")
                    lines.append(f'{indent}return {value}')
                else:
                    values = [registers.get(a + j, f"var{a + j}") for j in range(b - 1)]
                    lines.append(f'{indent}return {", ".join(values)}')
        
        if num_params > 0:
            lines.append(f"{indent}end")
        
        # Если ничего не сгенерировали, показываем константы
        if not lines or len(lines) <= 2:
            lines = []
            lines.append(f"{indent}-- Constants:")
            for i, const in enumerate(constants):
                if isinstance(const, str):
                    lines.append(f'{indent}-- [{i}] "{const}"')
                else:
                    lines.append(f'{indent}-- [{i}] {const}')
            
            if protos:
                lines.append(f"{indent}-- {len(protos)} nested functions")
        
        # Добавляем вложенные функции
        for i, proto in enumerate(protos):
            lines.append(f"\n{indent}-- Nested function {i}:")
            lines.append(proto)
        
        return '\n'.join(lines)
    
    def get_rk_value(self, rk, registers, constants):
        """Получить значение RK (регистр или константа)"""
        if rk & 0x100:  # Это константа
            k = rk & 0xFF
            if k < len(constants):
                const = constants[k]
                if isinstance(const, str):
                    return f'"{const}"'
                return str(const)
            return f"K{k}"
        else:  # Это регистр
            return registers.get(rk, f"var{rk}")

def decompile_file(filepath):
    """Декомпиляция файла"""
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    if not data.startswith(b'\x1bLua'):
        return None, "Not Lua bytecode"
    
    try:
        decompiler = LuaDecompiler(data)
        code = decompiler.decompile()
        return code, "OK"
    except Exception as e:
        import traceback
        return None, traceback.format_exc()

def main():
    print("=" * 80)
    print("🔥 ПРОДВИНУТЫЙ ДЕКОМПИЛЯТОР LUA 5.1")
    print("=" * 80)
    print()
    
    # Тест
    test_files = [
        "decrypted_lua_FINAL/version.lua",
        "decrypted_lua_FINAL/app/config/hero.lua",
    ]
    
    for test_file in test_files:
        filepath = Path(test_file)
        
        if not filepath.exists():
            print(f"❌ Файл не найден: {filepath}")
            continue
        
        print(f"📁 Декомпиляция: {filepath.name}")
        print("-" * 80)
        
        code, status = decompile_file(filepath)
        
        if code:
            print(code[:500])  # Первые 500 символов
            print("\n...")
            print("-" * 80)
            print("✅ Успешно!")
        else:
            print(f"❌ Ошибка: {status[:200]}")
        
        print()

if __name__ == "__main__":
    main()
