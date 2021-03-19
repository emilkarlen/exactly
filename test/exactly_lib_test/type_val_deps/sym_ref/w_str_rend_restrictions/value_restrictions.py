import unittest

from exactly_lib.symbol import value_type
from exactly_lib.symbol.value_type import WithStrRenderingType
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import value_restrictions as sut
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.type_val_deps.types.list_.test_resources import list_
from exactly_lib_test.type_val_deps.types.path.test_resources import symbol_context as path
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import PathSymbolValueContext
from exactly_lib_test.type_val_deps.types.path.test_resources.simple_path import path_test_impl
from exactly_lib_test.type_val_deps.types.string_.test_resources import symbol_context as string
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolValueContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources import symbol_context as st_symbol_context
from exactly_lib_test.type_val_deps.types.test_resources import file_matcher


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnySymbolTypeRestriction),
        unittest.makeSuite(TestStringRestriction),
        unittest.makeSuite(TestPathRelativityRestriction),
    ])


class TestAnySymbolTypeRestriction(unittest.TestCase):
    def test_any__pass_WHEN_type_is_w_str_rendering(self):
        # ARRANGE #
        test_cases = [
            string.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            path.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            list_.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
        restriction = sut.ArbitraryValueWStrRenderingRestriction.of_any()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value.container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_any__fail_WHEN_type_is_wo_str_rendering(self):
        # ARRANGE #
        test_cases = [
            file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            st_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
        restriction = sut.ArbitraryValueWStrRenderingRestriction.of_any()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value.container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')

    def test_single__pass_WHEN_type_expected(self):
        # ARRANGE #
        test_cases = [
            string.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            path.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            list_.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
        symbols = empty_symbol_table()
        for value in test_cases:
            restriction = sut.ArbitraryValueWStrRenderingRestriction.of_single(
                value_type.VALUE_TYPE_2_W_STR_RENDERING_TYPE[value.value_type]
            )
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value.container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_single__fail_WHEN_type_is_unexpected(self):
        # ARRANGE #
        restriction = sut.ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING)
        test_cases = [
            path.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            list_.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            st_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
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
        restriction = sut.is_string()
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
        restriction = sut.is_string()
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
        restriction = sut.PathAndRelativityRestriction(
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
        restriction = sut.PathAndRelativityRestriction(
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


def path_constant_sdv() -> PathSdv:
    return path_sdvs.constant(path_test_impl('file-name-rel-home',
                                             relativity=RelOptionType.REL_HDS_CASE))
