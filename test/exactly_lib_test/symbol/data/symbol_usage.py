import unittest

from exactly_lib.symbol import symbol_usage as sut
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnySymbolTypeRestriction
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import file_ref_constant_container


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSymbolUsageVisitor)


class TestSymbolUsageVisitor(unittest.TestCase):
    def test_visit_definition(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        ret_val = visitor.visit(sut.SymbolDefinition('name', file_ref_constant_container()))
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
            sut.SymbolReference('name', ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction())))
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
