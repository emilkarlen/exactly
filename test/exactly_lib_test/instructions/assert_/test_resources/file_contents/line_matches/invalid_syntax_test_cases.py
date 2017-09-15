import unittest

from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.line_matches.utils import \
    InstructionArgumentsVariantConstructor


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


QUANTIFIER_KEYWORDS = (instruction_options.EXISTS_QUANTIFIER_ARGUMENT,
                       instruction_options.ALL_QUANTIFIER_ARGUMENT)


class _TestCaseBase(unittest.TestCase):
    def __init__(self,
                 configuration: InstructionTestConfigurationForContentsOrEquals):
        super().__init__()
        self.configuration = configuration

    def _check_variants_with_expectation_type_and_any_or_every(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor):
        for expectation_type in ExpectationType:
            for quantifier_keyword in QUANTIFIER_KEYWORDS:
                with self.subTest(expectation_type=expectation_type,
                                  any_or_every_keyword=quantifier_keyword):
                    args_variant = args_variant_constructor.construct(expectation_type,
                                                                      quantifier_keyword)
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
