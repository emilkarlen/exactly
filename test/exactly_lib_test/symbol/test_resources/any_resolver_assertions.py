import unittest

from exactly_lib.symbol.concrete_resolvers import SymbolValueResolverVisitor
from exactly_lib.symbol.list_resolver import ListResolver
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_file_ref_resolver, \
    equals_string_resolver
from exactly_lib_test.symbol.test_resources.list_assertions import equals_list_resolver
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_resolver(expected: SymbolValueResolver) -> asrt.ValueAssertion:
    return _EqualsValue(expected)


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
