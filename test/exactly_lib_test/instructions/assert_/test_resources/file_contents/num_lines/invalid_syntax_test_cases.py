import unittest

from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.num_lines.utils import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.named_element.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_case_constructors = [
        _ParseShouldFailWhenOperandIsMissing,
        _ParseShouldFailWhenOperatorIsInvalid,
        _ParseShouldFailWhenThereAreSuperfluousArguments,
        _ParseShouldFailWhenTransformerIsInvalid,
    ]
    return unittest.TestSuite([
        test_case_constructor(configuration)
        for test_case_constructor in test_case_constructors
    ])


class _TestCaseBase(unittest.TestCase):
    def __init__(self,
                 configuration: InstructionTestConfigurationForContentsOrEquals):
        super().__init__()
        self.configuration = configuration

    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                args_variant = args_variant_constructor.construct(expectation_type)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    self.configuration.new_parser().parse(
                        self.configuration.source_for(args_variant))


class _ParseShouldFailWhenOperandIsMissing(_TestCaseBase):
    def runTest(self):
        for transformer in ['', 'valid_symbol_name']:
            argument_variant_con = InstructionArgumentsVariantConstructor(operator=comparators.EQ.name,
                                                                          operand='')
            with self.subTest(transformer=transformer):
                self._check_variants_with_expectation_type(argument_variant_con)


class _ParseShouldFailWhenOperatorIsInvalid(_TestCaseBase):
    def runTest(self):
        for transformer in ['', 'valid_symbol_name']:
            argument_variant_con = InstructionArgumentsVariantConstructor(operator='not_an_operator',
                                                                          operand='5')
            with self.subTest(transformer=transformer):
                self._check_variants_with_expectation_type(argument_variant_con)


class _ParseShouldFailWhenThereAreSuperfluousArguments(_TestCaseBase):
    def runTest(self):
        for transformer in ['', 'valid_symbol_name']:
            argument_variant_con = InstructionArgumentsVariantConstructor(operator=comparators.EQ.name,
                                                                          operand='5',
                                                                          superfluous_args_str='superfluous_argument')
            with self.subTest(transformer=transformer):
                self._check_variants_with_expectation_type(argument_variant_con)


class _ParseShouldFailWhenTransformerIsInvalid(_TestCaseBase):
    def runTest(self):
        argument_variant_con = InstructionArgumentsVariantConstructor(operator=comparators.EQ.name,
                                                                      operand='5',
                                                                      transformer=NOT_A_VALID_SYMBOL_NAME)
        self._check_variants_with_expectation_type(argument_variant_con)
