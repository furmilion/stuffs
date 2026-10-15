"""
'Module' file editor for Domino MIDI Editor, with GUI based on Dear ImGui.
"""
from this import d
import typing
try:
    from imgui_bundle import imgui, immapp, implot
except ImportError:
    print("imgui_bundle not found. Please install it using 'pip install imgui_bundle'.")
    exit(1)

dpiScale = imgui.get_window_dpi_scale  # used for slider scaling

# useful functions
def CENTER_TEXT(text):
    imgui.set_cursor_pos_x(
        imgui.get_cursor_pos_x() +
        0.5 * (imgui.get_content_region_avail().x - imgui.calc_text_size(text).x)
    )
def CENTER_VSLIDER():
    imgui.set_cursor_pos_x(
        imgui.get_cursor_pos_x() +
        0.5 * imgui.get_content_region_avail().x -
        10 * dpiScale()
    )
def TOOLTIP_TEXT(text):
    if imgui.is_item_hovered():
        imgui.set_tooltip(text)
