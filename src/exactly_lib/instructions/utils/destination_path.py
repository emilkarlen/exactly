import enum
import pathlib

from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.instructions.utils.parse_utils import ensure_is_not_option_argument, \
    is_option_argument
from exactly_lib.instructions.utils.relative_path_options import REL_ACT_OPTION, REL_TMP_OPTION, RelOptionType
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException

OPTIONS = (REL_ACT_OPTION, REL_TMP_OPTION)
ALL_OPTIONS = (RelOptionType.REL_ACT, RelOptionType.REL_TMP)


class DestinationType(enum.Enum):
    REL_ACT_DIR = 0
    REL_TMP_DIR = 1
    REL_CWD = 2


class DestinationPath(tuple):
    def __new__(cls,
                destination_type: DestinationType,
                directory_argument: pathlib.PurePath):
        return tuple.__new__(cls, (destination_type, directory_argument))

    @property
    def destination_type(self) -> DestinationType:
        return self[0]

    @property
    def path_argument(self) -> pathlib.PurePath:
        return self[1]

    def root_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        if self.destination_type is DestinationType.REL_ACT_DIR:
            return eds.act_dir
        elif self.destination_type is DestinationType.REL_TMP_DIR:
            return eds.tmp.user_dir
        else:
            return pathlib.Path.cwd()

    def resolved_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        return self.root_path(eds) / self.path_argument


def parse_destination_type(default_type: DestinationType,
                           arguments: list) -> (DestinationType, list):
    path_type = default_type
    if arguments and is_option_argument(arguments[0]):
        option_argument = arguments[0]
        if option_argument == REL_ACT_OPTION:
            path_type = DestinationType.REL_ACT_DIR
        elif option_argument == REL_TMP_OPTION:
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
