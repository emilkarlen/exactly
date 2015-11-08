import pathlib

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string, ensure_is_not_option_argument

DESCRIPTION = Description(
    'Makes a directory in the current directory',
    """
    Makes parent components, if needed.


    Does not fail if the given directory already exists.
    """,
    [InvokationVariant('DIRECTORY',
                       ''),
     ])


def parse(source: SingleInstructionParserSource) -> str:
    arguments = spit_arguments_list_string(source.instruction_argument)
    if len(arguments) != 1:
        raise SingleInstructionInvalidArgumentException('Usage: DIRECTORY')
    argument = arguments[0]
    ensure_is_not_option_argument(argument)
    return argument


def make_dir_in_current_dir(directory_components: str) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = pathlib.Path() / directory_components
    if dir_path.is_dir():
        return None
    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return 'Path exists, but is not a directory: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Clash with existing file: {}'.format(dir_path)
    return None
