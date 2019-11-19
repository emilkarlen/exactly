import unittest

from exactly_lib.symbol import restriction as sut
from exactly_lib.symbol.data import string_sdvs, path_sdvs
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.concrete_strings import string_ddv_of_single_string
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.logic.program.command_value import CommandValue
from exactly_lib.type_system.logic.program.command_values import CommandDriverValueForShell
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.data.test_resources.list_sdvs import ListSdvTestImplForConstantListDdv
from exactly_lib_test.symbol.test_resources.command_sdvs import CommandDriverSdvForConstantTestImpl
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSdvConstantTestImpl
from exactly_lib_test.symbol.test_resources.files_matcher import FilesMatcherSdvConstantTestImpl
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherSdvConstantTestImpl
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSdvConstantTestImpl
from exactly_lib_test.symbol.test_resources.string_transformer import StringTransformerSdvConstantTestImpl
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
    element_type_2_sdv_of_type = {
        TypeCategory.DATA:
            string_sdvs.str_constant('string value'),

        TypeCategory.LOGIC:
            FileMatcherSdvConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl()),
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
    arbitrary_list_sdv = ListSdvTestImplForConstantListDdv(ListDdv([]))

    value_type_2_sdv_of_type = {

        ValueType.STRING:
            string_sdvs.str_constant('string value'),

        ValueType.LIST:
            arbitrary_list_sdv,

        ValueType.PATH:
            path_sdvs.constant(paths.rel_sandbox(RelSdsOptionType.REL_ACT, paths.empty_path_part())),

        ValueType.LINE_MATCHER:
            LineMatcherSdvConstantTestImpl(LineMatcherNotImplementedTestImpl()),

        ValueType.FILE_MATCHER:
            FileMatcherSdvConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl()),

        ValueType.FILES_MATCHER:
            FilesMatcherSdvConstantTestImpl(),

        ValueType.STRING_MATCHER:
            StringMatcherSdvConstantTestImpl(StringMatcherConstant(None)),

        ValueType.STRING_TRANSFORMER:
            StringTransformerSdvConstantTestImpl(FakeStringTransformer(), []),

        ValueType.PROGRAM:
            ProgramSdvForCommand(
                CommandSdv(
                    CommandDriverSdvForConstantTestImpl(
                        CommandValue(
                            CommandDriverValueForShell(string_ddv_of_single_string('the shell command line')),
                            ListDdv.empty())),
                    ArgumentsSdv(arbitrary_list_sdv),
                ),
                accumulator.empty()
            ),
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
