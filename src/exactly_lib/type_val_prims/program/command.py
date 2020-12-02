"""
OS independent representation of something that is executable in process.

Supports the different variants of executable things used by Exactly.
"""
from abc import ABC, abstractmethod
from typing import List, Sequence

from exactly_lib.type_val_prims.description.structure_building import StructureBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree.renderer import NodeRenderer, NODE_DATA
from exactly_lib.util.description_tree.tree import Node


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

    def structure(self) -> StructureBuilder:
        """:returns A new object on each invokation."""
        return self._driver.structure_for(self._arguments)

    def structure_renderer(self) -> StructureRenderer:
        return _CommandStructureRenderer(self)

    @property
    def driver(self) -> CommandDriver:
        return self._driver

    @property
    def arguments(self) -> List[str]:
        return self._arguments


class _CommandStructureRenderer(NodeRenderer[None]):
    def __init__(self, command: Command):
        self._command = command

    def render(self) -> Node[NODE_DATA]:
        return self._command.structure().build().render()
