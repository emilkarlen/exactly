import pathlib
from typing import Union, Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.definitions.path import REL_SYMBOL_OPTION_NAME, REL_SOURCE_FILE_DIR_OPTION_NAME
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import is_option_argument
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions
from exactly_lib.tcfs import relative_path_options as rel_opts
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib.util.cli_syntax import option_parsing
from exactly_lib.util.parse.token import Token


def reference_restrictions_for_path_symbol(accepted_relativity_variants: PathRelativityVariants
                                           ) -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(
        PathAndRelativityRestriction(accepted_relativity_variants))


def parse_explicit_relativity_info(options: RelOptionsConfiguration,
                                   source_file_location: Optional[pathlib.Path],
                                   source: TokenStream) -> Optional[
    Union[RelOptionType, SymbolReference, pathlib.Path]]:
    """
    :return None if relativity is not given explicitly
    """
    if source.is_null:
        return None
    token = source.head
    if not is_option_argument(token.source_string):
        return None

    info = _try_parse_rel_symbol_option(options, source)
    if info is not None:
        return info
    if source_file_location is not None:
        if _parse_rel_source_file(source):
            return source_file_location

    return _parse_rel_option_type(options, source)


def _raise_invalid_argument_exception_if_symbol_does_not_have_valid_syntax(symbol_name_token: Token,
                                                                           option_str: str):
    symbol_name = symbol_name_token.source_string
    if symbol_name_token.is_quoted:
        msg = 'Symbol name argument for {} must not be quoted: {}'.format(option_str,
                                                                          symbol_name)
        raise SingleInstructionInvalidArgumentException(msg)
    if not symbol_syntax.is_symbol_name(symbol_name_token.source_string):
        msg = 'Invalid name of {symbol_concept}: {invalid_value}'.format(
            symbol_concept=SYMBOL_CONCEPT_INFO.name.singular,
            invalid_value=symbol_name_token.source_string,
        )
        raise SingleInstructionInvalidArgumentException(msg)


def _try_parse_rel_symbol_option(options: RelOptionsConfiguration,
                                 source: TokenStream) -> Optional[SymbolReference]:
    option_str = source.head.string
    if not option_parsing.matches(REL_SYMBOL_OPTION_NAME, option_str):
        return None
    source.consume()
    if source.is_null:
        msg = 'Missing symbol name argument for {} option'.format(option_str)
        raise SingleInstructionInvalidArgumentException(msg)
    _raise_invalid_argument_exception_if_symbol_does_not_have_valid_syntax(source.head, option_str)
    symbol_name = source.consume().string
    return SymbolReference(symbol_name,
                           reference_restrictions_for_path_symbol(options.accepted_relativity_variants))


def _parse_rel_option_type(options: RelOptionsConfiguration,
                           source: TokenStream) -> RelOptionType:
    option_str = source.head.string
    rel_option_type = _resolve_relativity_option_type(option_str)
    if rel_option_type not in options.accepted_options:
        return _raise_invalid_option(option_str, options)
    source.consume()
    return rel_option_type


def _parse_rel_source_file(source: TokenStream) -> bool:
    option_str = source.head.string
    if option_parsing.matches(REL_SOURCE_FILE_DIR_OPTION_NAME, option_str):
        source.consume()
        return True
    return False


def _raise_invalid_option(actual: str, options: RelOptionsConfiguration):
    lines = [
        'Illegal relativity option : {}'.format(actual),
        'Legal relativity options  :'
    ]
    lines.extend(_valid_options_info_lines(options))
    msg = '\n'.join(lines)
    raise SingleInstructionInvalidArgumentException(msg)


def _resolve_relativity_option_type(option_argument: str) -> RelOptionType:
    for option_type in rel_opts.REL_OPTIONS_MAP:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type]._option_name
        if option_parsing.matches(option_name, option_argument):
            return option_type
    raise SingleInstructionInvalidArgumentException('Invalid option: {}'.format(option_argument))


def _valid_options_info_lines(options: RelOptionsConfiguration) -> list:
    ret_val = []
    ret_val.append('  {rel_symbol_option} {symbol_syntax_element_name}'.format(
        rel_symbol_option=option_parsing.long_option_syntax(REL_SYMBOL_OPTION_NAME.long),
        symbol_syntax_element_name=instruction_arguments.SYMBOL_SYNTAX_ELEMENT_NAME))
    for option_type in options.accepted_options:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type]._option_name
        option_str = option_parsing.long_option_syntax(option_name.long)
        ret_val.append('  ' + option_str)
    return ret_val
