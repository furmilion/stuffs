"""
A GUI editor tool for editing Roland SC-55 ROMs.
This is the GUI.

The GUI handles the following:
    Displaying and exposing the data provided by the engine to the user
    Allowing the user to edit the data and save the changes
"""
try:
    from imgui_bundle import IM_COL32, ImVec2, ImVec4, imgui, imgui_ctx, immapp, implot
except ImportError:
    print("imgui_bundle not found. Please install it using 'pip install imgui_bundle'.")
    exit(1)
try:
    import numpy as np
except ImportError:
    print("numpy not found. Please install it using 'pip install numpy'.")
    exit(1)
print("this works")


import random
import sys
sys.path.append("..")
print(f"55_gui: {sys.path}")
from math import ceil
import FurWave

try:
    import sc55_rom_editor_engine as engine
except ImportError as e:
    print(e)
    try:
        import scripts.roland.sc55_rom_editor_engine as engine
    except ImportError as e:
        print("GUI module cannot be separated from the engine")
        print(e)
        exit(1)


print("random")

TEST_AREA = True      # tab with varoius tests
dpiScale = imgui.get_window_dpi_scale  # used for slider scaling
ver = "dev2"

def array_parse(array: str = ""):
    if not array:
        yield 0
    else:
        pre = array.split(",")
        for x in pre:
            x = x.replace(" ", "")
            try:
                if x.startswith("0x"):
                    x = float(int(x, 16))
                elif x.startswith("0b"):
                    x = float(int(x, 2))
                elif x.startswith("0o"):
                    x = float(int(x, 8))
                else:
                    x = float(x)
                yield x
            except ValueError:
                yield 0
print("array_parse")

