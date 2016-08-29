"""
Base exceptions.

These are special exception classes used to re-write tracebacks.
However, they derive from the appropriate exception class, so can be caught like normal.
"""


class NFBaseException(Exception):
    """
    Class used as a base exception.
    """
    NAME = "UnknownException"
    BASE_TYPE = Exception

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._tb = None

    @property
    def __traceback__(self):
        return self._tb


class NFNameError(NFBaseException, NameError):
    """
    An NF name error.
    """
    NAME = "NameError"
    BASE_TYPE = NameError
