import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.instruction_description import InvokationVariant, Description
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.result import svh
from shellcheck_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.util.textformat import parse as text_parse
from shellcheck_lib.util.textformat.structure.paragraph import single_para


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            Parser(),
            TheDescription(instruction_name))


class TheDescription(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Install existing files in the home directory into the current directory.'

    def main_description_rest(self) -> list:
        text = """\
            As many attributes as possible of the files are preserved (this depends on Python implementation).

            Mimics the behaviour of Unix cp, when a DESTINATION is given.
            If DESTINATION does not exist, then the source is installed under the name DESTINATION.

            If DESTINATION does exist, it must be a directory, and FILE is installed inside that directory.

            NOTE: DESTINATION:s with multiple path components are NOT handled intelligently.
            The behaviour is undefined.
            """
        return text_parse.normalize_and_parse(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'FILE [DESTINATION]',
                    single_para('A plain file.')),
            InvokationVariant(
                    'DIRECTORY [DESTINATION]',
                    single_para("The directory and it's contents are installed.")),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
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

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        path = self._src_path(environment)
        if not path.exists():
            return svh.new_svh_validation_error('File does not exist: {}'.format(str(path)))
        return svh.new_svh_success()

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def _src_path(self,
                  environment: GlobalEnvironmentForPreEdsStep) -> pathlib.Path:
        return environment.home_directory / self.source_file_name


class _InstallSourceWithoutExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self, source_file_name: str):
        super().__init__(source_file_name)

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
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
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
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