def envelope_plot(attack1_rate, attack2_rate, decay1_rate, decay2_rate, release_rate,
                  attack1_level, attack2_level, decay1_level, decay2_level,
                  attack1_level_is_exponential, attack2_level_is_exponential, decay1_level_is_exponential, decay2_level_is_exponential, release_level_is_exponential,
                  invert_plot = False, plot_name = "generic envelope",
                  ):
    plot_x = np.linspace(0, 5, 6, dtype=np.float32)
    plot_y = np.linspace(0, 0, 6, dtype=np.float32)
    log_curve_inc = np.linspace(0, 1, 128, dtype=np.float32) ** 2
    log_curve_dec = np.linspace(1, 0, 128, dtype=np.float32) ** 2
    if attack1_rate:
        attack1_line_y = np.linspace(0, attack1_level/127, attack1_rate + 1, dtype=np.float32)
        if not attack1_level_is_exponential:
            attack1_line_x = np.linspace(0, attack1_rate/127, attack1_rate + 1, dtype=np.float32)
        else:
            attack1_line_x = (np.linspace(0, attack1_rate/127, attack1_rate + 1, dtype=np.float32) ** .5)
            attack1_line_x /= max(attack1_line_x)/(attack1_rate/127)
    else:
        attack1_line_y = np.array([0, attack1_level/127], dtype=np.float32)
        attack1_line_x = np.array([0, 0], dtype=np.float32)

    if attack2_rate:
        attack2_line_y = np.linspace(attack1_level/127, attack2_level/127, attack2_rate + 1, dtype=np.float32)
        if not attack2_level_is_exponential:
            attack2_line_x = np.linspace(0, attack2_rate/127, attack2_rate + 1, dtype=np.float32) + max(attack1_line_x)
        else:
            attack2_line_x = (np.linspace(0, attack2_rate/127, attack2_rate + 1, dtype=np.float32) ** .5)
            attack2_line_x /= max(attack2_line_x)/(attack2_rate/127)
            attack2_line_x += max(attack1_line_x)
    else:
        attack2_line_y = np.array([attack1_level/127, attack2_level/127], dtype=np.float32)
        attack2_line_x = np.array([max(attack1_line_x), max(attack1_line_x)], dtype=np.float32)

    if decay1_rate:
        decay1_line_y  = np.linspace(attack2_level/127, decay1_level/127,  decay1_rate + 1, dtype=np.float32)
        if not decay1_level_is_exponential:
            decay1_line_x = np.linspace(0, decay1_rate/127, decay1_rate + 1, dtype=np.float32) + max(attack2_line_x)
        else:
            decay1_line_x = (np.linspace(0, decay1_rate/127, decay1_rate + 1, dtype=np.float32) ** .5)
            decay1_line_x /= max(decay1_line_x)/(decay1_rate/127)
            decay1_line_x += max(attack2_line_x)
    else:
        decay1_line_y  = np.array([attack2_level/127, decay1_level/127], dtype=np.float32)
        decay1_line_x = np.array([max(attack2_line_x), max(attack2_line_x)], dtype=np.float32)

    if decay2_rate:
        decay2_line_y  = np.linspace(decay1_level/127, decay2_level/127,  decay2_rate + 1, dtype=np.float32)
        if not decay2_level_is_exponential:
            decay2_line_x = np.linspace(0, decay2_rate/127, decay2_rate + 1, dtype=np.float32) + max(decay1_line_x)
        else:
            decay2_line_x = (np.linspace(0, decay2_rate/127, decay2_rate + 1, dtype=np.float32) ** .5)
            decay2_line_x /= max(decay2_line_x)/(decay2_rate/127)
            decay2_line_x += max(decay1_line_x)
    else:
        decay2_line_y  = np.array([decay1_level/127, decay2_level/127], dtype=np.float32)
        decay2_line_x = np.array([max(decay1_line_x), max(decay1_line_x)], dtype=np.float32)

    if release_rate:
        release_line_y_1 = np.linspace(1, 0, release_rate + 1, dtype=np.float32)  # release from the start of the plot
        release_line_y_2 = np.linspace(decay2_level/127, 0, release_rate + 1, dtype=np.float32)  # release from decay 2
        if not release_level_is_exponential:
            release_line_x_1 = np.linspace(0, release_rate/127, release_rate + 1, dtype=np.float32)
            release_line_x_2 = np.linspace(0, release_rate/127, release_rate + 1, dtype=np.float32) + max(decay2_line_x)
        else:
            release_line_x_1 = np.linspace(0, release_rate/127, release_rate + 1, dtype=np.float32) ** .5
            release_line_x_1 /= max(release_line_x_1)/(release_rate/127)
            release_line_x_2 = np.linspace(0, release_rate/127, release_rate + 1, dtype=np.float32) ** .5
            release_line_x_2 /= max(release_line_x_2)/(release_rate/127)
            release_line_x_2 += max(decay2_line_x)
    else:
        release_line_y_1 = np.array([1, 0], dtype=np.float32)
        release_line_y_2 = np.array([decay2_level/127, 0], dtype=np.float32)
        release_line_x_1 = np.array([0, 0], dtype=np.float32)
        release_line_x_2 = np.array([max(decay2_line_x), max(decay2_line_x)], dtype=np.float32)

    if implot.begin_plot(title_id=plot_name,
                         size=None,
                         flags=implot.Flags_.no_inputs
                        ):
        implot.setup_axes("time", "level",
            implot.AxisFlags_.auto_fit | implot.AxisFlags_.no_menus,
            implot.AxisFlags_.auto_fit | implot.AxisFlags_.no_menus)
        implot.setup_legend(location=1,
                            flags=implot.LegendFlags_.no_menus |
                                  implot.LegendFlags_.no_buttons |
                                  implot.LegendFlags_.outside |
                                  implot.LegendFlags_.horizontal)

        implot.plot_line("attack phase 1", attack1_line_x, attack1_line_y)
        implot.plot_line("attack phase 2", attack2_line_x, attack2_line_y)
        implot.plot_line("decay phase 1",  decay1_line_x,  decay1_line_y)
        implot.plot_line("decay phase 2",  decay2_line_x,  decay2_line_y)
        implot.plot_line("release phase",  release_line_x_1, release_line_y_1)
        implot.plot_line("release phase",  release_line_x_2, release_line_y_2)
        implot.plot_line("", plot_x, plot_y)
        implot.end_plot()
print("envelope_plot")

def draw_dpcm_block_line(at: int) -> None:
    implot.plot_line("DPCM block boundary", np.array([at, at], dtype=np.float32), np.array([-1, 1], dtype=np.float32))

def sample_plot(data: np.ndarray | list[float], start: int = 0, loop_start: int = 0, loop_end: int = 0) -> None:
    start = max(start, 0)
    if isinstance(data, list):
        data = np.array(data, dtype=np.float32)
    plot_x = np.linspace(0 + start, len(data) - 1 + start, len(data), dtype=np.float32)
    plot_y = data
    if implot.begin_plot("sample",
                         size=None,
                         flags=implot.Flags_.no_inputs):
        implot.setup_axes("offset", "value",
            implot.AxisFlags_.auto_fit | implot.AxisFlags_.no_menus,
            implot.AxisFlags_.auto_fit | implot.AxisFlags_.no_menus)
        implot.plot_line("sample", plot_x, plot_y)
        if len(data):
            initial_block = ceil(start / 16) - 1
            initial_block = max(initial_block, 0)
            for block in range(ceil(len(data) / 16) + 2):
                draw_dpcm_block_line((block + initial_block) * 16)
        if not min(max(loop_end, 0), len(data) - 1) <= min(max(loop_start, 0), len(data) - 1) and not loop_end > len(data):
            implot.plot_line("loop start", np.array([loop_start, loop_start], dtype=np.float32), np.array([-1, 1], dtype=np.float32))
            implot.plot_line("loop end",   np.array([loop_end, loop_end], dtype=np.float32), np.array([-1, 1], dtype=np.float32))

        implot.end_plot()

