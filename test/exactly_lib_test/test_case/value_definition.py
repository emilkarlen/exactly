import unittest

from exactly_lib.test_case import value_definition as sut
from exactly_lib_test.test_case.test_resources import value_definition as tr


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueDefinitionVisitor),
        unittest.makeSuite(TestValueReferenceVisitor),

    ])


class TestValueReferenceVisitor(unittest.TestCase):
    def test_visit_path(self):
        # ARRANGE #
        visitor = _ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        visitor.visit(sut.ValueReferenceOfPath('name', sut.PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.ValueReferenceOfPath],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class _ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueReferenceVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_path(self, path_reference: sut.ValueReferenceOfPath):
        self.visited_classes.append(sut.ValueReferenceOfPath)


class TestValueDefinitionVisitor(unittest.TestCase):
    def test_visit_path(self):
        # ARRANGE #
        visitor = _ValueDefinitionVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        visitor.visit(sut.ValueDefinitionOfPath('name', tr.file_ref_value()))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.ValueDefinitionOfPath],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueDefinitionVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class _ValueDefinitionVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueDefinitionVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_path(self, value_definition: sut.ValueDefinitionOfPath):
        self.visited_classes.append(sut.ValueDefinitionOfPath)
