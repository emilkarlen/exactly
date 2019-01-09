import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import tr
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    AssertionVariantArgumentsConstructor
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseInvalidSyntax)


class TestParseInvalidSyntax(tr.TestCaseBaseForParser):
    def test_raise_exception_WHEN_no_arguments(self):
        parser = sut.files_matcher_parser()
        for source in equivalent_source_variants(self, ''):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                parser.parse(source)

    def test_raise_exception_WHEN_invalid_assertion_variant(self):
        parser = sut.files_matcher_parser()
        cases = [
            NameAndValue(
                'valid file argument, but no operator',
                args.complete_arguments_constructor(
                    InvalidAssertionVariantArgumentsConstructor('')
                ),
            ),
            NameAndValue(
                'valid file argument, invalid check',
                args.complete_arguments_constructor(
                    InvalidAssertionVariantArgumentsConstructor(symbol_reference_syntax_for_name('invalidCheck'))
                ),
            ),
        ]
        for case in cases:
            for expectation_type in ExpectationType:
                etc = pfh_expectation_type_config(expectation_type)
                instruction_arguments = case.value.apply(etc)
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
