import unittest

from exactly_lib.symbol.data import string_resolver as sr, path_resolver as pr, list_resolver as lr, \
    concrete_resolvers as sut
from exactly_lib.symbol.data.string_resolver import string_constant
from exactly_lib.symbol.data.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    equals_multi_dir_dependent_value
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
        actual = sut.list_constant(constant)
        # ASSERT #
        self.assertEqual([], actual.references,
                         'references')
        actual_value = actual.resolve(empty_symbol_table())
        expected_value = AMultiDirDependentValue(resolving_dependencies=set(),
                                                 value_when_no_dir_dependencies=do_return(constant),
                                                 value_of_any_dependency=do_return(constant))
        equals_multi_dir_dependent_value(expected_value).apply_with_message(self, actual_value, 'resolve value')


class TestValueVisitor(unittest.TestCase):
    def test_visit_file_ref(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('ret-val')
        # ACT #
        ret_val = visitor.visit(FileRefConstant(file_ref_test_impl()))
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
        ret_val = visitor.visit(string_constant('string'))
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
            visitor.visit('a string is not a SymbolReference')


class _ValueVisitorTestThatRegistersClassOfVisitedObjects(sut.SymbolValueResolverVisitor):
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.visited_classes = []

    def _visit_file_ref(self, value: pr.FileRefResolver):
        self.visited_classes.append(pr.FileRefResolver)
        return self.ret_val

    def _visit_string(self, value: sr.StringResolver):
        self.visited_classes.append(sr.StringResolver)
        return self.ret_val

    def _visit_list(self, value: lr.ListResolver):
        self.visited_classes.append(lr.ListResolver)
        return self.ret_val
