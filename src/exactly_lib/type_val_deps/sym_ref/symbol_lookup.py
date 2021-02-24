from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesConditionSdv
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv
from exactly_lib.type_val_deps.types.integer_matcher import IntegerMatcherSdv
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
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


def lookup_integer_matcher(symbols: SymbolTable, name: str) -> IntegerMatcherSdv:
    container = lookup_container(symbols, name)
    ret_val = container.sdv
    assert isinstance(ret_val, MatcherSdv), 'Referenced symbol must be MatcherSdv'
    return ret_val


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
