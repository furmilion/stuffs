try:
    from imgui_bundle import imgui, immapp, implot, imgui_ctx, ImVec4, ImVec2, IM_COL32
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
print("random")

TEST_AREA = True      # tab with varoius tests
dpiScale = imgui.get_window_dpi_scale  # used for slider scaling
ver = "dev1"

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

def sample_plot(data: np.ndarray | list[float]) -> None:
    if isinstance(data, list):
        data = np.array(data, dtype=np.float32)
    plot_x = np.linspace(0, 1, len(data), dtype=np.float32)
    plot_y = data
    #print(f"x {plot_x} y {plot_y}")
    if implot.begin_plot("sample",
                         size=None,
                         flags=implot.Flags_.no_inputs):
        implot.setup_axes("time", "value",
            implot.AxisFlags_.auto_fit | implot.AxisFlags_.no_menus,
            implot.AxisFlags_.auto_fit | implot.AxisFlags_.no_menus)
        implot.plot_line("sample", plot_x, plot_y)
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
    if not hasattr(self, "test_sample_data"): self.test_sample_data = "0"

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
            _, self.test_sample_data = imgui.input_text("test sample data", self.test_sample_data)
            imgui.same_line()
            if imgui.button("generate random data"):
                self.test_sample_data = str([random.random() for _ in range(200)])
            #print(self.test_sample_data)
            #print([_ for _ in array_parse(self.test_sample_data)])
            sample_plot([_ for _ in array_parse(self.test_sample_data)])
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
        pass
print("AppState")

def gui(state: AppState):
    """
    The GUI itself
    """
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
            imgui.text("placeholder")
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
