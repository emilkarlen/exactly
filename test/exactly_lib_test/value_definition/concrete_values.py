import unittest

from exactly_lib.value_definition import concrete_values as sut
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestValueVisitor)


class TestValueVisitor(unittest.TestCase):
    def test_visit_file_ref(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        visitor.visit(sut.FileRefValue(file_ref_test_impl()))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.FileRefValue],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class _ValueVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_file_ref(self, value: sut.FileRefValue):
        self.visited_classes.append(sut.FileRefValue)
