"""
OS independent representation of something that is executable in process.

Supports the different variants of executable things used by Exactly.
"""
from abc import ABC, abstractmethod
from typing import List, Union, Sequence

from exactly_lib.type_system.description.structure_building import StructureBuilder


class ProgramAndArguments:
    def __init__(self,
                 program: str,
                 arguments: List[str]):
        self.program = program
        self.arguments = arguments


class CommandDriver(ABC):
    # Some func is needed here because Command has not been completely
    # refactored - it still has some functionality that should probably
    # be removed.

    @abstractmethod
    def structure_for(self, arguments: List[str]) -> StructureBuilder:
        """:returns A new object on each invokation."""
        pass

    @abstractmethod
    def arg_list_or_str_for(self, arguments: List[str]) -> Union[str, List[str]]:
        pass

    @property
    @abstractmethod
    def is_shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        # Maybe remove (low priority for the moment)
        pass


class Command:
    """
    Something that is executable in process.

    Is translated to an Executable, for execution.
    """

    def __init__(self,
                 driver: CommandDriver,
                 arguments: List[str]):
        super().__init__()
        self._driver = driver
        self._arguments = arguments

    def new_with_appended_arguments(self, tail_arguments: Sequence[str]) -> 'Command':
        return Command(
            self._driver,
            self._arguments + list(tail_arguments)
        )

    def structure(self) -> StructureBuilder:
        """:returns A new object on each invokation."""
        return self._driver.structure_for(self._arguments)

    @property
    def driver(self) -> CommandDriver:
        return self._driver

    @property
    def arguments(self) -> List[str]:
        return self._arguments

    @property
    def args(self) -> Union[str, List[str]]:
        # Maybe remove (low priority for the moment)
        return self.driver.arg_list_or_str_for(self.arguments)

    @property
    def shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        # Maybe remove (low priority for the moment)
        return self._driver.is_shell
