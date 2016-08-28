"""
Contains the "state" for the function currently running.
"""

import collections
import inspect

from naft.exc import BadPopException

# "Special" value.
# Used to signify a null value in the names or varnames.
# This does *not* mean that it is None; an actual None will be filled in then.
# Instead, this signifies that no value currently exists, and Python would normally segfault on this.

NAFT_NULL = type("NAFTNULL", (), {})


class FunctionState:
    """
    This is the state for a function.

    It contains the stack, the "storage" for varnames and names, and other information like that.
    This is heavily passed around to other functions in the engine, allowing functions to modify the state.

    :ivar stack: The current function stack.
    :ivar names: The current storage for the names.
    :ivar varnames: The current storage for the varnames.
    """

    def __init__(self, func, consts: tuple, names: list, varnames: list,
                 globals_: dict):
        self._wrapped_func = func
        self.consts = consts
        self.names = names
        self.names_stored = [NAFT_NULL for x in range(len(names))]
        self.varnames = varnames
        self.varnames_stored = [NAFT_NULL for x in range(len(varnames))]
        # The stack is only as big as the func's stack size.
        stack_size = func.__code__.co_stacksize

        self.stack = collections.deque(maxlen=stack_size)

        self._name = self._wrapped_func.__name__

        self.globals = globals_

        # The current NAFTEngine that the state is associated with.
        self.engine = None

    def pop(self):
        """
        Pops the right most item off of the function stack.

        If there is no value here, it will raise a :class:`naft.exc.BadPopException`.
        :return: The item existing at the left of the function stack.
        """
        try:
            return self.stack.pop()
        except IndexError as e:
            raise BadPopException() from e

    def push(self, value: object):
        """
        Pushes an item onto the stack.

        :param value: The item to push onto the stack.
        """
        self.stack.append(value)
