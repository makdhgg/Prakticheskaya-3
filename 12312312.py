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
        raise ValueError(f"Значение константы {const_val} вне диапазона для {CONST_BITS}-битного поля (макс {MAX_CONST})")

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A
    cmd_int |= ((const_val & mask(CONST_BITS)) << OPCODE_BITS)  # идея из файла преподавателя: сдвиг и установка битов B

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


def encode_read(offset_val: int) -> int:
    """
    Чтение значения из памяти.
    A (4 бита, 0-3) = 15
    B (6 бит, 4-9) = offset_val
    Размер: 3 байта.
    """
    A_OPCODE = 15
    OPCODE_BITS = 4
    OFFSET_BITS = 6
    MAX_OFFSET = mask(OFFSET_BITS)

    if not (0 <= offset_val <= MAX_OFFSET):
        raise ValueError(f"Значение смещения {offset_val} вне диапазона для {OFFSET_BITS}-битного поля (макс {MAX_OFFSET})")

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A
    cmd_int |= ((offset_val & mask(OFFSET_BITS)) << OPCODE_BITS)  # идея из файла преподавателя: сдвиг и установка битов B

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


def encode_write() -> int:
    """
    Запись значения в память.
    A (4 бита, 0-3) = 3
    Размер: 3 байта.
    """
    A_OPCODE = 3
    OPCODE_BITS = 4

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


def encode_gt(offset_val: int) -> int:
    """
    Бинарная операция: ">".
    A (4 бита, 0-3) = 5
    B (6 бит, 4-9) = offset_val
    Размер: 3 байта.
    """
    A_OPCODE = 5
    OPCODE_BITS = 4
    OFFSET_BITS = 6
    MAX_OFFSET = mask(OFFSET_BITS)

    if not (0 <= offset_val <= MAX_OFFSET):
        raise ValueError(f"Значение смещения {offset_val} вне диапазона для {OFFSET_BITS}-битного поля (макс {MAX_OFFSET})")

    cmd_int = 0
    cmd_int |= (A_OPCODE & mask(OPCODE_BITS))  # идея из файла преподавателя: установка битов A
    cmd_int |= ((offset_val & mask(OFFSET_BITS)) << OPCODE_BITS)  # идея из файла преподавателя: сдвиг и установка битов B

    return cmd_int  # идея из файла преподавателя: возврат целого числа, представляющего команду


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
        raise ValueError(f"Неверный формат аргумента в строке: {row}")

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
                print(f"Ошибка при разборе CSV файла в строке {i}: {e}")
                raise  # Прерываем с ошибкой

    return intermediate_repr  # идея из файла преподавателя: возврат внутреннего представления программы


