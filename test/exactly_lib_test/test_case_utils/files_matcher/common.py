import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.expression import syntax_documentation
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.help.test_resources.syntax_contents_structure_assertions import \
    is_syntax_element_description
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_syntax import \
    NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    AssertionVariantArgumentsConstructor
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDocumentation),
        unittest.makeSuite(TestParseInvalidSyntax),
    ])


class TestDocumentation(unittest.TestCase):
    def test(self):
        # ACT #
        sed = syntax_documentation.syntax_element_description(sut.GRAMMAR)
        # ASSERT #
        is_syntax_element_description.apply_without_message(self, sed)


class TestParseInvalidSyntax(unittest.TestCase):
    def test_raise_exception_WHEN_no_arguments(self):
        parser = sut.parsers(must_be_on_current_line=True).full
        for source in equivalent_source_variants(self, ''):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                parser.parse(source)

    def test_raise_exception_WHEN_invalid_assertion_variant(self):
        parser = sut.parsers(must_be_on_current_line=True).full
        cases = [
            NameAndValue(
                'Matcher is missing',
                args.complete_arguments_constructor(
                    InvalidAssertionVariantArgumentsConstructor('')
                ),
            ),
            NameAndValue(
                'Matcher has invalid syntax',
                args.complete_arguments_constructor(
                    InvalidAssertionVariantArgumentsConstructor(
                        NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME
                    )
                ),
            ),
        ]
        for case in cases:
            for expectation_type in ExpectationType:
                etc = pfh_expectation_type_config(expectation_type)
                instruction_arguments = case.value.apply(etc)
                source = remaining_source(instruction_arguments)
                with self.subTest(case_name=case.name,
                                  expectation_type=str(expectation_type)):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)


class InvalidAssertionVariantArgumentsConstructor(AssertionVariantArgumentsConstructor):
    def __init__(self, assertion_variant_argument: str):
        self._assertion_variant_argument = assertion_variant_argument

    def __str__(self):
        return self._assertion_variant_argument


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
