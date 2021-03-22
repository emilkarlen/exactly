import re
from typing import Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import string
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.impls.types.string_.syntax_elements import TEXT_UNTIL_EOL_TOKEN_MATCHER
from exactly_lib.section_document import defs
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol import symbol_syntax
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.either import Either
from exactly_lib.util.parse.token import TokenMatcher, Token
from exactly_lib.util.str_.misc_formatting import lines_content
from . import syntax_elements as _rs_syntax_elements


class HereDocArgTokenMatcher(TokenMatcher):
    def matches(self, token: Token) -> bool:
        return (
                token.is_plain and
                token.string.startswith(string.HERE_DOCUMENT_MARKER_PREFIX)
        )


class HereDocumentContentsParsingException(SingleInstructionInvalidArgumentException):
    def __init__(self, error_message: str):
        super().__init__(error_message)


DEFAULT_CONFIGURATION = parse_string.Configuration(syntax_elements.RICH_STRING_SYNTAX_ELEMENT.singular_name,
                                                   reference_restrictions=None)

_SYNTAX_ELEMENT_NAME = _rs_syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT_NAME


class RichStringParser(ParserFromTokenParserBase[StringSdv]):
    def __init__(self, conf: parse_string.Configuration = DEFAULT_CONFIGURATION):
        super().__init__(False, False)
        self._sym_name_or_string_parser = SymbolNameOrStringRichStringParser(conf)
        self._string_parser = parse_string.StringFromTokensParser(conf)

    def parse_from_token_parser(self, token_parser: TokenParser) -> StringSdv:
        either_sym_name_or_string = self._sym_name_or_string_parser.parse_from_token_parser(token_parser)
        if either_sym_name_or_string.is_right():
            return either_sym_name_or_string.right()
        else:
            return parse_string.string_sdv_from_fragments(
                [symbol_syntax.symbol(either_sym_name_or_string.left())],
                parse_string.DEFAULT_CONFIGURATION.reference_restrictions,
            )


class SymbolNameOrStringRichStringParser(ParserFromTokenParserBase[Either[str, StringSdv]]):
    def __init__(self, conf: parse_string.Configuration = DEFAULT_CONFIGURATION):
        super().__init__(False, False)
        self._conf = conf
        self._plain_string_parser = parse_string.StringFromTokensParser(conf)
        self._here_doc_parser = HereDocParser(True)

    def parse_from_token_parser(self, token_parser: TokenParser) -> Either[str, StringSdv]:
        token_parser.require_has_valid_head_token(self._conf.argument_name)
        head = token_parser.head
        if head.source_string.startswith(string.HERE_DOCUMENT_MARKER_PREFIX):
            string_sdv = self._here_doc_parser.parse_from_token_parser(token_parser)
            return Either.of_right(string_sdv)
        elif TEXT_UNTIL_EOL_TOKEN_MATCHER.matches(head):
            token_parser.consume_head()
            string_sdv = parse_string.parse_rest_of_line_as_single_string(token_parser, strip_space=True)
            return Either.of_right(string_sdv)
        else:
            return self._parse_sym_ref_or_plain_string(token_parser)

    def _parse_sym_ref_or_plain_string(self, token_parser: TokenParser) -> Either[str, StringSdv]:
        head = token_parser.head

        if head.is_plain:
            mb_symbol_name = symbol_syntax.parse_maybe_symbol_reference(head.source_string)
            if mb_symbol_name is not None:
                token_parser.consume_head()
                return Either.of_left(mb_symbol_name)

        return Either.of_right(self._plain_string_parser.parse(token_parser))


class HereDocParser(ParserFromTokenParserBase[Optional[StringSdv]]):
    """
    Expects the here-document marker to be the one and only token remaining on the current line.
    Stops at the end of the final line (the line with the end marker).

    Gives a string if a here-doc is present, or None if doc is not mandatory and not present.
    """

    def __init__(self, here_document_is_mandatory: bool):
        super().__init__(False, False)
        self._here_document_is_mandatory = here_document_is_mandatory

    def parse_from_token_parser(self, token_parser: TokenParser) -> Optional[StringSdv]:
        if not self._here_document_is_mandatory and token_parser.is_at_eol:
            return None

        token_parser.require_has_valid_head_token(_rs_syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT_NAME)

        first_token = token_parser.token_stream.head
        if first_token.is_quoted:
            return _raise_not_a_here_doc_exception(token_parser.remaining_part_of_current_line)
        start_token = token_parser.consume_mandatory_token('impl: will succeed since because of check above')
        return self._parse_from_start_str(start_token.string, token_parser)

    def _parse_from_start_str(self, here_doc_start: str, token_parser: TokenParser) -> StringSdv:
        marker_match = re.fullmatch(string.HERE_DOCUMENT_TOKEN_RE, here_doc_start)
        if not marker_match:
            return _raise_not_a_here_doc_exception(here_doc_start)
        marker = marker_match.group(2)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        return self._parse_contents(marker, token_parser)

    @staticmethod
    def _parse_contents(marker: str, token_parser: TokenParser) -> StringSdv:
        here_doc = []
        while token_parser.has_current_line:
            line = token_parser.consume_remaining_part_of_current_line_as_string()
            if line == marker:
                return _sdv_from_lines(here_doc)
            here_doc.append(line)
            token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        return _raise_end_marker_not_found(marker)


def _sdv_from_lines(lines: list) -> StringSdv:
    lines_string = lines_content(lines)
    return parse_string.string_sdv_from_string(lines_string)


def _raise_not_a_here_doc_exception(source: str) -> StringSdv:
    raise SingleInstructionInvalidArgumentException('Not a {}: {}'.format(
        _rs_syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT_NAME,
        source))


def _raise_end_marker_not_found(marker: str) -> StringSdv:
    raise HereDocumentContentsParsingException(
        "{eof} reached without finding MARKER: '{m}'".format(
            eof=defs.END_OF_FILE,
            m=marker,
        )
    )
