import pathlib

from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import is_option_argument, ensure_is_not_option_argument
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.destination_path import DestinationPath
from exactly_lib.instructions.utils.relativity_root import RelOptionType
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token import TokenType
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.util.cli_syntax.option_parsing import matches


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
    relativity_type = _parse_relativity_type__token_stream(options.options, source)
    if source.is_null:
        if path_argument_is_mandatory:
            raise SingleInstructionInvalidArgumentException(
                'Missing {} argument: {}'.format(options.argument_syntax_name,
                                                 initial_argument_string))
        path_argument = pathlib.PurePath()
        return DestinationPath(relativity_type, path_argument)
    else:
        token = source.consume()
        if token.type is TokenType.PLAIN:
            ensure_is_not_option_argument(token.string)
        path_argument = pathlib.PurePosixPath(token.string)
        return DestinationPath(relativity_type, path_argument)


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
                            arguments: list) -> (RelOptionType, list):
    rel_option_type = options.default_option
    if arguments and is_option_argument(arguments[0]):
        option_argument = arguments[0]
        rel_option_type = _resolve_relativity_option_type(option_argument)
        if rel_option_type not in options.accepted_options:
            msg = 'Option cannot be used in this context: {}'.format(option_argument)
            raise SingleInstructionInvalidArgumentException(msg)
        return rel_option_type, arguments[1:]
    return rel_option_type, arguments


def _parse_relativity_type__token_stream(options: RelOptionsConfiguration,
                                         source: TokenStream2) -> RelOptionType:
    rel_option_type = options.default_option
    if not source.is_null:
        token = source.head
        if is_option_argument(token.source_string):
            option_argument = token.string
            rel_option_type = _resolve_relativity_option_type(option_argument)
            if rel_option_type not in options.accepted_options:
                msg = 'Option cannot be used in this context: {}'.format(option_argument)
                raise SingleInstructionInvalidArgumentException(msg)
            source.consume()
    return rel_option_type


def _resolve_relativity_option_type(option_argument: str) -> RelOptionType:
    for option_type in rel_opts.REL_OPTIONS_MAP:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type].option_name
        if matches(option_name, option_argument):
            return option_type
    raise SingleInstructionInvalidArgumentException('Invalid option: {}'.format(option_argument))
