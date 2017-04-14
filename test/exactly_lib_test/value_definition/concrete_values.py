import unittest

from exactly_lib.value_definition import concrete_values as sut
from exactly_lib.value_definition.file_ref_resolvers import FileRefConstant
from exactly_lib.value_definition.value_resolvers.string_resolvers import StringConstant
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestValueVisitor)


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
        ret_val = visitor.visit(StringConstant('string'))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.StringResolver],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class _ValueVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueVisitor):
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.visited_classes = []

    def _visit_file_ref(self, value: sut.FileRefResolver):
        self.visited_classes.append(sut.FileRefResolver)
        return self.ret_val

    def _visit_string(self, value: sut.StringResolver):
        self.visited_classes.append(sut.StringResolver)
        return self.ret_val
