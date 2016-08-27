"""
Exception files.
"""


class BadOpcode(SystemError):
    """
    Called when an opcode that  can't parse is encountered.

    This doesn't mean the CPython bytecode was invalid; often that the opcode is new or otherwise unimplemented.
    """
