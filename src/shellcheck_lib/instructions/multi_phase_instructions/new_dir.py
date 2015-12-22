import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string, ensure_is_not_option_argument
from shellcheck_lib.test_case.help.instruction_description import InvokationVariant, DescriptionWithConstantValues, \
    Description


def description(instruction_name: str) -> Description:
    return DescriptionWithConstantValues(
            'Makes a directory in the current directory',
            """
            Makes parent components, if needed.


            Does not fail if the given directory already exists.
            """,
            [InvokationVariant('DIRECTORY',
                               ''),
             ],
            instruction_name=instruction_name)


def parse(argument: str) -> str:
    arguments = spit_arguments_list_string(argument)
    if len(arguments) != 1:
        raise SingleInstructionInvalidArgumentException('Usage: DIRECTORY')
    directory_argument = arguments[0]
    ensure_is_not_option_argument(directory_argument)
    return directory_argument


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
