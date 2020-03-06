from exactly_lib.symbol.logic.file_matcher import FileMatcherStv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv, ProgramStv
from exactly_lib.symbol.logic.string_matcher import StringMatcherStv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv, StringTransformerStv
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.type_system.logic.file_matcher import GenericFileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import GenericFilesMatcherSdv
from exactly_lib.type_system.logic.line_matcher import GenericLineMatcherSdv
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib_test.symbol.test_resources import symbol_utils


def container_of_program_sdv(sdv: ProgramSdv) -> SymbolContainer:
    return symbol_utils.container(ProgramStv(sdv))


def container_of_string_transformer_sdv(sdv: StringTransformerSdv) -> SymbolContainer:
    return symbol_utils.container(StringTransformerStv(sdv))


def container_of_line_matcher_sdv(sdv: GenericLineMatcherSdv) -> SymbolContainer:
    return symbol_utils.container(LineMatcherStv(sdv))


def container_of_string_matcher_sdv(sdv: GenericStringMatcherSdv) -> SymbolContainer:
    return symbol_utils.container(StringMatcherStv(sdv))


def container_of_file_matcher_sdv(sdv: GenericFileMatcherSdv) -> SymbolContainer:
    return symbol_utils.container(FileMatcherStv(sdv))


def container_of_files_matcher_sdv(sdv: GenericFilesMatcherSdv) -> SymbolContainer:
    return symbol_utils.container(FilesMatcherStv(sdv))
