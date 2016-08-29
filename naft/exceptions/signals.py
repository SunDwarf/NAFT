"""
Signals tell the engine to do certain actions when running.

They're exceptions, but not errors.
"""


class NAFTSignal(BaseException):
    """
    Base class for a signal.
    """


class ReturnValue(NAFTSignal):
    """
    Signals the engine to return a value.
    """
    def __init__(self, value):
        # Val is used as the actual return value inside the engine.
        self.val = value
