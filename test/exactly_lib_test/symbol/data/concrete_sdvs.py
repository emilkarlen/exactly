import unittest

from exactly_lib.symbol.data import list_sdvs, path_sdvs
from exactly_lib.symbol.data import string_sdv as sr, path_sdv as pr, list_sdv as lr, \
    visitor as sut
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.string_sdvs import str_constant
from exactly_lib.tcfs.dir_dependent_value import DependenciesAwareDdv
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.tcfs.test_resources.dir_dependent_value import \
    matches_multi_dir_dependent_value
from exactly_lib_test.tcfs.test_resources.simple_path import path_test_impl
from exactly_lib_test.tcfs.test_resources_test.dir_dependent_value import AMultiDirDependentValue
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
        actual = list_sdvs.from_str_constants(constant)
        # ASSERT #
        self.assertEqual([], actual.references,
                         'references')
        actual_value = actual.resolve(empty_symbol_table())
        expected_value = AMultiDirDependentValue(resolving_dependencies=set(),
                                                 get_value_when_no_dir_dependencies=do_return(constant),
                                                 get_value_of_any_dependency=do_return(constant))
        matches_multi_dir_dependent_value(expected_value).apply_with_message(self, actual_value, 'resolve value')


class TestValueVisitor(unittest.TestCase):
    def test_visit_path(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('ret-val')
        # ACT #
        ret_val = visitor.visit(path_sdvs.constant(path_test_impl()))
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [pr.PathSdv],
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
                             [sr.StringSdv],
                             'visited classes')

    def test_visit_list(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(lr.ListSdv([]))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [lr.ListSdv],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(_UnknownDataTypeSdv())


class _ValueVisitorTestThatRegistersClassOfVisitedObjects(sut.DataTypeSdvPseudoVisitor):
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.visited_classes = []

    def visit_path(self, value: pr.PathSdv):
        self.visited_classes.append(pr.PathSdv)
        return self.ret_val

    def visit_string(self, value: sr.StringSdv):
        self.visited_classes.append(sr.StringSdv)
        return self.ret_val

    def visit_list(self, value: lr.ListSdv):
        self.visited_classes.append(lr.ListSdv)
        return self.ret_val


class _UnknownDataTypeSdv(DataTypeSdv):
    @property
    def references(self) -> list:
        raise NotImplementedError('not used')

    def resolve(self, symbols: SymbolTable) -> DependenciesAwareDdv:
        raise NotImplementedError('not used')
