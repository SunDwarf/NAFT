"""
Mock frame objects.
"""


class NFrame:
    """
    A mock frame object.

    This emulates the original frame.
    """

    def __init__(self):
        self.f_builtins = __builtins__
        self.f_globals = {}
        self.f_locals = {}
        self.f_code = None
        self.f_lineno = 0

        # These don't have a proper implementation.
        self.f_back = None
        self.f_trace = None
        self.f_lasti = 0
