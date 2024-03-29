import unittest

from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref import restrictions as sut
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources import symbol_context as file_matcher
from exactly_lib_test.type_val_deps.types.files_condition.test_resources import symbol_context as files_condition
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources import \
    symbol_context as files_matcher_symbol_context
from exactly_lib_test.type_val_deps.types.files_source.test_resources import \
    symbol_context as files_source_symbol_context
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources import symbol_context as integer_matcher
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources import symbol_context as line_matcher
from exactly_lib_test.type_val_deps.types.list_.test_resources import symbol_context as list_
from exactly_lib_test.type_val_deps.types.path.test_resources import symbol_context as path
from exactly_lib_test.type_val_deps.types.program.test_resources import symbol_context as program
from exactly_lib_test.type_val_deps.types.string_.test_resources import symbol_context as string
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources import symbol_context as string_matcher
from exactly_lib_test.type_val_deps.types.string_source.test_resources import symbol_context as string_source
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources import symbol_context as st_symbol_context


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestValueTypeRestriction)


class TestValueTypeRestriction(unittest.TestCase):
    ARBITRARY_LIST_CONTEXT = list_.ARBITRARY_SYMBOL_VALUE_CONTEXT

    value_type_2_symbol_value_context_of_type = {

        ValueType.STRING:
            string.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.LIST:
            ARBITRARY_LIST_CONTEXT,

        ValueType.PATH:
            path.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.INTEGER_MATCHER:
            integer_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.LINE_MATCHER:
            line_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.FILE_MATCHER:
            file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.FILES_CONDITION:
            files_condition.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.FILES_MATCHER:
            files_matcher_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.FILES_SOURCE:
            files_source_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.STRING_SOURCE:
            string_source.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.STRING_MATCHER:
            string_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.STRING_TRANSFORMER:
            st_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,

        ValueType.PROGRAM:
            program.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_value_type in ValueType:
            container_of_sdv = self.value_type_2_symbol_value_context_of_type[expected_value_type].container
            with self.subTest(element_type=str(expected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction.of_single(expected_value_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_sdv)
                # ASSERT #
                self.assertIsNone(error_message)

    def test_satisfied_restriction__multi(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_value_type in ValueType:
            container_of_sdv = self.value_type_2_symbol_value_context_of_type[expected_value_type].container
            with self.subTest(element_type=str(expected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction([expected_value_type, ValueType.STRING])
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
            ValueType.PATH: ValueType.INTEGER_MATCHER,
            ValueType.INTEGER_MATCHER: ValueType.FILE_MATCHER,
            ValueType.FILE_MATCHER: ValueType.FILES_MATCHER,
            ValueType.FILES_MATCHER: ValueType.STRING_SOURCE,
            ValueType.STRING_SOURCE: ValueType.STRING_MATCHER,
            ValueType.STRING_MATCHER: ValueType.STRING_TRANSFORMER,
            ValueType.STRING_TRANSFORMER: ValueType.PROGRAM,
            ValueType.PROGRAM: ValueType.FILES_CONDITION,
            ValueType.FILES_CONDITION: ValueType.FILES_SOURCE,
            ValueType.FILES_SOURCE: ValueType.STRING,
        }

        symbols = empty_symbol_table()
        for expected_value_type, unexpected_value_type in cases.items():
            container_of_unexpected = self.value_type_2_symbol_value_context_of_type[unexpected_value_type].container
            with self.subTest(expected_element_type=str(expected_value_type),
                              unexpected_element_type=str(unexpected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction.of_single(expected_value_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_unexpected)
                # ASSERT #
                self.assertIsNotNone(error_message)

    def test_dissatisfied_restriction__multiple(self):
        # ARRANGE #
        cases = {
            ValueType.LIST: [ValueType.STRING, ValueType.INTEGER_MATCHER],
            ValueType.PATH: [ValueType.LIST, ValueType.FILE_MATCHER],
            ValueType.INTEGER_MATCHER: [ValueType.PATH, ValueType.LIST],
            ValueType.FILE_MATCHER: [ValueType.INTEGER_MATCHER, ValueType.PATH],
            ValueType.FILES_MATCHER: [ValueType.FILE_MATCHER, ValueType.STRING],
            ValueType.STRING_MATCHER: [ValueType.FILES_MATCHER, ValueType.STRING],
            ValueType.STRING_TRANSFORMER: [ValueType.STRING_MATCHER, ValueType.PATH],
            ValueType.PROGRAM: [ValueType.STRING_TRANSFORMER, ValueType.PATH],
            ValueType.FILES_CONDITION: [ValueType.FILES_SOURCE, ValueType.PATH],
            ValueType.FILES_SOURCE: [ValueType.FILES_MATCHER, ValueType.PATH],
            ValueType.STRING: [ValueType.FILES_CONDITION, ValueType.PATH],
        }

        symbols = empty_symbol_table()
        for unexpected_value_type, expected_value_types in cases.items():
            container_of_unexpected = self.value_type_2_symbol_value_context_of_type[unexpected_value_type].container
            with self.subTest(expected_element_type=str(expected_value_types),
                              unexpected_element_type=str(unexpected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction(expected_value_types)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_unexpected)
                # ASSERT #
                self.assertIsNotNone(error_message)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
