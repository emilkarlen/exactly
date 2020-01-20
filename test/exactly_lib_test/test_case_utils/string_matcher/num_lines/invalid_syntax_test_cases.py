import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case_utils.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.test_case_utils.string_matcher.test_resources import test_configuration


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _ParseShouldFailWhenOperandIsMissing(),
        _ParseShouldFailWhenOperatorIsInvalid(),
        _ParseShouldFailWhenTransformerIsInvalid(),
    ])


class _TestCaseBase(unittest.TestCase):
    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                args_variant = args_variant_constructor.construct(expectation_type)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.string_matcher_parser().parse(
                        test_configuration.source_for(args_variant)
                    )


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


class _ParseShouldFailWhenTransformerIsInvalid(_TestCaseBase):
    def runTest(self):
        argument_variant_con = InstructionArgumentsVariantConstructor(operator=comparators.EQ.name,
                                                                      operand='5',
                                                                      transformer=NOT_A_VALID_SYMBOL_NAME)
        self._check_variants_with_expectation_type(argument_variant_con)