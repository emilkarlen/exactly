import unittest

from exactly_lib.symbol import sdv_structure as sut
from exactly_lib.symbol.sdv_structure import SymbolDefinition, SymbolContainer
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.symbol.test_resources.reference_restrictions import UnconditionallyValidReferenceRestrictions
from exactly_lib_test.symbol.test_resources.symbol_dependent_value import SymbolDependentValueForTest


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSymbolUsageVisitor)


class TestSymbolUsageVisitor(unittest.TestCase):
    def test_visit_definition(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        definition = SymbolDefinition('name',
                                      SymbolContainer(SymbolDependentValueForTest(),
                                                      ValueType.STRING,
                                                      None),
                                      )
        # ACT #
        ret_val = visitor.visit(definition)
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.SymbolReference],
                             'visited classes')
        self.assertEqual('name', ret_val,
                         'Visitor is expected to return return value of visit-method')

    def test_visit_reference(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        ret_val = visitor.visit(
            sut.SymbolReference('name', UnconditionallyValidReferenceRestrictions()))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.SymbolReference],
                             'visited classes')
        self.assertEqual('name', ret_val,
                         'Visitor is expected to return return value of visit-method')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a SymbolReference')


class _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects(sut.SymbolUsageVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_reference(self, usage: sut.SymbolReference):
        self.visited_classes.append(sut.SymbolReference)
        return usage.name

    def _visit_definition(self, usage: sut.SymbolDefinition):
        self.visited_classes.append(sut.SymbolReference)
        return usage.name
