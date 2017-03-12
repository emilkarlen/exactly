import pathlib

from exactly_lib.instructions.utils import destination_path as dp
from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import is_option_argument, ensure_is_not_option_argument
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_VARIABLE_DEFINITION_OPTION_NAME
from exactly_lib.instructions.utils.destination_path import DestinationPath
from exactly_lib.instructions.utils.relativity_root import RelOptionType
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token import TokenType
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case.value_definition import ValueReferenceOfPath
from exactly_lib.util.cli_syntax import option_parsing


def parse_destination__parse_source(options: RelOptionArgumentConfiguration,
                                    path_argument_is_mandatory: bool,
                                    source: ParseSource) -> DestinationPath:
    token_stream = TokenStream2(source.remaining_source)
    ret_val = parse_destination_path__token_stream(options, path_argument_is_mandatory, token_stream)
    source.consume(token_stream.position)
    return ret_val


def parse_destination_path__token_stream(options: RelOptionArgumentConfiguration,
                                         path_argument_is_mandatory: bool,
                                         source: TokenStream2) -> DestinationPath:
    initial_argument_string = source.remaining_part_of_current_line
    relativity_info = _parse_relativity_info(options.options, source)
    if source.is_null:
        if path_argument_is_mandatory:
            raise SingleInstructionInvalidArgumentException(
                'Missing {} argument: {}'.format(options.argument_syntax_name,
                                                 initial_argument_string))
        path_argument = pathlib.PurePath()
        return _from_relativity_info(relativity_info, path_argument)
    else:
        token = source.consume()
        if token.type is TokenType.PLAIN:
            ensure_is_not_option_argument(token.string)
        path_argument = pathlib.PurePosixPath(token.string)
        return _from_relativity_info(relativity_info, path_argument)


def _parse_relativity_info(options: RelOptionsConfiguration,
                           source: TokenStream2):
    """
    :return: Either a `RelOptionType` or a str that is the name of a value definition.
    """
    if source.is_null:
        return options.default_option
    token = source.head
    if not is_option_argument(token.source_string):
        return options.default_option

    info = _try_parse_rel_val_def_option(options, source)
    if info is not None:
        return info
    return _parse_rel_option_type(options, source)


def _try_parse_rel_val_def_option(options: RelOptionsConfiguration,
                                  source: TokenStream2) -> ValueReferenceOfPath:
    option_str = source.head.string
    if not option_parsing.matches(REL_VARIABLE_DEFINITION_OPTION_NAME, option_str):
        return None
    if not options.is_rel_val_def_option_accepted:
        return _raise_invalid_option(option_str, options)
    source.consume()
    if source.is_null:
        msg = 'Missing value definition name argument for {} option'.format(option_str)
        raise SingleInstructionInvalidArgumentException(msg)
    val_def_name = source.head.source_string
    if source.head.is_quoted:
        msg = 'Value definition name argument for {} must not be quoted: {}'.format(option_str,
                                                                                    val_def_name)
        raise SingleInstructionInvalidArgumentException(msg)
    source.consume()
    return ValueReferenceOfPath(val_def_name, options.accepted_relativity_variants)


def _parse_rel_option_type(options: RelOptionsConfiguration,
                           source: TokenStream2) -> RelOptionType:
    option_str = source.head.string
    rel_option_type = _resolve_relativity_option_type(option_str)
    if rel_option_type not in options.accepted_options:
        return _raise_invalid_option(option_str, options)
    source.consume()
    return rel_option_type


def _raise_invalid_option(actual: str, options: RelOptionsConfiguration):
    lines = ['Option cannot be used in this context: {}'.format(actual)]
    lines.extend(_valid_options_info_lines(options))
    msg = '\n'.join(lines)
    raise SingleInstructionInvalidArgumentException(msg)


def _resolve_relativity_option_type(option_argument: str) -> RelOptionType:
    for option_type in rel_opts.REL_OPTIONS_MAP:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type].option_name
        if option_parsing.matches(option_name, option_argument):
            return option_type
    raise SingleInstructionInvalidArgumentException('Invalid option: {}'.format(option_argument))


def _from_relativity_info(relativity_info, path_argument: pathlib.PurePath) -> DestinationPath:
    if isinstance(relativity_info, RelOptionType):
        return dp.from_rel_option(relativity_info, path_argument)
    elif isinstance(relativity_info, ValueReferenceOfPath):
        return dp.from_value_definition(relativity_info, path_argument)


def _valid_options_info_lines(options: RelOptionsConfiguration) -> list:
    ret_val = []
    if options.is_rel_val_def_option_accepted:
        ret_val.append('  {} VALUE-DEFINITION-NAME'.format(
            option_parsing.long_option_syntax(REL_VARIABLE_DEFINITION_OPTION_NAME.long)))
    for option_type in options.accepted_options:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type].option_name
        option_str = option_parsing.long_option_syntax(option_name.long)
        ret_val.append('  ' + option_parsing.long_option_syntax(option_str))
    return ret_val
