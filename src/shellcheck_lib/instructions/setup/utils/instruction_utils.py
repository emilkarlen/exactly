from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction


class InstructionWithFileRefsBase(SetupPhaseInstruction):
    def __init__(self,
                 file_ref_list_tuple: tuple):
        self.file_ref_list_tuple = file_ref_list_tuple

    def pre_validate(self, environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for file_reference in self.file_ref_list_tuple:
            if file_reference.exists_pre_eds:
                file_path = file_reference.file_path_pre_eds(environment.home_directory)
                if not file_path.exists():
                    return svh.new_svh_validation_error('File does not exist: ' + str(file_path))
        return svh.new_svh_success()

    def post_validate(self,
                      environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        for file_reference in self.file_ref_list_tuple:
            if not file_reference.exists_pre_eds:
                file_path = file_reference.file_path_pre_eds(environment.home_directory)
                if not file_path.exists():
                    return svh.new_svh_validation_error('File does not exist: ' + str(file_path))
        return svh.new_svh_success()
