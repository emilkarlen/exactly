import unittest

from exactly_lib.symbol import restriction as sut
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.data.test_resources import list_
from exactly_lib_test.symbol.data.test_resources import path
from exactly_lib_test.symbol.test_resources import line_matcher, string_matcher, string_transformer, \
    file_matcher, program
from exactly_lib_test.symbol.test_resources import string
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSymbolValueContext
from exactly_lib_test.symbol.test_resources.string import StringSymbolValueContext
from exactly_lib_test.test_case_utils.files_matcher.test_resources import symbol_context as files_matcher_symbol_context


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestElementTypeRestriction),
        unittest.makeSuite(TestValueTypeRestriction),
    ])


class TestElementTypeRestriction(unittest.TestCase):
    element_type_2_sdv_of_type = {
        TypeCategory.DATA:
            StringSymbolValueContext.of_arbitrary_value(),

        TypeCategory.LOGIC:
            FileMatcherSymbolValueContext.of_arbitrary_value(),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_element_type in TypeCategory:
            container_of_sdv = self.element_type_2_sdv_of_type[expected_element_type].container
            with self.subTest(element_type=str(expected_element_type)):
                restriction_to_check = sut.TypeCategoryRestriction(expected_element_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_sdv)
                # ASSERT #
                self.assertIsNone(error_message)

    def test_dissatisfied_restriction(self):
        # ARRANGE #
        cases = {
            TypeCategory.DATA: TypeCategory.LOGIC,

            TypeCategory.LOGIC: TypeCategory.DATA,
        }

        symbols = empty_symbol_table()
        for expected_element_type, unexpected_element_type in cases.items():
            container_of_unexpected = self.element_type_2_sdv_of_type[unexpected_element_type].container
            with self.subTest(expected_element_type=str(expected_element_type),
                              unexpected_element_type=str(unexpected_element_type)):
                restriction_to_check = sut.TypeCategoryRestriction(expected_element_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_unexpected)
                # ASSERT #
                self.assertIsNotNone(error_message)


class TestValueTypeRestriction(unittest.TestCase):
    ARBITRARY_LIST_CONTEXT = list_.ARBITRARY_SYMBOL_VALUE_CONTEXT

    value_type_2_symbol_value_context_of_type = {

        ValueType.STRING:
            string.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.LIST:
            ARBITRARY_LIST_CONTEXT,

        ValueType.PATH:
            path.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.LINE_MATCHER:
            line_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.FILE_MATCHER:
            file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.FILES_MATCHER:
            files_matcher_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.STRING_MATCHER:
            string_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.STRING_TRANSFORMER:
            string_transformer.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.PROGRAM:
            program.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_value_type in ValueType:
            container_of_sdv = self.value_type_2_symbol_value_context_of_type[expected_value_type].container
            with self.subTest(element_type=str(expected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction(expected_value_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_sdv)
                # ASSERT #
                self.assertIsNone(error_message)

    def test_dissatisfied_restriction(self):
        # ARRANGE #
        cases = {
            ValueType.STRING: ValueType.LIST,
            ValueType.LIST: ValueType.PATH,
            ValueType.PATH: ValueType.FILE_MATCHER,
            ValueType.FILE_MATCHER: ValueType.STRING_TRANSFORMER,
            ValueType.FILES_MATCHER: ValueType.FILE_MATCHER,
            ValueType.STRING_MATCHER: ValueType.STRING_TRANSFORMER,
            ValueType.STRING_TRANSFORMER: ValueType.STRING,
            ValueType.PROGRAM: ValueType.STRING_TRANSFORMER,
        }

        symbols = empty_symbol_table()
        for expected_value_type, unexpected_value_type in cases.items():
            container_of_unexpected = self.value_type_2_symbol_value_context_of_type[unexpected_value_type].container
            with self.subTest(expected_element_type=str(expected_value_type),
                              unexpected_element_type=str(unexpected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction(expected_value_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_unexpected)
                # ASSERT #
                self.assertIsNotNone(error_message)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
