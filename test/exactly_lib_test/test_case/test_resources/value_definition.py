import exactly_lib.test_case.file_refs
from exactly_lib.test_case import file_ref as _file_ref
from exactly_lib.test_case.value_definition import ValueInfo, ValueEntry, SymbolTable
from exactly_lib.util.line_source import Line


def info(file_ref: _file_ref.FileRef = exactly_lib.test_case.file_refs.rel_cwd('file-name-rel-cd'),
         line_num: int = 1,
         source_line: str = 'value def line') -> ValueInfo:
    return ValueInfo(Line(line_num, source_line),
                     file_ref)


def entry(name: str, info_: ValueInfo = info()) -> ValueEntry:
    return ValueEntry(name, info_)


def symbol_table_from_names(names: iter) -> SymbolTable:
    elements = [(name, info(source_line=name,
                            file_ref=exactly_lib.test_case.file_refs.rel_cwd(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_value_definitions(value_definitions: iter) -> SymbolTable:
    elements = [(vd.name, info(source_line=vd.name,
                               file_ref=exactly_lib.test_case.file_refs.rel_cwd(vd.name)))
                for vd in value_definitions]
    return SymbolTable(dict(elements))
