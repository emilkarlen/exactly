from exactly_lib.help_texts.test_case.instructions.assign_symbol import STRING_TYPE
from exactly_lib.instructions.utils.arg_parse import symbol_syntax
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.symbol.concrete_restrictions import NoRestriction
from exactly_lib.symbol.string_resolver import StringResolver, ConstantStringFragmentResolver, StringFragmentResolver, \
    SymbolStringFragmentResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.value_restriction import ReferenceRestrictions


class Configuration:
    def __init__(self, argument_name: str):
        self.argument_name = argument_name


DEFAULT_CONFIGURATION = Configuration(STRING_TYPE)


def parse_string_resolver_from_parse_source(source: ParseSource,
                                            conf: Configuration = DEFAULT_CONFIGURATION) -> StringResolver:
    """
    :param source: Has a current line
    :raises SingleInstructionInvalidArgumentException: If cannot parse a FileRef
    """

    ts = TokenStream2(source.remaining_part_of_current_line)
    ret_val = parse_string_resolver(ts, conf)
    source.consume(ts.position)
    return ret_val


def parse_string_resolver(tokens: TokenStream2,
                          conf: Configuration = DEFAULT_CONFIGURATION) -> StringResolver:
    """
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    fragments = parse_fragments_from_token(tokens, conf)
    return StringResolver(tuple([fragment_resolver_from_fragment(f) for f in fragments]))


def parse_fragments_from_token(tokens: TokenStream2,
                               conf: Configuration = DEFAULT_CONFIGURATION) -> list:
    """
    Consumes a single token.
    :raises SingleInstructionInvalidArgumentException: Missing argument
    :rtype [Fragment]
    """

    if tokens.is_null:
        raise SingleInstructionInvalidArgumentException('Missing {} argument'.format(conf.argument_name))
    string_token = tokens.consume()
    if string_token.is_quoted and string_token.is_hard_quote_type:
        return [symbol_syntax.Fragment(string_token.string, is_symbol=False)]
    return symbol_syntax.split(string_token.string)


def fragment_resolver_from_fragment(fragment: symbol_syntax.Fragment) -> StringFragmentResolver:
    if fragment.is_constant:
        return ConstantStringFragmentResolver(fragment.value)
    else:
        sr = SymbolReference(fragment.value,
                             ReferenceRestrictions(direct=NoRestriction(),
                                                   indirect=None))
        return SymbolStringFragmentResolver(sr)
