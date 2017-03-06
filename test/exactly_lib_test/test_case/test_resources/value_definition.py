from exactly_lib.test_case import file_ref as _file_ref
from exactly_lib.test_case import file_refs
from exactly_lib.test_case.value_definition import FileRefValue
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Value, Entry


def file_ref_value(file_ref: _file_ref.FileRef = file_refs.rel_cwd('file-name-rel-cd'),
                   line_num: int = 1,
                   source_line: str = 'value def line') -> Value:
    return FileRefValue(Line(line_num, source_line),
                        file_ref)


def entry(name: str, value_: Value = file_ref_value()) -> Entry:
    return Entry(name, value_)


def symbol_table_from_none_or_value(symbol_table_or_none: SymbolTable) -> SymbolTable:
    return SymbolTable() if symbol_table_or_none is None else symbol_table_or_none


def symbol_table_from_names(names: iter) -> SymbolTable:
    elements = [(name, file_ref_value(source_line=name,
                                      file_ref=file_refs.rel_cwd(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_value_definitions(value_definitions: iter) -> SymbolTable:
    elements = [(vd.name, file_ref_value(source_line=vd.name,
                                         file_ref=file_refs.rel_cwd(vd.name)))
                for vd in value_definitions]
    return SymbolTable(dict(elements))
