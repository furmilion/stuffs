# TODO: other envelope stages
# TODO: picking out the best set with shared rate correction

vib_strengths = [0, 3.376,
                 5.065, 6.75,
                 10.114, 20.17,
                 40.108, 79.307]
am_strengths = [0, 1.781,
                2.906, 3.656,
                4.406, 5.906,
                7.406, 11.91]
lfo_speeds = [0.168, 2.019,
              3.196, 4.206,
              5.215, 5.888,
              6.224, 7.056]
sustains = [0, 3, 6, 9,
            12, 15, 18, 21,
            24, 27, 30, 33,
            36, 39, 42, 93]

attacks = [float("inf"), float("inf"), float("inf"), float("inf"),
           6222.95, 4978.37, 4148.66, 3556.011,
           3111.47, 2489.21, 2074.33, 1778,
           1555.74, 1244.63, 1037.19, 889.02,
           777.87, 622.31, 518.59, 444.54,
           388.93, 311.16, 259.32, 222.27,
           194.47, 155.6, 129.66, 111.16,
           97.23, 77.82, 64.85, 55.6,
           48.62, 38.91, 32.43, 27.8,
           24.31, 19.46, 16.24, 13.92,
           12.15, 9.75, 8.12, 6.98,
           6.08, 4.9, 4.08, 3.49,
           3.04, 2.49, 2.13, 1.9,
           1.72, 1.41, 1.18, 1.04,
           .91, .73, .59, .5,
           .45, .45, .45, 0,
           ]
decays = [float("inf"), float("inf"), float("inf"), float("inf"),
          89164.63, 71331.75, 59443.13, 50951.25,
          44582.31, 35665.9, 29721.59, 25475.65,
          22291.16, 17832.97, 14860.82, 12737.82,
          11145.58, 8916.51, 7430.43, 6368.93,
          5572.79, 4458.28, 3715.24, 3184.49,
          2786.39, 2229.16, 1857.64, 1592.24,
          1393.2, 1114.6, 928.84, 796.15,
          696.6, 557.32, 464.44, 398.1,
          348.3, 278.68, 232.24, 199.05,
          174.15, 139.37, 116.15, 99.55,
          87.07, 69.71, 58.1, 49.8,
          43.54, 34.83, 29.02, 24.9,
          21.77, 17.41, 14.51, 12.43,
          10.08, 8.71, 7.23, 6.21,
          5.44, 5.44, 5.44, 5.44,
          ]


target_atk = float(input("Target attack  time  (s): ")) * 1000
target_de1 = float(input("Target decay1  time  (s): ")) * 1000
target_sus = float(input("Target sustain level (%): "))
target_de2 = float(input("Target decay2  time  (s): ")) * 1000
target_rel = float(input("Target release time  (s): ")) * 1000

atk_candidates = []; atk_errors = []
de1_candidates = []; de1_errors = []
de2_candidates = []; de2_errors = []
rel_candidates = []; rel_errors = []

from funcs import clamp
def get_pars(
        type: str = "none",
        param1: int = 0,
        param2: int = 0,
        rate = 44100
) -> str | float | int:
    """
    returns parameter values
    """
    match type.lower():
        case "vib":
            return (vib_strengths[param1] / 44100) * rate \
                if rate != 44100 else vib_strengths[param1]
        case "am":
            return (am_strengths[param1] / 44100) * rate \
                if rate != 44100 else am_strengths[param1]
        case "lfo":
            return (lfo_speeds[param1] / 44100) * rate \
                if rate != 44100 else lfo_speeds[param1]
        case "sus":
            return sustains[param1]
        case "atk":
            match param1:
                case 0:
                    return float('inf')
                case 15:
                    return attacks[63]
                case _:
                    return round((attacks[clamp(param1 + param2, 0, 63)] / 44100) * rate, 3) \
                        if rate != 44100 else attacks[clamp(param1 + param2, 0, 63)]
        case "dec":
            match param1:
                case 0:
                    return float('inf')
                case 15:
                    return decays[63]
                case _:
                    return round((decays[clamp(param1 + param2, 0, 63)] / 44100) * rate, 3) \
                        if rate != 44100 else decays[clamp(param1 + param2, 0, 63)]
        case _:
            return "Placeholder"

for rate_correction in range(16):
    for rate in range(16):
        if  get_pars("atk", rate, rate_correction) >= target_atk and \
           (get_pars("atk", rate, rate_correction)  - target_atk) < (target_atk * .125) and \
        abs(get_pars("atk", rate, rate_correction)) != float('inf'):
            #print("got candidate")
            atk_candidates.append(
                (
                    # rate correction value
                    rate_correction,

                    # env rate
                    rate,

                    # env time
                    get_pars("atk", rate, rate_correction),

                    # inaccuracy
                    get_pars("atk", rate, rate_correction) - target_atk,
                 )
            )
            atk_errors.append(get_pars("atk", rate, rate_correction) - target_atk)
        if get_pars("dec", rate, rate_correction) >= target_de1 and \
           (get_pars("dec", rate, rate_correction) - target_de1) < (target_de1 * .125) and \
            abs(get_pars("dec", rate, rate_correction)) != float('inf'):
            #print("got candidate")
            de1_candidates.append(
                (
                    # rate correction values
                    rate_correction,

                    # env rate
                    rate,

                    # env time
                    get_pars("dec", rate, rate_correction),

                    # inaccuracy
                    get_pars("dec", rate, rate_correction) - target_de1,
                 )
            )
            de1_errors.append(get_pars("dec", rate, rate_correction) - target_de1)
        if get_pars("dec", rate, rate_correction) >= target_de2 and \
           (get_pars("dec", rate, rate_correction) - target_de2) < (target_de2 * .125) and \
            abs(get_pars("dec", rate, rate_correction)) != float('inf'):
            #print("got candidate")
            de2_candidates.append(
                (
                    # rate correction value
                    rate_correction,

                    # env rate
                    rate,

                    # env time
                    get_pars("dec", rate, rate_correction),

                    # inaccuracy
                    get_pars("dec", rate, rate_correction) - target_de2,
                 )
            )
            de2_errors.append(get_pars("dec", rate, rate_correction) - target_de2)
        if get_pars("dec", rate, rate_correction) >= target_rel and \
           (get_pars("dec", rate, rate_correction) - target_rel) < (target_rel * .125) and \
            abs(get_pars("dec", rate, rate_correction)) != float('inf'):
            #print("got candidate")
            rel_candidates.append(
                (
                    # rate correction value
                    rate_correction,

                    # env rate
                    rate,

                    # env time
                    get_pars("dec", rate, rate_correction),

                    # inaccuracy
                    get_pars("dec", rate, rate_correction) - target_rel,
                 )
            )
            rel_errors.append(get_pars("dec", rate, rate_correction) - target_rel)
    else: pass

# TODO: read second TODO
# print(
#     "\n"
#     "ATTACK RATE CANDIDATES"
#     ""
# )
# for _ in atk_candidates:
#     print(
#         f"Attack Rate:     {_[0]}\n"
#         f"Attack Time:     {_[1]/1000}s\n"
#         f"Rate Correction: {_[2]}\n"
#         f"Inaccuracy:      {_[3]/1000}s\n"
#     )
# else:
#     print(None)

atk_candidates.sort()
de1_candidates.sort()
de2_candidates.sort()
rel_candidates.sort()

# TODO: read second TODO
# TODO: split each list into separate ones, one for each KSR and then display the possible combos