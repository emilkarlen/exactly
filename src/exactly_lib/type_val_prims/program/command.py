"""
OS independent representation of something that is executable in process.

Supports the different variants of executable things used by Exactly.
"""
from abc import ABC, abstractmethod
from typing import List, Sequence

from exactly_lib.type_val_prims.description.structure_building import StructureBuilder


class ProgramAndArguments:
    def __init__(self,
                 program: str,
                 arguments: List[str]):
        self.program = program
        self.arguments = arguments


class CommandDriver(ABC):
    @abstractmethod
    def structure_for(self, arguments: List[str]) -> StructureBuilder:
        """:returns A new object on each invokation."""
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

    def new_structure_builder(self) -> StructureBuilder:
        """:returns A new object on each invokation."""
        return self._driver.structure_for(self._arguments)

    @property
    def driver(self) -> CommandDriver:
        return self._driver

    @property
    def arguments(self) -> List[str]:
        return self._arguments
