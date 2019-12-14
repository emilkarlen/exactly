import unittest

from exactly_lib.symbol import restriction as sut
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.data.test_resources import list_sdvs as list_sdvs_tr, path_sdvs as path_sdvs_tr, \
    string_sdvs as string_sdvs_tr
from exactly_lib_test.symbol.test_resources import line_matcher, string_matcher, files_matcher, string_transformer, \
    file_matcher
from exactly_lib_test.symbol.test_resources.file_matcher import file_matcher_sdv_constant_test_impl
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.type_system.logic.test_resources.file_matcher import FileMatcherThatSelectsAllFilesTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestElementTypeRestriction),
        unittest.makeSuite(TestValueTypeRestriction),
    ])


class TestElementTypeRestriction(unittest.TestCase):
    element_type_2_sdv_of_type = {
        TypeCategory.DATA:
            string_sdvs.str_constant('string value'),

        TypeCategory.LOGIC:
            file_matcher_sdv_constant_test_impl(FileMatcherThatSelectsAllFilesTestImpl()),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_element_type in TypeCategory:
            container_of_sdv = container(self.element_type_2_sdv_of_type[expected_element_type])
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
            container_of_unexpected = container(self.element_type_2_sdv_of_type[unexpected_element_type])
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
    arbitrary_list_sdv = list_sdvs_tr.arbitrary_sdv()

    value_type_2_sdv_of_type = {

        ValueType.STRING:
            string_sdvs_tr.arbitrary_sdv(),

        ValueType.LIST:
            arbitrary_list_sdv,

        ValueType.PATH:
            path_sdvs_tr.arbitrary_sdv(),

        ValueType.LINE_MATCHER:
            line_matcher.arbitrary_sdv(),

        ValueType.FILE_MATCHER:
            file_matcher.arbitrary_sdv(),

        ValueType.FILES_MATCHER:
            files_matcher.arbitrary_sdv(),

        ValueType.STRING_MATCHER:
            string_matcher.arbitrary_sdv(),

        ValueType.STRING_TRANSFORMER:
            string_transformer.arbitrary_sdv(),

        ValueType.PROGRAM:
            program_sdvs.arbitrary_sdv(),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_value_type in ValueType:
            container_of_sdv = container(self.value_type_2_sdv_of_type[expected_value_type])
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
            container_of_unexpected = container(self.value_type_2_sdv_of_type[unexpected_value_type])
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
