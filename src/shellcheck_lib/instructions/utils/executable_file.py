import pathlib
import stat

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.general.string import lines_content
from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.instructions.utils.file_ref import FileRefValidatorBase
from shellcheck_lib.instructions.utils.parse_utils import is_option_argument, TokenStream
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION, REL_SYSTEM_OPTION
from shellcheck_lib.test_case.sections.common import HomeAndEds


class ExecutableFile:
    def __init__(self, file_reference: file_ref.FileRef):
        self._file_reference = file_reference
        self._validator = ExistingExecutableFile(file_reference)

    def path(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        return self._file_reference.file_path_pre_or_post_eds(home_and_eds)

    def path_string(self, home_and_eds: HomeAndEds) -> str:
        return str(self.path(home_and_eds))

    @property
    def exists_pre_eds(self) -> bool:
        return self._file_reference.exists_pre_eds

    @property
    def validator(self) -> PreOrPostEdsValidator:
        return self._validator


def parse(tokens0: TokenStream) -> (ExecutableFile, TokenStream):
    """
    :param tokens0: instruction argument
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    if tokens0.is_null:
        raise SingleInstructionInvalidArgumentException('Missing EXECUTABLE argument: '.format(tokens0.source))
    first_argument_path = pathlib.PurePath(tokens0.head)
    if first_argument_path.is_absolute():
        return _executable_from_absolute_path(tokens0.head), tokens0.tail
    if not is_option_argument(tokens0.head):
        msg = 'Missing option to specify where EXECUTABLE is located. Use {}'.format(ALL_REL_OPTIONS_SYNTAX_DESCRIPTION)
        raise SingleInstructionInvalidArgumentException(msg)
    tokens1 = tokens0.tail
    if tokens1.is_null == 1:
        msg = 'Missing EXECUTABLE argument: {}'.format(tokens0.source)
        raise SingleInstructionInvalidArgumentException(msg)
    return _executable_file_from(tokens0.head, tokens1.head), tokens1.tail


def _executable_from_absolute_path(abs_path_str: str) -> ExecutableFile:
    return ExecutableFile(file_ref.absolute_file_name(abs_path_str))


def _executable_file_from(relativity_option: str, file_argument: str) -> ExecutableFile:
    if relativity_option == REL_HOME_OPTION:
        return ExecutableFile(file_ref.rel_home(file_argument))
    else:
        msg = lines_content(['Invalid option for specifying where FILE is located: {}'.format(relativity_option),
                             'Expecting {}'.format(ALL_REL_OPTIONS_SYNTAX_DESCRIPTION)])
        raise SingleInstructionInvalidArgumentException(msg)


def _empty_string_or_value(singleton_or_empty_list: list) -> str:
    return '' if not singleton_or_empty_list else singleton_or_empty_list[0]


class ExistingExecutableFile(FileRefValidatorBase):
    def _validate_path(self, file_path: pathlib.Path) -> str:
        if not file_path.is_file():
            return 'File does not exist: {}'.format(file_path)
        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return 'File is not executable. Mode is {}: {}'.format(stat.filemode(mode), file_path)
        return None


ALL_REL_OPTIONS = (REL_HOME_OPTION, REL_SYSTEM_OPTION)
ALL_REL_OPTIONS_SYNTAX_DESCRIPTION = '|'.join(ALL_REL_OPTIONS)
