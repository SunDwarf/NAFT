"""
Handling for LOAD_ opcodes.
"""
import dis

from naft.exceptions.base import NFNameError
from naft.state import FunctionState, NAFT_NULL


def handle_op_116(state: FunctionState, instruction: dis.Instruction):
    """
    Handles a LOAD_GLOBAL opcode.
    """
    globals = state.globals
    # Extract the argument from the instruction, and check the `names`.
    arg = instruction.arg
    if arg > len(state.names) - 1:
        raise IndexError("{} is longer than names".format(arg))
    val = state.names[arg]
    # Look up the global in the globals.
    if val not in globals:
        # Raise a NameError.
        raise NFNameError("name '{}' is not defined".format(val))
    # Push it onto the stack.
    state.push(globals[val])


def handle_op_100(state: FunctionState, instruction: dis.Instruction):
    """
    Handles a LOAD_CONST opcode.

    This will load the constant from the state's consts, and place it on the stack.
    """
    const = state.consts[instruction.arg]
    state.push(const)


def handle_op_124(state: FunctionState, instruction: dis.Instruction):
    """
    Handles a LOAD_FAST opcode.

    Used for varnames.
    """
    arg = instruction.arg
    # This should always be something, so it's most likely to be safe.
    # Python will automatically unwrap bad names into a LOAD_GLOBAL, so we shouldn't need to do checks here.
    varname = state.varnames_stored[arg]
    # Run a check, anyway.
    if varname == NAFT_NULL:
        raise SystemError("unable to load varname '{}'".format(state.varnames[arg]))

    # Push it onto the stack.
    state.push(varname)
