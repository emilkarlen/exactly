from shellcheck_lib.instructions.utils.file_ref_check import FileRefCheck, pre_eds_validate, post_eds_validate
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction


class InstructionWithFileRefsBase(SetupPhaseInstruction):
    def __init__(self,
                 file_ref_check_list_tuple: tuple):
        """
        :param file_ref_check_list_tuple: [FileRefCheck] Sequence of files to be validates
        """
        self.file_ref_check_list_tuple = file_ref_check_list_tuple

    def pre_validate(self, environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            result = pre_eds_validate(file_ref_check, environment)
            if not result.is_success:
                return result
        return svh.new_svh_success()

    def post_validate(self,
                      environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            result = post_eds_validate(file_ref_check, environment)
            if not result.is_success:
                return result
        return svh.new_svh_success()
