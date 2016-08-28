"""
CALL_FUNCTION opcode.

This function is pretty heavy handed, which is why it needs to be isolated and special cased.
"""
import dis
import functools

from naft.state import FunctionState
from naft.wrapper import NFunction, _NRunnableObject


def handle_op_131(state: FunctionState, instruction: dis.Instruction):
    """
    Handles CALL_FUNCTION.
    """
    # args are on the stack backwards
    # this means we have to use a reverse() on a list.
    args_to_get = instruction.arg
    args = []
    for i in range(0, args_to_get):
        # Pop from the stack and add it to args.
        args.append(state.pop())

    # Reverse the args.
    args = list(reversed(args))
    # Pop the function.
    func = state.pop()
    if isinstance(func, NFunction):
        # No need to wrap, just create the _NRunnableObject.
        runnable = func(*args)
        runnable = functools.partial(state.engine.run_function, runnable)
    # Check if the function is marked with a `_no_naft_execute`
    if hasattr(func, "_no_naft_execute"):
        # Create a plain executor.
        runnable = functools.partial(func, *args)
    else:
        # Wrap the function in an _NRunnableObject.
        wrapped = _NRunnableObject(func, args, {})
        runnable = functools.partial(state.engine.run_function, wrapped)

    # Run the runnable.
    result = runnable()
    # Push it onto the stack.
    state.push(result)
