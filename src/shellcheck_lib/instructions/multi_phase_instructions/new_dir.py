import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.general.textformat import parse as text_parse
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string, ensure_is_not_option_argument
from shellcheck_lib.test_case.instruction_description import InvokationVariant, Description
from shellcheck_lib.test_case.phases.result import sh


class TheDescription(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Makes a directory in the current directory.'

    def main_description_rest(self) -> list:
        # return single_para()
        text = """\
            Makes parent components, if needed.


            Does not fail if the given directory already exists.
            """
        return text_parse.normalize_and_parse(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant('DIRECTORY',
                              []),
        ]


def parse(argument: str) -> str:
    arguments = split_arguments_list_string(argument)
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
    try:
        if dir_path.is_dir():
            return None
    except NotADirectoryError:
        return 'Part of path exists, but is not a directory: %s' % str(dir_path)
    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return 'Path exists, but is not a directory: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Clash with existing file: {}'.format(dir_path)
    return None


def execute_and_return_sh(directory_components: str) -> sh.SuccessOrHardError:
    error_message = make_dir_in_current_dir(directory_components)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
