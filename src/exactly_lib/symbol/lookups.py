from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherSdv
from exactly_lib.type_system.logic.line_matcher import LineMatcherSdv
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
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


def lookup_line_matcher(symbols: SymbolTable, name: str) -> LineMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, MatcherSdv), 'Referenced symbol must be MatcherSdv'
    return ret_val


def lookup_file_matcher(symbols: SymbolTable, name: str) -> FileMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, MatcherSdv), 'Referenced symbol must be MatcherSdv'
    return ret_val


def lookup_files_matcher(symbols: SymbolTable, name: str) -> FilesMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, MatcherSdv), 'Referenced symbol must be MatcherSdv'
    return ret_val


def lookup_string_matcher(symbols: SymbolTable, name: str) -> StringMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, MatcherSdv), 'Referenced symbol must be MatcherSdv'
    return ret_val


def lookup_string_transformer(symbols: SymbolTable, name: str) -> StringTransformerSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, StringTransformerSdv), 'Referenced symbol must be StringTransformerSdv'
    return ret_val


def lookup_and_resolve_string_transformer(symbols: SymbolTable, name: str) -> StringTransformerDdv:
    return lookup_string_transformer(symbols, name).resolve(symbols)


def lookup_program(symbols: SymbolTable, name: str) -> ProgramSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, ProgramSdv), 'Referenced symbol must be ProgramSdv'
    return ret_val


def lookup_files_condition(symbols: SymbolTable, name: str) -> FilesConditionSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, FilesConditionSdv), 'Referenced symbol must be FilesConditionSdv'
    return ret_val


def lookup_and_resolve_program(symbols: SymbolTable, name: str) -> ProgramDdv:
    return lookup_program(symbols, name).resolve(symbols)


def lookup_container(symbols: SymbolTable, name: str) -> SymbolContainer:
    container = symbols.lookup(name)
    assert isinstance(container, SymbolContainer), 'Value in SymTbl must be SymbolContainer'
    return container
