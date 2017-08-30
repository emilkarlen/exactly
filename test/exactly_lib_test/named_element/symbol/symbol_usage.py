import unittest

from exactly_lib.named_element import named_element_usage as sut
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.named_element.symbol.restrictions.value_restrictions import AnySymbolTypeRestriction
from exactly_lib_test.named_element.symbol.test_resources.symbol_utils import file_ref_constant_container


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSymbolUsageVisitor)


class TestSymbolUsageVisitor(unittest.TestCase):
    def test_visit_definition(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        ret_val = visitor.visit(sut.NamedElementDefinition('name', file_ref_constant_container()))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.NamedElementReference],
                             'visited classes')
        self.assertEqual('name', ret_val,
                         'Visitor is expected to return return value of visit-method')

    def test_visit_reference(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        ret_val = visitor.visit(
            sut.NamedElementReference('name', ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction())))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.NamedElementReference],
                             'visited classes')
        self.assertEqual('name', ret_val,
                         'Visitor is expected to return return value of visit-method')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a SymbolReference')


class _SymbolUsageVisitorTestThatRegistersClassOfVisitedObjects(sut.NamedElementUsageVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_reference(self, usage: sut.NamedElementReference):
        self.visited_classes.append(sut.NamedElementReference)
        return usage.name

    def _visit_definition(self, usage: sut.NamedElementDefinition):
        self.visited_classes.append(sut.NamedElementReference)
        return usage.name
