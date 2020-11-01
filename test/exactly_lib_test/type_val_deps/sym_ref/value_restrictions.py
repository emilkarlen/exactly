import unittest
from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.data import value_restrictions as vr
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.tcfs.test_resources.simple_path import path_test_impl
from exactly_lib_test.type_val_deps.types.list_.test_resources import list_
from exactly_lib_test.type_val_deps.types.path.test_resources import path
from exactly_lib_test.type_val_deps.types.path.test_resources.path import PathSymbolValueContext
from exactly_lib_test.type_val_deps.types.string.test_resources import string
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolValueContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources import symbol_context as st_symbol_context
from exactly_lib_test.type_val_deps.types.test_resources import file_matcher


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnySymbolTypeRestriction),
        unittest.makeSuite(TestStringRestriction),
        unittest.makeSuite(TestPathRelativityRestriction),
        unittest.makeSuite(TestValueRestrictionVisitor),
    ])


class TestAnySymbolTypeRestriction(unittest.TestCase):
    def test_pass_WHEN_type_category_is_data(self):
        # ARRANGE #
        test_cases = [
            string.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            path.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            list_.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
        restriction = vr.AnyDataTypeRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value.container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail_WHEN_type_category_is_not_data(self):
        # ARRANGE #
        test_cases = [
            file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            st_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
        restriction = vr.AnyDataTypeRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value.container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestStringRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            StringSymbolValueContext.of_constant('string'),
            StringSymbolValueContext.of_constant(''),
        ]
        restriction = vr.StringRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value.container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__not_a_string(self):
        # ARRANGE #
        test_cases = [
            path.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
        restriction = vr.StringRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value.container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestPathRelativityRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            RelOptionType.REL_ACT,
            RelOptionType.REL_HDS_CASE,
        ]
        restriction = vr.PathRelativityRestriction(
            PathRelativityVariants(
                {RelOptionType.REL_ACT, RelOptionType.REL_HDS_CASE, RelOptionType.REL_RESULT},
                False))
        symbols = empty_symbol_table()
        for actual_relativity in test_cases:
            with self.subTest(msg='actual_relativity=' + str(actual_relativity)):
                container = PathSymbolValueContext.of_rel_opt_and_suffix(actual_relativity, 'base-name').container
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__relative_paths(self):
        # ARRANGE #
        test_cases = [
            RelOptionType.REL_ACT,
            RelOptionType.REL_HDS_CASE,
        ]
        restriction = vr.PathRelativityRestriction(
            PathRelativityVariants(
                {RelOptionType.REL_RESULT},
                False))
        symbols = empty_symbol_table()
        for actual_relativity in test_cases:
            with self.subTest(msg='value=' + str(actual_relativity)):
                container = PathSymbolValueContext.of_rel_opt_and_suffix(actual_relativity, 'base-name').container
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestValueRestrictionVisitor(unittest.TestCase):
    def test_none(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(vr.AnyDataTypeRestriction())
        # ASSERT #
        self.assertEqual([vr.AnyDataTypeRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_string(self):
        # ARRANGE #
        expected_return_value = 87
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(vr.StringRestriction())
        # ASSERT #
        self.assertEqual([vr.StringRestriction],
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
            vr.PathRelativityRestriction(
                PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertEqual([vr.PathRelativityRestriction],
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
            visitor.visit(UnknownValueRestriction())


class _VisitorThatRegisterClassOfVisitMethod(vr.ValueRestrictionVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_none(self, x: vr.AnyDataTypeRestriction):
        self.visited_classes.append(vr.AnyDataTypeRestriction)
        return self.return_value

    def visit_string(self, x: vr.StringRestriction):
        self.visited_classes.append(vr.StringRestriction)
        return self.return_value

    def visit_path_relativity(self,
                              x: vr.PathRelativityRestriction):
        self.visited_classes.append(vr.PathRelativityRestriction)
        return self.return_value


def path_constant_sdv() -> PathSdv:
    return path_sdvs.constant(path_test_impl('file-name-rel-home',
                                             relativity=RelOptionType.REL_HDS_CASE))


class UnknownValueRestriction(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        raise NotImplementedError('the method should never be called')
