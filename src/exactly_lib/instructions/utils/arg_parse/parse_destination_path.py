import pathlib

from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import is_option_argument, ensure_is_not_option_argument
from exactly_lib.instructions.utils.destination_path import DestinationType, DestinationPath
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.cli_syntax.option_parsing import matches

ALL_OPTIONS = (rel_opts.RelOptionType.REL_ACT,
               rel_opts.RelOptionType.REL_TMP)


def parse_destination_path(default_type: rel_opts.RelOptionType,
                           path_argument_is_mandatory: bool,
                           arguments: list,
                           accepted_rel_option_types: iter = rel_opts.RelOptionType) -> (DestinationPath, list):
    (destination_type, remaining_arguments) = _parse_destination_type(default_type,
                                                                      arguments,
                                                                      accepted_rel_option_types)
    if not remaining_arguments:
        if path_argument_is_mandatory:
            raise SingleInstructionInvalidArgumentException('Missing PATH argument: {}'.format(arguments))
        path_argument = pathlib.PurePath()
        return DestinationPath(destination_type, path_argument), remaining_arguments
    else:
        ensure_is_not_option_argument(remaining_arguments[0])
        path_argument = pathlib.PurePosixPath(remaining_arguments[0])
        return DestinationPath(destination_type, path_argument), remaining_arguments[1:]


def _parse_destination_type(default_type: rel_opts.RelOptionType,
                            arguments: list,
                            accepted_rel_option_types: iter) -> (DestinationType, list):
    rel_option_type = default_type
    if arguments and is_option_argument(arguments[0]):
        option_argument = arguments[0]
        rel_option_type = _resolve_relativity_option_type(option_argument)
        if rel_option_type not in accepted_rel_option_types:
            msg = 'Option cannot be used in this context: {}'.format(option_argument)
            raise SingleInstructionInvalidArgumentException(msg)
        return rel_option_type, arguments[1:]
    return rel_option_type, arguments


def _resolve_relativity_option_type(option_argument: str) -> DestinationType:
    for option_type in rel_opts.REL_OPTIONS_MAP:
        option_name = rel_opts.REL_OPTIONS_MAP[option_type].option_name
        if matches(option_name, option_argument):
            return option_type
    raise SingleInstructionInvalidArgumentException('Invalid option: {}'.format(option_argument))
