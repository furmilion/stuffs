uint32_t unscramble_address(uint32_t address)
{
	// Discovered and written by NewRisingSun
	uint32_t new_addr = 0;
	if (address >= 0x20) {	// The first 32 bytes are not encrypted
		static const int addressOrder [20] = {0x02, 0x00, 0x03, 0x04, 0x01, 0x09, 0x0D, 0x0A, 0x12,
			0x11, 0x06, 0x0F, 0x0B, 0x10, 0x08, 0x05, 0x0C, 0x07, 0x0E, 0x13};
		for (uint32_t bit = 0; bit < 20; bit++) {
			new_addr |= ((address >> addressOrder[bit]) & 1) << bit;
		}
	} else {
		new_addr = address;
	}

	return new_addr;
}

int8_t unscramble_byte(int8_t byte)
{
	uint8_t byte_order[8] = {2, 0, 4, 5, 7, 6, 3, 1};
	uint32_t new_byte = 0;

	for (uint32_t bit = 0; bit < 8; bit++) {
		new_byte |= ((byte >> byte_order[bit]) & 1) << bit;
	}

	return new_byte;
}

bool decode_wave_rom(uint8_t *dec_buf)
{
	char *files_in[3] = {"roms"PATH_DIV"roland-gss.a_r15209276.ic28", "roms"PATH_DIV"roland-gss.b_r15209277.ic27", "roms"PATH_DIV"roland-gss.c_r15209281.ic26"};

	uint8_t *enc_buf = calloc(1, 0x100000);

	for (int32_t x = 0; x < 3; x++) {
		FILE *f_in = fopen(files_in[x], "rb");
		if (!f_in) {
			printf("Unable to find wave roms. Results will be corrupt.\n");
			return false;
		}
		fread(&enc_buf[0], 1, 0x100000, f_in);
		fclose(f_in);
		for (uint32_t y = 0; y < 0x100000; y++) {
			dec_buf[unscramble_address(y) + (0x100000 * x)] = unscramble_byte(enc_buf[y]);
		}
	}

	FILE *fo = fopen("wave_dec.rom", "wb");
	fwrite(dec_buf, 0x300000, 1, fo);
	fclose (fo);

	free(enc_buf);
	return true;
}