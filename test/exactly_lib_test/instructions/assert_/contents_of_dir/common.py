import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import tr
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.instruction_arguments import \
    AssertionVariantArgumentsConstructor
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import equivalent_source_variants
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        suite_for_instruction_documentation(sut.setup('the-instruction-name').documentation),
    ])


class TestParseInvalidSyntax(tr.TestCaseBaseForParser):
    def test_raise_exception_WHEN_no_arguments(self):
        parser = sut.parser.Parser()
        for source in equivalent_source_variants(self, ''):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                parser.parse(source)

    def test_raise_exception_WHEN_invalid_assertion_variant(self):
        parser = sut.parser.Parser()
        cases = [
            NameAndValue(
                'valid file argument, but no operator',
                tr.CompleteArgumentsConstructor(
                    tr.CommonArgumentsConstructor('file-name'),
                    InvalidAssertionVariantArgumentsConstructor('')
                ),
            ),
            NameAndValue(
                'valid file argument, invalid check',
                tr.CompleteArgumentsConstructor(
                    tr.CommonArgumentsConstructor('file-name'),
                    InvalidAssertionVariantArgumentsConstructor('invalidCheck')
                ),
            ),
        ]
        for case in cases:
            for rel_opt_config in [tr.DEFAULT_REL_OPT_CONFIG,
                                   tr.ARBITRARY_ACCEPTED_REL_OPT_CONFIG]:
                for expectation_type in ExpectationType:
                    etc = ExpectationTypeConfig(expectation_type)
                    instruction_arguments = case.value.apply(etc, rel_opt_config)
                    with self.subTest(case_name=case.name,
                                      expectation_type=str(expectation_type)):
                        for source in equivalent_source_variants(self,
                                                                 instruction_arguments):
                            with self.assertRaises(SingleInstructionInvalidArgumentException):
                                parser.parse(source)


class InvalidAssertionVariantArgumentsConstructor(AssertionVariantArgumentsConstructor):
    def __init__(self, assertion_variant_argument: str):
        self._assertion_variant_argument = assertion_variant_argument

    def __str__(self):
        return self._assertion_variant_argument


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
