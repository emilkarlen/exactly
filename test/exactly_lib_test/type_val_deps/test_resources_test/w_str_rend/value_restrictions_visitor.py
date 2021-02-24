import unittest
from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import value_restrictions as vr
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.value_restrictions_visitor import \
    ProdValueRestrictionVariantsVisitor


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestProdValueRestrictionVisitor)


class TestProdValueRestrictionVisitor(unittest.TestCase):
    def test_any(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(vr.ArbitraryValueWStrRenderingRestriction.of_any())
        # ASSERT #
        self.assertEqual([vr.ArbitraryValueWStrRenderingRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_path(self):
        # ARRANGE #
        expected_return_value = 69
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(
            vr.PathAndRelativityRestriction(
                PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertEqual([vr.PathAndRelativityRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        visitor = _VisitorThatRegisterClassOfVisitMethod("not used")
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            visitor.visit(_UnknownValueRestriction())


class _UnknownValueRestriction(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        raise NotImplementedError('the method should never be called')


class _VisitorThatRegisterClassOfVisitMethod(ProdValueRestrictionVariantsVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_any(self, x: vr.ArbitraryValueWStrRenderingRestriction):
        self.visited_classes.append(vr.ArbitraryValueWStrRenderingRestriction)
        return self.return_value

    def visit_path_relativity(self,
                              x: vr.PathAndRelativityRestriction):
        self.visited_classes.append(vr.PathAndRelativityRestriction)
        return self.return_value


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
