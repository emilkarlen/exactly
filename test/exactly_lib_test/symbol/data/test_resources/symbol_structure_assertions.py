import unittest

from exactly_lib.symbol import resolver_structure as rs, symbol_usage as su
from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib_test.symbol.data.test_resources.any_resolver_assertions import equals_resolver
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def equals_container(expected: rs.SymbolContainer,
                     ignore_source_line: bool = True) -> ValueAssertion[rs.SymbolContainer]:
    component_assertions = []
    if not ignore_source_line:
        component_assertions.append(asrt.sub_component('source',
                                                       rs.SymbolContainer.definition_source.fget,
                                                       equals_line_sequence(expected.definition_source)))
    expected_resolver = expected.resolver
    assert isinstance(expected_resolver, DataValueResolver), 'All actual values must be DataValueResolver'
    component_assertions.append(asrt.sub_component('resolver',
                                                   rs.SymbolContainer.resolver.fget,
                                                   equals_resolver(expected_resolver)))
    return asrt.is_instance_with(rs.SymbolContainer,
                                 asrt.and_(component_assertions))


def equals_symbol(expected: su.SymbolDefinition,
                  ignore_source_line: bool = True) -> ValueAssertion[su.SymbolDefinition]:
    return asrt.is_instance_with(su.SymbolDefinition,
                                 asrt.And([
                                     asrt.sub_component('name',
                                                        su.SymbolDefinition.name.fget,
                                                        asrt.equals(expected.name)),
                                     asrt.sub_component('resolver_container',
                                                        su.SymbolDefinition.resolver_container.fget,
                                                        equals_container(expected.resolver_container,
                                                                         ignore_source_line)),

                                 ])
                                 )


def equals_symbol_table(expected: rs.SymbolTable,
                        ignore_source_line: bool = True) -> ValueAssertion[rs.SymbolTable]:
    return _EqualsSymbolTable(expected, ignore_source_line)


class _EqualsSymbolTable(ValueAssertionBase):
    def __init__(self,
                 expected: rs.SymbolTable,
                 ignore_source_line: bool = True
                 ):
        self.ignore_source_line = ignore_source_line
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, rs.SymbolTable)
        assert isinstance(value, rs.SymbolTable)
        put.assertEqual(self.expected.names_set,
                        value.names_set,
                        message_builder.apply('names in symbol table'))
        for name in self.expected.names_set:
            actual_value = value.lookup(name)

            put.assertIsInstance(actual_value, rs.SymbolContainer,
                                 message_builder.apply('actual container for ' + name))
            assert isinstance(actual_value, rs.SymbolContainer)

            expected_container = self.expected.lookup(name)

            put.assertIsInstance(expected_container, rs.SymbolContainer,
                                 message_builder.apply('expected container for ' + name))
            assert isinstance(expected_container, rs.SymbolContainer)

            equals_container(expected_container).apply(put,
                                                       actual_value,
                                                       message_builder.for_sub_component('Value of symbol ' + name))
