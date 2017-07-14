import unittest

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol import value_structure as stc
from exactly_lib.symbol.value_structure import SymbolValueResolver
from exactly_lib_test.section_document.test_resources.assertions import equals_line
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_resolver
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_container(expected: stc.ResolverContainer,
                     ignore_source_line: bool = True) -> asrt.ValueAssertion:
    component_assertions = []
    if not ignore_source_line:
        component_assertions.append(asrt.sub_component('source',
                                                       stc.ResolverContainer.definition_source.fget,
                                                       equals_line(expected.definition_source)))
    expected_value = expected.value
    assert isinstance(expected_value, SymbolValueResolver), 'All actual values must be SymbolValue'
    component_assertions.append(asrt.sub_component('value',
                                                   stc.ResolverContainer.value.fget,
                                                   equals_resolver(expected_value)))
    return asrt.is_instance_with(stc.ResolverContainer,
                                 asrt.and_(component_assertions))


def equals_symbol(expected: su.SymbolDefinition,
                  ignore_source_line: bool = True) -> asrt.ValueAssertion:
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


def equals_symbol_table(expected: stc.SymbolTable,
                        ignore_source_line: bool = True) -> asrt.ValueAssertion:
    return _EqualsSymbolTable(expected, ignore_source_line)


class _EqualsSymbolTable(asrt.ValueAssertion):
    def __init__(self,
                 expected: stc.SymbolTable,
                 ignore_source_line: bool = True
                 ):
        self.ignore_source_line = ignore_source_line
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, stc.SymbolTable)
        assert isinstance(value, stc.SymbolTable)
        put.assertEqual(self.expected.names_set,
                        value.names_set,
                        message_builder.apply('names in symbol table'))
        for name in self.expected.names_set:
            actual_value = value.lookup(name)
            expected_container = self.expected.lookup(name)
            equals_container(expected_container).apply_with_message(put, actual_value,
                                                                    message_builder.apply('Value of symbol ' + name))
