import unittest
from contextlib import contextmanager
from typing import Callable, Sequence, Generic, TypeVar

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parsing import LocationAwareParser
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse import token
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line__abs_stx
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.source import layout as tokens_layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.layout import STANDARD_LAYOUT_SPECS

T = TypeVar('T')


class Checker(Generic[T]):
    def __init__(self, parser: LocationAwareParser[T]):
        self.parser = parser

    def check_invalid_arguments(self,
                                put: unittest.TestCase,
                                invalid_source: ParseSource,
                                ):
        with put.assertRaises(SingleInstructionInvalidArgumentException) as cx:
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, invalid_source)

        put.assertIsInstance(cx.exception.error_message,
                             str,
                             'error message')

    def check_invalid_syntax__abs_stx(self,
                                      put: unittest.TestCase,
                                      invalid_source: AbstractSyntax,
                                      **sub_test_identifiers
                                      ):
        for layout_case in STANDARD_LAYOUT_SPECS:
            parse_source = ParseSource(invalid_source.tokenization().layout(layout_case.value))
            with put.subTest(layout=layout_case.name, **sub_test_identifiers):
                self.check_invalid_arguments(put, parse_source)

    def check_invalid_syntax__src_var_consume_last_line_abs_stx(self,
                                                                put: unittest.TestCase,
                                                                invalid_source: AbstractSyntax,
                                                                ):
        for case in equivalent_source_variants__with_source_check__consume_last_line__abs_stx(invalid_source):
            with put.subTest(layout=case.name):
                self.check_invalid_arguments(put, case.value.source)

    def check_invalid_syntax_cases_for_expected_valid_token(self,
                                                            put: unittest.TestCase,
                                                            make_arguments: Callable[[str], ArgumentElementsRenderer],
                                                            ):
        for case in invalid_syntax_cases_for_expected_valid_token(make_arguments):
            with put.subTest(case.name):
                self.check_invalid_arguments(put, case.value)

    def check_valid_arguments(self,
                              put: unittest.TestCase,
                              valid_source: ParseSource,
                              ):
        actual = self.parser.parse(ARBITRARY_FS_LOCATION_INFO, valid_source)
        put.assertIsNotNone(actual,
                            'parsed object')

    def parse__abs_stx(self,
                       put: unittest.TestCase,
                       valid_source: AbstractSyntax,
                       layout: tokens_layout.LayoutSpec = tokens_layout.LayoutSpec.of_default(),
                       ) -> T:
        parse_source = remaining_source(valid_source.tokenization().layout(layout))
        actual = self.parser.parse(ARBITRARY_FS_LOCATION_INFO, parse_source)
        put.assertIsNotNone(actual,
                            'parsed object')
        return actual


@contextmanager
def assert_raises_invalid_argument_exception(put: unittest.TestCase):
    with put.assertRaises(SingleInstructionInvalidArgumentException) as cx:
        yield
    put.assertIsInstance(cx.exception.error_message,
                         str,
                         'error message')


def invalid_syntax_cases_for_expected_valid_token(make_arguments: Callable[[str], ArgumentElementsRenderer],
                                                  ) -> Sequence[NameAndValue[ParseSource]]:
    return [
        NameAndValue(
            'missing token',
            make_arguments('').as_remaining_source,
        ),
        NameAndValue(
            'invalid syntax of token',
            make_arguments(
                token.HARD_QUOTE_CHAR + 'quoted token without ending quote'
            ).as_remaining_source,
        ),
    ]
