import pathlib
import shlex
import shutil

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        if len(arguments) != 1:
            msg = 'Invalid number of arguments (exactly one expected), found {}'.format(str(len(arguments)))
            raise SingleInstructionInvalidArgumentException(msg)
        return _InstallSourceInstruction(arguments[0])


class _InstallSourceInstruction(SetupPhaseInstruction):
    def __init__(self,
                 source_file_name: str):
        self.source_file_name = source_file_name

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        path = self._src_path(global_environment)
        if not path.exists():
            return svh.new_svh_validation_error('File does not exist: {}'.format(str(path)))
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src = str(self._src_path(environment))
        dst = '.'
        try:
            shutil.copy2(src, dst)
            return sh.new_sh_success()
        except OSError as ex:
            return sh.new_sh_hard_error('Failed to install {}: {}'.format(src, str(ex)))

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def _src_path(self,
                  environment: GlobalEnvironmentForPreEdsStep) -> pathlib.Path:
        return environment.home_directory / self.source_file_name
