from typing import Sequence, Callable

from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser, PARSE_RESULT
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse import token
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser
from exactly_lib_test.section_document.test_resources.parse_checker import Checker
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer


def parse_checker(parser: Parser[PARSE_RESULT]) -> Checker:
    return Checker(ParserAsLocationAwareParser(parser))


def invalid_syntax_cases_for_expected_valid_token(make_arguments: Callable[[str], ArgumentElementsRenderer],
                                                  ) -> Sequence[NameAndValue[ParseSource]]:
    return [
        NameAndValue(
            'missing',
            make_arguments('').as_remaining_source,
        ),
        NameAndValue(
            'invalid token syntax',
            make_arguments(
                token.HARD_QUOTE_CHAR + 'quoted token without ending quote'
            ).as_remaining_source,
        ),
    ]
