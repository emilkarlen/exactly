from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        raise NotImplementedError()


class _InstallSourceInstruction(SetupPhaseInstruction):
    def __init__(self,
                 source_file_name: str):
        self.source_file_name = source_file_name

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        pass

    def main(self, global_environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        pass

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()
