import sys
import argparse
import json

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def mask(n):
    """Возвращает маску из n единиц (2^n - 1).""" # идея из файла преподавателя: создание битовой маски
    return (1 << n) - 1


# --- МОДЕЛЬ ВИРТУАЛЬНОЙ МАШИНЫ ---

MEMORY_SIZE = 1024
INITIAL_MEMORY_VALUE = 0

class UVM:
    """
    Модель виртуальной машины.
    Объединённая память для данных. Использует стек для операций.
    """ # идея из файла преподавателя: модель состояния (вместо глобальных переменных reg, mem)
    def __init__(self, memory_size=MEMORY_SIZE):
        self.memory = [INITIAL_MEMORY_VALUE] * memory_size
        self.stack = [] # идея из файла преподавателя: стек для операций (вместо reg)

    def push(self, value):
        self.stack.append(value) # идея из файла преподавателя: операции со стеком/регистром

    def pop(self):
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop() # идея из файла преподавателя: операции со стеком/регистром

    def read_memory(self, address):
        if 0 <= address < len(self.memory):
            return self.memory[address] # идея из файла преподавателя: операции с памятью
        else:
            print(f"Warning: Reading from out-of-bounds address {address}")
            return 0

    def write_memory(self, address, value):
        if 0 <= address < len(self.memory):
            self.memory[address] = value # идея из файла преподавателя: операции с памятью
        else:
            print(f"Error: Writing to out-of-bounds address {address}")


# --- ВЫПОЛНЕНИЕ БАЙТКОДА ---

def execute(bytecode, vm_instance): # идея из файла преподавателя: функция execute
    """
    Выполняет байткод на виртуальной машине.
    """
    pc = 0 # идея из файла преподавателя: счётчик команд
    print("Starting interpretation loop...")

    while pc < len(bytecode): # идея из файла преподавателя: цикл по байткоду
        # --- ЧТЕНИЕ КОМАНДЫ ---
        if pc + 2 >= len(bytecode):
            print(f"Warning: Reached end of bytecode at PC {pc}, stopping.")
            break

        cmd_bytes = bytecode[pc:pc+3] # идея из файла преподавателя: чтение байтов команды
        cmd_int = int.from_bytes(cmd_bytes, 'little') # идея из файла преподавателя: преобразование байтов в int

        # --- ИЗВЛЕЧЕНИЕ ПОЛЕЙ КОМАНДЫ (A и B) ---
        # Вариант 20: A (биты 0-3), B (биты 4-21 для load/gt, 4-9 для read)
        A_OPCODE = cmd_int & mask(4) # идея из файла преподавателя: извлечение битов с помощью маски и &
        # B_VALUE используется для load (18 бит) и gt (6 бит)
        B_VALUE = (cmd_int >> 4) & mask(18) # идея из файла преподавателя: сдвиг и извлечение битов
        # B_OFFSET используется для read (6 бит) и gt (6 бит)
        B_OFFSET = (cmd_int >> 4) & mask(6) # идея из файла преподавателя: сдвиг и извлечение битов

        # --- ВЫПОЛНЕНИЕ КОМАНД ---
        # Вариант 20: A=1 (load), A=15 (read), A=3 (write), A=5 (gt)
        if A_OPCODE == 1: # load: A=1, B=const_val (18 бит)
            const_val = B_VALUE
            vm_instance.push(const_val) # идея из файла преподавателя: операции с памятью/регистром/стеком
            print(f"PC: {pc}, Executed: load {const_val}. Stack: {vm_instance.stack}")
            pc += 3
        elif A_OPCODE == 15: # read: A=15, B=offset_val (6 бит)
            offset_val = B_OFFSET
            addr = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            effective_addr = addr + offset_val
            value = vm_instance.read_memory(effective_addr) # идея из файла преподавателя: операции с памятью/регистром/стеком
            vm_instance.push(value) # идея из файла преподавателя: операции с памятью/регистром/стеком
            print(f"PC: {pc}, Executed: read {offset_val}. Address: {addr}, Offset: {offset_val}, Effective: {effective_addr}, Value: {value}. Stack: {vm_instance.stack}")
            pc += 3
        elif A_OPCODE == 3: # write: A=3
            value = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            addr = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            vm_instance.write_memory(addr, value) # идея из файла преподавателя: операции с памятью/регистром/стеком
            print(f"PC: {pc}, Executed: write. Address: {addr}, Value: {value}. Stack: {vm_instance.stack}")
            pc += 3
        elif A_OPCODE == 5: # gt: A=5, B=offset_val (6 бит) - Реализуем для полноты спецификации, хотя Этап 3 требует load, read, write
            # Согласно спецификации: val1 (снятый первым), val2 (снятый вторым), addr (снятый третьим)
            # Результат (1 или 0) записывается в mem[addr + offset_val]
            offset_val = B_OFFSET
            val1 = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            val2 = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            addr = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            effective_addr = addr + offset_val
            result = 1 if val2 > val1 else 0 # идея из файла преподавателя: операции с памятью/регистром/стеком
            vm_instance.write_memory(effective_addr, result) # идея из файла преподавателя: операции с памятью/регистром/стеком
            print(f"PC: {pc}, Executed: gt {offset_val}. Val2: {val2}, Val1: {val1}, Addr: {addr}, Offset: {offset_val}, Effective: {effective_addr}, Result: {result}. Memory[{effective_addr}] = {result}. Stack: {vm_instance.stack}")
            pc += 3
        else:
            print(f"Error: Unknown opcode {A_OPCODE} at PC {pc}")
            break # Прерываем выполнение при ошибке

    print("Interpretation finished.")


