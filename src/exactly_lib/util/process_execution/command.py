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
        raise NotImplementedError('abstract method')

    @property
    def shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        raise NotImplementedError('abstract method')

    @property
    def shell_command_line(self) -> str:
        raise ValueError('this object is not a shell command: ' + str(self.args))

    @property
    def program_and_arguments(self) -> ProgramAndArguments:
        raise ValueError('this object is not a program with arguments: ' + str(self.args))
