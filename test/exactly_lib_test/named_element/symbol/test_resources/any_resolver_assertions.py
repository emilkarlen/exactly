import unittest

from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.named_element.resolver_structure import SymbolValueResolver
from exactly_lib.named_element.symbol.concrete_resolvers import SymbolValueResolverVisitor
from exactly_lib.named_element.symbol.list_resolver import ListResolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.named_element.symbol.string_resolver import StringResolver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.named_element.symbol.test_resources.concrete_value_assertions import equals_file_ref_resolver, \
    equals_string_resolver
from exactly_lib_test.named_element.symbol.test_resources.list_assertions import equals_list_resolver
from exactly_lib_test.named_element.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_resolver(expected: SymbolValueResolver) -> asrt.ValueAssertion:
    return _EqualsValue(expected)


class MatchesPrimitiveValueResolvedOfAnyDependency(asrt.ValueAssertion):
    def __init__(self,
                 expected_resolved_primitive_value: asrt.ValueAssertion,
                 symbol_references: list,
                 symbols: SymbolTable):
        self.symbol_references = symbol_references
        self.symbols = symbols
        self.expected_resolved_primitive_value = expected_resolved_primitive_value

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, StringResolver)
        assert isinstance(value, StringResolver)  # Type info for IDE
        equals_symbol_references(self.symbol_references).apply_with_message(put,
                                                                            value.references,
                                                                            'symbol references')
        environment = PathResolvingEnvironmentPreOrPostSds(fake_home_and_sds(),
                                                           self.symbols)
        actual_resolved_prim_val = value.resolve_value_of_any_dependency(environment)
        self.expected_resolved_primitive_value.apply_with_message(put, actual_resolved_prim_val,
                                                                  'resolved primitive value')


class _EqualsSymbolValueResolverVisitor(SymbolValueResolverVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def _visit_file_ref(self, expected: FileRefResolver):
        return equals_file_ref_resolver(expected).apply(self.put, self.actual, self.message_builder)

    def _visit_string(self, expected: StringResolver):
        return equals_string_resolver(expected).apply(self.put, self.actual, self.message_builder)

    def _visit_list(self, expected: ListResolver):
        return equals_list_resolver(expected).apply(self.put, self.actual, self.message_builder)


class _EqualsValue(asrt.ValueAssertion):
    def __init__(self, expected: SymbolValueResolver):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsSymbolValueResolverVisitor(value, put, message_builder).visit(self.expected)
