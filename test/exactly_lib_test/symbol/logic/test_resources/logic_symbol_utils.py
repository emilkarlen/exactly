from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv, ProgramStv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv, StringTransformerStv
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib_test.symbol.test_resources import symbol_utils


def container_of_program_sdv(sdv: ProgramSdv) -> SymbolContainer:
    return symbol_utils.container(ProgramStv(sdv))


def container_of_string_transformer_sdv(sdv: StringTransformerSdv) -> SymbolContainer:
    return symbol_utils.container(StringTransformerStv(sdv))
