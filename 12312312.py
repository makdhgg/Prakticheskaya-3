import csv
import sys
import argparse

def mask(n):
    """Возвращает маску из n единиц (2^n - 1)."""
    return (1 << n) - 1  # идея из файла преподавателя: создание битовой маски

def encode_load(const_val: int) -> int:
    """
    Загрузка константы.
    A (4 бита, 0-3) = 1
    B (18 бит, 4-21) = const_val
    Размер: 3 байта.
    """
    A_OPCODE = 1
    OPCODE_BITS = 4
    CONST_BITS = 18
    MAX_CONST = mask(CONST_BITS)

    if not (0 <= const_val <= MAX_CONST):
        raise ValueError(f"Constant value {const_val} out of range for {CONST_BITS}-bit field (max {MAX_CONST})")

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A
    cmd_int |= ((const_val & mask(CONST_BITS)) << OPCODE_BITS)  # идея из файла преподавателя: сдвиг и установка битов B

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


def encode_read(offset_val: int) -> int:

    A_OPCODE = 15
    OPCODE_BITS = 4
    OFFSET_BITS = 6
    MAX_OFFSET = mask(OFFSET_BITS)

    if not (0 <= offset_val <= MAX_OFFSET):
        raise ValueError(f"Offset value {offset_val} out of range for {OFFSET_BITS}-bit field (max {MAX_OFFSET})")

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A
    cmd_int |= ((offset_val & mask(
        OFFSET_BITS)) << OPCODE_BITS)  # идея из файла преподавателя: сдвиг и установка битов B

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


def encode_write() -> int:

    A_OPCODE = 3
    OPCODE_BITS = 4

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


def encode_gt(offset_val: int) -> int:

    A_OPCODE = 5
    OPCODE_BITS = 4
    OFFSET_BITS = 6
    MAX_OFFSET = mask(OFFSET_BITS)

    if not (0 <= offset_val <= MAX_OFFSET):
        raise ValueError(f"Offset value {offset_val} out of range for {OFFSET_BITS}-bit field (max {MAX_OFFSET})")

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A
    cmd_int |= ((offset_val & mask(
        OFFSET_BITS)) << OPCODE_BITS)  # идея из файла преподавателя: сдвиг и установка битов B

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


# --- АССЕМБЛЕР (Этап 1) ---

def parse_csv_row(row):
    """Парсит одну строку CSV."""
    if not row or not any(field.strip() for field in row):  # Пропускаем пустые строки
        return None

    op = row[0].strip().lower()
    args = []
    try:
        for arg in row[1:]:
            if arg.strip():  # Пропускаем пустые аргументы
                args.append(int(arg.strip()))
    except ValueError:
        raise ValueError(f"Invalid argument format in row: {row}")

    return {"op": op, "args": args}


def assemble_from_csv(csv_filename: str):
    """
    Транслирует CSV файл с ассемблерным кодом в промежуточное представление.
    """
    intermediate_repr = []
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader, start=1):
            try:
                parsed_instr = parse_csv_row(row)
                if parsed_instr:  # Пропускаем пустые строки
                    intermediate_repr.append(
                        parsed_instr)  # идея из файла преподавателя: формирование списка команд (хотя там YAML -> список)
            except ValueError as e:
                print(f"Error parsing CSV file at line {i}: {e}")
                raise  # Прерываем с ошибкой

    return intermediate_repr  # идея из файла преподавателя: возврат внутреннего представления программы


# --- ТЕСТИРОВАНИЕ И ВЫВОД (Этап 1) ---

