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


class CommandDriver:
    # Some func is needed here because Command has not been completely
    # refactored - it still has some functionality that should probably
    # be removed.
    def arg_list_or_str_for(self, arguments: List[str]):
        """
        :rtype: str or List[str]
        """
        raise NotImplementedError('abstract method')

    @property
    def is_shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        # Maybe remove (low priority for the moment)
        raise NotImplementedError('abstract method')


class Command:
    """
    Something that is executable in process.

    Is translated to an Executable, for execution.
    """

    def __init__(self,
                 driver: CommandDriver,
                 arguments: List[str]):
        self._driver = driver
        self._arguments = arguments

    @property
    def driver(self) -> CommandDriver:
        return self._driver

    @property
    def arguments(self) -> List[str]:
        return self._arguments

    @property
    def args(self):
        """
        :return: Either a string or an iterable of strings
        """
        # Maybe remove (low priority for the moment)
        return self.driver.arg_list_or_str_for(self.arguments)

    @property
    def shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        # Maybe remove (low priority for the moment)
        return self._driver.is_shell
