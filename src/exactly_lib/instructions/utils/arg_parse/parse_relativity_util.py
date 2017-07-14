from exactly_lib.help_texts.file_ref import REL_SYMBOL_OPTION_NAME
from exactly_lib.instructions.utils.arg_parse.parse_utils import is_option_argument
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.symbol.restrictions.concrete_restrictions import FileRefRelativityRestriction, \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure import relative_path_options as rel_opts
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.cli_syntax import option_parsing


def parse_explicit_relativity_info(options: RelOptionsConfiguration,
                                   source: TokenStream):
    """
    :return None if relativity is not given explicitly
    
    :rtype: None|`RelOptionType`|`SymbolReference`
    """
    if source.is_null:
        return None
    token = source.head
    if not is_option_argument(token.source_string):
        return None

    info = _try_parse_rel_symbol_option(options, source)
    if info is not None:
        return info
    return _parse_rel_option_type(options, source)


def _try_parse_rel_symbol_option(options: RelOptionsConfiguration,
                                 source: TokenStream) -> SymbolReference:
    option_str = source.head.string
    if not option_parsing.matches(REL_SYMBOL_OPTION_NAME, option_str):
        return None
    if not options.is_rel_symbol_option_accepted:
        return _raise_invalid_option(option_str, options)
    source.consume()
    if source.is_null:
        msg = 'Missing symbol name argument for {} option'.format(option_str)
        raise SingleInstructionInvalidArgumentException(msg)
    symbol_name = source.head.source_string
    if source.head.is_quoted:
        msg = 'Symbol name argument for {} must not be quoted: {}'.format(option_str,
                                                                          symbol_name)
        raise SingleInstructionInvalidArgumentException(msg)
    source.consume()
    return SymbolReference(symbol_name,
                           ReferenceRestrictionsOnDirectAndIndirect(
                               FileRefRelativityRestriction(options.accepted_relativity_variants)))


def _parse_rel_option_type(options: RelOptionsConfiguration,
                           source: TokenStream) -> RelOptionType:
    option_str = source.head.string
    rel_option_type = _resolve_relativity_option_type(option_str)
    if rel_option_type not in options.accepted_options:
        return _raise_invalid_option(option_str, options)
    source.consume()
    return rel_option_type


def _raise_invalid_option(actual: str, options: RelOptionsConfiguration):
    lines = [
        'Unaccepted relativity option: {}'.format(actual),
        'Accepted relativity options:'
    ]
    lines.extend(_valid_options_info_lines(options))
    msg = '\n'.join(lines)
    raise SingleInstructionInvalidArgumentException(msg)


def _resolve_relativity_option_type(option_argument: str) -> RelOptionType:
    for option_type in rel_opts.REL_OPTIONS_MAP:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type].option_name
        if option_parsing.matches(option_name, option_argument):
            return option_type
    raise SingleInstructionInvalidArgumentException('Invalid option: {}'.format(option_argument))


def _valid_options_info_lines(options: RelOptionsConfiguration) -> list:
    ret_val = []
    if options.is_rel_symbol_option_accepted:
        ret_val.append('  {} SYMBOL-NAME'.format(
            option_parsing.long_option_syntax(REL_SYMBOL_OPTION_NAME.long)))
    for option_type in options.accepted_options:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type].option_name
        option_str = option_parsing.long_option_syntax(option_name.long)
        ret_val.append('  ' + option_str)
    return ret_val