def run_tests():
    """Проверяет правильность кодирования команд по тестовым векторам."""
    print("--- Запуск тестов ---")  # Переведено
    try:
        # Тесты из спецификации
        test_load_int = encode_load(267)
        expected_load_bytes = bytes([0xB1, 0x10, 0x00])
        generated_load_bytes = test_load_int.to_bytes(3,
                                                      "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_load_bytes == expected_load_bytes, \
            f"Load test failed: got {list(generated_load_bytes)}, expected {list(expected_load_bytes)}"
        print(f"Load(267) test passed: {list(generated_load_bytes)}")

        test_read_int = encode_read(34)
        expected_read_bytes = bytes([0x2F, 0x02, 0x00])
        generated_read_bytes = test_read_int.to_bytes(3,
                                                      "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_read_bytes == expected_read_bytes, \
            f"Read test failed: got {list(generated_read_bytes)}, expected {list(expected_read_bytes)}"
        print(f"Read(34) test passed: {list(generated_read_bytes)}")

        test_write_int = encode_write()
        expected_write_bytes = bytes([0x03, 0x00, 0x00])
        generated_write_bytes = test_write_int.to_bytes(3,
                                                        "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_write_bytes == expected_write_bytes, \
            f"Write test failed: got {list(generated_write_bytes)}, expected {list(expected_write_bytes)}"
        print(f"Write() test passed: {list(generated_write_bytes)}")

        test_gt_int = encode_gt(27)
        expected_gt_bytes = bytes([0xB5, 0x01, 0x00])
        generated_gt_bytes = test_gt_int.to_bytes(3,
                                                  "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_gt_bytes == expected_gt_bytes, \
            f"Gt test failed: got {list(generated_gt_bytes)}, expected {list(expected_gt_bytes)}"
        print(f"Gt(27) test passed: {list(generated_gt_bytes)}")

        print("All tests passed!")
        return True

    except AssertionError as e:
        print(f"Test failed: {e}")  # идея из файла преподавателя: проверка через assert
        return False
    except Exception as e:
        print(f"Unexpected error during tests: {e}")
        return False


def display_intermediate_fields(interp_program):
    """Отображает внутреннее представление как поля и значения, как в тестах."""
    print("\n--- Внутреннее представление (Поля и Значения, Тестовый режим) ---")  # Переведено
    for instr in interp_program:
        op = instr["op"]
        args = instr["args"]

        print(f"Op: {op}")
        if op == "load":
            # A=1 (из спецификации), B=args[0]
            print(f"  A: 1 (4 bits)")
            print(f"  B: {args[0]} (18 bits)")
        elif op == "read":
            # A=15 (из спецификации), B=args[0]
            print(f"  A: 15 (4 bits)")
            print(f"  B: {args[0]} (6 bits)")
        elif op == "write":
            # A=3 (из спецификации)
            print(f"  A: 3 (4 bits)")
        elif op == "gt":
            # A=5 (из спецификации), B=args[0]
            print(f"  A: 5 (4 bits)")
            print(f"  B: {args[0]} (6 bits)")
        else:
            print(f"  Unknown op: {op}")


def translate_to_machine_code_bytes(intermediate_program):
    """
    Преобразует список команд из промежуточного представления в бинарный код.
    """
    bytecode = b""
    for instruction in intermediate_program:  # идея из файла преподавателя: цикл по списку команд
        op = instruction.get("op")
        args = instruction.get("args", [])

        if op == "load":
            if len(args) != 1:
                raise ValueError(f"'load' instruction expects 1 argument, got {len(args)}")
            bytecode += encode_load(args[0]).to_bytes(3,
                                                      "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        elif op == "read":
            if len(args) != 1:
                raise ValueError(f"'read' instruction expects 1 argument, got {len(args)}")
            bytecode += encode_read(args[0]).to_bytes(3,
                                                      "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        elif op == "write":
            if len(args) != 0:
                raise ValueError(f"'write' instruction expects 0 arguments, got {len(args)}")
            bytecode += encode_write().to_bytes(3,
                                                "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        elif op == "gt":
            if len(args) != 1:
                raise ValueError(f"'gt' instruction expects 1 argument, got {len(args)}")
            bytecode += encode_gt(args[0]).to_bytes(3,
                                                    "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        else:
            raise ValueError(f"Unknown instruction: {op}")

    return bytecode  # идея из файла преподавателя: возврат собранного байтового объекта

def main():
    parser = argparse.ArgumentParser(description="Assembler for UVM Variant 20.")
    parser.add_argument("input_file", help="Path to the source assembly CSV file (.csv)")
    parser.add_argument("output_file", help="Path to the output binary file (.bin)")
    parser.add_argument("--test-mode", action="store_true",
                        help="Run internal tests and show intermediate representation / bytecode.")

    args = parser.parse_args()

    if args.test_mode:
        # Запуск тестов кодирования
        if not run_tests():
            sys.exit(1)  # Если тесты не прошли, завершаем

        # Загружаем промежуточное представление из CSV файла
        try:
            intermediate_program = assemble_from_csv(args.input_file)

            # Вывод внутреннего представления (поля и значения) - Требование Этапа 1
            display_intermediate_fields(intermediate_program)

            # Генерация и вывод байткода - Также полезно для проверки на Этапе 1
            bytecode = translate_to_machine_code_bytes(intermediate_program)

            print("\n--- Сгенерированный байткод (Тестовый режим) ---")  # Переведено
            print(" ".join([f"0x{b:02X}" for b in
                            bytecode]))  # идея из файла преподавателя: вывод байтов в шестнадцатеричном формате
            print(f"Bytecode length: {len(bytecode)} bytes")  # идея из файла преподавателя: вывод размера результата

        except FileNotFoundError:
            print(f"Input CSV file {args.input_file} not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error during assembly or testing: {e}")
            sys.exit(1)

    else:
        # Обычная сборка
        try:
            intermediate_program = assemble_from_csv(args.input_file)
            bytecode = translate_to_machine_code_bytes(
                intermediate_program)  # идея из файла преподавателя: вызов функции генерации байтов

            with open(args.output_file, 'wb') as f:
                f.write(bytecode)  # идея из файла преподавателя: запись результата в бинарный файл

            print(f"Assembled {args.input_file} -> {args.output_file}")
            print(
                f"Number of instructions assembled: {len(intermediate_program)}")  # Требование Этап 2, но логично выводить
            print(
                f"Size of binary file: {len(bytecode)} bytes")  # идея из файла преподавателя: вывод размера результата

        except FileNotFoundError:
            print(f"Error: Input file '{args.input_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error during assembly: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()