"""
Engine class.

Used to actually run the bytecode.
"""
import collections
import dis
import inspect
import logging
import types

from naft import signals
from naft.exc import BadOpcode
from naft.ops import find_operator_implementation
from naft.state import FunctionState
from naft.wrapper import _NRunnableObject


class NAFTEngine(object):
    """
    The engine is responsible for executing bytecode. It does so by looping over each instruction, and modifying the
    function state at the time, then continuing.

    The engine uses several SignallingException subclasses to signal to the loop how to proceed.
    These should never leak out of the loop. If they do, this is a major bug.

    :param print_call_stacks: If an exception is raised, will our own call stack be printed?
    """

    def __init__(self, *, print_call_stacks=True):
        # Define our own call stack.
        # This allows us to print a proper call stack, if we can.
        self._call_stack = collections.deque()

        self.print_call_stacks = print_call_stacks

        self.logger = logging.getLogger("NAFT.engine")

    def _get_function_object(self, object_to_inspect):
        """
        Gets a function object from the _NRunnableObject, if we need to.
        """
        if isinstance(object_to_inspect, _NRunnableObject):
            return object_to_inspect.func
        elif callable(object_to_inspect):
            return object_to_inspect
        else:
            raise TypeError("Object is not callable")

    def _run_instruction(self, state: FunctionState, instruction: dis.Instruction):
        """
        Work function for running an instruction.
        """
        opcode, opname = instruction.opcode, instruction.opname
        self.logger.debug("Running operation {}:{} at line {}".format(opcode, opname, instruction.starts_line))

        # Get the op function.
        func = find_operator_implementation(opcode)
        # Call the function.
        if func is None:
            raise BadOpcode(instruction, None)
        result = func(state, instruction)
        return result

    def run_function(self, function: _NRunnableObject):
        """
        Runs a function inside the NAFT engine.

        This is the main entry point for the engine. It will automatically proceed down the function chain and call
        every non-builtin function with the engine.

        :param function: The _NRunnableObject to call.
        :return: The return result of the function.
        """

        # Check if it's a builtin.
        f = self._get_function_object(function)
        if isinstance(f, types.BuiltinFunctionType) or not hasattr(f, "__code__"):
            # Just call it.
            return function.run_natively()

        # Since we operate on the function directly, we ask the NRunnableObject to give us some useful data.
        # Like, yknow, the consts, names, varnames, etc.
        consts, names, varnames = function.get_data()

        # Get the filled in data.
        filled_in_data = function.get_varnames_filled_in()

        # Create the function state.
        # Merge globals and builtins.
        globs = globals().copy()
        globs.update(__builtins__)
        state = FunctionState(f, consts, names, varnames, globs)

        state.engine = self

        # Fill in the state.
        for position, item in enumerate(filled_in_data):
            state.varnames_stored[position] = item

        # Alright, we're ready.
        # Get a disassembled function.
        instructions = dis.get_instructions(f)

        # Begin iterating over the instructions.
        for instruction in instructions:
            # Call the work function.
            # This scans the instruction, sets up the state, and saves the result.
            # It also uses several signalling exceptions to signal to the runner how to proceed.
            try:
                result = self._run_instruction(state, instruction)
            except signals.ReturnValue as e:
                # We've been told to return a value.
                # So, that's what we do!
                return e.val
            except Exception:
                # Bare exception.
                # This means an error within NAFT.
                # Re-raise.
                self.logger.critical("Code raised an error!")
                self.logger.critical("Function stack: {}".format(state.stack))
                raise
