import unittest

from exactly_lib.symbol import symbol_usage as sut
from exactly_lib.symbol.concrete_restrictions import NoRestriction
from exactly_lib.symbol.value_structure import ReferenceRestrictions
from exactly_lib_test.symbol.test_resources.symbol_utils import file_ref_value_container


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSymbolUsageVisitor)


class TestSymbolUsageVisitor(unittest.TestCase):
    def test_visit_definition(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        ret_val = visitor.visit(sut.SymbolDefinition('name', file_ref_value_container()))
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
            sut.SymbolReference('name', ReferenceRestrictions(NoRestriction())))
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

    def _visit_reference(self, symbol_usage: sut.SymbolReference):
        self.visited_classes.append(sut.SymbolReference)
        return symbol_usage.name

    def _visit_definition(self, symbol_usage: sut.SymbolDefinition):
        self.visited_classes.append(sut.SymbolReference)
        return symbol_usage.name
