from exactly_lib.help_texts.entity.types import STRING_TYPE_INFO
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import new_token_stream
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_resolver import StringResolver, ConstantStringFragmentResolver, \
    StringFragmentResolver, \
    SymbolStringFragmentResolver
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.parse.token import Token


class Configuration:
    def __init__(self, argument_name: str):
        self.argument_name = argument_name


DEFAULT_CONFIGURATION = Configuration(STRING_TYPE_INFO.identifier)


def parse_string_resolver_from_parse_source(source: ParseSource,
                                            conf: Configuration = DEFAULT_CONFIGURATION) -> StringResolver:
    """
    :param source: Has a current line
    :raises SingleInstructionInvalidArgumentException: If cannot parse a FileRef
    """

    ts = new_token_stream(source.remaining_part_of_current_line)
    ret_val = parse_string_resolver(ts, conf)
    source.consume(ts.position)
    return ret_val


def parse_string_from_token_parser(token_parser: TokenParser,
                                   conf: Configuration = DEFAULT_CONFIGURATION) -> StringResolver:
    """
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    return parse_string_resolver(token_parser.token_stream, conf)


def parse_string_resolver(tokens: TokenStream,
                          conf: Configuration = DEFAULT_CONFIGURATION) -> StringResolver:
    """
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    fragments = parse_fragments_from_tokens(tokens, conf)
    return string_resolver_from_fragments(fragments)


def parse_string_resolver_from_token(token: Token,
                                     reference_restrictions: ReferenceRestrictions = None) -> StringResolver:
    fragments = parse_fragments_from_token(token)
    return string_resolver_from_fragments(fragments, reference_restrictions)


def parse_fragments_from_tokens(tokens: TokenStream,
                                conf: Configuration = DEFAULT_CONFIGURATION) -> list:
    """
    Consumes a single token.
    :raises SingleInstructionInvalidArgumentException: Missing argument
    :rtype [Fragment]
    """

    if tokens.is_null:
        raise SingleInstructionInvalidArgumentException('Missing {} argument'.format(conf.argument_name))
    string_token = tokens.consume()
    return parse_fragments_from_token(string_token)


def parse_fragments_from_token(token: Token) -> list:
    """
    :rtype [symbol_syntax.Fragment]
    """

    if token.is_quoted and token.is_hard_quote_type:
        return [symbol_syntax.Fragment(token.string, is_symbol=False)]
    return symbol_syntax.split(token.string)


def string_resolver_from_string(source: str) -> StringResolver:
    fragments = symbol_syntax.split(source)
    return string_resolver_from_fragments(fragments)


def fragment_resolver_from_fragment(fragment: symbol_syntax.Fragment,
                                    reference_restrictions: ReferenceRestrictions) -> StringFragmentResolver:
    if fragment.is_constant:
        return ConstantStringFragmentResolver(fragment.value)
    else:
        sr = SymbolReference(fragment.value, reference_restrictions)
        return SymbolStringFragmentResolver(sr)


def string_resolver_from_fragments(fragments,
                                   reference_restrictions: ReferenceRestrictions = None) -> StringResolver:
    """
    :type fragments: List of `symbol_syntax.Fragment`
    """
    if reference_restrictions is None:
        reference_restrictions = is_any_data_type()
    return StringResolver(tuple([fragment_resolver_from_fragment(f, reference_restrictions)
                                 for f in fragments]))
