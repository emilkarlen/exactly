from typing import Sequence

from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.phases.common import SymbolUser


class ProgramToExecute(SymbolUser):
    def __init__(self, program: ProgramSdv):
        self._program = program

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._program.references

    @property
    def program(self) -> ProgramSdv:
        return self._program
