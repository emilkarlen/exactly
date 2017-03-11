from exactly_lib.test_case import file_ref as _file_ref
from exactly_lib.test_case import file_refs
from exactly_lib.test_case.value_definition import FileRefValue, ValueReference
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Value, Entry
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


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
    """
    :param value_definitions: [`ValueDefinition`]
    """
    elements = [(vd.name, file_ref_value(source_line=vd.name,
                                         file_ref=file_refs.rel_cwd(vd.name)))
                for vd in value_definitions]
    return SymbolTable(dict(elements))


def symbol_table_from_entries(entries: iter) -> SymbolTable:
    """
    :param entries: [`Entry`]
    """
    elements = [(entry.name, entry.value)
                for entry in entries]
    return SymbolTable(dict(elements))


def assert_value_usages_is_singleton_list_with_value_reference(expected: ValueReference) -> asrt.ValueAssertion:
    return asrt.is_instance_with(list,
                                 asrt.And([
                                     asrt.len_equals(1),
                                     asrt.sub_component('singleton element',
                                                        lambda l: l[0],
                                                        equals_value_reference(expected))
                                 ]))


def equals_value_reference(expected: ValueReference) -> asrt.ValueAssertion:
    return asrt.is_instance_with(ValueReference,
                                 asrt.And([
                                     asrt.sub_component('name',
                                                        ValueReference.name.fget,
                                                        asrt.equals(expected.name)),

                                 ]))
