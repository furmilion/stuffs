"""
A cheap console graph tool that takes an array or a file as an input and
spits out a graph with a set width and height.
"""

from time import sleep
def graph(
        arr: list | bytes | tuple | bytearray | str = None,
        bytes_per_selection: int = 1,
        width: int = 16,
        height: int = 16,
        v_divisions: int = 4  # vertical divisions;
                        ):
    if not arr:
        raise ValueError("You must provide at least some data!")

    if not isinstance(arr, (list, bytes, tuple, bytearray, str)):
        raise TypeError("Input must be one of the following: list, bytes, bytearray, tuple, str")
    if isinstance(arr, str):
        arr = [bytes(_, "utf8")[0] for _ in arr]

    if height <= 0 or width <= 0:
        raise ValueError("Width and heigth must be at least 1!")

    if bytes_per_selection <= 0:
        raise ValueError("Bytes per selection must be at least 1!")
    elif bytes_per_selection >= len(arr):
        raise ValueError("Bytes per selection must not be larger than the length of data!")

    height_multiplier = height / max(arr)  # maybe later round to multiples of 16?
    width_multiplier = width / len(arr)    # b


if __name__ == "__main__":
    graph("random ass text")
