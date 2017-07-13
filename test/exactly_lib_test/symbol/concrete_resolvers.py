import unittest

from exactly_lib.symbol import concrete_resolvers as sut
from exactly_lib.symbol import string_resolver as sr
from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueVisitor),
    ])


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
                             [sut.FileRefResolver],
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

    def _visit_file_ref(self, value: sut.FileRefResolver):
        self.visited_classes.append(sut.FileRefResolver)
        return self.ret_val

    def _visit_string(self, value: sr.StringResolver):
        self.visited_classes.append(sr.StringResolver)
        return self.ret_val
