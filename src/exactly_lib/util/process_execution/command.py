"""
OS independent representation of something that is executable in process.

Supports the different variants of executable things used by Exactly.
"""
from typing import List


class ProgramAndArguments:
    def __init__(self,
                 program: str,
                 arguments: List[str]):
        self.program = program
        self.arguments = arguments


class Command:
    """
    Something that is executable in process.

    Is translated to an Executable, for execution.
    """

    @property
    def args(self):
        """
        :return: Either a string or an iterable of strings
        """
        # Maybe remove (low priority for the moment)
        raise NotImplementedError('abstract method')

    @property
    def shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        # Maybe remove (low priority for the moment)
        raise NotImplementedError('abstract method')
