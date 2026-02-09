"""
This will likely never be finished, sorry guys
"""


class LFSR:

    """
    A simple class to create, tick and otherwise manage LFSRs.
    LFSR is short for Linear Feedback Shift Register.
    In LFSR world, there are taps.
    A tap (or tap bit) is a bit that will be operated on with a tap method.

    In this example we will use an LFSR of size 6 and initial state of 0b100010,
    taps 0, 2, 4 and 5 and tap method for all taps being XOR.

    XOR table:
    0 ^ 0 = 0
    1 ^ 0 = 1
    0 ^ 1 = 1
    1 ^ 1 = 0

    Note that the rightmost bit is always tapped.

    The LFSR works as follows:
    1. Get defined with size x (6), initial state y (0b100010), taps (0, 2, 4 and 5) and tap method (XOR).
    2. Tick:
    2.1. XOR last bit with first tap bit, aka bit 5 ^ bit 4. b5^b4 = 1, according to XOR table.
    2.2. XOR the result with next tap: 1^0 = 1
    2.3. XOR with the last tap: 1^1 = 0
    2.4. Right shift the state and insert the result bit at the first position.
    3. Repeat.

    """

    class ArgumentError(Exception):
        """
        An exception for use with argument errors.
        """
        def __init__(self, *args, **kwargs):
            """Initialize self."""
            pass

    class СатурнError(Exception):
        def __init__(self, *args, **kwargs):
            pass

    def raiseError(self, exception, message):
        raise exception(message)

    def _(self):
        return None

    def __init__(self):
        """
        Initializes self.
        """
        self.data = {}
        self.all_names = []
        self.last_calculation = 0
        self.temp_taps = [0]
        self.temp_taps2 = []
        self.len_mask = 0b1
        self.temp_state = 0
        self.name = None
        self.index = None
        self.lfsr_exists = False
        self.temp = 0
        self.temp2 = 0
        self.current_tap1, self.current_tap2 = None, None
        self.return_binary = False
        self.lfsr_types = [
                           "and",  "or",  "xor",
                           "nand", "nor", "xnor",
                           # "imply", "nimply"
                           ]

    def create(self, **kwargs):
        """
        Creates and contains a new LFSR with a name, initial state, size and tap bits.
        Raises a ValueError if either of parameters not passed.
        If an LFSR already exists, its parameters get overwritten (default dict behavior).
        Following values are accepted for taps: 'no','0', 'and', 'nand', 'or', 'xor', 'xnor'
        """
        kwargs["name"] if "name" in kwargs else self.raiseError(self.ArgumentError, "LFSR name not provided (provide via 'name' keyword).")
        temp_state = kwargs["state"] if "state" in kwargs else self.raiseError(self.ArgumentError, "LFSR initial state not provided (provide via 'state' keyword).")
        temp = kwargs["size"] if "size" in kwargs else self.raiseError(self.ArgumentError, "LFSR size not provided (provide via 'size' keyword).")
        temp_taps = kwargs["taps"] if "taps" in kwargs else self.raiseError(self.ArgumentError, "LFSR taps not provided (provide via 'taps' keyword).")
        len_mask = 0b1
        for i in range(kwargs["size"]):
            len_mask |= 2**i
        if type(temp_state) is int:
            temp_state &= len_mask
        elif temp_state == "max":
            temp_state = len_mask
        else:
            raise ValueError("'state' keyword only accepts integers or 'max' as a value.")
        if type(kwargs["taps"]) is not list:
            temp_taps = list(kwargs["taps"])
        temp_taps2 = list(range(kwargs["size"] - len(temp_taps)))
        for i in range(len(temp_taps2)):
            temp_taps2[i] = 0
        temp_taps2.append(temp_taps)
        for i in range(len(self.data)):
            if kwargs["name"] in self.data[i]:
                self.lfsr_exists = True
                self.data[len(self.data)] = {"name": kwargs["name"], "state": self.temp_state,
                                                      "taps": self.temp_taps2, "size": kwargs["size"]}
                for j in range(len(self.data)):
                    if self.data[j]["name"] not in self.all_names:
                        self.all_names.append(self.data[j]["name"])
                return (f"Successfully modified an LFSR at position {len(self.data) - 1}:\n"
                        f"{self.data[f'lfsr{len(self.data) - 1}']}")
            else:
                self.lfsr_exists = False
        if not self.lfsr_exists:
            self.data[len(self.data)] = {"name": kwargs["name"], "state": self.temp_state,
                                         "taps": self.temp_taps, "size": kwargs["size"]}
            for j in range(len(self.data)):
                if self.data[j]["name"] not in self.all_names:
                    self.all_names.append(self.data[j]["name"])
            return (f"Successfully created an LFSR at position {len(self.data) - 1}:\n"
                    f"{self.data[len(self.data) - 1]}")

    def list_all(self):
        """
        Lists names of all currently created LFSRs.
        """
        for i in range(len(self.data)):
            try:
                if self.data[i]["name"] not in self.all_names:
                    self.all_names.append(self.data[i]["name"])
            except KeyError:
                pass
        return self.all_names

    def return_state(self, **kwargs):
        """
        Returns the current state of an LFSR.
        Raises a ValueError if name or index not passed or an LFSR with that name or at that index does not exist.
        Returns binary view if 'return_binary' keyword set.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        self.name = kwargs["name"] if "name" in kwargs else None
        self.index = kwargs["index"] if "index" in kwargs else None
        self.return_binary = kwargs["return_binary"] if "return_binary" in kwargs else 0
        if self.name is None and self.index is None:
            raise self.ArgumentError("Name of LFSR not passed as an argument.")
        try:
            if self.return_binary:
                return bin(self.data[self.all_names.index(self.name)]["state"])
            else:
                return self.data[self.all_names.index(self.name)]["state"]
        except ValueError:
            raise ValueError(f"LFSR with name {self.name} does not exist."
                             f"Use list_all() method to get a list of all names.")

    def flush(self):
        """
        Flushes: returns a dict of all LFSRs and their states and clears it.
        """
        print(self.data)
        self.data = {}
        self.all_names = []

    def get_all(self):
        """
        Returns the dict containing all LFSRs.
        """
        return self.data

    def pop(self, **kwargs):
        """
        Remove and return LFSR at index or at name.
        Raises an IndexError if no LFSRs are present.
        Raises a ValueError if neither of arguments is passed.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        index = kwargs["index"] if "index" in kwargs else None
        name = kwargs["name"] if "name" in kwargs else None
        if (index is None) and (name is None):
            raise self.ArgumentError("Name nor index of LFSR not passed as an argument.")
        elif name is not None and index is not None or name is not None:
            try:
                if self.all_names.index(name) == (len(self.all_names) - 1):
                    temp = self.data[self.all_names.index(name)]
                    self.data.pop(self.all_names.index(name))
                    self.all_names.pop(self.all_names.index(name))
                    return temp
                else:
                    temp = self.data[self.all_names.index(name)]
                    for i in range(self.all_names.index(name), len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(self.all_names.index(name))
                    return temp
            except KeyError:
                raise KeyError(f"LFSR with name {name} does not exist."
                               f"Use list_all() method to get a list of all names.")
        elif name is None and index is not None:
            try:
                if index == (len(self.all_names) - 1):
                    temp = self.data[index]
                    self.all_names.pop(self.data[index]["name"])
                    self.data.pop(index)
                    return temp
                else:
                    temp = self.data[index]
                    for i in range(index, len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(index)
                    return temp
            except KeyError:
                raise IndexError(f"LFSR at index {index} does not exist."
                                 f"Use list_all() method to get a list of all names.")

    def remove(self, **kwargs):
        """
        Remove an LFSR at index or at name.
        Raises an IndexError if no LFSRs are present.
        Raises a ValueError if neither of arguments is passed.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        index = kwargs["index"] if "index" in kwargs else None
        name = kwargs["name"]  if "name" in kwargs else None
        if (index is None) and (name is None):
            raise self.ArgumentError("Name nor index of LFSR not passed as an argument.")
        elif name is not None and index is not None or name is not None:
            try:
                if self.all_names.index(name) == (len(self.all_names) - 1):
                    self.data.pop(self.all_names.index(name))
                    self.all_names.pop(self.all_names.index(name))
                    return
                else:
                    for i in range(self.all_names.index(name), len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(self.all_names.index(name))
                    return
            except KeyError:
                raise KeyError(f"LFSR with name {name} does not exist."
                               f"Use list_all() method to get a list of all names.")
        elif name is None and index is not None:
            try:
                if index == (len(self.all_names) - 1):
                    self.all_names.pop(self.data[index]["name"])
                    self.data.pop(index)
                    return
                else:
                    for i in range(index, len(self.data)):
                        try:
                            temp2 = self.data[i + 1]
                            self.data[i] = temp2
                        except KeyError:
                            pass
                    self.data.pop(len(self.data) - 1)
                    self.all_names.pop(index)
                    return
            except KeyError:
                raise IndexError(f"LFSR at index {index} does not exist."
                                 f"Use list_all() method to get a list of all names.")

    def tick(self, **kwargs):
        """
        Advances the LFSR at name or index by a single tick and returns the bit that got thrown out when right-shifting.
        Raises a ValueError if neither of arguments is passed.
        If both arguments are passed, name takes priority.
        Handling of arguments is subject to change.
        """
        index = kwargs["index"] if "index" in kwargs else None
        name = kwargs["name"] if "name" in kwargs else None
        current_tap1, current_tap2, *_, = [None for _ in range(16)]
        if index is None and name is None:
            raise self.ArgumentError("Name nor index of LFSR not passed as an argument.")

        if name is not None and (index is not None) or name is not None:
            if name in self.data:
                temp = self.data[self.all_names.index(name)]["state"]
                temp2 = self.data[self.all_names.index(name)]["size"]
                temp_taps = self.data[self.all_names.index(name)]["taps"]

                for i in range(len(temp_taps), 0):
                    try:
                        calculated = False
                        if temp_taps[i] not in self.lfsr_types:
                            pass
                        else:
                            if current_tap1 is None:
                                current_tap1 = temp_taps[i]
                            elif current_tap2 is None:
                                current_tap2 = temp_taps[i]
                            elif "h":
                                pass


                    except:  # i'll probably finish everything later
                        ""
            else:
                raise KeyError(f"LFSR with name {name} does not exist."
                               f"Use list_all() method to get a list of all names.")
