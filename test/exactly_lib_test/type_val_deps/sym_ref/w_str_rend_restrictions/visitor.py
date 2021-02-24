import unittest

from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions as sut, \
    value_restrictions as vr
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_type_reference_visitor


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestReferenceRestrictionVisitor)


class TestReferenceRestrictionVisitor(unittest.TestCase):
    def test_direct_and_indirect(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.ReferenceRestrictionsOnDirectAndIndirect(
            vr.ArbitraryValueWStrRenderingRestriction.of_any()))
        # ASSERT #
        self.assertEqual([sut.ReferenceRestrictionsOnDirectAndIndirect],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_or(self):
        # ARRANGE #
        expected_return_value = 87
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.OrReferenceRestrictions([]))
        # ASSERT #
        self.assertEqual([sut.OrReferenceRestrictions],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod("not used")
        invalid_value = 'a string is not a sub class of ' + str(ValueRestriction)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            visitor.visit(invalid_value)


class _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(
    data_type_reference_visitor.TypeWithStrRenderingReferenceRestrictionsVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_direct_and_indirect(self, x: sut.ReferenceRestrictionsOnDirectAndIndirect):
        self.visited_classes.append(sut.ReferenceRestrictionsOnDirectAndIndirect)
        return self.return_value

    def visit_or(self, x: sut.OrReferenceRestrictions):
        self.visited_classes.append(sut.OrReferenceRestrictions)
        return self.return_value


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
