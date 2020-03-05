from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv, ProgramStv
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib_test.symbol.test_resources import symbol_utils


def container_of_program_sdv(sdv: ProgramSdv) -> SymbolContainer:
    return symbol_utils.container(ProgramStv(sdv))
