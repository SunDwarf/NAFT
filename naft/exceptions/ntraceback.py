"""
Contains the "mock" traceback class.
"""
from types import FrameType as frame


class NTraceback:
    """
    A mock traceback.

    This is set on exceptions returned by NAFT as the `__traceback__` attribute.
    """

    def __init__(self, next_: 'NTraceback' = None,
                 lineno: int=0):
        self.tb_next = next_
        self.tb_lasti = 0
        self.tb_lineno = lineno
        # TODO: Implement a proper ``tb_frame``.
        self.tb_frame = None
