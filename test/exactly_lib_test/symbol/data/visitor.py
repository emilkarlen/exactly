import unittest
from typing import List
from typing import Type

from exactly_lib.symbol.data import visitor as sut
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.dir_dependent_value import DependenciesAwareDdv
from exactly_lib.type_system.value_type import DataValueType
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.test_resources import string_resolvers, list_resolvers, path_resolvers


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestVisitor)


class TestVisitor(unittest.TestCase):
    def _check(self,
               resolver_class: Type,
               resolver: sut.DataValueResolver,
               expected_ret_val: str,
               ):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods(expected_ret_val)

        actual_ret_val = visitor.visit(resolver)

        # ASSERT #

        self.assertEqual(expected_ret_val,
                         actual_ret_val,
                         'return value')

        self.assertEqual([resolver_class],
                         visitor.visited_types,
                         'visited classes')

    def test_visit_string(self):
        self._check(
            sut.StringResolver,
            string_resolvers.arbitrary_resolver(),
            'ret val',
        )

    def test_visit_path(self):
        self._check(
            sut.PathResolver,
            path_resolvers.arbitrary_resolver(),
            'other ret val',
        )

    def test_visit_list(self):
        self._check(
            sut.ListResolver,
            list_resolvers.arbitrary_resolver(),
            'ret val',
        )

    def test_visit_unknown_type(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(UnknownDataTypeResolverClass())
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.DataValueResolverPseudoVisitor[str]):
    def __init__(self, ret_val: str):
        self._ret_val = ret_val
        self.visited_types = []

    def visit_string(self, value: sut.StringResolver) -> str:
        self.visited_types.append(sut.StringResolver)
        return self._ret_val

    def visit_path(self, value: sut.PathResolver) -> str:
        self.visited_types.append(sut.PathResolver)
        return self._ret_val

    def visit_list(self, value: sut.ListResolver) -> str:
        self.visited_types.append(sut.ListResolver)
        return self._ret_val


class UnknownDataTypeResolverClass(sut.DataValueResolver):
    @property
    def data_value_type(self) -> DataValueType:
        raise NotImplementedError('unsupported')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('unsupported')

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('unsupported')

    def resolve(self, symbols: SymbolTable) -> DependenciesAwareDdv:
        raise NotImplementedError('unsupported')
