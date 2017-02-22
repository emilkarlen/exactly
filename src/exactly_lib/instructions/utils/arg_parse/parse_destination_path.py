import pathlib

from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import is_option_argument, ensure_is_not_option_argument
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.destination_path import DestinationType, DestinationPath
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_parse import TokenType
from exactly_lib.util.cli_syntax.option_parsing import matches


def parse_destination_pathInstrDesc(options: RelOptionArgumentConfiguration,
                                    path_argument_is_mandatory: bool,
                                    source: ParseSource) -> DestinationPath:
    source.consume_initial_space_on_current_line()
    initial_argument_string = source.remaining_part_of_current_line
    destination_type = _parse_destination_typeInstrDesc(options.options, source)
    source.consume_initial_space_on_current_line()
    if source.is_at_eol:
        if path_argument_is_mandatory:
            raise SingleInstructionInvalidArgumentException(
                'Missing {} argument: {}'.format(options.argument_syntax_name,
                                                 initial_argument_string))
        path_argument = pathlib.PurePath()
        # TODO invalid argument type to DestinationPath
        return DestinationPath(destination_type, path_argument)
    else:
        token = token_parse.parse_token_on_current_line(source)
        if token.type is TokenType.PLAIN:
            ensure_is_not_option_argument(token.string)
        path_argument = pathlib.PurePosixPath(token.string)
        return DestinationPath(destination_type, path_argument)


# TODO [instr-desc] Remove when new parser structures are fully integrated
# (perhaps should remain since there are valid usages of this variant, but then rename methods)
def parse_destination_path(options: RelOptionArgumentConfiguration,
                           path_argument_is_mandatory: bool,
                           arguments: list) -> (DestinationPath, list):
    (destination_type, remaining_arguments) = _parse_destination_type(options.options,
                                                                      arguments)
    if not remaining_arguments:
        if path_argument_is_mandatory:
            raise SingleInstructionInvalidArgumentException(
                'Missing {} argument: {}'.format(options.argument_syntax_name,
                                                 arguments))
        path_argument = pathlib.PurePath()
        return DestinationPath(destination_type, path_argument), remaining_arguments
    else:
        ensure_is_not_option_argument(remaining_arguments[0])
        path_argument = pathlib.PurePosixPath(remaining_arguments[0])
        return DestinationPath(destination_type, path_argument), remaining_arguments[1:]


def _parse_destination_type(options: RelOptionsConfiguration,
                            arguments: list) -> (DestinationType, list):
    rel_option_type = options.default_option
    if arguments and is_option_argument(arguments[0]):
        option_argument = arguments[0]
        rel_option_type = _resolve_relativity_option_type(option_argument)
        if rel_option_type not in options.accepted_options:
            msg = 'Option cannot be used in this context: {}'.format(option_argument)
            raise SingleInstructionInvalidArgumentException(msg)
        return rel_option_type, arguments[1:]
    return rel_option_type, arguments


def _parse_destination_typeInstrDesc(options: RelOptionsConfiguration,
                                     source: ParseSource) -> DestinationType:
    rel_option_type = options.default_option
    source_copy = source.copy
    if source_copy.is_at_eol:
        return rel_option_type
    token = token_parse.parse_token_on_current_line(source_copy)
    if token.type == TokenType.PLAIN and is_option_argument(token.string):
        option_argument = token.string
        rel_option_type = _resolve_relativity_option_type(option_argument)
        if rel_option_type not in options.accepted_options:
            msg = 'Option cannot be used in this context: {}'.format(option_argument)
            raise SingleInstructionInvalidArgumentException(msg)
        source.catch_up_with(source_copy)
        return rel_option_type
    return rel_option_type


def _resolve_relativity_option_type(option_argument: str) -> DestinationType:
    for option_type in rel_opts.REL_OPTIONS_MAP:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type].option_name
        if matches(option_name, option_argument):
            return option_type
    raise SingleInstructionInvalidArgumentException('Invalid option: {}'.format(option_argument))
