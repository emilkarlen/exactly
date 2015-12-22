import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string
from shellcheck_lib.test_case.help.instruction_description import InvokationVariant, DescriptionWithConstantValues
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder

DESCRIPTION = DescriptionWithConstantValues(
    'Install existing files in the home directory into the current directory.',
    """As many attributes as possible of the files are preserved (this depends on Python implementation).

    Mimics the behaviour of Unix cp, when a DESTINATION is given.
    If DESTINATION does not exist, then the source is installed under the name DESTINATION.

    If DESTINATION does exist, it must be a directory, and FILE is installed inside that directory.

    NOTE: DESTINATION:s with multiple path components are NOT handled intelligently.
    The behaviour is undefined.
    """,
    [InvokationVariant('FILE [DESTINATION]',
                       'A plain file.'),
     InvokationVariant('DIRECTORY [DESTINATION]',
                       "The directory and it's contents are installed."),
     ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = spit_arguments_list_string(source.instruction_argument)
        num_arguments = len(arguments)
        if num_arguments == 0 or num_arguments > 2:
            msg = 'Invalid number of arguments (one or two expected), found {}'.format(str(num_arguments))
            raise SingleInstructionInvalidArgumentException(msg)
        if num_arguments == 1:
            return _InstallSourceWithoutExplicitDestinationInstruction(arguments[0])
        else:
            return _InstallSourceWithExplicitDestinationInstruction(arguments[0],
                                                                    arguments[1])


class _InstallInstructionBase(SetupPhaseInstruction):
    def __init__(self,
                 source_file_name: str):
        self.source_file_name = source_file_name

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        path = self._src_path(global_environment)
        if not path.exists():
            return svh.new_svh_validation_error('File does not exist: {}'.format(str(path)))
        return svh.new_svh_success()

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self, os_services: OsServices, environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def _src_path(self,
                  environment: GlobalEnvironmentForPreEdsStep) -> pathlib.Path:
        return environment.home_directory / self.source_file_name


class _InstallSourceWithoutExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self, source_file_name: str):
        super().__init__(source_file_name)

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        cwd = pathlib.Path()
        return _install_into_directory(os_services,
                                       src_path,
                                       src_path.name,
                                       cwd)


class _InstallSourceWithExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self,
                 source_file_name: str,
                 destination_file_name: str):
        super().__init__(source_file_name)
        self.destination_file_name = destination_file_name

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        basename = src_path.name
        cwd = pathlib.Path()
        direct_target = cwd / self.destination_file_name
        if direct_target.exists():
            if direct_target.is_dir():
                return _install_into_directory(os_services,
                                               src_path,
                                               basename,
                                               direct_target)
            else:
                return sh.new_sh_hard_error('Destination file already exists: {}'.format(direct_target))
        else:
            return _install_into_directory(os_services,
                                           src_path,
                                           self.destination_file_name,
                                           cwd)


def _install_into_directory(os_services: OsServices,
                            src_file_path: pathlib.Path,
                            dst_file_name: str,
                            dst_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
    target = dst_dir_path / dst_file_name
    if target.exists():
        return sh.new_sh_hard_error('Destination already exists: {}'.format(target))
    src = str(src_file_path)
    dst = str(target)
    if src_file_path.is_dir():
        return os_services.copy_tree_preserve_as_much_as_possible(src, dst)
    else:
        return os_services.copy_file_preserve_as_much_as_possible(src, dst)