def test_tab():
    self = test_tab
    # envelope test slider variables
    envelopeSliderSize = imgui.ImVec2(24 * dpiScale(), 128 * dpiScale())
    if not hasattr(self, "test_attack1_time"): self.test_attack1_time = 0
    if not hasattr(self, "test_attack1_level"): self.test_attack1_level = 0
    if not hasattr(self, "test_attack1_level_is_exponential"): self.test_attack1_level_is_exponential = False
    if not hasattr(self, "test_attack2_time"): self.test_attack2_time = 0
    if not hasattr(self, "test_attack2_level"): self.test_attack2_level = 0
    if not hasattr(self, "test_attack2_level_is_exponential"): self.test_attack2_level_is_exponential = False
    if not hasattr(self, "test_decay1_time"): self.test_decay1_time = 0
    if not hasattr(self, "test_decay1_level"): self.test_decay1_level = 0
    if not hasattr(self, "test_decay1_level_is_exponential"): self.test_decay1_level_is_exponential = False
    if not hasattr(self, "test_decay2_time"): self.test_decay2_time = 0
    if not hasattr(self, "test_decay2_level"): self.test_decay2_level = 0
    if not hasattr(self, "test_decay2_level_is_exponential"): self.test_decay2_level_is_exponential = False
    if not hasattr(self, "test_release_time"): self.test_release_time = 0
    if not hasattr(self, "test_release_level_is_exponential"): self.test_release_level_is_exponential = False

    if imgui.begin_tab_item("Test Area")[0]:
        if imgui.tree_node("basic plot test"):
            if imgui.begin_table("test table", 2):
                imgui.table_next_row()
                imgui.table_next_column()
                xs = np.linspace(0, 1, 1001, dtype=np.float32)
                ys = np.linspace(0, 1, 1001, dtype=np.float32)
                if implot.begin_plot("test plot"):
                    implot.setup_axes("x", "y")
                    implot.plot_line("line", xs, ys)
                    implot.end_plot()
                imgui.table_next_column()
                imgui.end_table()
            imgui.tree_pop()
        if imgui.tree_node("envelope plot test"):
            if imgui.begin_table("envelope table", 2):
                imgui.table_setup_column("sliders", imgui.TableColumnFlags_.width_fixed,   envelopeSliderSize.x * 6.4)
                imgui.table_setup_column("plot", imgui.TableColumnFlags_.width_stretch)

                imgui.table_next_row()
                imgui.table_next_column()

                if imgui.begin_table("sliders", 5):
                    imgui.table_setup_column("attack1", imgui.TableColumnFlags_.width_fixed,   envelopeSliderSize.x)
                    imgui.table_setup_column("attack2", imgui.TableColumnFlags_.width_fixed,   envelopeSliderSize.x)
                    imgui.table_setup_column("decay1",  imgui.TableColumnFlags_.width_fixed,   envelopeSliderSize.x)
                    imgui.table_setup_column("decay2",  imgui.TableColumnFlags_.width_fixed,   envelopeSliderSize.x)
                    imgui.table_setup_column("release", imgui.TableColumnFlags_.width_fixed,   envelopeSliderSize.x)

                    imgui.table_next_row()
                    imgui.table_next_column()
                    CENTER_TEXT("AR1")
                    imgui.text_unformatted("AR1")
                    TOOLTIP_TEXT("Attack Rate 1")
                    imgui.table_next_column()
                    CENTER_TEXT("AR2")
                    imgui.text_unformatted("AR2")
                    TOOLTIP_TEXT("Attack Rate 2")
                    imgui.table_next_column()
                    CENTER_TEXT("DR1")
                    imgui.text_unformatted("DR1")
                    TOOLTIP_TEXT("Decay Rate 1")
                    imgui.table_next_column()
                    CENTER_TEXT("DR2")
                    imgui.text_unformatted("DR2")
                    TOOLTIP_TEXT("Decay Rate 2")
                    imgui.table_next_column()
                    CENTER_TEXT("RR")
                    imgui.text_unformatted("RR")
                    TOOLTIP_TEXT("Release Rate")
                    imgui.table_next_column()

                    imgui.table_next_row()
                    imgui.table_next_column()
                    _, self.test_attack1_time = imgui.v_slider_int(
                        "Attack 1 Rate", envelopeSliderSize,
                        self.test_attack1_time, 0, 127
                    )
                    _, self.test_attack1_level = imgui.v_slider_int(
                        "Attack 1 Level", envelopeSliderSize,
                        self.test_attack1_level, 0, 127
                    )
                    _, self.test_attack1_level_is_exponential = imgui.checkbox(
                        "Exponential#atk1", self.test_attack1_level_is_exponential
                    )

                    imgui.table_next_column()
                    _, self.test_attack2_time = imgui.v_slider_int(
                        "Attack 2 Rate", envelopeSliderSize,
                        self.test_attack2_time, 0, 127
                    )
                    _, self.test_attack2_level = imgui.v_slider_int(
                        "Attack 2 Level", envelopeSliderSize,
                        self.test_attack2_level, 0, 127
                    )
                    _, self.test_attack2_level_is_exponential = imgui.checkbox(
                        "Exponential#atk2", self.test_attack2_level_is_exponential
                    )

                    imgui.table_next_column()
                    _, self.test_decay1_time = imgui.v_slider_int(
                        "Decay 1 Rate", envelopeSliderSize,
                        self.test_decay1_time, 0, 127
                    )
                    _, self.test_decay1_level = imgui.v_slider_int(
                        "Decay 1 Level", envelopeSliderSize,
                        self.test_decay1_level, 0, 127
                    )
                    _, self.test_decay1_level_is_exponential = imgui.checkbox(
                        "Exponential#dec1", self.test_decay1_level_is_exponential
                    )

                    imgui.table_next_column()
                    _, self.test_decay2_time = imgui.v_slider_int(
                        "Decay 2 Rate", envelopeSliderSize,
                        self.test_decay2_time, 0, 127
                    )
                    _, self.test_decay2_level = imgui.v_slider_int(
                        "Decay 2 Level", envelopeSliderSize,
                        self.test_decay2_level, 0, 127
                    )
                    _, self.test_decay2_level_is_exponential = imgui.checkbox(
                        "Exponential#dec2", self.test_decay2_level_is_exponential
                    )

                    imgui.table_next_column()
                    _, self.test_release_time = imgui.v_slider_int(
                        "Release Rate", envelopeSliderSize,
                        self.test_release_time, 0, 127
                    )
                    _, self.test_release_level_is_exponential = imgui.checkbox(
                        "Exponential#rel", self.test_release_level_is_exponential
                    )
                    imgui.end_table()

                imgui.table_next_column()
                envelope_plot(
                    self.test_attack1_time, self.test_attack2_time, self.test_decay1_time, self.test_decay2_time, self.test_release_time,
                    self.test_attack1_level, self.test_attack2_level, self.test_decay1_level, self.test_decay2_level,
                    self.test_attack1_level_is_exponential, self.test_attack2_level_is_exponential, self.test_decay1_level_is_exponential, self.test_decay2_level_is_exponential, self.test_release_level_is_exponential,
                    False, "test envelope"
                )
                imgui.end_table()
            imgui.tree_pop()
        if imgui.tree_node("sample plot test"):
            if not hasattr(self, "test_sample_data"): self.test_sample_data = "0"
            if not hasattr(self, "test_sample_offset"): self.test_sample_offset = 0
            if not hasattr(self, "test_sample_loop_start"): self.test_sample_loop_start = 0
            if not hasattr(self, "test_sample_loop_end"): self.test_sample_loop_end = 0

            _, self.test_sample_data = imgui.input_text("test sample data", self.test_sample_data)
            imgui.same_line()
            if imgui.button("generate random data"):
                self.test_sample_data = str([random.random() * 2 - 1 for _ in range(256)])
            _, self.test_sample_offset = imgui.input_int("sample offset", self.test_sample_offset)
            _, self.test_sample_loop_start = imgui.input_int("loop start", self.test_sample_loop_start)
            _, self.test_sample_loop_end = imgui.input_int("loop end", self.test_sample_loop_end)

            imgui.text(
                f"info:\n"
                f"data length: {len(self.test_sample_data)} ({ceil(len(self.test_sample_data) / 16) + 1} blocks)\n"
                f"loop start: {self.test_sample_loop_start}\n"
                f"loop end: {self.test_sample_loop_end}\n"
                f"offset: {self.test_sample_offset}"
            )
            sample_plot([_ for _ in array_parse(self.test_sample_data)], self.test_sample_offset, self.test_sample_loop_start, self.test_sample_loop_end)
            imgui.tree_pop()
        imgui.end_tab_item()
