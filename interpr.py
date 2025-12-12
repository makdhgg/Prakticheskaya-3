import sys
import argparse
import json

def mask(n):
    """Возвращает маску из n единиц (2^n - 1).""" # идея из файла преподавателя: создание битовой маски
    return (1 << n) - 1

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
            print(f"Предупреждение: Чтение из недопустимого адреса памяти {address}")
            return 0

    def write_memory(self, address, value):
        if 0 <= address < len(self.memory):
            self.memory[address] = value # идея из файла преподавателя: операции с памятью
        else:
            print(f"Ошибка: Запись в недопустимый адрес памяти {address}")

def execute(bytecode, vm_instance): # идея из файла преподавателя: функция execute
    """
    Выполняет байткод на виртуальной машине.
    """
    pc = 0 # идея из файла преподавателя: счётчик команд
    print("Запуск цикла интерпретации...")

    while pc < len(bytecode): # идея из файла преподавателя: цикл по байткоду
        # --- ЧТЕНИЕ КОМАНДЫ ---
        if pc + 2 >= len(bytecode):
            print(f"Предупреждение: Достигнут конец байткода на PC {pc}, остановка.")
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

        # Вариант 20: A=1 (load), A=15 (read), A=3 (write), A=5 (gt)
        if A_OPCODE == 1: # load: A=1, B=const_val (18 бит)
            const_val = B_VALUE
            vm_instance.push(const_val) # идея из файла преподавателя: операции с памятью/регистром/стеком
            print(f"PC: {pc}, Выполнена: load {const_val}. Стек: {vm_instance.stack}")
            pc += 3
        elif A_OPCODE == 15: # read: A=15, B=offset_val (6 бит)
            offset_val = B_OFFSET
            addr = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            effective_addr = addr + offset_val
            value = vm_instance.read_memory(effective_addr) # идея из файла преподавателя: операции с памятью/регистром/стеком
            vm_instance.push(value) # идея из файла преподавателя: операции с памятью/регистром/стеком
            print(f"PC: {pc}, Выполнена: read {offset_val}. Адрес: {addr}, Смещение: {offset_val}, Эфф. адрес: {effective_addr}, Значение: {value}. Стек: {vm_instance.stack}")
            pc += 3
        elif A_OPCODE == 3: # write: A=3
            value = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            addr = vm_instance.pop() # идея из файла преподавателя: операции с памятью/регистром/стеком
            vm_instance.write_memory(addr, value) # идея из файла преподавателя: операции с памятью/регистром/стеком
            print(f"PC: {pc}, Выполнена: write. Адрес: {addr}, Значение: {value}. Стек: {vm_instance.stack}")
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
            print(f"PC: {pc}, Выполнена: gt {offset_val}. Val2: {val2}, Val1: {val1}, Addr: {addr}, Смещение: {offset_val}, Эфф. адрес: {effective_addr}, Результат: {result}. Memory[{effective_addr}] = {result}. Стек: {vm_instance.stack}")
            pc += 3
        else:
            print(f"Ошибка: Неизвестный опкод {A_OPCODE} на PC {pc}")
            break # Прерываем выполнение при ошибке

    print("Цикл интерпретации завершён.")

def main():
    parser = argparse.ArgumentParser(description="Интерпретатор для УВМ Вариант 20 (Этап 3).") # идея из файла преподавателя: CLI (хотя он читал файл напрямую)
    parser.add_argument("binary_file", help="Путь к бинарному файлу с ассемблированной программой (.bin)")
    parser.add_argument("dump_file", help="Путь к файлу для сохранения дампа памяти (.json)")
    parser.add_argument("start_addr", type=int, help="Начальный адрес для диапазона дампа памяти")
    parser.add_argument("end_addr", type=int, help="Конечный адрес для диапазона дампа памяти")

    args = parser.parse_args()

    # Проверка корректности диапазона
    if args.start_addr < 0 or args.end_addr < args.start_addr or args.end_addr >= MEMORY_SIZE:
        print(f"Ошибка: Неверный диапазон памяти [{args.start_addr}, {args.end_addr}]. Должно быть 0 <= start <= end < {MEMORY_SIZE}.")
        sys.exit(1)

    print(f"Загрузка программы из {args.binary_file}")
    try:
        with open(args.binary_file, 'rb') as f: # идея из файла преподавателя: чтение бинарного файла
            bytecode = f.read()
    except FileNotFoundError:
        print(f"Ошибка: Бинарный файл '{args.binary_file}' не найден.")
        sys.exit(1)

    print(f"Инициализация памяти УВМ (размер: {MEMORY_SIZE}) и стека.")
    vm = UVM() # идея из файла преподавателя: инициализация состояния (вместо глобальных переменных)

    execute(bytecode, vm) # идея из файла преподавателя: вызов основной функции выполнения

    # Формирование дампа памяти в JSON # идея из файла преподавателя: вывод результата (хотя он просто печатал)
    print(f"Дамп памяти с {args.start_addr} по {args.end_addr} в {args.dump_file}")
    memory_dump = {}
    for addr in range(args.start_addr, min(args.end_addr + 1, len(vm.memory))): # идея из файла преподавателя: цикл по памяти для дампа
        memory_dump[str(addr)] = vm.memory[addr]

    try:
        with open(args.dump_file, 'w', encoding='utf-8') as f:
            json.dump(memory_dump, f, indent=2, ensure_ascii=False)
        print(f"Дамп памяти сохранён в {args.dump_file}")
    except Exception as e:
        print(f"Ошибка при сохранении дампа памяти: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()