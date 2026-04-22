from funcs import *

def generate_sine_table(length: int = 1, maxv: int = 1, signed: bool | int = False):
    """
    Generates a numpy.ndarray of values of
    sin(math.tau/length*x) across "length" values.
    """
    if not NUMPY:
        return "nah"
    if not signed:
        return np.array([
            round(
                (sin(tau / length * x) + 1)
                * maxv / 2
            ) for x in range(length)
        ])
    elif signed:
        return np.array([
            round(
                (sin(tau / length * x))
                * (maxv + .5) - .5
            ) for x in range(length)
        ])

def generate_fn_table_advanced(length: int = 1, maxv: int = 1, signed: bool | int = False, function = sin, constant: float = tau):
    """
    Generates a numpy.ndarray of values of
    sin(math.tau/length*x) across "length" values.
    """
    if not NUMPY:
        return "nah"
    if not signed:
        return np.array([
            round(
                (function(constant / length * x) + 1 ) # +1 is to unsign it, as in make it go from 0..2 instead of from -1 to 1
                * maxv / 2
            )
            for x in range(length)
        ], 0, )
    elif signed:
        return np.array([
            round(
                ( function(constant / length * x) )
                * (maxv + .5) - .5
            ) for x in range(length)
        ])