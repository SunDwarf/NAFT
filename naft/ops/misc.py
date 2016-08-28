"""
"Misc" operators.
"""
import dis

from naft import signals
from naft.state import FunctionState


def handle_op_83(state: FunctionState, instruction: dis.Instruction):
    """
    Handles RETURN_VALUE.
    """
    # Pop the latest value off of the stack
    val = state.pop()
    # Signal a return.
    raise signals.ReturnValue(val)
