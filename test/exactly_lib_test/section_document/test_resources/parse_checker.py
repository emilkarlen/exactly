import unittest
from contextlib import contextmanager
from typing import Callable, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parsing import LocationAwareParser
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse import token
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer


class Checker:
    def __init__(self, parser: LocationAwareParser):
        self.parser = parser

    def check_invalid_arguments(self,
                                put: unittest.TestCase,
                                source: ParseSource,
                                ):
        with put.assertRaises(SingleInstructionInvalidArgumentException) as cx:
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

        put.assertIsInstance(cx.exception.error_message,
                             str,
                             'error message')

    def check_invalid_syntax_cases_for_expected_valid_token(self,
                                                            put: unittest.TestCase,
                                                            make_arguments: Callable[[str], ArgumentElementsRenderer],
                                                            ):
        for case in invalid_syntax_cases_for_expected_valid_token(make_arguments):
            with put.subTest(case.name):
                self.check_invalid_arguments(put, case.value)

    def check_valid_arguments(self,
                              put: unittest.TestCase,
                              source: ParseSource,
                              ):
        actual = self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        put.assertIsNotNone(actual,
                            'parsed object')


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
