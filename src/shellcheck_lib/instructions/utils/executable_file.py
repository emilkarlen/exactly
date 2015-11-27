import pathlib
import stat

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.string import lines_content
from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.instructions.utils.parse_utils import is_option_argument
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION, REL_SYSTEM_OPTION
from shellcheck_lib.test_case.sections.common import HomeAndEds


class ExecutableFile:
    def __init__(self, file_reference: file_ref.FileRef):
        self._file_reference = file_reference

    def path(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        return self._file_reference.file_path_post_eds(home_and_eds)

    def path_string(self, home_and_eds: HomeAndEds) -> str:
        return str(self.path(home_and_eds))

    @property
    def exists_pre_eds(self) -> bool:
        return self._file_reference.exists_pre_eds

    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        """
        Validates the executable if it is expected to exist pre-EDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        if self.exists_pre_eds:
            file_path = self._file_reference.file_path_pre_eds(home_dir_path)
            if not file_path.is_file():
                return 'File does not exist: {}'.format(file_path)
            stat_value = file_path.stat()
            mode = stat_value.st_mode
            if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                return 'File is not executable. Mode is {}: {}'.format(stat.filemode(mode), file_path)
        return None

    def validate_post_eds_if_applicable(self, eds: ExecutionDirectoryStructure) -> str:
        """
        Validates the executable if it is expected to NOT exist pre-EDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        if self.exists_pre_eds:
            return None
        return None

    def validate_pre_or_post_eds(self, home_and_eds: HomeAndEds) -> str:
        """
        Validates the executable using either pre- or post- EDS.
        :return: Error message iff validation failed.
        """
        error_message = self.validate_pre_eds_if_applicable(home_and_eds.home_dir_path)
        if error_message is not None:
            return error_message
        return self.validate_post_eds_if_applicable(home_and_eds.eds)


def parse_as_first_space_separated_part(arguments_string: str) -> (ExecutableFile, str):
    """
    Parses an ExecutableFile from the first part of the given arguments-string.
    Consumes just the part that makes up the file argument. The remaining part, after any separating
    space, is returned.

    Purpose is to make it possible to parse the part after the file in different way (either as a single string,
    or to split it using shell-syntax, e.g.).
    :param arguments_string: All remaining arguments as a single string - initial part is assumed to
    be the file-argument.
    :return: (file, the part of the given arguments-string that follows the file argument)
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    first_and_remaining_tokens = arguments_string.split(maxsplit=2)
    if len(first_and_remaining_tokens) < 2:
        msg = 'Invalid FILE argument syntax ({} FILE)'.format(ALL_REL_OPTIONS_SYNTAX_DESCRIPTION)
        raise SingleInstructionInvalidArgumentException(msg)
    relativity_option = first_and_remaining_tokens[0]
    file_argument = first_and_remaining_tokens[1]
    remaining_arguments_str = '' if len(first_and_remaining_tokens) == 2 else first_and_remaining_tokens[2]
    if not is_option_argument(relativity_option):
        msg = 'Missing option to specify where FILE is located. Requires {}'.format(ALL_REL_OPTIONS_SYNTAX_DESCRIPTION)
        raise SingleInstructionInvalidArgumentException(msg)
    return _executable_file_from(relativity_option, file_argument), remaining_arguments_str


def _executable_file_from(relativity_option: str, file_argument: str) -> ExecutableFile:
    if relativity_option == REL_HOME_OPTION:
        return ExecutableFile(file_ref.rel_home(file_argument))
    else:
        msg = lines_content(['Invalid option for specifying where FILE is located: {}'.format(relativity_option),
                             'Expecting {}'.format(ALL_REL_OPTIONS_SYNTAX_DESCRIPTION)])
        raise SingleInstructionInvalidArgumentException(msg)


ALL_REL_OPTIONS = (REL_HOME_OPTION, REL_SYSTEM_OPTION)
ALL_REL_OPTIONS_SYNTAX_DESCRIPTION = '|'.join(ALL_REL_OPTIONS)
