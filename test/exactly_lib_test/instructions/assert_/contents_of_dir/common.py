import unittest

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import \
    TheInstructionArgumentsVariantConstructorForNotAndRelOpt, replace_not_op, instruction_arguments_for_emptiness_check
from exactly_lib_test.instructions.assert_.existence_of_file import ACCEPTED_REL_OPT_CONFIGURATIONS, \
    UNACCEPTED_REL_OPT_CONFIGURATIONS
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionChecker
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import TestCaseBase
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, sym_link
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('the-instruction-name')),
    ])


class TestParseInvalidSyntax(TestCaseBase):
    test_cases_with_negation_operator_place_holder = [
        NameAndValue(
            'no arguments',
            '',
        ),
        NameAndValue(
            'valid file argument, but no operator',
            'file-name <not_opt>',
        ),
        NameAndValue(
            'valid file argument, invalid check',
            'file-name <not_opt> invalid-check',
        ),
        NameAndValue(
            'invalid option before file argument',
            '{invalid_option} file-name <not_opt> {empty}'.format(
                invalid_option=long_option_syntax('invalidOption'),
                empty=sut.EMPTINESS_CHECK_ARGUMENT)
        ),
        NameAndValue(
            'missing argument for matcher option ' + sut.SELECTION_OPTION.name.long,
            'file-name {selection_option} <not_opt> {empty}'.format(
                selection_option=option_syntax.option_syntax(
                    instruction_arguments.SELECTION_OPTION.name),
                empty=sut.EMPTINESS_CHECK_ARGUMENT
            )
        ),
        NameAndValue(
            'missing argument for num-files option ' + sut.SELECTION_OPTION.name.long,
            'file-name <not_opt> {num_files}'.format(
                selection_option=option_syntax.option_syntax(
                    instruction_arguments.SELECTION_OPTION.name),
                num_files=sut.NUM_FILES_CHECK_ARGUMENT
            )
        ),
        NameAndValue(
            'superfluous argument for num-files option ' + sut.SELECTION_OPTION.name.long,
            'file-name <not_opt> {num_files} {eq} 10 superfluous'.format(
                selection_option=option_syntax.option_syntax(
                    instruction_arguments.SELECTION_OPTION.name),
                num_files=sut.NUM_FILES_CHECK_ARGUMENT,
                eq=comparators.EQ.name,
            )
        ),
    ]

    def test_raise_exception_WHEN_syntax_is_invalid(self):

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(
            self.test_cases_with_negation_operator_place_holder)

    def test_raise_exception_WHEN_relativity_is_unaccepted(self):

        test_cases = [
            NameAndValue('relativity:' + rel_opt_config.option_string,
                         instruction_arguments_for_emptiness_check(rel_opt_config,
                                                                   'file-name')
                         )
            for rel_opt_config in UNACCEPTED_REL_OPT_CONFIGURATIONS
        ]

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(test_cases)

    def _assert_each_case_raises_SingleInstructionInvalidArgumentException(self, test_cases: list):
        parser = sut.Parser()
        for expectation_type in ExpectationType:
            etc = ExpectationTypeConfig(expectation_type)
            for name_and_instruction_argument_str in test_cases:
                with self.subTest(case_name=name_and_instruction_argument_str.name,
                                  expectation_type=str(expectation_type)):
                    first_line_arguments = replace_not_op(etc, name_and_instruction_argument_str.value)
                    for source in equivalent_source_variants(self, first_line_arguments):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(source)


class TestCommonFailureConditionsBase:
    @property
    def _checker(self) -> InstructionChecker:
        return InstructionChecker(
            self._get_unittest_test_case(),
            sut.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS,
        )

    def _get_unittest_test_case(self) -> unittest.TestCase:
        raise NotImplementedError('abstract method')

    def _arguments_for_valid_syntax(
            self, path_to_check: str) -> TheInstructionArgumentsVariantConstructorForNotAndRelOpt:
        raise NotImplementedError('abstract method')

    def test_fail_WHEN_file_does_not_exist(self):
        instruction_argument_constructor = self._arguments_for_valid_syntax('name-of-non-existing-file')

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail())

    def test_fail_WHEN_file_does_exist_but_is_not_a_directory(self):
        name_of_regular_file = 'name-of-existing-regular-file'

        instruction_argument_constructor = self._arguments_for_valid_syntax(name_of_regular_file)

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=DirContents([empty_file(name_of_regular_file)]))

    def test_fail_WHEN_file_is_a_sym_link_to_a_non_existing_file(self):
        broken_sym_link = sym_link('broken-sym-link', 'non-existing-file')

        instruction_argument_constructor = self._arguments_for_valid_syntax(broken_sym_link.name)

        contents_of_relativity_option_root = DirContents([broken_sym_link])

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=contents_of_relativity_option_root)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
