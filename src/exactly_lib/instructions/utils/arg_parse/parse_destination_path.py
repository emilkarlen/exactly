import pathlib

from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import is_option_argument, ensure_is_not_option_argument
from exactly_lib.instructions.utils.destination_path import DestinationType, DestinationPath
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.cli_syntax.option_parsing import matches

ALL_OPTIONS = (rel_opts.RelOptionType.REL_ACT,
               rel_opts.RelOptionType.REL_TMP)


def parse_destination_type(default_type: DestinationType,
                           arguments: list) -> (DestinationType, list):
    path_type = default_type
    if arguments and is_option_argument(arguments[0]):
        option_argument = arguments[0]
        if matches(rel_opts.REL_ACT_OPTION_NAME, option_argument):
            path_type = DestinationType.REL_ACT_DIR
        elif matches(rel_opts.REL_TMP_OPTION_NAME, option_argument):
            path_type = DestinationType.REL_TMP_DIR
        else:
            raise SingleInstructionInvalidArgumentException('Invalid option: {}'.format(option_argument))
        return path_type, arguments[1:]
    return path_type, arguments


def parse_destination_path(default_type: DestinationType,
                           path_argument_is_mandatory: bool,
                           arguments: list) -> (DestinationPath, list):
    (destination_type, remaining_arguments) = parse_destination_type(default_type, arguments)
    if not remaining_arguments:
        if path_argument_is_mandatory:
            raise SingleInstructionInvalidArgumentException('Missing PATH argument: {}'.format(arguments))
        path_argument = pathlib.PurePath()
        return DestinationPath(destination_type, path_argument), remaining_arguments
    else:
        ensure_is_not_option_argument(remaining_arguments[0])
        path_argument = pathlib.PurePosixPath(remaining_arguments[0])
        return DestinationPath(destination_type, path_argument), remaining_arguments[1:]
