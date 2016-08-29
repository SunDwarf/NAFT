"""
Engine class.

Used to actually run the bytecode.
"""
import collections
import dis
import logging
import traceback
import types

import sys
from naft.exceptions import signals
from naft.exceptions.base import NFBaseException
from naft.exceptions.internal import BadOpcode
from naft.exceptions.nframe import NFrame
from naft.exceptions.ntraceback import NTraceback
from naft.ops import find_operator_implementation
from naft.state import FunctionState, NAFT_NULL
from naft.wrapper import _NRunnableObject


class NAFTEngine(object):
    """
    The engine is responsible for executing bytecode. It does so by looping over each instruction, and modifying the
    function state at the time, then continuing.

    The engine uses several SignallingException subclasses to signal to the loop how to proceed.
    These should never leak out of the loop. If they do, this is a major bug.
    """

    def __init__(self, ):
        # Define our own call stack.
        # This allows us to print a proper call stack, if we can.
        self._call_stack = collections.deque()

        self.logger = logging.getLogger("NAFT.engine")

        self._root = None

    @staticmethod
    def _get_function_object(object_to_inspect):
        """
        Gets a function object from the _NRunnableObject, if we need to.
        """
        if isinstance(object_to_inspect, _NRunnableObject):
            return object_to_inspect.func
        elif callable(object_to_inspect):
            return object_to_inspect
        else:
            raise TypeError("Object is not callable")

    def _rewrite_traceback(self, exception: NFBaseException):
        """
        Rewrites a traceback using the call stack.

        :param exception: The exception that was raised.
        :return: A :class:`naft.exceptions.ntraceback.NTraceback` that represents the current traceback.
        """
        tracebacks = []
        for x in range(len(self._call_stack)):
            # Pop the left of the traceback.
            state, instruction = self._call_stack.popleft()
            # Create a frame object.
            assert isinstance(state, FunctionState)
            assert isinstance(instruction, dis.Instruction)
            frame = NFrame()
            frame.f_code = state._wrapped_func.__code__
            frame.f_globals = state._wrapped_func.__globals__
            # Calculate locals.
            for xx, val in enumerate(state.names_stored):
                if val == NAFT_NULL:
                    continue

                name = state.names[xx]
                frame.f_locals[name] = val

            frame.f_lineno = state.line_no
            # Create a traceback object that is associated with this frame.
            tbobb = NTraceback()
            tbobb.tb_frame = frame
            tbobb.tb_lineno = frame.f_lineno
            # Set tb_next of the tracebacks.
            if tracebacks:
                tracebacks[-1].tb_next = tbobb
            # Add it to the tracebacks.
            tracebacks.append(tbobb)

        return tracebacks[0]

    def _run_instruction(self, state: FunctionState, instruction: dis.Instruction):
        """
        Work function for running an instruction.
        """
        opcode, opname = instruction.opcode, instruction.opname
        self.logger.debug("Running operation {}:{} at line {} in function {}".format(opcode, opname,
                                                                                     instruction.starts_line,
                                                                                     state._wrapped_func.__name__))

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
        if self._root is None:
            self._root = function

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
        globs = f.__globals__.copy()
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
            # Update the state with the current line number.
            if instruction.starts_line:
                state.line_no = instruction.starts_line
            # Push onto the call stack.
            self._call_stack.append((state, instruction))
            # Call the work function.
            # This scans the instruction, sets up the state, and saves the result.
            # It also uses several signalling exceptions to signal to the runner how to proceed.
            try:
                result = self._run_instruction(state, instruction)
            except signals.ReturnValue as e:
                # We've been told to return a value.
                # So, that's what we do!
                return e.val
            except NFBaseException as e:
                # Overriding Python's exception interpreter is, unfortunately, not possible.
                # Well, not in pure-python, as far as I can tell.
                # It *might* be possible using ctypes magic, but that's out of scope.
                # The best we can do is print our own traceback, then drop the original exception back down.
                # This produces terrible traceback spammery, but it's the best we can do.

                # Know if we need to re-write the call stack.
                if self._root != function:
                    raise
                # Re-write the traceback.
                tb = self._rewrite_traceback(e)
                e._tb = tb
                # Call traceback.print_exception.
                # We can't override the CPython interpreter's output.
                # So we print our own.
                # TODO: Make this print the right exception type.
                traceback.print_exception(e.BASE_TYPE, e.BASE_TYPE(*e.args), tb)
                print(file=sys.stderr)
                raise e.BASE_TYPE(*e.args) from e
            except Exception:
                # Bare exception.
                # This means an error within NAFT.
                # Re-raise.
                self.logger.critical("Code raised an error!")
                self.logger.critical("Function stack: {}".format(state.stack))
                raise
            else:
                self._call_stack.pop()
            finally:
                pass
