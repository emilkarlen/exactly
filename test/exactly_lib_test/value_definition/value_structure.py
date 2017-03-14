import unittest

from exactly_lib.value_definition import value_structure as sut
from exactly_lib.value_definition.concrete_restrictions import NoRestriction
from exactly_lib_test.value_definition.test_resources.values2 import file_ref_value_container


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestValueVisitor)


class TestValueVisitor(unittest.TestCase):
    def test_visit_definition(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        ret_val = visitor.visit(sut.ValueDefinition2('name', file_ref_value_container()))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.ValueReference2],
                             'visited classes')
        self.assertEqual('name', ret_val,
                         'Visitor is expected to return return value of visit-method')

    def test_visit_reference(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        ret_val = visitor.visit(sut.ValueReference2('name', NoRestriction()))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.ValueReference2],
                             'visited classes')
        self.assertEqual('name', ret_val,
                         'Visitor is expected to return return value of visit-method')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class _ValueVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueUsageVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_reference(self, value_usage: sut.ValueReference2):
        self.visited_classes.append(sut.ValueReference2)
        return value_usage.name

    def _visit_definition(self, value_usage: sut.ValueDefinition2):
        self.visited_classes.append(sut.ValueReference2)
        return value_usage.name