print("test_tab")

# useful functions
def CENTER_TEXT(text):
    imgui.set_cursor_pos_x(
        imgui.get_cursor_pos_x() +
        0.5 * (imgui.get_content_region_avail().x - imgui.calc_text_size(text).x)
    )
print("CENTER_TEXT")
def CENTER_VSLIDER():
    imgui.set_cursor_pos_x(
        imgui.get_cursor_pos_x() +
        0.5 * imgui.get_content_region_avail().x -
        10 * dpiScale()
    )
print("CENTER_VSLIDER")
def TOOLTIP_TEXT(text):
    if imgui.is_item_hovered():
        imgui.set_tooltip(text)
print("TOOLTIP_TEXT")

class AppState:
    """
    Holds the state of the GUI application.
    """
    def __init__(self):
        # format: (path, hash, status, family)
        self.loaded_roms = [
            ["None", "None", -1, "Unknown"],  # CPU
            ["None", "None", -1, "Unknown"],  # Control
            ["None", "None", -1, "Unknown"],  # Wave 1
            ["None", "None", -1, "Unknown"],  # Wave 2
            ["None", "None", -1, "Unknown"],  # Wave 3
        ]
        self.choices: list[str] = ["CPU", "Control", "Wave 1", "Wave 2", "Wave 3"]
        self.current_choice: int = 0

    def check_rom_family(self, ):
        match self.loaded_roms[0][1]: # cpu
            case 'c4e923344906aa630ab1b950720db386': # mk1 v1.00
                self.loaded_roms[0][3] = "SC-55mkI CPU ROM v1.00"
            case 'b301bfdaac9650ac97322f533396fdfb': # mk1 v1.10
                self.loaded_roms[0][3] = "SC-55mkI CPU ROM v1.10"
            case '462cb3a2ce9e54f4e54a52f643931ffd': # mk1 v1.20/v1.21
                self.loaded_roms[0][3] = "SC-55mkI CPU ROM v1.20/v1.21"
            case '6b74988a79c2a48239809f07a54175b3': # mk1 v2.00
                self.loaded_roms[0][3] = "SC-55mkI CPU ROM v2.00"
            case _: # unknown
                self.loaded_roms[0][3] = "Unknown"
        match self.loaded_roms[1][1]: # control
            case '7e90b34c777e2c5e1277ae559d959c26': # mk1 v1.00
                self.loaded_roms[1][3] = "SC-55mkI CPU ROM v1.00"
            case 'c0f0c8c2ffcfaf9a56c7e0d2dd440857': # mk1 v1.10
                self.loaded_roms[1][3] = "SC-55mkI CPU ROM v1.10"
            case '181b86f1c5a81caa65b6cebbf7c2678b': # mk1 v1.20
                self.loaded_roms[1][3] = "SC-55mkI CPU ROM v1.20"
            case '6b61186953b50d900e430ae6a996bda7': # mk1 v1.21
                self.loaded_roms[1][3] = "SC-55mkI CPU ROM v1.21"
            case 'd79cf9c9aa88416372cb0fd318f79beb': # mk1 v2.00
                self.loaded_roms[1][3] = "SC-55mkI CPU ROM v2.00"
            case _: # unknown
                self.loaded_roms[2][3] = "Unknown"
        match self.loaded_roms[2][1]: # wave1
            case '5f40d5297f47358ddea43b8d225874cc' | '37a8e5b695b6681093ca4e798cc76cac': # mk1
                self.loaded_roms[2][3] = 0
            case _: # unknown
                self.loaded_roms[2][3] = "Unknown"
        match self.loaded_roms[3][1]: # wave1
            case 'f78fb079a7d8c5f1eb04e0fd5aedbc9e' | '09618b6fce04342b5085b0005bb6e218': # mk1
                self.loaded_roms[3][3] = 0
            case _: # unknown
                self.loaded_roms[3][3] = "Unknown"
        match self.loaded_roms[4][1]: # wave1
            case '53c013d4bad0337385cfda2631e5b78e' | '9b9e2b29b8dd3bb46a652fd91561fc82': # mk1
                self.loaded_roms[4][3] = 0
            case _: # unknown
                self.loaded_roms[4][3] = "Unknown"






