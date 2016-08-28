"""
This package contains the NAFT operators.

They're grouped into files that are similar.
"""

import functools

# Imports.
# Make sure to keep these updated.
from naft.ops import load
from naft.ops import call
from naft.ops import misc


@functools.lru_cache(maxsize=None)
def find_operator_implementation(opcode: int):
    """
    Finds the NAFT implementation of this opcode.

    This will return a function that can be called with the state and the instruction, and will modify the state as
    appropriate.
    If the function could not be found, it will return None.

    :param opcode: The opcode to search.
    :return: The callable function.
    """
    for k, v in globals().items():
        f = getattr(v, "handle_op_{}".format(opcode), None)
        if f:
            return f

    return None
