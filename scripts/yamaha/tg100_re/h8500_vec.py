import struct

def parse_h8_500_vectors(rom_path):
    print(f"--- TG100 Vector table analysis ({rom_path}) ---")
    
    with open(rom_path, "rb") as f:
        rom_data = f.read()

    # Векторы занимают первые 256 байт (64 вектора по 4 байта)
    vector_table_size = 256
    
    # Имена базовых аппаратных векторов H8/500
    vector_names = {
        0: "Reset (Entry point)",
        32: "Trap / Interrupt 32",
        41: "SCI / Timer 41",
        42: "SCI / Timer 42",
        45: "Peripheral 45",
        46: "Peripheral 46",
        48: "Peripheral 48",
        49: "Peripheral 49",
        52: "Peripheral 52",
        53: "Peripheral 53",
        54: "Peripheral 54",
        56: "Peripheral 56",
        57: "Peripheral 57",
        58: "Peripheral 58",
        60: "Peripheral 60",
    }

    for vec_num in range(64):
        offset = vec_num * 4
        if offset >= len(rom_data):
            break
            
        vec_bytes = rom_data[offset:offset+4]
        if len(vec_bytes) < 4:
            break
            
        # Распаковываем: первые 2 байта — смещение (little-endian), 3-й — сегмент CP
        #low_offset, segment_cp, reserved = struct.unpack("<HBB", vec_bytes)
        #low_offset, segment_cp, reserved = struct.unpack(">BBH", vec_bytes)
        #low_offset, segment_cp, reserved = struct.unpack(">HBB", vec_bytes)
        b1, b2, b3, b4 = struct.unpack(">BBBB", vec_bytes)
        
        # Проверка на пустые векторы
        if b1 == b2 == b3 == b4 == 0 or b1 == b2 == b3 == b4 == 0xFF:
            continue
            
        # В зависимости от архитектуры H8/500 Максимального режима:
        # Обычно: b1 = резерв (0), b2 = номер сегмента (CP), (b3 << 8) | b4 = 16-битное смещение
        segment_cp = b2
        low_offset = (b3 << 8) | b4

        name = vector_names.get(vec_num, f"Interrupt Vector {vec_num}")
        
        # Физический адрес в файле ПЗУ (в предположении, что ПЗУ мапится линейно с 0 страницы)
        # В реальном Maximum Mode физический адрес = (segment_cp << 16) + low_offset
        # Но для самого первого банка прошивки обычно segment_cp == 0
        phys_addr = (segment_cp << 16) + low_offset
        
        print(f"Vec {vec_num:02d} | {name:<25} -> CP seg: 0x{segment_cp:02X}, ROM ofs: 0x{low_offset:04X} [Phys addr: 0x{phys_addr:06X}]")

# Укажите путь к вашему файлу прошивки tg100prog.bin
# parse_h8_500_vectors("tg100prog.bin")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
                    prog='Анализатор таблицы векторов H8/500',
                    description='Анализирует таблицу векторов H8/500',
                    epilog='"-e" indicates whether the extended mode of H8/500 is used')
    parser.add_argument('filename')
    parser.add_argument('-e', '--extended',
                        action='store_true')  # on/off flag
    args = parser.parse_args()
    print(f"running with: {args}")
    parse_h8_500_vectors(args.filename)
    #parse_h8_500_vectors_big_endian(args.filename)