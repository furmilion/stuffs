import struct

class H8500Decoder:
    def __init__(self, rom_path, base_segment=0x08):
        with open(rom_path, "rb") as f:
            self.rom_data = f.read()
        self.base_segment = base_segment

    def to_file_offset(self, segment, offset):
        """Перевод виртуального адреса H8/500 в физическое смещение в файле"""
        return (segment - self.base_segment) * 65536 + offset

    def decode_instruction(self, file_offset):
        """
        Декодирует ОДНУ инструкцию по указанному смещению в файле.
        Возвращает кортеж: (кол-во прочитанных байт, строка ассемблера, тип_инструкции)
        """
        if file_offset >= len(self.rom_data):
            return 0, "END OF FILE", "EOF"

        pc = file_offset

        # --- СЛУЧАЙ 1: Расширенные команды с префиксом 0x1A ---
        # if-else нахуй шёл
        match self.rom_data[pc]:
            case 0x1A:
                if pc + 1 >= len(self.rom_data): return 1, "db 1Ah", "DATA"
                match self.rom_data[pc + 1]:
                    case 0x30: # а вдруг там JMP иль JSR?
                               # хуй там знает, на авось
                               # буду байты декодировать
                               # а уж дальше мануал
                        addr_bytes = self.rom_data[pc+2:pc+6]
                        # танцы с бубном и Big-Endian
                        seg = addr_bytes[0]
                        high = addr_bytes[1]
                        low = (addr_bytes[2] << 8) | addr_bytes[3]
                        full_addr = (seg << 16) | (high << 8) | low
                        return 6, f"JMP @0x{full_addr:06X}", "JMP"
                    case 0x40: # саб
                        addr_bytes = self.rom_data[pc+2:pc+6]
                        seg = addr_bytes[0]
                        high = addr_bytes[1]
                        low = (addr_bytes[2] << 8) | addr_bytes[3]
                        full_addr = (seg << 16) | (high << 8) | low
                        return 6, f"JSR @0x{full_addr:06X}", "JSR"
                    case _: return 2, f"HEX: 1A {self.rom_data[pc + 1]:02X} (Unknown prefix 1A)", "UNKNOWN"

            case 0x04: return 1, "NOP", "MISC"
            case 0x11: return 1, "RTS", "RET"
            case 0x13: return 1, "RTE", "RET"
            case 0x7F:
                return 2, f"CHG / MOV ptn (7F {self.rom_data[pc + 1]:02X})", "DATA_PREPARATION"
            case 0x8F: # движуха ееееееее
                match self.rom_data[pc + 1]:
                    case 0x5F:
                        val = (self.rom_data[pc + 2] << 8) | self.rom_data[pc + 3]
                        return 4, f"MOV.L #0x{val:04X}, SP", "MOV"
                    case _: return 2, f"HEX: 8F {self.rom_data[pc + 1]:02X} (Unknown prefix 8F)", "UNKNOWN"
            case 0x9C:
                return 3, f"CLR/MOV control loop (9C {self.rom_data[pc + 1]:02X} {self.rom_data[pc + 2]:02X})", "LOOP"
            case 0x9D:
                return 1, "DBRA (Decrement and Branch)", "BRANCH"
            case 0xAF: # IO-движуха
                dest = self.rom_data[pc + 1]
                return 4, f"MOV.B #0x{self.rom_data[pc + 2]:02X}, @0xFF{self.rom_data[pc + 3]:02X}", "MOV"
            case 0xF8:
                return 2, f"LINK / SUB.W #0x{self.rom_data[pc + 1]:02X}, SP", "STACK"
            case _: # потом заполню
                return 1, f"HEX: {self.rom_data[pc]:02X}", "UNKNOWN"

    def disassemble_range(self, start_offset, num_instructions=10):
        """Цикл дизассемблирования последовательного участка памяти"""

        if isinstance(start_offset, str):
            try:
                if start_offset.lower().startswith("0x"):
                    current_offset = int(start_offset, 16)
                elif start_offset.lower().startswith("0o"):
                    current_offset = int(start_offset, 8)
                elif start_offset.lower().startswith("0b"):
                    current_offset = int(start_offset, 2)
                else:
                    current_offset = int(start_offset)
            except ValueError:
                print(f"unknown value: {start_offset}")
                current_offset = 0
        elif isinstance(start_offset, int):
            pass
        else:
            print(f"unknown value: {start_offset}, defaulting to 0")
            current_offset = 0

        if isinstance(num_instructions, str):
            try:
                if num_instructions.lower().startswith("0x"):
                    num_instructions = int(num_instructions, 16)
                elif num_instructions.lower().startswith("0o"):
                    num_instructions = int(num_instructions, 8)
                elif num_instructions.lower().startswith("0b"):
                    num_instructions = int(num_instructions, 2)
                else:
                    num_instructions = int(num_instructions)
            except ValueError:
                print(f"unknown value: {num_instructions}")
                num_instructions = 10
        elif isinstance(num_instructions, int):
            pass
        else:
            print(f"unknown value: {num_instructions}, defaulting to 10")
            num_instructions = 10

        print(f"\n--- Disassembling chunk from 0x{current_offset:04X} ---")

        for _ in range(num_instructions):
            bytes_read, asm_string, ins_type = self.decode_instruction(current_offset)
            if bytes_read == 0:
                break

            # Собираем байты инструкции для красивого вывода
            ins_bytes = self.rom_data[current_offset:current_offset+bytes_read]
            bytes_str = " ".join(f"{b:02X}" for b in ins_bytes)

            print(f"0x{current_offset:04X}:  {bytes_str:<17} | {asm_string}")
            current_offset += bytes_read

# Пример инициализации:
# decoder = H8500Decoder("tg100prog.bin")
# decoder.disassemble_range(0x032C, 15)
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
                    prog='H8/500 Opcode Decoder',
                    description='Self-explanatory',
                    epilog='"-o" indicates from which offset to decode\n"-c" indicates the amount of bytes to decode')
    parser.add_argument('filename')
    parser.add_argument('-o', '--offset')
    parser.add_argument('-c', '--count')
    args = parser.parse_args()
    print(f"running with: {args}")
    decoder = H8500Decoder(args.filename)
    decoder.disassemble_range(args.offset, args.count)
