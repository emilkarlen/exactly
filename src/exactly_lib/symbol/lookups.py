from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.file_matcher import FileMatcherStv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv, ProgramStv
from exactly_lib.symbol.logic.string_matcher import StringMatcherStv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv, StringTransformerStv
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.file_matcher import GenericFileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import GenericFilesMatcherSdv
from exactly_lib.type_system.logic.line_matcher import GenericLineMatcherSdv
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.util.symbol_table import SymbolTable


def lookup_string(symbols: SymbolTable, name: str) -> StringSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, StringSdv), 'Referenced symbol must be StringSdv'
    return ret_val


def lookup_and_resolve_string(symbols: SymbolTable, name: str) -> StringDdv:
    return lookup_string(symbols, name).resolve(symbols)


def lookup_list(symbols: SymbolTable, name: str) -> ListSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, ListSdv), 'Referenced symbol must be ListSdv'
    return ret_val


def lookup_and_resolve_list(symbols: SymbolTable, name: str) -> ListDdv:
    return lookup_list(symbols, name).resolve(symbols)


def lookup_path(symbols: SymbolTable, name: str) -> PathSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, PathSdv), 'Referenced symbol must be PathSdv'
    return ret_val


def lookup_and_resolve_path(symbols: SymbolTable, name: str) -> PathDdv:
    return lookup_path(symbols, name).resolve(symbols)


def lookup_line_matcher(symbols: SymbolTable, name: str) -> GenericLineMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, LineMatcherStv), 'Referenced symbol must be LineMatcherStv'
    return ret_val.value()


def lookup_file_matcher(symbols: SymbolTable, name: str) -> GenericFileMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, FileMatcherStv), 'Referenced symbol must be FileMatcherStv'
    return ret_val.value()


def lookup_files_matcher(symbols: SymbolTable, name: str) -> GenericFilesMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, FilesMatcherStv), 'Referenced symbol must be FilesMatcherStv'
    return ret_val.value()


def lookup_string_matcher(symbols: SymbolTable, name: str) -> GenericStringMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, StringMatcherStv), 'Referenced symbol must be StringMatcherStv'
    return ret_val.value()


def lookup_string_transformer(symbols: SymbolTable, name: str) -> StringTransformerSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, StringTransformerStv), 'Referenced symbol must be StringTransformerStv'
    return ret_val.value()


def lookup_and_resolve_string_transformer(symbols: SymbolTable, name: str) -> StringTransformerDdv:
    return lookup_string_transformer(symbols, name).resolve(symbols)


def lookup_program(symbols: SymbolTable, name: str) -> ProgramSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, ProgramStv), 'Referenced symbol must be ProgramStv'
    return ret_val.value()


def lookup_and_resolve_program(symbols: SymbolTable, name: str) -> ProgramDdv:
    return lookup_program(symbols, name).resolve(symbols)


def lookup_container(symbols: SymbolTable, name: str) -> SymbolContainer:
    container = symbols.lookup(name)
    assert isinstance(container, SymbolContainer), 'Value in SymTbl must be SymbolContainer'
    return container
