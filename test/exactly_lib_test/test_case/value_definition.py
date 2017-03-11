import unittest

from exactly_lib.test_case import value_definition as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueReferenceVisitor)

    ])


class TestValueReferenceVisitor(unittest.TestCase):
    def test_visit_path(self):
        # ARRANGE #
        visitor = ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        visitor.visit(sut.ValueReferenceOfPath('name', sut.PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.ValueReferenceOfPath],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueReferenceVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_path(self, path_reference: sut.ValueReferenceOfPath):
        self.visited_classes.append(sut.ValueReferenceOfPath)
