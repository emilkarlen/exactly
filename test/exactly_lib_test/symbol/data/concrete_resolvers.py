import unittest

from exactly_lib.symbol.data import list_resolvers, file_ref_resolvers
from exactly_lib.symbol.data import string_resolver as sr, file_ref_resolver as pr, list_resolver as lr, \
    visitor as sut
from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib.symbol.data.string_resolvers import str_constant
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system.value_type import ValueType, DataValueType
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    matches_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueVisitor),
        unittest.makeSuite(TestConstants),
    ])


class TestConstants(unittest.TestCase):
    def test_list_constant(self):
        # ARRANGE #
        constant = ['a', 'b' 'c']
        # ACT #
        actual = list_resolvers.from_str_constants(constant)
        # ASSERT #
        self.assertEqual([], actual.references,
                         'references')
        actual_value = actual.resolve(empty_symbol_table())
        expected_value = AMultiDirDependentValue(resolving_dependencies=set(),
                                                 get_value_when_no_dir_dependencies=do_return(constant),
                                                 get_value_of_any_dependency=do_return(constant))
        matches_multi_dir_dependent_value(expected_value).apply_with_message(self, actual_value, 'resolve value')


class TestValueVisitor(unittest.TestCase):
    def test_visit_file_ref(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('ret-val')
        # ACT #
        ret_val = visitor.visit(file_ref_resolvers.constant(file_ref_test_impl()))
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [pr.FileRefResolver],
                             'visited classes')

    def test_visit_string(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(str_constant('string'))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sr.StringResolver],
                             'visited classes')

    def test_visit_list(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(lr.ListResolver([]))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [lr.ListResolver],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(_UnknownDataValueResolver())


class _ValueVisitorTestThatRegistersClassOfVisitedObjects(sut.DataValueResolverPseudoVisitor):
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.visited_classes = []

    def visit_file_ref(self, value: pr.FileRefResolver):
        self.visited_classes.append(pr.FileRefResolver)
        return self.ret_val

    def visit_string(self, value: sr.StringResolver):
        self.visited_classes.append(sr.StringResolver)
        return self.ret_val

    def visit_list(self, value: lr.ListResolver):
        self.visited_classes.append(lr.ListResolver)
        return self.ret_val


class _UnknownDataValueResolver(DataValueResolver):
    @property
    def data_value_type(self) -> DataValueType:
        raise NotImplementedError('not used')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('not used')

    @property
    def references(self) -> list:
        raise NotImplementedError('not used')

    def resolve(self, symbols: SymbolTable) -> DirDependentValue:
        raise NotImplementedError('not used')
