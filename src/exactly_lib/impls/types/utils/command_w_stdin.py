from typing import Sequence

from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program import program
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class CommandWStdin:
    def __init__(self,
                 command: Command,
                 stdin: Sequence[StringSource],
                 ):
        self.command = command
        self.stdin = stdin

    def structure(self) -> StructureRenderer:
        return program.command_w_stdin_renderer(
            self.command.new_structure_builder(),
            self.stdin,
        )
