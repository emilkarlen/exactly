import unittest

from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_case_constructors = [
        _ParseWithMissingRegExArgument,
        _ParseWithSuperfluousArgument,
        _ParseWithInvalidRegEx,
    ]
    return unittest.TestSuite([
        test_case_constructor(configuration)
        for test_case_constructor in test_case_constructors
    ])


ANY_OR_EVERY_KEYWORDS = (instruction_options.ANY_LINE_ARGUMENT,)


class InstructionArgumentsVariantConstructor:
    def __init__(self,
                 regex_arg_str: str,
                 superfluous_args_str: str):
        self.regex_arg_str = regex_arg_str
        self.superfluous_args_str = superfluous_args_str

    def construct(self,
                  expectation_type: ExpectationType,
                  any_or_every_keyword: str,
                  ) -> str:
        superfluous_args_str = self.superfluous_args_str
        if superfluous_args_str:
            superfluous_args_str = ' ' + superfluous_args_str
        return '{maybe_not} {any_or_every} {line_matches} {regex}{superfluous_args_str}'.format(
            maybe_not=ExpectationTypeConfig(expectation_type).expectation_type_str,
            any_or_every=any_or_every_keyword,
            line_matches=instruction_options.LINE_ARGUMENT + ' ' + instruction_options.MATCHES_ARGUMENT,
            regex=self.regex_arg_str,
            superfluous_args_str=superfluous_args_str,
        )


class _TestCaseBase(unittest.TestCase):
    def __init__(self,
                 configuration: InstructionTestConfigurationForContentsOrEquals):
        super().__init__()
        self.configuration = configuration

    def _check_variants_with_expectation_type_and_any_or_every(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor):
        for expectation_type in ExpectationType:
            for any_or_every_keyword in ANY_OR_EVERY_KEYWORDS:
                with self.subTest(expectation_type=expectation_type,
                                  any_or_every_keyword=any_or_every_keyword):
                    args_variant = args_variant_constructor.construct(expectation_type,
                                                                      any_or_every_keyword)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        self.configuration.new_parser().parse(
                            self.configuration.source_for(args_variant))


class _ParseWithMissingRegExArgument(_TestCaseBase):
    def runTest(self):
        self._check_variants_with_expectation_type_and_any_or_every(
            InstructionArgumentsVariantConstructor(regex_arg_str='',
                                                   superfluous_args_str=''))


class _ParseWithSuperfluousArgument(_TestCaseBase):
    def runTest(self):
        self._check_variants_with_expectation_type_and_any_or_every(
            InstructionArgumentsVariantConstructor(regex_arg_str='regex',
                                                   superfluous_args_str='superfluous'))


class _ParseWithInvalidRegEx(_TestCaseBase):
    def runTest(self):
        self._check_variants_with_expectation_type_and_any_or_every(
            InstructionArgumentsVariantConstructor(regex_arg_str='**',
                                                   superfluous_args_str=''))
