from typing import List, Optional, Sequence, Tuple

from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import new_token_stream
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions, SymbolName
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions as _reference_restrictions
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv, StringFragmentSdv
from exactly_lib.util.either import Either
from exactly_lib.util.parse.token import Token


class Configuration:
    def __init__(self,
                 argument_name: str,
                 reference_restrictions: Optional[ReferenceRestrictions] = None):
        self.argument_name = argument_name
        self.reference_restrictions = reference_restrictions


DEFAULT_CONFIGURATION = Configuration(types.STRING_TYPE_INFO.identifier,
                                      reference_restrictions=None)


class StringFromTokensParser(ParserFromTokens[StringSdv]):
    def __init__(self, conf: Configuration):
        self._conf = conf

    def parse(self, token_parser: TokenParser) -> StringSdv:
        return parse_string_from_token_parser(token_parser, self._conf)


class SymbolReferenceOrStringParser(ParserFromTokens[Either[SymbolName, StringSdv]]):
    """Gives the name of the symbol, the token represents a single unquoted symbol reference."""

    def __init__(self, conf: Configuration):
        self._conf = conf

    def parse(self, token_parser: TokenParser) -> Either[SymbolName, StringSdv]:
        is_plain_token, fragments = parse_fragments_from_tokens__w_is_plain(token_parser.token_stream, self._conf)
        mb_just_symbol_name = _is_single_sym_ref(fragments)
        if is_plain_token and mb_just_symbol_name is not None:
            return Either.of_left(fragments[0].value)
        else:
            return Either.of_right(
                string_sdv_from_fragments(fragments, self._conf.reference_restrictions)
            )


def parse_string_sdv_from_parse_source(source: ParseSource,
                                       conf: Configuration = DEFAULT_CONFIGURATION) -> StringSdv:
    """
    :param source: Has a current line
    :raises SingleInstructionInvalidArgumentException: If cannot parse a PathDdv
    """

    ts = new_token_stream(source.remaining_part_of_current_line)
    ret_val = parse_string_sdv(ts, conf)
    source.consume(ts.position)
    return ret_val


def parse_string_from_token_parser(token_parser: TokenParser,
                                   conf: Configuration = DEFAULT_CONFIGURATION) -> StringSdv:
    """
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    return parse_string_sdv(token_parser.token_stream, conf)


def parse_rest_of_line_as_single_string(token_parser: TokenParser,
                                        strip_space: bool = False) -> StringSdv:
    argument_string = token_parser.consume_remaining_part_of_current_line_as_string()
    if strip_space:
        argument_string = argument_string.strip()
    return string_sdv_from_string(argument_string)


def parse_rest_of_line_as_single_string_and_consume_line(token_parser: TokenParser,
                                                         strip_space: bool = False) -> StringSdv:
    argument_string = token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    if strip_space:
        argument_string = argument_string.strip()
    return string_sdv_from_string(argument_string)


def parse_string_sdv(tokens: TokenStream,
                     conf: Configuration = DEFAULT_CONFIGURATION) -> StringSdv:
    """
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    fragments = parse_fragments_from_tokens(tokens, conf)
    return string_sdv_from_fragments(fragments, conf.reference_restrictions)


def parse_string_sdv_from_token(token: Token,
                                reference_restrictions: ReferenceRestrictions = None) -> StringSdv:
    fragments = parse_fragments_from_token(token)
    return string_sdv_from_fragments(fragments, reference_restrictions)


def parse_fragments_from_tokens(tokens: TokenStream,
                                conf: Configuration = DEFAULT_CONFIGURATION) -> List[symbol_syntax.Fragment]:
    """
    Consumes a single token.
    :raises SingleInstructionInvalidArgumentException: Missing argument
    """

    return parse_fragments_from_tokens__w_is_plain(tokens, conf)[1]


def parse_fragments_from_tokens__w_is_plain(
        tokens: TokenStream,
        conf: Configuration = DEFAULT_CONFIGURATION) -> Tuple[bool, List[symbol_syntax.Fragment]]:
    """
    Consumes a single token.
    :raises SingleInstructionInvalidArgumentException: Missing argument
    """

    if tokens.is_null:
        raise SingleInstructionInvalidArgumentException('Expecting {} argument'.format(conf.argument_name))
    string_token = tokens.consume()
    if string_token.is_plain and string_token.source_string in reserved_words.RESERVED_TOKENS:
        raise SingleInstructionInvalidArgumentException(
            'Illegal {}: {}'.format(conf.argument_name,
                                    string_token.source_string),
        )
    return string_token.is_plain, parse_fragments_from_token(string_token)


def parse_fragments_from_token(token: Token) -> List[symbol_syntax.Fragment]:
    if token.is_quoted and token.is_hard_quote_type:
        return [symbol_syntax.constant(token.string)]
    return symbol_syntax.split(token.string)


def parse_sym_ref_or_fragments_from_token(token: Token) -> Either[SymbolName, List[symbol_syntax.Fragment]]:
    if token.is_quoted and token.is_hard_quote_type:
        return Either.of_right([symbol_syntax.constant(token.string)])
    fragments = symbol_syntax.split(token.string)
    mb_just_symbol_name = _is_single_sym_ref(fragments)
    return (
        Either.of_left(mb_just_symbol_name)
        if token.is_plain and mb_just_symbol_name is not None
        else
        Either.of_right(fragments)
    )


def string_sdv_from_string(source: str,
                           reference_restrictions: ReferenceRestrictions = None
                           ) -> StringSdv:
    fragments = symbol_syntax.split(source)
    return string_sdv_from_fragments(fragments, reference_restrictions)


def fragment_sdv_from_fragment(fragment: symbol_syntax.Fragment,
                               reference_restrictions: ReferenceRestrictions) -> StringFragmentSdv:
    if fragment.is_constant:
        return string_sdvs.str_fragment(fragment.value)
    else:
        sr = SymbolReference(fragment.value, reference_restrictions)
        return string_sdvs.symbol_fragment(sr)


def string_sdv_from_fragments(fragments: Sequence[symbol_syntax.Fragment],
                              reference_restrictions: Optional[ReferenceRestrictions] = None,
                              ) -> StringSdv:
    if reference_restrictions is None:
        reference_restrictions = _reference_restrictions.is_any_type_w_str_rendering()
    return StringSdv(tuple([fragment_sdv_from_fragment(f, reference_restrictions)
                            for f in fragments]))


def _is_single_sym_ref(fragments: Sequence[symbol_syntax.Fragment]) -> Optional[str]:
    return (
        fragments[0].value
        if len(fragments) == 1 and fragments[0].is_symbol
        else
        None
    )
