import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.contents_of_dir import config
from exactly_lib.instructions.assert_.utils.condition import comparators
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import tr
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.instruction_arguments import \
    arguments_with_selection_options, \
    CompleteArgumentsConstructor, NumFilesAssertionVariant, AssertionVariantArgumentsConstructor, \
    CommonArgumentsConstructor
from exactly_lib_test.instructions.assert_.test_resources import expression
from exactly_lib_test.instructions.assert_.test_resources.expression import int_condition
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail, ExpectationTypeConfig
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_resources.file_structure import Dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestCommonFailureConditions),

        unittest.makeSuite(TestSymbolReferences),

        unittest.makeSuite(TestDifferentSourceVariants),
        unittest.makeSuite(TestFailingValidationPreSdsDueToInvalidIntegerArgument),
    ])


class TestWithAssertionVariantForNumFiles(tr.TestWithAssertionVariantBase):
    @property
    def assertion_variant_without_symbol_references(self) -> AssertionVariantArgumentsConstructor:
        return NumFilesAssertionVariant(int_condition(comparators.EQ, 0))


class TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(
    expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        return 'ignored-name-of-dir-to-check {num_files} {condition}'.format(
            num_files=config.NUM_FILES_CHECK_ARGUMENT,
            condition=condition_str)


class TestParseInvalidSyntax(tr.TestParseInvalidSyntaxBase,
                             TestWithAssertionVariantForNumFiles):
    pass


class TestCommonFailureConditions(tr.TestCommonFailureConditionsBase,
                                  TestWithAssertionVariantForNumFiles):
    pass


class TestFailingValidationPreSdsDueToInvalidIntegerArgument(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.parser.Parser(),
                                        TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(),
                                        invalid_integers_according_to_custom_validation=[-1, -2])


class TestSymbolReferences(tr.TestCommonSymbolReferencesBase,
                           TestWithAssertionVariantForNumFiles):
    def test_symbols_from_comparison_SHOULD_be_reported(self):
        # ARRANGE #

        operand_sym_ref = SymbolReference('operand_symbol_name',
                                          string_made_up_by_just_strings())

        condition_str = '{operator} {symbol_reference}'.format(
            operator=comparators.EQ.name,
            symbol_reference=symbol_reference_syntax_for_name(operand_sym_ref.name)
        )
        arguments_constructor = CompleteArgumentsConstructor(
            CommonArgumentsConstructor('ignored-dir-path'),
            NumFilesAssertionVariant(condition_str))

        argument = arguments_constructor.apply(ExpectationTypeConfig(ExpectationType.NEGATIVE),
                                               tr.DEFAULT_REL_OPT_CONFIG)

        source = remaining_source(argument)

        # ACT #

        actual_instruction = sut.parser.Parser().parse(source)

        assert isinstance(actual_instruction, AssertPhaseInstruction)

        actual_symbol_references = actual_instruction.symbol_usages()

        # ASSERT #

        expected_symbol_references = [
            operand_sym_ref,
        ]
        assertion = equals_symbol_references(expected_symbol_references)

        assertion.apply_without_message(self, actual_symbol_references)


class TestDifferentSourceVariants(tr.TestCaseBaseForParser):
    def test_file_is_directory_that_has_expected_number_of_files(self):
        directory_with_one_file = Dir('name-of-dir', [empty_file('a-file-in-checked-dir')])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            directory_with_one_file.name,
            int_condition(comparators.EQ, 1))

        contents_of_relativity_option_root = DirContents([directory_with_one_file])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_a_directory_that_has_unexpected_number_of_files(self):
        directory_with_one_file = Dir('name-of-non-empty-dir',
                                      [empty_file('file-in-dir')])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            directory_with_one_file.name,
            int_condition(comparators.EQ, 2))

        contents_of_relativity_option_root = DirContents([directory_with_one_file])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_directory_with_files_but_none_that_matches_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern_that_matches_exactly_one_file = 'a*'

        dir_with_two_files = Dir(name_of_directory,
                                 [
                                     empty_file('a file'),
                                     empty_file('b file'),
                                 ])

        contents_of_relativity_option_root = DirContents([dir_with_two_files])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            dir_with_two_files.name,
            int_condition(comparators.EQ, 1),
            name_option_pattern=pattern_that_matches_exactly_one_file)

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )


def argument_constructor_for_num_files_check(file_name: str,
                                             int_condition: str,
                                             name_option_pattern: str = '',
                                             type_matcher: FileType = None,
                                             named_matcher: str = '',
                                             ) -> CompleteArgumentsConstructor:
    return arguments_with_selection_options(
        file_name,
        NumFilesAssertionVariant(int_condition),
        name_option_pattern=name_option_pattern,
        type_matcher=type_matcher,
        named_matcher=named_matcher,
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
