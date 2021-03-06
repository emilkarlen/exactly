import unittest

from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.string_matcher import parse_string_matcher as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.types.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.impls.types.string_matcher.test_resources import test_configuration


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _ParseShouldFailWhenOperandIsMissing(),
        _ParseShouldFailWhenOperatorIsInvalid(),
    ])


class _TestCaseBase(unittest.TestCase):
    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                args_variant = args_variant_constructor.construct(expectation_type)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parsers().full.parse(
                        test_configuration.source_for(args_variant)
                    )


class _ParseShouldFailWhenOperandIsMissing(_TestCaseBase):
    def runTest(self):
        argument_variant_con = InstructionArgumentsVariantConstructor(operator=comparators.EQ.name,
                                                                      operand='')
        self._check_variants_with_expectation_type(argument_variant_con)


class _ParseShouldFailWhenOperatorIsInvalid(_TestCaseBase):
    def runTest(self):
        argument_variant_con = InstructionArgumentsVariantConstructor(operator='<>',
                                                                      operand='5')
        self._check_variants_with_expectation_type(argument_variant_con)
