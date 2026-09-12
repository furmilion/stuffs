"""
lookup table conversion tools for SC-55
"""

def lfo_rate_convert(raw: int) -> float:
    return round(raw * 125 / 65535, 3)

def lfo_time_convert(raw: int) -> int:
    return round(65535 / (125 * raw))



def get_lut_offset(lut: int = 0, model: int = 0):
    """
    Returns the offset for the given LUT and model.
    """
    if model == 0: # SC-55mkI, firmware version 1.00
        if lut == 0:
            return 0
        else:
            return 0
    elif model == 1: # SC-55mkI, firmware version 1.10
        if lut == 0:
            return 0
        else:
            return 0
    elif model == 2: # SC-55mkI, firmware version 1.20
        if lut == 0:
            return 0
        else:
            return 0
    elif model == 3: # SC-55mkI, firmware version 1.21; cpu rom actually doesnt differ from 1.20
        if lut == 0:
            return 0
        else:
            return 0
    elif model == 4: # SC-55mkI, firmware version 2.00
        if lut == 0:
            return 0
        else:
            return 0
    elif model == 5: # SC-155mkI, firmware version 1.13....?  says so in the control rom
        if lut == 0:
            return 0
        else:
            return 0

    elif model == 6: # SC-55mkII, firmware version 1.01
        if lut == 0:
            return 0
        else:
            return 0
    elif model == 7: # SC-55st, firmware version 2.00
        if lut == 0:
            return 0
        else:
            return 0
    elif model == 10: # SCC-1A, firmware version 1.30
        if lut == 0:
            return 0
        else:
            return 0