print("AppState")

def gui(state: AppState):
    """
    The GUI itself
    """
    self = gui
    style = imgui.get_style()
    global_scale = style.font_scale_main * style.font_scale_dpi * imgui.get_font_size()
    header = global_scale * 3

    imgui.push_font(None, header)
    imgui.text("Hello, World!")
    imgui.pop_font()

    if imgui.begin_tab_bar("ed"):
        if TEST_AREA:
            test_tab()

        if imgui.begin_tab_item("Overview")[0]:
            _, state.current_choice = imgui.combo("ROM Type", state.current_choice, state.choices)
            _, state.loaded_roms[state.current_choice][0] = imgui.input_text(f"{state.choices[state.current_choice]} ROM Path", state.loaded_roms[state.current_choice][0])
            if imgui.button("Load ROM"):
                if not hasattr(self, "waveroms_loaded"): self.waveroms_loaded = 0
                else: self.waveroms_loaded = 0
                status, state.loaded_roms[state.current_choice][1] = engine.load_rom(state.loaded_roms[state.current_choice][0], state.current_choice)
                if status:
                    state.loaded_roms[state.current_choice][2] = 1
                    if not hasattr(self, "wave1_addresses"): self.wave1_addresses = list(range(len(engine.CURRENT_ROMS[2])))
                    else: self.wave1_addresses = list(range(len(engine.CURRENT_ROMS[2])))
                    if not hasattr(self, "wave2_addresses"): self.wave2_addresses = list(range(len(engine.CURRENT_ROMS[2]), len(engine.CURRENT_ROMS[2]) + len(engine.CURRENT_ROMS[3])))
                    else: self.wave2_addresses = list(range(len(engine.CURRENT_ROMS[2]), len(engine.CURRENT_ROMS[2]) + len(engine.CURRENT_ROMS[3])))
                    if not hasattr(self, "wave3_addresses"): self.wave3_addresses = list(range(len(engine.CURRENT_ROMS[2]) + len(engine.CURRENT_ROMS[3]), len(engine.CURRENT_ROMS[2]) + len(engine.CURRENT_ROMS[3]) + len(engine.CURRENT_ROMS[4])))
                    else: self.wave3_addresses = list(range(len(engine.CURRENT_ROMS[2]) + len(engine.CURRENT_ROMS[3]), len(engine.CURRENT_ROMS[2]) + len(engine.CURRENT_ROMS[3]) + len(engine.CURRENT_ROMS[4])))
                    if len(self.wave1_addresses) <= 0: self.wave1_addresses = [0]
                    if len(self.wave2_addresses) <= 0: self.wave2_addresses = [self.wave1_addresses[-1]]
                    if len(self.wave3_addresses) <= 0: self.wave3_addresses = [self.wave2_addresses[-1]]
                else: state.loaded_roms[state.current_choice][2] = 0
                for waverom in range(2, 5):
                    if state.loaded_roms[state.current_choice][2] == 1:
                        self.waveroms_loaded += 1
            if state.loaded_roms[state.current_choice][2] == 1:
                imgui.same_line()
                imgui.text_colored(imgui.ImVec4(.3, 1, .1, 1), "Loaded successfully")
                imgui.text(f"sha256: {state.loaded_roms[state.current_choice][1]}")
            elif state.loaded_roms[state.current_choice][2] == 0:
                imgui.same_line()
                imgui.text_colored(imgui.ImVec4(1, .2, 0, 1), f"Failed to load ROM: {state.loaded_roms[state.current_choice][1]}")
            else:
                imgui.same_line()
                imgui.text_colored(imgui.ImVec4(1, .8, 0, 1), "No ROM loaded")
            imgui.end_tab_item()

        if imgui.begin_tab_item("Samples")[0]:
            if imgui.begin_tab_bar("sampling"):

                if imgui.begin_tab_item("Control ROM work")[0]:
                    if state.loaded_roms[1][2] in [-1, 0]:
                        imgui.text_colored(imgui.ImVec4(1, .2, 0, 1), "No Control ROM loaded")
                        imgui.end_tab_item()
                    elif state.loaded_roms[2][2] in [-1, 0] and state.loaded_roms[3][2] in [-1, 0] and state.loaded_roms[4][2] in [-1, 0]:
                        imgui.text_colored(imgui.ImVec4(1, .2, 0, 1), "Please load at least one sample ROM before working with samples")
                        imgui.end_tab_item()
                    else:
                        if not hasattr(self, "sample_def_address"): self.sample_def_address = 0
                        if not hasattr(self, "sample_def_num"): self.sample_def_num = 0
                        if not hasattr(self, "sample"): self.sample = engine.SC55_Sample()
                        if not hasattr(self, "sample_waverom"): self.sample_waverom = 0
                        if not hasattr(self, "sample_waverom_override"): self.sample_waverom_override = 0
                        if not hasattr(self, "sample_data"): self.sample_data = [0]
                        if not hasattr(self, "save_sample_rate"): self.save_sample_rate = 32000
                        if not hasattr(self, "save_path"): self.save_path = "./"

                        sample_changed = False

                        imgui.text("until i implement proper things you will have to work with this")
                        _, self.sample_def_address = imgui.input_int("sample definitions address", self.sample_def_address)
                        _, self.sample_def_num = imgui.input_int("sample definition number", self.sample_def_num)
                        self.sample_def_num = max(self.sample_def_num, 0)
                        self.sample_def_address = max(self.sample_def_address, 0)
                        _, self.sample_waverom_override = imgui.input_int("override the wave rom the sample is taken from", self.sample_waverom_override)
                        self.sample_waverom_override = max(self.sample_waverom_override, 0)
                        if imgui.button("Get sample"):
                            self.sample.decode(engine.CURRENT_ROMS[1][self.sample_def_address + (self.sample_def_num * 16):self.sample_def_address + (self.sample_def_num * 16) + 16])
                            self.sample_waverom = 1 if self.sample.address in self.wave1_addresses else 2 if self.sample.address in self.wave2_addresses else 3 if self.sample.address in self.wave3_addresses else 0
                            sample_changed = True
                        imgui.text(f"sample definition address: {self.sample_def_address + (self.sample_def_num * 16)}..{self.sample_def_address + (self.sample_def_num * 16) + 16}")
                        imgui.text(f"waveroms loaded: {self.waveroms_loaded}/3")
                        imgui.text(
                            f"waverom addresses:\n"
                            f"  wave 1: {self.wave1_addresses[0]}..{self.wave1_addresses[-1]}\n"
                            f"  wave 2: {self.wave2_addresses[0]}..{self.wave2_addresses[-1]}\n"
                            f"  wave 3: {self.wave3_addresses[0]}..{self.wave3_addresses[-1]}\n"
                        )
                        imgui.text(
                            "sample info:\n"
                            f"  attenuation: {self.sample.attenuation}\n"
                            f"  address: {self.sample.address} (wave rom {((self.sample.address & 0x700000) >> 20) + 1} bank {self.sample.address // 1048576})\n"
                            f"  porta offset: {self.sample.porta_ofs}\n"
                            f"  length: {self.sample.length}\n"
                            f"  loop length: {self.sample.loop_length}\n"
                            f"  loop mode: {self.sample.loop_mode}\n"
                            f"  root key: {self.sample.root_key}\n"
                            f"  pre-loop pitch offset: {self.sample.initial_pitch_offset}\n"
                            f"  loop pitch offset: {self.sample.loop_pitch_offset}\n"
                        )
                        if sample_changed:
                            print(f"gui: sample waverom {self.sample_waverom}")
                            if self.sample.length <= 0: pass
                            if self.sample_waverom_override > 0: self.sample_waverom = self.sample_waverom_override
                            if self.sample_waverom <= 0: pass
                            else:
                                try:
                                    self.sample_data = engine.decompress_range(self.sample_waverom - 1, self.sample.address % len(engine.CURRENT_ROMS[self.sample_waverom + 1]), self.sample.length)
                                except Exception as e:
                                    print(f"gui: decompress_range exception: {e}")

                            sample_changed = False
                        sample_plot(self.sample_data, self.sample.address & 15, self.sample.length - self.sample.loop_length, self.sample.length)

                        center = imgui.get_main_viewport().get_center()
                        imgui.set_next_window_pos(center, imgui.Cond_.appearing, ImVec2(0.5, 0.5))
                        if imgui.button("Save WAV"):
                            imgui.open_popup("Save WAV")
                        if imgui.begin_popup_modal("Save WAV", None, imgui.WindowFlags_.always_auto_resize)[0]:
                            imgui.text(f"The sample will be saved as smpl_{self.sample.address}_{self.sample.length}.wav")
                            _, self.save_sample_rate = imgui.input_int("Sample rate", self.save_sample_rate)
                            _, self.save_path = imgui.input_text("Save path", self.save_path)
                            if self.sample.length <= 0:
                                imgui.text_colored(ImVec4(1, .3, 0, 1), "WARNING: sample length is 0, cannot save as there is nothing to")
                            else:
                                if imgui.button("Save"):
                                    writer = FurWave.WaveWriter(
                                        channels=1,
                                        samplerate=self.save_sample_rate if self.save_sample_rate > 0 else 32000,
                                        bitdepth=32.0,
                                        packed=True,
                                        data=self.sample_data if self.sample_data else [0.0]
                                    )
                                    if self.sample.loop_length > 0 or self.sample.loop_mode != 2:
                                        writer.set_smpl_chunk(
                                            sample_loop_count=1,
                                            loop_types=[self.sample.loop_mode],
                                            loop_starts=[self.sample.length - self.sample.loop_length - 1],
                                            loop_ends=[self.sample.length - 1]
                                        )
                                    writer.write_file(f"{self.save_path}/smpl_{self.sample.address}_{self.sample.length}.wav", True)
                                    imgui.close_current_popup()
                                if imgui.button("Cancel"):
                                    imgui.close_current_popup()
                                imgui.end_popup()
                        imgui.end_tab_item()
                if imgui.begin_tab_item("Manual sample work")[0]:
                    if state.loaded_roms[2][2] in [-1, 0] and state.loaded_roms[3][2] in [-1, 0] and state.loaded_roms[4][2] in [-1, 0]:
                        imgui.text_colored(imgui.ImVec4(1, .2, 0, 1), "Please load at least one sample ROM before working with samples")
                        imgui.end_tab_item()
                    else:
                        if not hasattr(self, "manual_decompression_sample_address"): self.manual_decompression_sample_address = 0
                        if not hasattr(self, "manual_decompression_sample_length"): self.manual_decompression_sample_length = 0
                        if not hasattr(self, "manual_decompression_wave_rom"): self.manual_decompression_wave_rom = 0
                        if not hasattr(self, "manual_decompression_available_wave_roms"): self.manual_decompression_available_wave_roms = ["No", "No", "No"]
                        if not hasattr(self, "manual_decompression_sample_data"): self.manual_decompression_sample_data = [0]
                        if not hasattr(self, "save_sample_rate"): self.save_sample_rate = 32000
                        if not hasattr(self, "save_path"): self.save_path = "./"

                        for rom, data in enumerate(state.loaded_roms):
                            if rom < 2: continue
                            # print(rom)
                            # print(state.loaded_roms[rom])
                            if data[2] not in [-1, 0]:
                                self.manual_decompression_available_wave_roms[rom - 2] = f"Wave {rom - 1}"

                        _, self.manual_decompression_sample_address = imgui.input_int("Sample address", self.manual_decompression_sample_address)
                        _, self.manual_decompression_sample_length = imgui.input_int("Sample length", self.manual_decompression_sample_length)
                        _, self.manual_decompression_wave_rom = imgui.combo("Wave ROM", self.manual_decompression_wave_rom, self.manual_decompression_available_wave_roms)
                        if imgui.button("Decompress"):
                            if self.manual_decompression_sample_length <= 0: pass
                            else: self.manual_decompression_sample_data = engine.decompress_range(self.manual_decompression_wave_rom, self.manual_decompression_sample_address, self.manual_decompression_sample_length)
                        sample_plot(self.manual_decompression_sample_data, self.manual_decompression_sample_address & 15)

                        center = imgui.get_main_viewport().get_center()
                        imgui.set_next_window_pos(center, imgui.Cond_.appearing, ImVec2(0.5, 0.5))
                        if imgui.button("Save WAV"):
                            imgui.open_popup("Save WAV")
                        if imgui.begin_popup_modal("Save WAV", None, imgui.WindowFlags_.always_auto_resize)[0]:
                            imgui.text(f"The sample will be saved as smpl_man_{self.manual_decompression_sample_address}_{self.manual_decompression_sample_length}.wav")
                            _, self.save_sample_rate = imgui.input_int("Sample rate", self.save_sample_rate)
                            _, self.save_path = imgui.input_text("Save path", self.save_path)
                            if self.manual_decompression_sample_length <= 0:
                                imgui.text_colored(ImVec4(1, .3, 0, 1), "WARNING: sample length is 0, cannot save as there is nothing to")
                            else:
                                if imgui.button("Save"):
                                    writer = FurWave.WaveWriter(
                                        channels=1,
                                        samplerate=self.save_sample_rate if self.save_sample_rate > 0 else 32000,
                                        bitdepth=32.0,
                                        packed=True,
                                        data=self.manual_decompression_sample_data if self.manual_decompression_sample_data else [0.0]
                                    )
                                    writer.write_file(f"{self.save_path}/smpl_man_{self.manual_decompression_sample_address}_{self.manual_decompression_sample_length}.wav", True)
                                    imgui.close_current_popup()
                                if imgui.button("Cancel"):
                                    imgui.close_current_popup()
                                imgui.end_popup()
                        imgui.end_tab_item()

                imgui.end_tab_bar()

            imgui.end_tab_item()
        imgui.end_tab_bar()
print("gui")

def main():
    """
    The main entry point of the application.
    """
    print("test")
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_size=(640, 480),
        window_title=f"SC-55 ROM Editor v.{ver}",
        #with_markdown=True,
        with_implot=True,
    )
print("main")
print("a bunch of nonsensical console shit nobody cares about")
if __name__ == "__main__":
    print("run main")
    main()
