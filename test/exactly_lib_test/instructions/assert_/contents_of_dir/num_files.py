import unittest

from exactly_lib.help_texts.file_ref import REL_symbol_OPTION
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_relativity
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import tr
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.instruction_arguments import \
    arguments_with_selection_options, \
    CompleteArgumentsConstructor, NumFilesAssertionVariant, AssertionVariantArgumentsConstructor
from exactly_lib_test.instructions.assert_.test_resources import expression
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import TestCaseBase, Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.named_element.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.named_element.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_utils.parse.test_resources.selection_arguments import selection_arguments
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.file_structure import Dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestCommonFailureConditions),

        unittest.makeSuite(TestDifferentSourceVariants),
        unittest.makeSuite(TestFailingValidationPreSdsDueToInvalidIntegerArgument),
        unittest.makeSuite(TestFailingValidationPreSdsCausedByCustomValidation),
    ])


class TestWithAssertionVariantForEmpty(tr.TestWithAssertionVariantBase):
    @property
    def arbitrary_assertion_variant(self) -> AssertionVariantArgumentsConstructor:
        return NumFilesAssertionVariant(_int_condition(comparators.EQ, 0))


class TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(
    expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        return 'ignored-name-of-dir-to-check {num_files} {condition}'.format(
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            condition=condition_str)


class TestParseInvalidSyntax(tr.TestParseInvalidSyntaxBase,
                             TestWithAssertionVariantForEmpty):
    pass


class TestCommonFailureConditions(tr.TestCommonFailureConditionsBase,
                                  TestWithAssertionVariantForEmpty):
    pass


class TestFailingValidationPreSdsDueToInvalidIntegerArgument(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.Parser(),
                                        TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck())


class TestFailingValidationPreSdsCausedByCustomValidation(TestCaseBase):
    def test_fail_WHEN_integer_operand_is_negative(self):
        cases = [
            -1,
            -2,
        ]
        for invalid_value in cases:
            arguments = 'ignored-file-name {num_files} {invalid_condition}'.format(
                num_files=sut.NUM_FILES_CHECK_ARGUMENT,
                invalid_condition=_int_condition(comparators.EQ, invalid_value))

            with self.subTest(invalid_value=invalid_value):
                self._check(
                    sut.Parser(),
                    remaining_source(arguments,
                                     ['following line']),
                    ArrangementPostAct(),
                    Expectation(
                        validation_pre_sds=svh_assertions.is_validation_error(),
                    ),
                )


class TestSymbolReferencesForNumFiles(unittest.TestCase):
    def test_file_matcher_reference_is_reported(self):
        name_of_file_matcher = 'a_file_matcher'

        arguments = 'dir-name {selection} {num_files} {cmp_op} 0'.format(
            selection=selection_arguments(named_matcher=name_of_file_matcher),
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            cmp_op=comparators.EQ.name)

        source = remaining_source(arguments)
        # ACT #
        instruction = sut.Parser().parse(source)
        assert isinstance(instruction, AssertPhaseInstruction)
        actual = instruction.symbol_usages()
        # ASSERT #
        expected_references = asrt.matches_sequence([
            is_file_matcher_reference_to(name_of_file_matcher)
        ])
        expected_references.apply_without_message(self, actual)

    def test_both_symbols_from_path_and_comparison_SHOULD_be_reported(self):
        # ARRANGE #

        path_sym_ref = NamedElementReference(
            'path_symbol_name',
            parse_relativity.reference_restrictions_for_path_symbol(
                sut.ACTUAL_RELATIVITY_CONFIGURATION.options.accepted_relativity_variants))

        operand_sym_ref = NamedElementReference('operand_symbol_name',
                                                string_made_up_by_just_strings())

        argument = '{rel_sym_opt} {path_sym} file-name {num_files} {cmp_op} {operand_sym_ref}'.format(
            rel_sym_opt=REL_symbol_OPTION,
            path_sym=path_sym_ref.name,
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            cmp_op=comparators.EQ.name,
            operand_sym_ref=symbol_reference_syntax_for_name(operand_sym_ref.name))

        source = remaining_source(argument)

        # ACT #

        actual_instruction = sut.Parser().parse(source)

        assert isinstance(actual_instruction, AssertPhaseInstruction)

        actual_symbol_references = actual_instruction.symbol_usages()

        # ASSERT #

        expected_symbol_references = [
            path_sym_ref,
            operand_sym_ref,
        ]
        assertion = equals_symbol_references(expected_symbol_references)

        assertion.apply_without_message(self, actual_symbol_references)


class TestDifferentSourceVariants(tr.TestCaseBaseForParser):
    def test_file_is_directory_that_has_expected_number_of_files(self):
        directory_with_one_file = Dir('name-of-dir', [empty_file('a-file-in-checked-dir')])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            directory_with_one_file.name,
            _int_condition(comparators.EQ, 1))

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
            _int_condition(comparators.EQ, 2))

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
            _int_condition(comparators.EQ, 1),
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


def _int_condition(operator: comparators.ComparisonOperator,
                   value: int) -> str:
    return operator.name + ' ' + str(value)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
