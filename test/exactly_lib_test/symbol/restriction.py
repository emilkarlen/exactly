import unittest

from exactly_lib.symbol import restriction as sut
from exactly_lib.symbol.data import string_resolvers, file_ref_resolvers
from exactly_lib.symbol.logic.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.logic.program.command_resolver import CommandResolver
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.program.resolvers import accumulator
from exactly_lib.test_case_utils.program.resolvers.command_program_resolver import ProgramResolverForCommand
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_string_values import string_value_of_single_string
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.logic.program.command_value import CommandValue
from exactly_lib.type_system.logic.program.command_values import CommandDriverValueForShell
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.data.test_resources.list_resolvers import ListResolverTestImplForConstantListValue
from exactly_lib_test.symbol.test_resources.command_resolvers import CommandDriverResolverForConstantTestImpl
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.files_matcher import FilesMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.string_transformer import StringTransformerResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.type_system.logic.test_resources.file_matcher import FileMatcherThatSelectsAllFilesTestImpl
from exactly_lib_test.type_system.logic.test_resources.string_matchers import StringMatcherConstant
from exactly_lib_test.type_system.logic.test_resources.values import FakeStringTransformer, \
    LineMatcherNotImplementedTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestElementTypeRestriction),
        unittest.makeSuite(TestValueTypeRestriction),
    ])


class TestElementTypeRestriction(unittest.TestCase):
    element_type_2_resolver_of_type = {
        TypeCategory.DATA:
            string_resolvers.str_constant('string value'),

        TypeCategory.LOGIC:
            FileMatcherResolverConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl()),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_element_type in TypeCategory:
            container_of_resolver = container(self.element_type_2_resolver_of_type[expected_element_type])
            with self.subTest(element_type=str(expected_element_type)):
                restriction_to_check = sut.TypeCategoryRestriction(expected_element_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_resolver)
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
            container_of_unexpected = container(self.element_type_2_resolver_of_type[unexpected_element_type])
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
    arbitrary_list_resolver = ListResolverTestImplForConstantListValue(ListValue([]))

    value_type_2_resolver_of_type = {

        ValueType.STRING:
            string_resolvers.str_constant('string value'),

        ValueType.LIST:
            arbitrary_list_resolver,

        ValueType.PATH:
            file_ref_resolvers.constant(file_refs.rel_sandbox(RelSdsOptionType.REL_ACT, file_refs.empty_path_part())),

        ValueType.LINE_MATCHER:
            LineMatcherResolverConstantTestImpl(LineMatcherNotImplementedTestImpl()),

        ValueType.FILE_MATCHER:
            FileMatcherResolverConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl()),

        ValueType.FILES_MATCHER:
            FilesMatcherResolverConstantTestImpl(),

        ValueType.STRING_MATCHER:
            StringMatcherResolverConstantTestImpl(StringMatcherConstant(None)),

        ValueType.STRING_TRANSFORMER:
            StringTransformerResolverConstantTestImpl(FakeStringTransformer(), []),

        ValueType.PROGRAM:
            ProgramResolverForCommand(
                CommandResolver(
                    CommandDriverResolverForConstantTestImpl(
                        CommandValue(
                            CommandDriverValueForShell(string_value_of_single_string('the shell command line')),
                            ListValue.empty())),
                    ArgumentsResolver(arbitrary_list_resolver),
                ),
                accumulator.empty()
            ),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        symbols = empty_symbol_table()
        for expected_value_type in ValueType:
            container_of_resolver = container(self.value_type_2_resolver_of_type[expected_value_type])
            with self.subTest(element_type=str(expected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction(expected_value_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(symbols,
                                                                     'symbol name',
                                                                     container_of_resolver)
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
            container_of_unexpected = container(self.value_type_2_resolver_of_type[unexpected_value_type])
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