def run_tests():
    """Проверяет правильность кодирования команд по тестовым векторам."""
    print("--- Запуск тестов ---")  # Переведено
    try:
        # Тесты из спецификации
        test_load_int = encode_load(267)
        expected_load_bytes = bytes([0xB1, 0x10, 0x00])
        generated_load_bytes = test_load_int.to_bytes(3, "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_load_bytes == expected_load_bytes, \
            f"Тест Load не пройден: получено {list(generated_load_bytes)}, ожидалось {list(expected_load_bytes)}"
        print(f"Load(267) тест пройден: {list(generated_load_bytes)}")

        test_read_int = encode_read(34)
        expected_read_bytes = bytes([0x2F, 0x02, 0x00])
        generated_read_bytes = test_read_int.to_bytes(3, "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_read_bytes == expected_read_bytes, \
            f"Тест Read не пройден: получено {list(generated_read_bytes)}, ожидалось {list(expected_read_bytes)}"
        print(f"Read(34) тест пройден: {list(generated_read_bytes)}")

        test_write_int = encode_write()
        expected_write_bytes = bytes([0x03, 0x00, 0x00])
        generated_write_bytes = test_write_int.to_bytes(3, "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_write_bytes == expected_write_bytes, \
            f"Тест Write не пройден: получено {list(generated_write_bytes)}, ожидалось {list(expected_write_bytes)}"
        print(f"Write() тест пройден: {list(generated_write_bytes)}")

        test_gt_int = encode_gt(27)
        expected_gt_bytes = bytes([0xB5, 0x01, 0x00])
        generated_gt_bytes = test_gt_int.to_bytes(3, "little")  # идея из файла преподавателя: преобразование числа в байты
        assert generated_gt_bytes == expected_gt_bytes, \
            f"Тест Gt не пройден: получено {list(generated_gt_bytes)}, ожидалось {list(expected_gt_bytes)}"
        print(f"Gt(27) тест пройден: {list(generated_gt_bytes)}")

        print("Все тесты пройдены!")
        return True

    except AssertionError as e:
        print(f"Тест не пройден: {e}")  # идея из файла преподавателя: проверка через assert
        return False
    except Exception as e:
        print(f"Неожиданная ошибка во время тестов: {e}")
        return False


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
                raise ValueError(f"Команда 'load' ожидает 1 аргумент, получено {len(args)}")
            bytecode += encode_load(args[0]).to_bytes(3, "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        elif op == "read":
            if len(args) != 1:
                raise ValueError(f"Команда 'read' ожидает 1 аргумент, получено {len(args)}")
            bytecode += encode_read(args[0]).to_bytes(3, "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        elif op == "write":
            if len(args) != 0:
                raise ValueError(f"Команда 'write' ожидает 0 аргументов, получено {len(args)}")
            bytecode += encode_write().to_bytes(3, "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        elif op == "gt":
            if len(args) != 1:
                raise ValueError(f"Команда 'gt' ожидает 1 аргумент, получено {len(args)}")
            bytecode += encode_gt(args[0]).to_bytes(3, "little")  # идея из файла преподавателя: вызов функции кодирования и добавление к результату
        else:
            raise ValueError(f"Неизвестная команда: {op}")

    return bytecode  # идея из файла преподавателя: возврат собранного байтового объекта

def main():
    parser = argparse.ArgumentParser(description="Ассемблер для УВМ Вариант 20 (Этап 2).")
    parser.add_argument("input_file", help="Путь к исходному CSV файлу с ассемблерным кодом (.csv)")
    parser.add_argument("output_file", help="Путь к выходному бинарному файлу (.bin)")
    parser.add_argument("--test-mode", action="store_true", help="Запустить внутренние тесты и показать сгенерированный байткод.")

    args = parser.parse_args()

    if args.test_mode:
        # Запуск тестов кодирования (Требование 4 & 6)
        if not run_tests():
            sys.exit(1)  # Если тесты не прошли, завершаем

        # Загружаем промежуточное представление из CSV файла
        try:
            intermediate_program = assemble_from_csv(args.input_file)

            # Генерация байткода (Требование 1)
            bytecode = translate_to_machine_code_bytes(intermediate_program)

            # Вывод байткода в тестовом режиме (Требование 4)
            print("\n--- Сгенерированный байткод (Тестовый режим) ---")  # Переведено
            print(" ".join([f"0x{b:02X}" for b in bytecode]))  # идея из файла преподавателя: вывод байтов в шестнадцатеричном формате, как в тесте из спецификации УВМ
            print(f"Длина байткода: {len(bytecode)} байт")  # идея из файла преподавателя: вывод размера результата
            print(f"Количество ассемблированных команд: {len(intermediate_program)}")  # Требование 3

            # Проверка соответствия тестовому байтовому коду (Требование 5 & 6)
            expected_full_test_code = bytes([0xB1, 0x10, 0x00, 0x2F, 0x02, 0x00, 0x03, 0x00, 0x00, 0xB5, 0x01, 0x00])
            if bytecode == expected_full_test_code:
                print("\n*** Тест полной последовательности (load->read->write->gt) ПРОЙДЕН! Соответствует тестовым векторам. ***")
            else:
                print("\n*** Тест полной последовательности НЕ ПРОЙДЕН! ***")
                print(f"Ожидалось: {[hex(b) for b in expected_full_test_code]}")
                print(f"Получено:  {[hex(b) for b in bytecode]}")

        except FileNotFoundError:
            print(f"Входной CSV файл {args.input_file} не найден.")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка во время ассемблирования или тестирования: {e}")
            sys.exit(1)

    else:
        # Обычная сборка (Требования 1, 2)
        try:
            intermediate_program = assemble_from_csv(args.input_file)
            bytecode = translate_to_machine_code_bytes(intermediate_program)  # идея из файла преподавателя: вызов функции генерации байтов

            with open(args.output_file, 'wb') as f:
                f.write(bytecode)  # идея из файла преподавателя: запись результата в бинарный файл

            print(f"Ассемблировано {args.input_file} -> {args.output_file}")
            print(f"Количество ассемблированных команд: {len(intermediate_program)}")  # Требование 3
            print(f"Размер бинарного файла: {len(bytecode)} байт")  # идея из файла преподавателя: вывод размера результата

        except FileNotFoundError:
            print(f"Ошибка: Входной файл '{args.input_file}' не найден.")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка во время ассемблирования: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()