from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.resolver_structure import SymbolContainer, StringTransformerResolver, LineMatcherResolver, \
    FileMatcherResolver
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.program.program_value import ProgramValue
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue
from exactly_lib.util.symbol_table import SymbolTable


def lookup_string(symbols: SymbolTable, name: str) -> StringResolver:
    container = lookup_container(symbols, name)
    ret_val = container.resolver
    assert isinstance(ret_val, StringResolver), 'Referenced symbol must be StringResolver'
    return ret_val


def lookup_and_resolve_string(symbols: SymbolTable, name: str) -> StringValue:
    return lookup_string(symbols, name).resolve(symbols)


def lookup_list(symbols: SymbolTable, name: str) -> ListResolver:
    container = lookup_container(symbols, name)
    ret_val = container.resolver
    assert isinstance(ret_val, ListResolver), 'Referenced symbol must be ListResolver'
    return ret_val


def lookup_and_resolve_list(symbols: SymbolTable, name: str) -> ListValue:
    return lookup_list(symbols, name).resolve(symbols)


def lookup_file_ref(symbols: SymbolTable, name: str) -> FileRefResolver:
    container = lookup_container(symbols, name)
    ret_val = container.resolver
    assert isinstance(ret_val, FileRefResolver), 'Referenced symbol must be FileRefResolver'
    return ret_val


def lookup_and_resolve_file_ref(symbols: SymbolTable, name: str) -> FileRef:
    return lookup_file_ref(symbols, name).resolve(symbols)


def lookup_line_matcher(symbols: SymbolTable, name: str) -> LineMatcherResolver:
    container = lookup_container(symbols, name)
    ret_val = container.resolver
    assert isinstance(ret_val, LineMatcherResolver), 'Referenced symbol must be LineMatcherResolver'
    return ret_val


def lookup_file_matcher(symbols: SymbolTable, name: str) -> FileMatcherResolver:
    container = lookup_container(symbols, name)
    ret_val = container.resolver
    assert isinstance(ret_val, FileMatcherResolver), 'Referenced symbol must be FileMatcherResolver'
    return ret_val


def lookup_string_transformer(symbols: SymbolTable, name: str) -> StringTransformerResolver:
    container = lookup_container(symbols, name)
    ret_val = container.resolver
    assert isinstance(ret_val, StringTransformerResolver), 'Referenced symbol must be ' + str(StringTransformerResolver)
    return ret_val


def lookup_and_resolve_string_transformer(symbols: SymbolTable, name: str) -> StringTransformerValue:
    return lookup_string_transformer(symbols, name).resolve(symbols)


def lookup_program(symbols: SymbolTable, name: str) -> ProgramResolver:
    container = lookup_container(symbols, name)
    ret_val = container.resolver
    assert isinstance(ret_val, ProgramResolver), 'Referenced symbol must be ProgramResolver'
    return ret_val


def lookup_and_resolve_program(symbols: SymbolTable, name: str) -> ProgramValue:
    return lookup_program(symbols, name).resolve(symbols)


def lookup_container(symbols: SymbolTable, name: str) -> SymbolContainer:
    container = symbols.lookup(name)
    assert isinstance(container, SymbolContainer), 'Value in SymTbl must be SymbolContainer'
    return container