# --- ТОЧКА ВХОДА (MAIN) ---

def main():
    parser = argparse.ArgumentParser(description="Interpreter for UVM Variant 20 (Stage 3).") # идея из файла преподавателя: CLI (хотя он читал файл напрямую)
    parser.add_argument("binary_file", help="Path to the binary file with assembled program (.bin)")
    parser.add_argument("dump_file", help="Path to the output file for memory dump (.json)")
    parser.add_argument("start_addr", type=int, help="Start address for memory dump range")
    parser.add_argument("end_addr", type=int, help="End address for memory dump range")

    args = parser.parse_args()

    # Проверка корректности диапазона
    if args.start_addr < 0 or args.end_addr < args.start_addr or args.end_addr >= MEMORY_SIZE:
        print(f"Error: Invalid memory range [{args.start_addr}, {args.end_addr}]. Must be 0 <= start <= end < {MEMORY_SIZE}.")
        sys.exit(1)

    print(f"Loading program from {args.binary_file}")
    try:
        with open(args.binary_file, 'rb') as f: # идея из файла преподавателя: чтение бинарного файла
            bytecode = f.read()
    except FileNotFoundError:
        print(f"Error: Binary file '{args.binary_file}' not found.")
        sys.exit(1)

    print(f"Initializing UVM memory (size: {MEMORY_SIZE}) and stack.")
    vm = UVM() # идея из файла преподавателя: инициализация состояния (вместо глобальных переменных)

    execute(bytecode, vm) # идея из файла преподавателя: вызов основной функции выполнения

    # Формирование дампа памяти в JSON # идея из файла преподавателя: вывод результата (хотя он просто печатал)
    print(f"Dumping memory from {args.start_addr} to {args.end_addr} to {args.dump_file}")
    memory_dump = {}
    for addr in range(args.start_addr, min(args.end_addr + 1, len(vm.memory))): # идея из файла преподавателя: цикл по памяти для дампа
        memory_dump[str(addr)] = vm.memory[addr]

    try:
        with open(args.dump_file, 'w', encoding='utf-8') as f:
            json.dump(memory_dump, f, indent=2, ensure_ascii=False)
        print(f"Memory dump saved to {args.dump_file}")
    except Exception as e:
        print(f"Error saving memory dump: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()