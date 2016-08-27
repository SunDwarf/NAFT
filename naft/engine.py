"""
Engine class.

Used to actually run the bytecode.
"""
import collections

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

    def run_function(self, function: _NRunnableObject):
        """
        Runs a function inside the NAFT engine.

        This is the main entry point for the engine. It will automatically proceed down the function chain and call
        every non-builtin function with the engine.

        :param function: The _NRunnableObject to call.
        :return: The return result of the function.
        """

        # Since we operate on the function directly, we ask the NRunnableObject to give us some useful data.
        # Like, yknow, the consts, names, varnames, etc.
        consts, names, varnames = function.get_data()

        # Get the filled in data.
        filled_in_data = function.get_varnames_filled_in()
