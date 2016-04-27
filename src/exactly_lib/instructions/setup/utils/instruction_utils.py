from exactly_lib.instructions.utils.file_ref_check import FileRefCheck, pre_eds_validate, pre_or_post_eds_validate
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction


class InstructionWithFileRefsBase(SetupPhaseInstruction):
    def __init__(self,
                 file_ref_check_list_tuple: tuple):
        """
        :param file_ref_check_list_tuple: [FileRefCheck] Sequence of files to be validates
        """
        self.file_ref_check_list_tuple = file_ref_check_list_tuple

    def validate_pre_eds(self, environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            if file_ref_check.file_reference.exists_pre_eds:
                result = pre_eds_validate(file_ref_check, environment)
                if not result.is_success:
                    return result
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            if not file_ref_check.file_reference.exists_pre_eds:
                result = pre_or_post_eds_validate(file_ref_check, environment.home_and_eds)
                if not result.is_success:
                    return result
        return svh.new_svh_success()
