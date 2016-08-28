"""
Exception files.
"""
import dis


class BadOpcode(SystemError):
    """
    Called when an opcode that NAFT can't parse is encountered.

    This doesn't mean the CPython bytecode was invalid; often that the opcode is new or otherwise unimplemented.

    :param instruction: The :class:`dis.Instruction` that we failed to parse properly.
        This contains useful introspection data.

    :param function: The function we're attempting to run. This is probably a :class:`_NRunnableObject` rather than
    the real function.
    """

    def __init__(self, instruction: dis.Instruction, function):
        self.instruction = instruction
        self.function = function

    def __repr__(self):
        base = "Unable to parse opcode `{}:{}`.\nThis is probably not a bug! The chances are that the opcode has " \
               "not been implemented yet.".format(self.instruction.opcode, self.instruction.opname)
        return base

    __str__ = __repr__


class BadPopException(IndexError):
    """
    Called when the function stack wasn't complete.

    This often means a bug in NAFT.
    """
